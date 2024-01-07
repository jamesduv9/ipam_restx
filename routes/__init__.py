"""
Author: James Duvall
Purpose: Configures the Api object and adds namespaces 
"""

from flask import jsonify, make_response
from flask_restx import Api
from sqlalchemy.exc import IntegrityError
from sqlite3 import IntegrityError as SQLIE
from routes.vrf import api as vrf_ns
from routes.supernet import api as supernet_ns
from routes.subnet import api as subnet_ns
from routes.address import api as address_ns
from routes.rpc import api as rpc_ns

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Ipam-Apikey'
    }
}
api = Api(
    title='IPAM API',
    version='1.0',
    description='Version 1 of IPAM API',
    authorizations=authorizations,
    doc="/docs"
)

@api.errorhandler(AttributeError)
@api.errorhandler(IntegrityError)
@api.errorhandler(SQLIE)
def conflict_errorhandler(error):
    return {"status": "Failed", "errors": [str(error)]}, 409

api.add_namespace(ns=vrf_ns)
api.add_namespace(ns=supernet_ns)
api.add_namespace(ns=subnet_ns)
api.add_namespace(ns=address_ns)
api.add_namespace(ns=rpc_ns)




