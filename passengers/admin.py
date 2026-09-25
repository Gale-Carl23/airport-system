from django.contrib import admin

from .models import (
    Assessment,
    Baggage,
    Flight,
    Inspection,
    Passenger,
    Payment,
    Clearance,
    Case,
)


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

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = (
        "baggage",
        "status",
        "result",
        "inspected_at",
        "created_at",
    )

    list_filter = (
        "status",
        "result",
    )

    search_fields = (
        "baggage__baggage_tag",
        "baggage__passenger__reference_number",
        "baggage__passenger__first_name",
        "baggage__passenger__last_name",
    )

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "inspection",
        "status",
        "declared_value",
        "assessed_value",
        "duty_amount",
        "tax_amount",
        "assessed_at",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "inspection__baggage__baggage_tag",
        "inspection__baggage__passenger__reference_number",
        "inspection__baggage__passenger__first_name",
        "inspection__baggage__passenger__last_name",
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "status",
        "amount_due",
        "amount_paid",
        "payment_method",
        "payment_reference",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
    )

    search_fields = (
        "payment_reference",
        "assessment__inspection__baggage__baggage_tag",
        "assessment__inspection__baggage__passenger__reference_number",
        "assessment__inspection__baggage__passenger__first_name",
        "assessment__inspection__baggage__passenger__last_name",
    )

@admin.register(Clearance)
class ClearanceAdmin(admin.ModelAdmin):
    list_display = (
        "clearance_reference",
        "baggage",
        "status",
        "cleared_at",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "clearance_reference",
        "baggage__baggage_tag",
        "baggage__passenger__reference_number",
        "baggage__passenger__first_name",
        "baggage__passenger__last_name",
    )

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        "case_reference",
        "baggage",
        "case_type",
        "status",
        "created_by",
        "resolved_by",
        "resolved_at",
        "created_at",
    )

    list_filter = (
        "case_type",
        "status",
    )

    search_fields = (
        "case_reference",
        "baggage__baggage_tag",
        "baggage__passenger__reference_number",
        "baggage__passenger__first_name",
        "baggage__passenger__last_name",
        "created_by__username",
        "resolved_by__username",
    )