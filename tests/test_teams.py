from work_api.models import Team


class TestTeamDetailRetrieve:

    def test_get_team_success(self, db, client, team):
        res = client.get(f"/api/v1/teams/{team.id}")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["team"]["id"] == team.id

    def test_get_team_404(self, db, client):
        res = client.get("/api/v1/teams/1231231")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Team not found"


class TestTeamDetailGetAndUpdateAndDelete:

    def test_update_team_success(self, db, client, team):

        data = {
            "name": "updated name"
        }

        res = client.patch(f"/api/v1/teams/{team.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["team"]["id"] == team.id
        assert res_json["team"]["name"] == "updated name"

    def test_update_team_error(self, db, client, team):

        data = {
            "name": "",
            "description": "",
        }

        res = client.patch(f"/api/v1/teams/{team.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert "Field cannot be empty" in res_json["name"]
        assert "Field cannot be empty" in res_json["description"]

    def test_delete_team_success(self, db, client, team):
        res = client.delete(f"/api/v1/teams/{team.id}")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "team deleted"

    def test_delete_team_404(self, db, client, team):
        res = client.delete("/api/v1/teams/12312312")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Team not found"


class TestTeamListAndCreation:

    def test_get_teams_success(self, db, client, team):
        res = client.get("/api/v1/teams")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["teams"]
        assert len(res_json["teams"]) == 1

    def test_create_team_success(self, db, client):
        data = {
            "name": "bello",
            "description": "brutto",
        }

        original_teams_count = Team.query.count()

        res = client.post("/api/v1/teams", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert original_teams_count != Team.query.count()
        assert res_json["message"] == "team created"
        assert res_json["team"]["name"] == data["name"]
        assert res_json["team"]["description"] == data["description"]

    def test_create_team_error(self, db, client):
        data = {
            "name": "bello",
        }

        res = client.post("/api/v1/teams", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["description"][0] == "Missing data for required field."
