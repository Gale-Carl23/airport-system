from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from passengers.models import (
    Passenger,
    Baggage,
    Inspection,
    Assessment,
    Payment,
    Clearance,
    Case,
)

# Create your views here.
@login_required
def dashboard(request):
    pending_inspections = Inspection.objects.filter(
    status="pending"
    ).select_related(
        "baggage",
    )

    pending_payments = Payment.objects.filter(
        status="pending"
    ).select_related(
        "assessment__inspection__baggage",
    )

    active_cases = Case.objects.filter(
        status__in=["open", "under_review"]
    ).select_related(
        "baggage",
    )

    pending_clearances = Clearance.objects.filter(
        status="pending"
    ).select_related(
        "baggage",
    )
    context = {
        "passenger_count": Passenger.objects.count(),
        "baggage_count": Baggage.objects.count(),

        "pending_inspection_count": pending_inspections.count(),

        "for_assessment_count": Inspection.objects.filter(
            result="for_assessment"
        ).count(),

        "pending_payment_count": pending_payments.count(),

        "active_case_count": active_cases.count(),

        "pending_clearance_count": pending_clearances.count(),

        "pending_inspections": pending_inspections[:5],
        "pending_payments": pending_payments[:5],
        "active_cases": active_cases[:5],
        "pending_clearances": pending_clearances[:5],
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )