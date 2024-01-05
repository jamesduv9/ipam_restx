from flask_restx import Api
from routes.supernet import api as supernet_ns


api = Api(
    title='IPAM API',
    version='1.0',
    description='Version 1 of IPAM API',
)

api.add_namespace(ns=supernet_ns)