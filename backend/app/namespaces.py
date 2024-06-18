from routes.api import api as api_namespace
from routes.profile import profile_ns

def register_namespaces(api):
    api.add_namespace(api_namespace, path='/api/v1')
    api.add_namespace(profile_ns, path='/api/v1/profile')