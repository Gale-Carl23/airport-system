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
]