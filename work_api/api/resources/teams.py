from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from work_api.models import Team
from work_api.api.schemas import TeamSchema


class TeamDetailResource(Resource):

    def get(self, team_id):
        schema = TeamSchema()
        team = Team.get_team(team_id)
        return {'team': schema.dump(team)}

    def patch(self, team_id):
        team = Team.get_team(team_id)
        schema = TeamSchema(partial=True, instance=team)

        try:
            team = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        team.save()
        return {'message': 'team updated', 'team': schema.dump(team)}

    def delete(self, team_id):
        team = Team.get_team(team_id)
        team.delete()
        return {'message': 'team deleted'}


class TeamListResource(Resource):
    """Creation and get_all"""

    def get(self):
        schema = TeamSchema(many=True)
        teams = Team.get_teams()
        return {"teams": schema.dump(teams)}

    def post(self):
        try:
            schema = TeamSchema()
            team = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        team.save()
        return {'message': 'team created', 'team': schema.dump(team)}, 201
