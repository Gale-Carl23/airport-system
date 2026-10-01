from django.contrib.auth.decorators import login_required
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


def get_age_info(created_at):
    """Return display text and priority information for a work item."""

    now = timezone.now()
    total_seconds = max(
        int((now - created_at).total_seconds()),
        0,
    )

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    if days:
        age_display = (
            f"{days} day{'s' if days != 1 else ''}"
            f"{f' {hours}h' if hours else ''}"
        )
    elif hours:
        age_display = (
            f"{hours} hour{'s' if hours != 1 else ''}"
            f"{f' {minutes}m' if minutes else ''}"
        )
    else:
        age_display = (
            f"{minutes} minute{'s' if minutes != 1 else ''}"
        )

    if total_seconds < 3600:
        age_class = "normal"
        age_label = "Normal"
    elif total_seconds < 14400:
        age_class = "waiting"
        age_label = "Waiting"
    elif total_seconds < 86400:
        age_class = "attention"
        age_label = "Attention"
    else:
        age_class = "overdue"
        age_label = "Overdue"

    return {
        "display": age_display,
        "class": age_class,
        "label": age_label,
        "seconds": total_seconds,
    }


def add_aging_info(items):
    """Attach temporary aging attributes to dashboard objects."""

    for item in items:
        info = get_age_info(item.created_at)

        item.age_display = info["display"]
        item.age_class = info["class"]
        item.age_label = info["label"]
        item.age_seconds = info["seconds"]

    return items


