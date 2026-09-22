from django.contrib import admin

from .models import Flight, Passenger, Baggage


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

@admin.register(Baggage)
class BaggageAdmin(admin.ModelAdmin):
    list_display = (
        "baggage_tag",
        "passenger",
        "description",
        "weight",
        "declared",
        "created_at",
    )

    search_fields = (
        "baggage_tag",
        "passenger__reference_number",
        "passenger__first_name",
        "passenger__last_name",
    )