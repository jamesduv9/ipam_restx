"""
Author: James Duvall
Purpose: RESTful API for creating and modifying addresses within the IPAM
"""
from ipaddress import IPv4Address
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel
from models.subnetmodel import SubnetModel
from models.addressmodel import AddressModel

api = Namespace("api/v1/address",
                description="RESTful api for adding/removing/viewing addresses")


@api.doc(params={"id": "Optional ID representing the desired network"})
@api.doc(security='apikey')
@api.response(200, "Success")
@api.response(409, "Conflict")
@api.route("/", strict_slashes=False)
class Address(Resource):
    """
    Handles the route /api/v1/address
    methods: GET, POST, DELETE
    """
    base_request_parser = reqparse.RequestParser()
    base_request_parser.add_argument(
        "X-Ipam-Apikey", location="headers", required=True)

    post_request_parser = base_request_parser.copy()
    post_request_parser.add_argument("address", location="json", required=True)
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
        "id": fields.Integer(required=True, description="ID as assigned by DB")
    })
    subnet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
    })
    address_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "address": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
        "vrf": fields.Nested(vrf_out_model, required=True, description="VRF assigned"),
        "subnet": fields.Nested(subnet_out_model, required=True, description="Assigned supernet")
    })

    @staticmethod
    def find_subnet(provided_address: str, provided_vrf: str) -> SubnetModel:
        """
        Queries the db for all supernets in the provided vrf
        finds the supernet that covers the requested subnet
        returns that supernet
        """
        provided_address = IPv4Address(provided_address)
        vrf = db.session.query(VRFModel).filter_by(name=provided_vrf).first()
        if not vrf:
            return False
        subnets = db.session.query(SubnetModel).filter_by(vrf=vrf).all()
        for subnet in subnets:
            if provided_address in subnet.network:
                return subnet

        return False


    @api.doc(security='apikey')
    @api.expect(post_request_parser)
    @apikey_validate(permission_level=10)
    def post(self):
        """
        Handles the POST method
        Creates addresses and autoassigns it to it's respective subnet
        """
        args = self.post_request_parser.parse_args()


        subnet = self.find_subnet(provided_address=args.get("address"),
                                  provided_vrf=args.get("vrf"))
        if not subnet:
            return make_response(jsonify({
                "status": "Failed",
                "errors": [f"No subnet exists within vrf {args.get('vrf')} that matches the provided address"]
            }), 400)

        vrf_instance = db.session.query(VRFModel).filter_by(
            name=args.get("vrf")).first()
        if not vrf_instance:
            return make_response(jsonify({
                "status": "Failed",
                "errors": [f"VRF {args.get('vrf')} not found"]
            }), 400)

        new_subnet = AddressModel(
            name=args.get("name"),
            vrf=vrf_instance,
            address=str(IPv4Address(args.get("address")))
        )
        new_subnet.subnet = subnet
        db.session.add(new_subnet)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }), 200)
