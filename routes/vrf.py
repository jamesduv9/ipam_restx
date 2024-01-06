"""
Author: James Duvall
Purpose: RESTful API for creating and modifying vrfs within the IPAM
"""
from flask_restx import Namespace, Resource, fields, reqparse
from flask import jsonify, make_response
from core.authen import apikey_validate
from core.db import db
from models.vrfmodel import VRFModel


api = Namespace("api/v1/vrf",
                description="RESTful api for adding/removing/viewing vrfs")


@api.doc(security='apikey')
@api.doc(params={"id": "Optional ID representing the desired vrf"})
@api.response(200, "Success")
@api.response(409, "Conflict")
@api.route("/", strict_slashes=False)
class VRF(Resource):
    """
    flaskrestx object for handling api/v1/vrf routes
    """
    base_request_parser = reqparse.RequestParser()
    base_request_parser.add_argument(
        "X-Ipam-Apikey", location="headers", required=True)

    post_request_parser = base_request_parser.copy()
    post_request_parser.add_argument("name", location="json", required=True)

    get_request_parser = base_request_parser.copy()
    get_request_parser.add_argument("id", location="args")
    get_request_parser.add_argument("name", location="args")

    delete_request_parser = base_request_parser.copy()
    delete_request_parser.add_argument("id", location="args")
    delete_request_parser.add_argument("name", location="args")

    supernet_out_model = api.model(name="supernet_out_model", model={
        "name": fields.String(required=True, description="Name assigned to the network"),
        "network": fields.String(required=True, description="Network in CIDR format"),
        "id": fields.Integer(required=True, description="ID as assigned by DB"),
    })

    vrf_out_model = api.model("vrf_out_model", model={
        "name": fields.String(required=True, description="Name of the VRF"),
        "id": fields.Integer(required=True, description="VRF DB Primary key"),
        "supernets": fields.Nested(supernet_out_model, required=True, description="The VRF's attached supernets")
    })

    @api.doc(security='apikey')
    @api.expect(post_request_parser)
    @apikey_validate(permission_level=10)
    def post(self):
        """
        Handles the POST method, creates a vrf
        """
        args = self.post_request_parser.parse_args()
        new_vrf = VRFModel(name=args.get("name"))
        db.session.add(new_vrf)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }))

    @api.doc(security='apikey')
    @api.expect(get_request_parser)
    @api.marshal_with(vrf_out_model, envelope="data")
    @apikey_validate(permission_level=5)
    def get(self):
        """
        Handles the GET method, displays single more multiple vrfs
        """
        args = self.get_request_parser.parse_args()
        if args.get("id"):
            target_vrf = db.session.query(
                VRFModel).filter_by(id=args.get("id")).first()
            return target_vrf
        elif args.get("name"):
            target_vrf = db.session.query(
                VRFModel).filter_by(name=args.get("name")).first()
            return target_vrf
        vrfs = db.session.query(VRFModel).all()
        return vrfs

    @api.doc(security='apikey')
    @api.expect(delete_request_parser)
    @apikey_validate(permission_level=10)
    def delete(self):
        """
        Handles the DELETE method, deletes vrf and ALL subordinate supernets/subnets
        """
        args = self.delete_request_parser.parse_args()
        if args.get("id"):
            target_vrf = db.session.query(
                VRFModel).filter_by(id=args.get("id")).first()
        elif args.get("name"):
            target_vrf = db.session.query(
                VRFModel).filter_by(name=args.get("name")).first()
        else:
            return make_response(jsonify({
                "status": "Failed",
                "errors": ["No id or name provided for the vrf"]
            }))
        db.session.delete(target_vrf)
        db.session.commit()
        return make_response(jsonify({
            "status": "Success"
        }), 200)
