from .swagger import SwaggerView
from .employees import EmployeeDetailResource, EmployeeListResource
from .teams import TeamDetailResource, TeamListResource
from .holidays import HolidayDetailResource, HolidayListResource

__all__ = [
    "SwaggerView",
    "EmployeeDetailResource",
    "EmployeeListResource",
    "TeamDetailResource",
    "TeamListResource",
    "HolidayDetailResource",
    "HolidayListResource",
]
