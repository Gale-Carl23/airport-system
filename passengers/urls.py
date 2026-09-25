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
    path(
    "payments/",
    views.payment_list,
    name="payment_list",
    ),

    path(
        "payments/add/",
        views.payment_create,
        name="payment_create",
    ),
    path(
    "payments/<int:payment_id>/edit/",
    views.payment_update,
    name="payment_update",
    ),
    path(
    "clearances/",
    views.clearance_list,
    name="clearance_list",
    ),

    path(
    "clearances/add/",
    views.clearance_create,
    name="clearance_create",
    ),

    path(
        "clearances/<int:clearance_id>/edit/",
        views.clearance_update,
        name="clearance_update",
    ),
    path(
    "cases/",
    views.case_list,
    name="case_list",
    ),

    path(
        "cases/add/",
        views.case_create,
        name="case_create",
    ),

    path(
        "cases/<int:case_id>/edit/",
        views.case_update,
        name="case_update",
    ),
]