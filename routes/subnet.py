"""
Author: James Duvall
Purpose: RESTful API for creating and modifying subnets within the IPAM
"""
from ipaddress import IPv4Network
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel
from models.subnetmodel import SubnetModel

api = Namespace("api/v1/subnet",
                description="RESTful api for adding/removing/viewing subnets")


@api.doc(params={"id": "Optional ID representing the desired network"})
@api.doc(security='apikey')
@api.response(200, "Success")
@api.response(409, "Conflict")
@api.route("/", strict_slashes=False)
class Subnet(Resource):
    """
    Handles the route /api/v1/subnet
    methods: GET, POST, DELETE
    """
    base_request_parser = reqparse.RequestParser()
    base_request_parser.add_argument(
        "X-Ipam-Apikey", location="headers", required=True)

    post_request_parser = base_request_parser.copy()
    post_request_parser.add_argument("network", location="json", required=True)
    post_request_parser.add_argument("name", location="json", required=True)
    post_request_parser.add_argument("vrf", location="json", default="Global")

    get_request_parser = base_request_parser.copy()
    get_request_parser.add_argument("id", location="args")
    get_request_parser.add_argument("name", location="args")

    delete_request_parser = base_request_parser.copy()
    delete_request_parser.add_argument("id", location="args")
    delete_request_parser.add_argument("name", location="args")

    

    vrf_out_model = api.model('vrf_out_model', {
        'name': fields.String(description='VRF name')
    })
    supernet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
    })
    subnet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
        "vrf": fields.Nested(vrf_out_model, required=True, description="VRF assigned"),
        "supernet": fields.Nested(supernet_out_model, required=True, description="Assigned supernet")
    })

    @staticmethod
    def find_supernet(provided_network: str, provided_vrf: str) -> SupernetModel:
        """
        Queries the db for all supernets in the provided vrf
        finds the supernet that covers the requested subnet
        returns that supernet
        """
        provided_network = IPv4Network(provided_network)
        vrf = db.session.query(VRFModel).filter_by(name=provided_vrf).first()
        if not vrf:
            return False
        supernets = db.session.query(SupernetModel).filter_by(vrf=vrf).all()
        for supernet in supernets:
            if provided_network.subnet_of(supernet.network):
                return supernet

        return False

    @staticmethod
    def check_for_network_conflict(provided_network: str, provided_vrf: str) -> bool:
        """
        Converts the provided str network into an IPv4 network and checks if
        the provided network is already a part of an existing supernet or encompasses any existing network.
        """
        provided_network = IPv4Network(provided_network)
        provided_vrf_model = db.session.query(
            VRFModel).filter_by(name=provided_vrf).first()
        all_networks = [
            IPv4Network(network.network) for network in db.session.query(SubnetModel).filter_by(vrf=provided_vrf_model).all()
        ]

        conflict = any(
            net.subnet_of(provided_network) or
            net.supernet_of(provided_network) or
            net == provided_network
            for net in all_networks
        )

        return conflict
    
    @api.doc(security='apikey')
    @api.expect(get_request_parser)
    @api.doc(params={"id": "id of the network you wish to get"})
    @api.marshal_with(subnet_out_model, envelope="data")
    @apikey_validate(permission_level=5)
    def get(self):
        """
        Handles the GET method
        returns subnets and subordinate addresses based on provided name or id
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            subnet = db.session.query(SubnetModel).filter_by(id=args.get("id")).first()
            return subnet
        elif args.get("name"):
            subnet = db.session.query(SubnetModel).filter_by(name=args.get("name")).first()
            return subnet
        subnets = db.session.query(SubnetModel).all()
        return subnets

    @api.doc(security='apikey')
    @api.expect(post_request_parser)
    @apikey_validate(permission_level=10)
    def post(self):
        """
        Handles the POST method
        Creates subnets and autoassigns it to it's respective supernet
        """
        args = self.post_request_parser.parse_args()
        if self.check_for_network_conflict(provided_network=args.get("network"),
                                        provided_vrf=args.get("vrf")):
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["Subnet already exists, or is within another subnet's range"]
            }), 409)

        supernet = self.find_supernet(provided_network=args.get("network"),
                                    provided_vrf=args.get("vrf"))
        if not supernet:
            return make_response(jsonify({
                "status": "Failed",
                "errors": [f"No supernet exists within vrf {args.get('vrf')} that matches the provided subnet"]
            }), 400)

        vrf_instance = db.session.query(VRFModel).filter_by(name=args.get("vrf")).first()
        if not vrf_instance:
            return make_response(jsonify({
                "status": "Failed",
                "errors": [f"VRF {args.get('vrf')} not found"]
            }), 400)

        new_subnet = SubnetModel(
            name=args.get("name"),
            vrf=vrf_instance,
            network=str(IPv4Network(args.get("network")))
        )
        new_subnet.supernet = supernet
        db.session.add(new_subnet)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }), 200)

    @api.doc(security='apikey')
    @api.expect(delete_request_parser)
    @api.doc(params={"id": "id of the network you wish to delete"})
    @apikey_validate(permission_level=10)
    def delete(self):
        """
        Handles the DELETE method
        Removes subnet from db based on id or name
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            subnet = db.session.query(SubnetModel).filter_by(id=args.get("id")).first()

        elif args.get("name"):
            subnet = db.session.query(SubnetModel).filter_by(name=args.get("name")).first()
        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["No subnet found with provided id or name"]
            }), 404)
        db.session.delete(subnet)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }))