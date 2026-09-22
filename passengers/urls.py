from django.urls import path
from . import views

urlpatterns = [
    path("", views.passenger_list, name="passenger_list"),
    path("add/", views.passenger_create, name="passenger_create"),
    path(
    "<int:passenger_id>/",
    views.passenger_detail,
    name="passenger_detail",
    ),
    path(
    "<int:passenger_id>/edit/",
    views.passenger_update,
    name="passenger_update",
    ),
    path("flights/", views.flight_list, name="flight_list"),
    path("flights/add/", views.flight_create, name="flight_create"),
    path(
    "baggage/",
    views.baggage_list,
    name="baggage_list",
    ),
    path(
        "baggage/add/",
        views.baggage_create,
        name="baggage_create",
    ),
    path(
    "inspections/",
    views.inspection_list,
    name="inspection_list",
    ),

    path(
        "inspections/add/",
        views.inspection_create,
        name="inspection_create",
    ),
    path(
    "inspections/<int:inspection_id>/edit/",
    views.inspection_update,
    name="inspection_update",
    ),
    path(
    "assessments/",
    views.assessment_list,
    name="assessment_list",
    ),

    path(
        "assessments/add/",
        views.assessment_create,
        name="assessment_create",
    ),
]