from flask import jsonify
from flask_restx import Api
from sqlalchemy.exc import IntegrityError
from routes.supernet import api as supernet_ns
from routes.vrf import api as vrf_ns

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
    authorizations=authorizations
)
api.add_namespace(ns=supernet_ns)
api.add_namespace(ns=vrf_ns)

@api.errorhandler(IntegrityError)
def conflict_errorhandler(error):
    return jsonify({
        "status": "Failed",
        "errors": [str(error)]
    })