@login_required
def dashboard(request):
    user = request.user

    # ------------------------------------------------------------
    # PERMISSIONS
    # ------------------------------------------------------------

    show_passengers = user.has_perm(
        "passengers.view_passenger"
    )
    show_flights = user.has_perm(
        "passengers.view_flight"
    )
    show_baggage = user.has_perm(
        "passengers.view_baggage"
    )
    show_inspections = user.has_perm(
        "passengers.view_inspection"
    )
    show_assessments = user.has_perm(
        "passengers.view_assessment"
    )
    show_payments = user.has_perm(
        "passengers.view_payment"
    )
    show_clearances = user.has_perm(
        "passengers.view_clearance"
    )
    show_cases = user.has_perm(
        "passengers.view_case"
    )
    show_audit_logs = user.has_perm(
        "passengers.view_auditlog"
    )

    # ------------------------------------------------------------
    # COUNTS
    # ------------------------------------------------------------

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
    pending_assessment_count = 0
    pending_payment_count = 0
    active_case_count = 0
    pending_clearance_count = 0

    if show_inspections:
        pending_inspection_count = Inspection.objects.filter(
            status__in=[
                "pending",
                "in_progress",
            ]
        ).count()

    if show_assessments:
        for_assessment_count = Inspection.objects.filter(
            status="completed",
            result="for_assessment",
        ).count()

        pending_assessment_count = Assessment.objects.filter(
            status="pending"
        ).count()

    if show_payments:
        pending_payment_count = Payment.objects.filter(
            status="pending"
        ).count()

    if show_cases:
        active_case_count = Case.objects.filter(
            status__in=[
                "open",
                "under_review",
            ]
        ).count()

    if show_clearances:
        pending_clearance_count = Clearance.objects.filter(
            status="pending"
        ).count()

    # ------------------------------------------------------------
    # WORK QUEUES
    # ------------------------------------------------------------

    pending_inspections = []
    pending_assessments = []
    pending_payments = []
    active_cases = []
    pending_clearances = []

    if show_inspections:
        pending_inspections = list(
            Inspection.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(
                status__in=[
                    "pending",
                    "in_progress",
                ]
            )
            .order_by("created_at")[:8]
        )
        add_aging_info(pending_inspections)

    if show_assessments:
        pending_assessments = list(
            Assessment.objects.select_related(
                "inspection",
                "inspection__baggage",
                "inspection__baggage__passenger",
            )
            .filter(
                status="pending"
            )
            .order_by("created_at")[:8]
        )
        add_aging_info(pending_assessments)

    if show_payments:
        pending_payments = list(
            Payment.objects.select_related(
                "assessment",
                "assessment__inspection",
                "assessment__inspection__baggage",
                "assessment__inspection__baggage__passenger",
            )
            .filter(
                status="pending"
            )
            .order_by("created_at")[:8]
        )
        add_aging_info(pending_payments)

    if show_cases:
        active_cases = list(
            Case.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(
                status__in=[
                    "open",
                    "under_review",
                ]
            )
            .order_by("created_at")[:8]
        )
        add_aging_info(active_cases)

    if show_clearances:
        pending_clearances = list(
            Clearance.objects.select_related(
                "baggage",
                "baggage__passenger",
            )
            .filter(
                status="pending"
            )
            .order_by("created_at")[:8]
        )
        add_aging_info(pending_clearances)

    # ------------------------------------------------------------
    # ROLE
    # ------------------------------------------------------------

    if user.is_superuser:
        role_name = "Administrator"
    else:
        role_names = list(
            user.groups.values_list(
                "name",
                flat=True,
            )
        )
        role_name = (
            role_names[0]
            if role_names
            else "User"
        )

    # ------------------------------------------------------------
    # ROLE QUEUE
    # ------------------------------------------------------------

    role_queue = []

    def add_queue_item(
        title,
        description,
        count,
        url_name,
        permission,
        queue_class,
    ):
        if user.has_perm(permission):
            role_queue.append(
                {
                    "title": title,
                    "description": description,
                    "count": count,
                    "url": url_name,
                    "class": queue_class,
                }
            )

    if (
        user.is_superuser
        or user.groups.filter(
            name="Administrator"
        ).exists()
    ):
        add_queue_item(
            "Audit Logs",
            "Review system activity and accountability records.",
            0,
            "audit_log_list",
            "passengers.view_auditlog",
            "admin",
        )

    if show_inspections:
        add_queue_item(
            "Pending Inspections",
            "Baggage awaiting inspection.",
            pending_inspection_count,
            "inspection_list",
            "passengers.view_inspection",
            "inspection",
        )

    if show_assessments:
        add_queue_item(
            "For Assessment",
            "Completed inspections requiring assessment.",
            for_assessment_count,
            "assessment_list",
            "passengers.view_assessment",
            "assessment",
        )

    if show_payments:
        add_queue_item(
            "Pending Payments",
            "Assessments awaiting payment.",
            pending_payment_count,
            "payment_list",
            "passengers.view_payment",
            "payment",
        )

    if show_cases:
        add_queue_item(
            "Active Cases",
            "Cases currently under enforcement review.",
            active_case_count,
            "case_list",
            "passengers.view_case",
            "case",
        )

    if show_clearances:
        add_queue_item(
            "Pending Clearances",
            "Baggage awaiting clearance processing.",
            pending_clearance_count,
            "clearance_list",
            "passengers.view_clearance",
            "clearance",
        )

    context = {
        "now": timezone.localtime(),
        "role_name": role_name,

        "passenger_count": passenger_count,
        "baggage_count": baggage_count,
        "pending_inspection_count": pending_inspection_count,
        "for_assessment_count": for_assessment_count,
        "pending_assessment_count": pending_assessment_count,
        "pending_payment_count": pending_payment_count,
        "active_case_count": active_case_count,
        "pending_clearance_count": pending_clearance_count,

        "pending_inspections": pending_inspections,
        "pending_assessments": pending_assessments,
        "pending_payments": pending_payments,
        "active_cases": active_cases,
        "pending_clearances": pending_clearances,

        "role_queue": role_queue,

        "show_passengers": show_passengers,
        "show_flights": show_flights,
        "show_baggage": show_baggage,
        "show_inspections": show_inspections,
        "show_assessments": show_assessments,
        "show_payments": show_payments,
        "show_clearances": show_clearances,
        "show_cases": show_cases,
        "show_audit_logs": show_audit_logs,

        "is_admin": (
            user.is_superuser
            or user.groups.filter(
                name="Administrator"
            ).exists()
        ),
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )