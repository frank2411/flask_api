class TestHolidayDetailRetrieve:

    def test_get_holiday_unpaid_success(self, db, client, unpaid_holiday):
        res = client.get(f"/api/v1/holidays/{unpaid_holiday.id}")
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holiday"]["id"] == unpaid_holiday.id
        assert res_json["holiday"]["employee"] == unpaid_holiday.employee.id
        assert res_json["holiday"]["holiday_type"] == "unpaid"
        assert res_json["holiday"]["holiday_subtype"] is None

    def test_get_holiday_paid_holiday_rtt_success(self, db, client, paid_holiday_rtt):
        res = client.get(f"/api/v1/holidays/{paid_holiday_rtt.id}")
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holiday"]["id"] == paid_holiday_rtt.id
        assert res_json["holiday"]["employee"] == paid_holiday_rtt.employee.id
        assert res_json["holiday"]["holiday_type"] == "paid"
        assert res_json["holiday"]["holiday_subtype"] == "rtt"

    def test_get_holiday_paid_holiday_normal_success(self, db, client, paid_holiday_normal):
        res = client.get(f"/api/v1/holidays/{paid_holiday_normal.id}")
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holiday"]["id"] == paid_holiday_normal.id
        assert res_json["holiday"]["employee"] == paid_holiday_normal.employee.id
        assert res_json["holiday"]["holiday_type"] == "paid"
        assert res_json["holiday"]["holiday_subtype"] == "normal"

    def test_get_holiday_404(self, db, client):
        res = client.get("/api/v1/holidays/1231231")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Holiday not found"


