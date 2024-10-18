from flask import Blueprint
from flask_restful import Api
from App.Api.wrapper.api import CreateRuleResource, CombineRulesResource, EvaluateRuleResource, GetAllRulesResource

route = Blueprint('route', __name__)
api_v1 = Api(route)

# New routes
api_v1.add_resource(CreateRuleResource, '/create')

api_v1.add_resource(CombineRulesResource, '/combine_rules')

api_v1.add_resource(EvaluateRuleResource, '/eval')

api_v1.add_resource(GetAllRulesResource, '/getRules')
