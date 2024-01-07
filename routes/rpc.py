"""
Author: James Duvall
Purpose: RPC-like action on the IPAM, like getting usable address, or utilization reports
"""
from ipaddress import IPv4Address, IPv4Network
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel
from models.subnetmodel import SubnetModel
from models.addressmodel import AddressModel


api = Namespace("api/v1/rpc",
                description="RPC-like action on the IPAM, like getting usable address, or utilization reports")


@api.route("/getUsableAddresses", strict_slashes=False)
@api.doc(security='apikey')
class UsableAddress(Resource):
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument(
        "network", location="args", type=IPv4Network)
    get_request_parser.add_argument("vrf", location="args")
    get_request_parser.add_argument("name", location="args")
    get_request_parser.add_argument("id", location="args")

    usable_model = api.model(name="usable_model",
                             model={
                                 "first_usable": fields.String,
                                 "all_usable": fields.List(fields.String),
                                 "percent_utilized": fields.Integer,
                             }
                             )

    @staticmethod
    def find_usable_addresses(target_subnet: SubnetModel) -> str:
        """
        Takes in a SubnetModel object, and parses through the db to find an available address
        """
        used_addresses = [str(address.address) for address in db.session.query(
            AddressModel).filter_by(subnet=target_subnet).all()]

        staging_data = {"first_usable": "",
                        "percent_utilized": 0}
        all_usable = []
        for host in target_subnet.network.hosts():
            host_str = str(host)
            if host_str not in used_addresses:
                if not staging_data.get("first_usable"):
                    staging_data["first_usable"] = host_str
                all_usable.append(host_str)
        
        total_addresses = len(list(target_subnet.network.hosts()))
        used_count = len(used_addresses)
        staging_data["percent_utilized"] = int((used_count / total_addresses) * 100) if total_addresses > 0 else 0

        staging_data['all_usable'] = all_usable
        return staging_data

    @api.doc(security='apikey')
    @api.expect(get_request_parser)
    @api.marshal_with(usable_model, envelope="data")
    @apikey_validate(permission_level=5)
    def get(self):
        """
        handles GET method
        Takes a subnet by id, name, or vrf+network
        returns first usable Address
        """
        args = self.get_request_parser.parse_args()
        if args.get("network") and args.get("vrf"):
            target_vrf = db.session.query(VRFModel).filter_by(
                name=args.get("vrf")).first()
            target_subnet = db.session.query(SubnetModel).filter_by(
                network=IPv4Network(args.get("network"))).filter_by(vrf=target_vrf).first()

        elif args.get("id"):
            target_subnet = db.session.query(
                SubnetModel).filter_by(id=args.get("id")).first()

        elif args.get("name"):
            target_subnet = db.session.query(SubnetModel).filter_by(
                name=args.get("name")).first()

        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["Not enough information provided to find subnet",
                           "Please provide subnet.network+subnet.vrf, subnet.name, or subnet.id"]
            }))

        if not target_subnet:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["Unable to find requested subnet"]
            }))
        usable_addresses = self.find_usable_addresses(
            target_subnet=target_subnet)
        if not usable_addresses:
            return jsonify({
                "status": "Failed",
                "errors": ["Pool for target subnet is depleted"]
            })
        return usable_addresses
