import pytest

from work_api.app import create_app
from work_api.models import db as rawdb
from work_api.models import Employee, Team, Holiday

from datetime import datetime
from datetime import timedelta


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        rawdb.init_db()

        yield rawdb

        rawdb.session.close()
        rawdb.drop_db()


@pytest.fixture
def team(db):
    team = Team(
        name="Test Team 1",
        description="Test Team 1 description"
    )
    team.save()
    return team


@pytest.fixture
def employee(db, team):
    employee = Employee(
        email="test@email.com",
        team_id=team.id
    )
    employee.save()
    return employee


@pytest.fixture
def unpaid_holiday(db, employee):
    unpaid_holiday = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-12",
        employee_id=employee.id,
        holiday_type="unpaid"
    )
    unpaid_holiday.save()
    return unpaid_holiday


@pytest.fixture
def paid_holiday_rtt(db, employee):
    paid_holiday_rtt = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-12",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="rtt"
    )
    paid_holiday_rtt.save()
    return paid_holiday_rtt


# When used together with 'paid_holiday_rtt' the first one is deleted, due to overlapping
@pytest.fixture
def paid_holiday_normal(db, employee):
    paid_holiday_normal = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-12",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="normal"
    )
    paid_holiday_normal.save()
    return paid_holiday_normal


@pytest.fixture
def paid_holiday_normal_to_overlap_start_date(db, employee):
    paid_holiday_normal = Holiday(
        start_date="2020-10-11",
        end_date="2020-10-19",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="normal"
    )
    paid_holiday_normal.save()
    return paid_holiday_normal


@pytest.fixture
def paid_holiday_normal_to_overlap_end_date(db, employee):
    paid_holiday_normal = Holiday(
        start_date="2020-10-09",
        end_date="2020-10-17",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="normal"
    )
    paid_holiday_normal.save()
    return paid_holiday_normal


@pytest.fixture
def long_paid_holiday_rtt(db, employee):
    paid_holiday_rtt = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-18",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="rtt"
    )
    paid_holiday_rtt.save()
    return paid_holiday_rtt
