from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from passengers.models import (
    Passenger,
    Baggage,
    Inspection,
    Assessment,
    Payment,
    Clearance,
    Case,
)


@login_required
def dashboard(request):
    """
    Role-aware dashboard for the BOC-NAIA Operations System.

    The dashboard uses Django permissions to determine which operational
    data a user may see. This is only the presentation layer; the actual
    passenger/inspection/assessment/payment/case/clearance views remain
    protected by their own permission_required decorators.
    """

    user = request.user

    # ------------------------------------------------------------
    # PERMISSION FLAGS
    # ------------------------------------------------------------

    show_passengers = user.has_perm("passengers.view_passenger")
    show_flights = user.has_perm("passengers.view_flight")
    show_baggage = user.has_perm("passengers.view_baggage")
    show_inspections = user.has_perm("passengers.view_inspection")
    show_assessments = user.has_perm("passengers.view_assessment")
    show_payments = user.has_perm("passengers.view_payment")
    show_clearances = user.has_perm("passengers.view_clearance")
    show_cases = user.has_perm("passengers.view_case")
    show_audit_logs = user.has_perm("passengers.view_auditlog")

    # ------------------------------------------------------------
    # COUNTS
    # ------------------------------------------------------------
    # Unauthorized modules return zero rather than exposing data.

    passenger_count = (
        Passenger.objects.count()
        if show_passengers
        else 0
    )

    baggage_count = (
        Baggage.objects.count()
        if show_baggage
        else 0
    )

    pending_inspection_count = 0
    for_assessment_count = 0
    pending_payment_count = 0
    active_case_count = 0
    pending_clearance_count = 0

    if show_inspections:
        pending_inspection_count = Inspection.objects.filter(
            status__in=["pending", "in_progress"]
        ).count()

    if show_assessments:
        for_assessment_count = Inspection.objects.filter(
            status="completed",
            result="for_assessment",
        ).count()

    if show_payments:
        pending_payment_count = Payment.objects.filter(
            status="pending"
        ).count()

    if show_cases:
        active_case_count = Case.objects.filter(
            status__in=["open", "under_review"]
        ).count()

    if show_clearances:
        pending_clearance_count = Clearance.objects.filter(
            status="pending"
        ).count()

    # ------------------------------------------------------------
    # NEEDS ATTENTION QUEUES
    # ------------------------------------------------------------

    pending_inspections = Inspection.objects.none()
    pending_payments = Payment.objects.none()
    active_cases = Case.objects.none()
    pending_clearances = Clearance.objects.none()

    if show_inspections:
        pending_inspections = (
            Inspection.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(status__in=["pending", "in_progress"])
            .order_by("created_at")[:8]
        )

    if show_payments:
        pending_payments = (
            Payment.objects.select_related(
                "assessment",
                "assessment__inspection",
                "assessment__inspection__baggage",
                "assessment__inspection__baggage__passenger",
            )
            .filter(status="pending")
            .order_by("created_at")[:8]
        )

    if show_cases:
        active_cases = (
            Case.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(status__in=["open", "under_review"])
            .order_by("created_at")[:8]
        )

    if show_clearances:
        pending_clearances = (
            Clearance.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(status="pending")
            .order_by("created_at")[:8]
        )

    # ------------------------------------------------------------
    # ROLE INFORMATION
    # ------------------------------------------------------------

    if user.is_superuser:
        role_name = "Administrator"
    else:
        role_names = list(
            user.groups.values_list("name", flat=True)
        )
        role_name = role_names[0] if role_names else "User"

    # ------------------------------------------------------------
    # RENDER
    # ------------------------------------------------------------

    context = {
        "now": timezone.localtime(),
        "role_name": role_name,

        # Summary cards
        "passenger_count": passenger_count,
        "baggage_count": baggage_count,
        "pending_inspection_count": pending_inspection_count,
        "for_assessment_count": for_assessment_count,
        "pending_payment_count": pending_payment_count,
        "active_case_count": active_case_count,
        "pending_clearance_count": pending_clearance_count,

        # Queues
        "pending_inspections": pending_inspections,
        "pending_payments": pending_payments,
        "active_cases": active_cases,
        "pending_clearances": pending_clearances,

        # Permission flags
        "show_passengers": show_passengers,
        "show_flights": show_flights,
        "show_baggage": show_baggage,
        "show_inspections": show_inspections,
        "show_assessments": show_assessments,
        "show_payments": show_payments,
        "show_clearances": show_clearances,
        "show_cases": show_cases,
        "show_audit_logs": show_audit_logs,

        # Convenience flags
        "is_admin": user.is_superuser or user.groups.filter(
            name="Administrator"
        ).exists(),
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )