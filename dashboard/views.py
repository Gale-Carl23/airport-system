from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render

from passengers.models import (
    Passenger,
    Flight,
    Baggage,
    Inspection,
    Assessment,
    Payment,
    Clearance,
    Case,
    AuditLog,
)


def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@login_required
def dashboard(request):

    user = request.user

    # ============================================================
    # ROLE DETECTION
    # ============================================================

    is_admin = (
        user.is_superuser
        or user_in_group(user, "Administrator")
    )

    is_examiner = user_in_group(
        user,
        "Customs Examiner",
    )

    is_assessment_officer = user_in_group(
        user,
        "Assessment Officer",
    )

    is_cashier = user_in_group(
        user,
        "Cashier",
    )

    is_enforcement_officer = user_in_group(
        user,
        "Enforcement Officer",
    )

    is_clearance_officer = user_in_group(
        user,
        "Clearance Officer",
    )

    # ============================================================
    # GENERAL COUNTS
    # ============================================================

    passenger_count = Passenger.objects.count()

    baggage_count = Baggage.objects.count()

    pending_inspection_count = Inspection.objects.filter(
        status__in=[
            "pending",
            "in_progress",
        ]
    ).count()

    for_assessment_count = Inspection.objects.filter(
        status="completed",
        result="for_assessment",
    ).count()

    pending_payment_count = Payment.objects.filter(
        status="pending",
    ).count()

    active_case_count = Case.objects.filter(
        status__in=[
            "open",
            "under_review",
        ]
    ).count()

    pending_clearance_count = Clearance.objects.filter(
        status="pending",
    ).count()

    # ============================================================
    # NEEDS ATTENTION
    # ============================================================

    pending_inspections = Inspection.objects.filter(
        status__in=[
            "pending",
            "in_progress",
        ]
    ).select_related(
        "baggage",
        "baggage__passenger",
    ).order_by(
        "-created_at"
    )[:10]

    pending_payments = Payment.objects.filter(
        status="pending",
    ).select_related(
        "assessment",
        "assessment__inspection",
        "assessment__inspection__baggage",
    ).order_by(
        "-created_at"
    )[:10]

    active_cases = Case.objects.filter(
        status__in=[
            "open",
            "under_review",
        ]
    ).select_related(
        "baggage",
        "baggage__passenger",
        "created_by",
    ).order_by(
        "-created_at"
    )[:10]

    pending_clearances = Clearance.objects.filter(
        status="pending",
    ).select_related(
        "baggage",
        "baggage__passenger",
    ).order_by(
        "-created_at"
    )[:10]

    # ============================================================
    # ROLE-SPECIFIC QUEUE
    # ============================================================

    role_queue = []

    def add_queue_item(
        title,
        description,
        url,
        permission,
        count,
    ):
        if user.has_perm(permission):
            role_queue.append(
                {
                    "title": title,
                    "description": description,
                    "url": url,
                    "count": count,
                }
            )

    # ------------------------------------------------------------
    # ADMINISTRATOR
    # ------------------------------------------------------------

    if is_admin:

        if user.has_perm(
            "passengers.view_auditlog"
        ):
            role_queue.append(
                {
                    "title": "Audit Logs",
                    "description": (
                        "Review system activity "
                        "and accountability records."
                    ),
                    "url": "audit_log_list",
                    "count": AuditLog.objects.count(),
                }
            )

    # ------------------------------------------------------------
    # CUSTOMS EXAMINER
    # ------------------------------------------------------------

    if is_examiner:

        add_queue_item(
            "Pending Inspections",
            "Inspect baggage awaiting examination.",
            "inspection_list",
            "passengers.view_inspection",
            pending_inspection_count,
        )

        add_queue_item(
            "Baggage",
            "Review baggage and passenger information.",
            "baggage_list",
            "passengers.view_baggage",
            baggage_count,
        )

    # ------------------------------------------------------------
    # ASSESSMENT OFFICER
    # ------------------------------------------------------------

    if is_assessment_officer:

        add_queue_item(
            "For Assessment",
            "Process baggage requiring customs assessment.",
            "assessment_list",
            "passengers.view_assessment",
            for_assessment_count,
        )

        add_queue_item(
            "Pending Assessments",
            "Review assessments awaiting completion.",
            "assessment_list",
            "passengers.view_assessment",
            Assessment.objects.filter(
                status="pending",
            ).count(),
        )

    # ------------------------------------------------------------
    # CASHIER
    # ------------------------------------------------------------

    if is_cashier:

        add_queue_item(
            "Pending Payments",
            "Process outstanding assessment payments.",
            "payment_list",
            "passengers.view_payment",
            pending_payment_count,
        )

        add_queue_item(
            "Assessments",
            "Review assessment information related to payments.",
            "assessment_list",
            "passengers.view_assessment",
            Assessment.objects.count(),
        )

    # ------------------------------------------------------------
    # ENFORCEMENT OFFICER
    # ------------------------------------------------------------

    if is_enforcement_officer:

        add_queue_item(
            "Active Cases",
            "Review and process active enforcement cases.",
            "case_list",
            "passengers.view_case",
            active_case_count,
        )

        add_queue_item(
            "Held / Seized Baggage",
            "Review baggage associated with enforcement cases.",
            "baggage_list",
            "passengers.view_baggage",
            Baggage.objects.filter(
                inspection__result__in=[
                    "held",
                    "seized",
                ]
            ).count(),
        )

    # ------------------------------------------------------------
    # CLEARANCE OFFICER
    # ------------------------------------------------------------

    if is_clearance_officer:

        add_queue_item(
            "Pending Clearances",
            "Process baggage awaiting clearance.",
            "clearance_list",
            "passengers.view_clearance",
            pending_clearance_count,
        )

        add_queue_item(
            "Payments",
            "Verify payment information before clearance.",
            "payment_list",
            "passengers.view_payment",
            Payment.objects.filter(
                status="paid",
            ).count(),
        )

    # ============================================================
    # PERMISSION-AWARE NAVIGATION
    # ============================================================

    context = {

        # --------------------------------------------------------
        # GENERAL
        # --------------------------------------------------------

        "role_name": (
            "Administrator"
            if is_admin
            else "Customs Examiner"
            if is_examiner
            else "Assessment Officer"
            if is_assessment_officer
            else "Cashier"
            if is_cashier
            else "Enforcement Officer"
            if is_enforcement_officer
            else "Clearance Officer"
            if is_clearance_officer
            else "User"
        ),

        "is_admin": is_admin,

        # --------------------------------------------------------
        # COUNTS
        # --------------------------------------------------------

        "passenger_count": passenger_count,
        "baggage_count": baggage_count,
        "pending_inspection_count": pending_inspection_count,
        "for_assessment_count": for_assessment_count,
        "pending_payment_count": pending_payment_count,
        "active_case_count": active_case_count,
        "pending_clearance_count": pending_clearance_count,

        # --------------------------------------------------------
        # NEEDS ATTENTION
        # --------------------------------------------------------

        "pending_inspections": pending_inspections,
        "pending_payments": pending_payments,
        "active_cases": active_cases,
        "pending_clearances": pending_clearances,

        # --------------------------------------------------------
        # ROLE QUEUE
        # --------------------------------------------------------

        "role_queue": role_queue,

        # --------------------------------------------------------
        # NAVIGATION PERMISSIONS
        # --------------------------------------------------------

        "show_passengers": user.has_perm(
            "passengers.view_passenger"
        ),

        "show_flights": user.has_perm(
            "passengers.view_flight"
        ),

        "show_baggage": user.has_perm(
            "passengers.view_baggage"
        ),

        "show_inspections": user.has_perm(
            "passengers.view_inspection"
        ),

        "show_assessments": user.has_perm(
            "passengers.view_assessment"
        ),

        "show_payments": user.has_perm(
            "passengers.view_payment"
        ),

        "show_clearances": user.has_perm(
            "passengers.view_clearance"
        ),

        "show_cases": user.has_perm(
            "passengers.view_case"
        ),

        "show_audit_logs": user.has_perm(
            "passengers.view_auditlog"
        ),
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )