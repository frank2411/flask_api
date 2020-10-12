from work_api.models import Employee


class TestTeamDetailRetrieve:

    def test_get_team_success(self, db, client, employee):
        res = client.get(f"/api/v1/employees/{employee.id}")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["employee"]["id"] == employee.id
        assert res_json["employee"]["team"] == employee.team.id

    def test_get_team_404(self, db, client):
        res = client.get("/api/v1/employees/1231231")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Employee not found"


class TestTeamDetailGetAndUpdateAndDelete:

    def test_update_employee_success(self, db, client, employee):

        data = {
            "email": "updated@email.com"
        }

        res = client.patch(f"/api/v1/employees/{employee.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["employee"]["id"] == employee.id
        assert res_json["employee"]["email"] == "updated@email.com"

    def test_update_employee_error(self, db, client, employee):

        data = {
            "email": "",
        }

        res = client.patch(f"/api/v1/employees/{employee.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert "Field cannot be empty" in res_json["email"]

    def test_delete_employee_success(self, db, client, employee):
        res = client.delete(f"/api/v1/employees/{employee.id}")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "employee deleted"

    def test_delete_team_404(self, db, client):
        res = client.delete("/api/v1/employees/12312312")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Employee not found"


class TestEmployeeListAndCreation:

    def test_get_employees_success(self, db, client, employee):
        res = client.get("/api/v1/employees")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["employees"]
        assert len(res_json["employees"]) == 1

    def test_create_employee_success(self, db, client, team):
        data = {
            "email": "another@email.com",
            "team": team.id,
        }

        original_teams_count = Employee.query.count()

        res = client.post("/api/v1/employees", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert original_teams_count != Employee.query.count()
        assert res_json["message"] == "employee created"
        assert res_json["employee"]["email"] == data["email"]
        assert res_json["employee"]["team"] == data["team"]

    def test_create_employee_error(self, db, client):
        data = {
            "email": "another@email.com",
        }

        res = client.post("/api/v1/employees", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["team"][0] == "Missing data for required field."

    def test_create_employee_error_nonexistent_team(self, db, client):
        data = {
            "email": "another@email.com",
            "team": 123123
        }

        res = client.post("/api/v1/employees", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["team"][0] == "Related Object doesn't exist in DB"
