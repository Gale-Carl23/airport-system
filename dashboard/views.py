from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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

    user = request.user

    context = {
        "passenger_count": 0,
        "baggage_count": 0,
        "pending_inspection_count": 0,
        "for_assessment_count": 0,
        "pending_payment_count": 0,
        "active_case_count": 0,
        "pending_clearance_count": 0,

        "show_passengers": user.has_perm("passengers.view_passenger"),
        "show_baggage": user.has_perm("passengers.view_baggage"),
        "show_inspections": user.has_perm("passengers.view_inspection"),
        "show_assessments": user.has_perm("passengers.view_assessment"),
        "show_payments": user.has_perm("passengers.view_payment"),
        "show_cases": user.has_perm("passengers.view_case"),
        "show_clearances": user.has_perm("passengers.view_clearance"),
    }

    if context["show_passengers"]:
        context["passenger_count"] = Passenger.objects.count()

    if context["show_baggage"]:
        context["baggage_count"] = Baggage.objects.count()

    if context["show_inspections"]:
        context["pending_inspection_count"] = Inspection.objects.filter(
            status="pending"
        ).count()

    if context["show_assessments"]:
        context["for_assessment_count"] = Inspection.objects.filter(
            result="for_assessment"
        ).count()

    if context["show_payments"]:
        context["pending_payment_count"] = Payment.objects.filter(
            status="pending"
        ).count()

    if context["show_cases"]:
        context["active_case_count"] = Case.objects.filter(
            status__in=["open", "under_review"]
        ).count()

    if context["show_clearances"]:
        context["pending_clearance_count"] = Clearance.objects.filter(
            status="pending"
        ).count()

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )