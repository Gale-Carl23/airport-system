from django.contrib import admin

from .models import Flight, Passenger


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "first_name",
        "last_name",
        "passport_number",
        "nationality",
        "flight",
        "arrival_datetime",
        "created_at",
    )

    search_fields = (
        "reference_number",
        "first_name",
        "last_name",
        "passport_number",
    )


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "airline",
        "origin",
        "arrival_datetime",
        "created_at",
    )

    search_fields = (
        "flight_number",
        "airline",
        "origin",
    )