from flask import Blueprint
from flask_restful import Api

from .resources import SwaggerView
from .resources import EmployeeDetailResource, EmployeeListResource
from .resources import TeamDetailResource, TeamListResource
from .resources import HolidayDetailResource, HolidayListResource


api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_blueprint)

# Swagger API
api.add_resource(SwaggerView, '/docs', methods=["GET"])

# Employee apis
api.add_resource(EmployeeDetailResource, '/employees/<int:employee_id>')
api.add_resource(EmployeeListResource, '/employees')

# Team apis
api.add_resource(TeamDetailResource, '/teams/<int:team_id>')
api.add_resource(TeamListResource, '/teams')

# Holiday apis
api.add_resource(HolidayDetailResource, '/holidays/<int:holiday_id>')
api.add_resource(HolidayListResource, '/holidays')
