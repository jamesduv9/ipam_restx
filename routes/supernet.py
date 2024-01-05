"""
Author: James Duvall
Purpose: RESTful API for creating and modifying supernets within the IPAM
"""
from ipaddress import IPv4Network
from flask_restx import Namespace, Resource, fields, reqparse, abort
from flask import jsonify
from core.authen import apikey_validate
from core.db import db
from models.supernetmodel import SupernetModel


api = Namespace("api/v1/supernet",
                description="RESTful api for adding/removing/viewing available supernets")


@api.doc(params={"id": "Optional ID representing the desired network"})
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
    post_request_parser.add_argument("network", location="json", required=True)
    post_request_parser.add_argument("name", location="json", required=True)

    get_request_parser = base_request_parser.copy()
    get_request_parser.add_argument("id", location="args")

    delete_request_parser = base_request_parser.copy()
    delete_request_parser.add_argument("id", location="args", required=True)

    supernet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True),
        "id": fields.Integer
    })

    @staticmethod
    def check_for_network_conflict(provided_network: str) -> bool:
        """
        Converts the provided str network into an IPv4 network and checks if
        the provided network if already apart of an existing supernet
        """
        provided_network = IPv4Network(provided_network)
        all_networks = [
            network.network for network in db.session.query(SupernetModel).all()]
        conflict = any(map(lambda net: provided_network.subnet_of(
            net) or provided_network == net, all_networks))
        if conflict:
            return True
        return False

    @staticmethod
    def check_for_supernet(provided_network: str) -> bool:
        """
        Converts the provided str network into an IPv4 network and checks if
        the provided network already exists
        """
        provided_network = IPv4Network(provided_network)
        all_networks = [
            network.network for network in db.session.query(SupernetModel).all()]
        if provided_network in all_networks:
            return True
        return False
    
    @api.expect(base_request_parser)
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
            if not net:
                return jsonify({
                    "status": "Failed",
                    "errors": [f"network not found with provided id {args.get('id')}"]
                }), 404
            return net
        all_nets = db.session.query(SupernetModel).all()
        return all_nets

    @api.expect(post_request_parser)
    @api.doc(params={"network": "Network in CIDR format ex. 10.1.1.0/24"})
    @apikey_validate(permission_level=10)
    def post(self):
        """
        Handles the POST method, Idempotent add of a supernet
        ensures no supernet exists that already covers provided supernet  
        """
        args = self.post_request_parser.parse_args()
        if self.check_for_supernet(args.get("network")):
            return jsonify({
                "status": "Failed",
                "errors": ["Supernet already exists"]
            })
        if self.check_for_network_conflict(args.get("network")):
            return jsonify({
                "status": "Failed",
                "errors": ["provided network is already a subset of another supernet"]
            })
        new_supernet = SupernetModel(name=args.get("name"),
                                     network=args.get("network"),
                                     )
        db.session.add(new_supernet)
        db.session.commit()
        return jsonify({
            "status": "Success"
        })

    @api.expect(delete_request_parser)
    @api.doc(params={"id": "id of the network you wish to delete"})
    @apikey_validate(permission_level=10)
    def delete(self):
        """
        Handles the DELETE method, must provide an id
        """
        args = self.delete_request_parser.parse_args()
        target_supernet = db.session.query(SupernetModel).filter_by(id=args.get("id")).first()
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
        