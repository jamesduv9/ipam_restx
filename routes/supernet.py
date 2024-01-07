"""
Author: James Duvall
Purpose: RESTful API for creating and modifying supernets within the IPAM
"""
from ipaddress import IPv4Network
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel


api = Namespace("api/v1/supernet",
                description="RESTful api for adding/removing/viewing available supernets")


@api.doc(params={"id": "Optional ID representing the desired network"})
@api.doc(security='apikey')
@api.response(200, "Success")
@api.response(409, "Conflict")
@api.route("/", strict_slashes=False)
class Supernet(Resource):
    """
    Supernet Object defines http methods of the /api/v1/supernet route
    """
    base_request_parser = reqparse.RequestParser()
    base_request_parser.add_argument(
        "X-Ipam-Apikey", location="headers", required=True)

    post_request_parser = base_request_parser.copy()
    post_request_parser.add_argument("network", location="json", required=True, type=IPv4Network)
    post_request_parser.add_argument("name", location="json", required=True)
    post_request_parser.add_argument("vrf", location="json", default="Global")

    get_request_parser = base_request_parser.copy()
    get_request_parser.add_argument("id", location="args")
    get_request_parser.add_argument("name", location="args")

    delete_request_parser = base_request_parser.copy()
    delete_request_parser.add_argument("id", location="args")
    delete_request_parser.add_argument("name", location="args")

    vrf_out_model = api.model('vrf_out_model', {
        'name': fields.String(description='VRF name'),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
    })

    subnet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
    })

    supernet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
        "vrf": fields.Nested(vrf_out_model, required=True, description="VRF name associated to supernet"),
        "subnets": fields.Nested(subnet_out_model, required=True, description="All subnets associated to this supernet")
    })

    @staticmethod
    def check_for_network_conflict(provided_network: str, provided_vrf: str) -> bool:
        """
        Converts the provided str network into an IPv4 network and checks if
        the provided network is already a part of an existing supernet or encompasses any existing network.
        """
        provided_network = IPv4Network(provided_network)
        provided_vrf_model = db.session.query(VRFModel).filter_by(name=provided_vrf).first()
        all_networks = [
            IPv4Network(network.network) for network in db.session.query(SupernetModel).filter_by(vrf=provided_vrf_model).all()
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
    @api.marshal_with(supernet_out_model, envelope="data")
    @apikey_validate(permission_level=5)
    def get(self):
        """
        Handles the GET method, provides specific supernet object details, 
        or specific through the id query param
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            net = db.session.query(SupernetModel).filter_by(
                id=args.get("id")).first()
            return net
        elif args.get("name"):
            net = db.session.query(SupernetModel).filter_by(
                name=args.get("name")).first()
            return net
        all_nets = db.session.query(SupernetModel).all()
        return all_nets

    @api.doc(security='apikey')
    @api.expect(post_request_parser)
    @api.doc(params={"network": "Network in CIDR format ex. 10.1.1.0/24"})
    @apikey_validate(permission_level=10)
    def post(self):
        """
        Handles the POST method, Idempotent add of a supernet
        ensures no supernet exists that already covers provided supernet  
        """
        args = self.post_request_parser.parse_args()
        associated_vrf = db.session.query(VRFModel).filter_by(name=args.get('vrf')).first()
        if not associated_vrf:
            return make_response(jsonify({
                "status": "Failed",
                "errors": [f"Provided VRF {args.get('vrf')} does not exist"]
            }), 404)

        if self.check_for_network_conflict(provided_network=args.get("network"), provided_vrf=args.get('vrf')):
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["provided network is already a subset of another supernet"]
            }), 409)

        new_supernet = SupernetModel(name=args.get("name"),
                                     network=args.get("network"),
                                     )
        new_supernet.vrf = associated_vrf
        db.session.add(new_supernet)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }))

    @api.doc(security='apikey')
    @api.expect(delete_request_parser)
    @api.doc(params={"id": "id of the network you wish to delete", "name": "name of item to delete"})
    @apikey_validate(permission_level=10)
    def delete(self):
        """
        Handles the DELETE method, must provide an id or name
        """
        args = self.delete_request_parser.parse_args()
        if args.get("id"):
            target_supernet = db.session.query(SupernetModel).filter_by(id=args.get("id")).first()
        elif args.get("name"):
            target_supernet = db.session.query(SupernetModel).filter_by(name=args.get("name")).first()
        if not target_supernet:
            return jsonify({
                "status": "Failed",
                "errors": ["Provided subnet id does not exist"]
            })
        db.session.delete(target_supernet)
        db.session.commit()
        return jsonify({
            "status": "Success"
        })
        