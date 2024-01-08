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

    post_request_parser = base_request_parser.copy()
    post_request_parser.add_argument(
        "address", location="json", required=True, type=IPv4Address)
    post_request_parser.add_argument("name", location="json", required=True)
    post_request_parser.add_argument("vrf", location="json", default="Global")

    get_request_parser = base_request_parser.copy()
    get_request_parser.add_argument("id", location="args")
    get_request_parser.add_argument("name", location="args")
    get_request_parser.add_argument("vrf", location="args")

    delete_request_parser = base_request_parser.copy()
    delete_request_parser.add_argument("id", location="args")
    delete_request_parser.add_argument("name", location="args")

    patch_request_parser = get_request_parser.copy()
    patch_request_parser.remove_argument("vrf")
    patch_request_parser.add_argument("mac_address", location="json")
    patch_request_parser.add_argument(
        "name", location="json", dest="target_name")

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

    @api.doc(security='apikey')
    @api.expect(get_request_parser)
    @api.marshal_with(address_out_model, envelope="data")
    @api.doc(params={"id": "id of the address you want to see details of", 
                     "name": "name of the address you want to see details", "vrf": "vrf you are wanting to see address info from"})
    @apikey_validate(permission_level=5)
    def get(self):
        """
        handles the GET method
        Takes optional ID or name, without will return all addresses
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            addr = db.session.query(AddressModel).filter_by(
                id=args.get("id")).first()
            return addr
        elif args.get("name"):
            addr = db.session.query(AddressModel).filter_by(
                name=args.get("name")).first()
            return addr
        if args.get("vrf"):
            target_vrf = db.session.query(VRFModel).filter_by(
                name=args.get("vrf")).first()
            all_addrs = db.session.query(
                AddressModel).filter_by(vrf=target_vrf).all()
        else:
            all_addrs = db.session.query(AddressModel).all()
        return all_addrs

    @api.doc(security='apikey')
    @api.expect(delete_request_parser)
    @api.doc(params={"id": "id of the address you wish to delete", "name": "name of address to delete"})
    @apikey_validate(permission_level=10)
    def delete(self):
        """
        Handles the DELETE method
        Removes address from db based on id or name
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            address = db.session.query(AddressModel).filter_by(
                id=args.get("id")).first()

        elif args.get("name"):
            address = db.session.query(AddressModel).filter_by(
                name=args.get("name")).first()
        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["No address found with provided id or name"]
            }), 404)
        db.session.delete(address)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }))

    @api.doc(security='apikey')
    @api.expect(patch_request_parser)
    @apikey_validate(permission_level=10)
    @api.doc(params={"id": "id of the address you wish to modify (id or name required)",
                     "name": "name of address to delete (id or name required) - In query string to identify address you want to change, in payload set the new value",
                     "mac_address": "Set the MAC address associated with the address"})
    def patch(self):
        """
        Handles the PATCH method
        Allows modification of mac_address and name fields
        Finds target address from query string, changes based on payload
        """
        args = self.patch_request_parser.parse_args()
        if args.get("id"):
            address = db.session.query(AddressModel).filter_by(
                id=args.get("id")).first()
        elif args.get("name"):
            address = db.session.query(AddressModel).filter_by(
                name=args.get("name")).first()
        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["No address found with provided id or name"]
            }), 404)
        if args.get("mac_address"):
            address.mac_address = args.get("mac_address")
        if args.get("target_name"):
            address.name = args.get("target_name")
        db.session.add(address)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success",
        }))