class TestHolidayDetailGetAndUpdateAndDelete:

    def test_update_holiday_success(self, db, client, unpaid_holiday):

        data = {
            "holiday_type": "paid"
        }

        res = client.patch(f"/api/v1/holidays/{unpaid_holiday.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holiday"]["id"] == unpaid_holiday.id
        assert res_json["holiday"]["holiday_type"] == data["holiday_type"]
        assert res_json["holiday"]["holiday_subtype"] == "normal"

    def test_update_holiday_start_date_success(self, db, client, unpaid_holiday):

        data = {
            "holiday_type": "paid",
            "start_date": "2020-10-11"
        }

        res = client.patch(f"/api/v1/holidays/{unpaid_holiday.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holiday"]["id"] == unpaid_holiday.id
        assert res_json["holiday"]["holiday_type"] == data["holiday_type"]
        assert res_json["holiday"]["holiday_subtype"] == "normal"

    def test_update_holiday_error(self, db, client, unpaid_holiday):

        data = {
            "start_date": "",
        }

        res = client.patch(f"/api/v1/holidays/{unpaid_holiday.id}", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert "Not a valid date." in res_json["start_date"]

    def test_delete_holiday_success(self, db, client, unpaid_holiday):
        res = client.delete(f"/api/v1/holidays/{unpaid_holiday.id}")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "holiday deleted"

    def test_delete_team_404(self, db, client):
        res = client.delete("/api/v1/holidays/12312312")

        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "Holiday not found"


class TestHolidayListAndCreation:

    def test_get_holidays_success(
        self, db, client, unpaid_holiday, paid_holiday_rtt, long_paid_holiday_rtt
    ):
        res = client.get("/api/v1/holidays")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holidays"]
        assert len(res_json["holidays"]) == 2

    def test_get_holidays_success_overlapping_start_date(
        self, db, client, unpaid_holiday,
        long_paid_holiday_rtt, paid_holiday_normal_to_overlap_start_date
    ):
        res = client.get("/api/v1/holidays")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holidays"]
        assert len(res_json["holidays"]) == 2

    def test_get_holidays_success_overlapping_end_date(
        self, db, client, unpaid_holiday,
        long_paid_holiday_rtt, paid_holiday_normal_to_overlap_end_date
    ):
        res = client.get("/api/v1/holidays")

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["holidays"]
        assert len(res_json["holidays"]) == 2

    def test_create_holiday_error_start_date_bigger_then_end_date(self, db, client, employee):
        data = {
            "start_date": "2020-10-12",
            "end_date": "2020-10-10",
            "employee": employee.id,
            "holiday_type": "unpaid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["dates"][0] == "Start date cannot be bigger then End date"

    def test_create_holiday_error_date_already_taken(self, db, client, employee, long_paid_holiday_rtt):
        data = {
            "start_date": "2020-10-11",
            "end_date": "2020-10-13",
            "employee": employee.id,
            "holiday_type": "paid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["days"][0] == "Those days are already taken for this type of holiday"

    def test_create_holiday_invalid_type_error(self, db, client, employee):
        data = {
            "start_date": "2020-10-12",
            "end_date": "2020-10-10",
            "employee": employee.id,
            "holiday_type": "unpaidss"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["holiday_type"][0] == "Holiday type not permitted"

    def test_create_holiday_invalid_subtype_error(self, db, client, employee):
        data = {
            "start_date": "2020-10-12",
            "end_date": "2020-10-10",
            "employee": employee.id,
            "holiday_type": "unpaid",
            "holiday_subtype": "notvalid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["holiday_subtype"][0] == "Holiday subtype not permitted"

    def test_create_holiday_error_no_dates(self, db, client, employee):
        data = {
            "employee": employee.id,
            "holiday_type": "unpaid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["start_date"][0] == "Missing data for required field."
        assert res_json["end_date"][0] == "Missing data for required field."

    def test_create_holiday_error_nonexistent_employee(self, db, client, employee):
        data = {
            "start_date": "2020-10-10",
            "end_date": "2020-10-12",
            "employee": 123123,
            "holiday_type": "unpaid"
        }

        res = client.post("/api/v1/holidays", json=data)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["employee"][0] == "Related Object doesn't exist in DB"

    def test_create_unpaid_holiday_success(self, db, client, employee):
        data = {
            "start_date": "2020-10-10",
            "end_date": "2020-10-12",
            "employee": employee.id,
            "holiday_type": "unpaid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json["message"] == "holiday created"
        assert res_json["holiday"]
        assert res_json["holiday"]["start_date"] == data["start_date"]
        assert res_json["holiday"]["end_date"] == data["end_date"]
        assert res_json["holiday"]["holiday_type"] == "unpaid"
        assert res_json["holiday"]["holiday_subtype"] is None

    def test_create_unpaid_holiday_ignored_subtype_success(self, db, client, employee):
        data = {
            "start_date": "2020-10-10",
            "end_date": "2020-10-12",
            "employee": employee.id,
            "holiday_type": "unpaid",
            "holiday_subtype": "normal"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json["message"] == "holiday created"
        assert res_json["holiday"]
        assert res_json["holiday"]["start_date"] == data["start_date"]
        assert res_json["holiday"]["end_date"] == data["end_date"]
        assert res_json["holiday"]["holiday_type"] == "unpaid"
        assert res_json["holiday"]["holiday_subtype"] is None

    def test_create_paid_holiday_normal_success(self, db, client, employee):
        data = {
            "start_date": "2020-10-10",
            "end_date": "2020-10-12",
            "employee": employee.id,
            "holiday_type": "paid"
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json["message"] == "holiday created"
        assert res_json["holiday"]
        assert res_json["holiday"]["start_date"] == data["start_date"]
        assert res_json["holiday"]["end_date"] == data["end_date"]
        assert res_json["holiday"]["holiday_type"] == "paid"
        assert res_json["holiday"]["holiday_subtype"] == "normal"

    def test_create_paid_holiday_rtt_success(self, db, client, employee):
        data = {
            "start_date": "2020-10-10",
            "end_date": "2020-10-12",
            "employee": employee.id,
            "holiday_type": "paid",
            "holiday_subtype": "rtt",
        }

        res = client.post("/api/v1/holidays", json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json["message"] == "holiday created"
        assert res_json["holiday"]
        assert res_json["holiday"]["start_date"] == data["start_date"]
        assert res_json["holiday"]["end_date"] == data["end_date"]
        assert res_json["holiday"]["holiday_type"] == "paid"
        assert res_json["holiday"]["holiday_subtype"] == "rtt"
