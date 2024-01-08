"""
Author: James Duvall
Purpose: RPC-like action on the IPAM, like getting usable address, or utilization reports
"""
from ipaddress import IPv4Network
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel
from models.subnetmodel import SubnetModel
from models.addressmodel import AddressModel


api = Namespace("api/v1/rpc",
                description="RPC-like actions on the IPAM, like getting usable address, or utilization reports")


@api.route("/getUsableAddresses", strict_slashes=False)
@api.doc(security='apikey')
class GetUsableAddress(Resource):
    """
    Handles the /api/v1/rpc/getUsableAddress route
    methods: GET
    returns the first usable, and all available addresses in a subnet
    """
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument(
        "network", location="args", type=IPv4Network)
    get_request_parser.add_argument("vrf", location="args")
    get_request_parser.add_argument("name", location="args")
    get_request_parser.add_argument("id", location="args")

    usable_address_model = api.model(name="usable_model",
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
    @api.marshal_with(usable_address_model, envelope="data")
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
            }), 404)
        usable_addresses = self.find_usable_addresses(
            target_subnet=target_subnet)
        if not usable_addresses:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["Pool for target subnet is depleted"]
            }), 409)
        return usable_addresses

@api.route("/getUsableSubnet", strict_slashes=False)
@api.doc(security='apikey')
class GetUsableSubnet(Resource):
    """
    handles the /api/v1/rpc/getUsableSubnet route
    methods: GET
    finds a usable subnet of size (cidr_length)
    """
    get_request_parser = GetUsableAddress.get_request_parser.copy()
    get_request_parser.add_argument("cidr_length", type=int, required=True)
    get_request_parser.add_argument("all", type=bool)

    usable_subnet_model = api.model("usable_subnets", model={
        "first_usable": fields.String(),
        "all_usable": fields.List(fields.String)
    })

    @staticmethod
    def find_usable_subnet(supernet: SupernetModel, cidr_length: int, all_: bool=False):
        """
        Takes in a supernet, cidr length, and optional all boolean
        finds the first available subnet of size cidr_length if all != True
        finds all available subnets of size cidr length is all == True
        """
        staging_data = {"first_usable": None}
        usable_subnets = []
        subnets = [subnet.network for subnet in supernet.subnets]
        for supernet_subnet in supernet.network.subnets(new_prefix=cidr_length):
            if not any(supernet_subnet.overlaps(existing_subnet) for existing_subnet in subnets):
                usable_subnets.append(str(supernet_subnet))
        
        if not usable_subnets:
            return None
        
        if all_:
            staging_data["all_usable"] = usable_subnets

        staging_data["first_usable"] = str(usable_subnets[0])

        return staging_data

    @api.expect(get_request_parser)
    @api.doc(security='apikey')
    @api.marshal_with(usable_subnet_model, envelope="data")
    @apikey_validate(permission_level=5)
    def get(self):
        """
        handles the GET method
        """
        args = self.get_request_parser.parse_args()
        if args.get("network") and args.get("vrf"):
            target_vrf = db.session.query(VRFModel).filter_by(
                name=args.get("vrf")).first()
            target_supernet = db.session.query(SupernetModel).filter_by(
                network=IPv4Network(args.get("network"))).filter_by(vrf=target_vrf).first()

        elif args.get("id"):
            target_supernet = db.session.query(
                SupernetModel).filter_by(id=args.get("id")).first()

        elif args.get("name"):
            target_supernet = db.session.query(SupernetModel).filter_by(
                name=args.get("name")).first()

        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["Not enough information provided to find supernet",
                           "Please provide supernet.network+supernet.vrf, supernet.name, or supernet.id"]
            }), 404)
        
        usable_subnet = self.find_usable_subnet(target_supernet, int(args.get("cidr_length")), all_=args.get("all"))

        return usable_subnet

