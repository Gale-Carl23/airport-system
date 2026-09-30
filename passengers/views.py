from django.core.paginator import Paginator
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import (
    Baggage,
    Flight,
    Inspection,
    Passenger,
    Assessment,
    Payment,
    Clearance,
    Case,
    AuditLog,
)
from .forms import (
    BaggageForm,
    FlightForm,
    InspectionForm,
    PassengerForm,
    AssessmentForm,
    PaymentForm,
    ClearanceForm,
    CaseForm,
)


@login_required
@permission_required(
    "passengers.view_passenger",
    raise_exception=True,
)
def passenger_list(request):
    passengers = Passenger.objects.select_related(
        "flight",
    ).all()

    search = request.GET.get("q", "").strip()
    nationality = request.GET.get("nationality", "").strip()
    flight_id = request.GET.get("flight", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if search:
        passengers = passengers.filter(
            Q(reference_number__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(passport_number__icontains=search)
        )

    if nationality:
        passengers = passengers.filter(
            nationality__iexact=nationality
        )

    if flight_id:
        passengers = passengers.filter(
            flight_id=flight_id
        )

    if date_from:
        parsed_from = parse_date(date_from)
        if parsed_from:
            passengers = passengers.filter(
                arrival_datetime__date__gte=parsed_from
            )

    if date_to:
        parsed_to = parse_date(date_to)
        if parsed_to:
            passengers = passengers.filter(
                arrival_datetime__date__lte=parsed_to
            )

    passengers = passengers.order_by("-arrival_datetime")

    return render(
        request,
        "passengers/passenger_list.html",
        {
            "passengers": passengers,
            "search": search,
            "selected_nationality": nationality,
            "selected_flight": flight_id,
            "date_from": date_from,
            "date_to": date_to,
            "flights": Flight.objects.order_by(
                "-arrival_datetime"
            ),
        },
    )

@login_required
@permission_required(
    "passengers.add_passenger",
    raise_exception=True,
)
def passenger_create(request):

    if request.method == "POST":
        form = PassengerForm(request.POST)

        if form.is_valid():
            passenger = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Passenger",
                object_id=passenger.id,
                description=f"Created passenger {passenger.reference_number}.",
                )

            return redirect("passenger_list")

    else:
        form = PassengerForm()

    return render(
        request,
        "passengers/passenger_form.html",
        {"form": form},
    )

@login_required
@permission_required(
    "passengers.change_passenger",
    raise_exception=True,
)
def passenger_update(request, passenger_id):
    passenger = get_object_or_404(
        Passenger,
        id=passenger_id,
    )

    if request.method == "POST":
        old_values = {
            "reference_number": passenger.reference_number,
            "first_name": passenger.first_name,
            "last_name": passenger.last_name,
            "passport_number": passenger.passport_number,
            "nationality": passenger.nationality,
            "flight": passenger.flight,
            "arrival_datetime": passenger.arrival_datetime,
        }

        form = PassengerForm(
            request.POST,
            instance=passenger,
        )

        if form.is_valid():
            updated_passenger = form.save()

            changes = []

            if old_values["reference_number"] != updated_passenger.reference_number:
                changes.append(
                    f"Reference Number: "
                    f"{old_values['reference_number']} → "
                    f"{updated_passenger.reference_number}"
                )

            if old_values["first_name"] != updated_passenger.first_name:
                changes.append(
                    f"First Name: "
                    f"{old_values['first_name']} → "
                    f"{updated_passenger.first_name}"
                )

            if old_values["last_name"] != updated_passenger.last_name:
                changes.append(
                    f"Last Name: "
                    f"{old_values['last_name']} → "
                    f"{updated_passenger.last_name}"
                )

            if old_values["passport_number"] != updated_passenger.passport_number:
                changes.append(
                    f"Passport Number: "
                    f"{old_values['passport_number']} → "
                    f"{updated_passenger.passport_number}"
                )

            if old_values["nationality"] != updated_passenger.nationality:
                changes.append(
                    f"Nationality: "
                    f"{old_values['nationality']} → "
                    f"{updated_passenger.nationality}"
                )

            if old_values["flight"] != updated_passenger.flight:
                old_flight = (
                    str(old_values["flight"])
                    if old_values["flight"]
                    else "None"
                )

                new_flight = (
                    str(updated_passenger.flight)
                    if updated_passenger.flight
                    else "None"
                )

                changes.append(
                    f"Flight: {old_flight} → {new_flight}"
                )

            if old_values["arrival_datetime"] != updated_passenger.arrival_datetime:
                changes.append(
                    f"Arrival Date/Time: "
                    f"{old_values['arrival_datetime']} → "
                    f"{updated_passenger.arrival_datetime}"
                )

            if changes:
                AuditLog.objects.create(
                    user=request.user,
                    action="update",
                    model_name="Passenger",
                    object_id=updated_passenger.id,
                    description=(
                        f"Updated passenger "
                        f"{updated_passenger.reference_number}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect(
                "passenger_detail",
                passenger_id=updated_passenger.id,
            )

    else:
        form = PassengerForm(
            instance=passenger,
        )

    return render(
        request,
        "passengers/passenger_form.html",
        {
            "form": form,
            "passenger": passenger,
        },
    )

@login_required
@permission_required(
    "passengers.view_passenger",
    raise_exception=True,
)
def passenger_detail(request, passenger_id):
    passenger = get_object_or_404(
        Passenger.objects.select_related("flight"),
        id=passenger_id,
    )

    baggage = (
        passenger.baggage
        .select_related()
        .prefetch_related(
            "inspection",
            "inspection__assessment",
            "inspection__assessment__payment",
            "clearance",
            "cases",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "passengers/passenger_detail.html",
        {
            "passenger": passenger,
            "baggage": baggage,
        },
    )

@login_required
@permission_required(
    "passengers.view_flight",
    raise_exception=True,
)
def flight_list(request):
    flights = Flight.objects.all().order_by("-arrival_datetime")

    return render(
        request,
        "passengers/flight_list.html",
        {
            "flights": flights,
        },
    )

@login_required
@permission_required(
    "passengers.add_flight",
    raise_exception=True,
)
def flight_create(request):
    if request.method == "POST":
        form = FlightForm(request.POST)

        if form.is_valid():
            flight = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Flight",
                object_id=flight.id,
                description=(
                    f"Created flight {flight.flight_number} "
                    f"({flight.airline})."
                ),
            )

            return redirect("flight_list")
    else:
        form = FlightForm()

    return render(
        request,
        "passengers/flight_form.html",
        {
            "form": form,
        },
    )

@login_required
@permission_required(
    "passengers.view_flight",
    raise_exception=True,
)
def flight_detail(request, flight_id):
    flight = get_object_or_404(
        Flight.objects.prefetch_related(
            "passengers",
            "passengers__baggage",
            "passengers__baggage__inspection",
            "passengers__baggage__clearance",
            "passengers__baggage__cases",
        ),
        id=flight_id,
    )

    return render(
        request,
        "passengers/flight_detail.html",
        {
            "flight": flight,
            "passengers": flight.passengers.all(),
        },
    )

@login_required
@permission_required(
    "passengers.view_baggage",
    raise_exception=True,
)
def baggage_list(request):
    baggage = Baggage.objects.select_related(
        "passenger"
    ).order_by("-created_at")

    return render(
        request,
        "passengers/baggage_list.html",
        {
            "baggage": baggage,
        },
    )

@login_required
@permission_required(
    "passengers.add_baggage",
    raise_exception=True,
)
def baggage_create(request):
    if request.method == "POST":
        form = BaggageForm(request.POST)

        if form.is_valid():
            baggage = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Baggage",
                object_id=baggage.id,
                description=(
                    f"Created baggage {baggage.baggage_tag} "
                    f"for passenger "
                    f"{baggage.passenger.reference_number}."
                ),
            )

            return redirect("baggage_list")

    else:
        form = BaggageForm()

    return render(
        request,
        "passengers/baggage_form.html",
        {"form": form},
    )

login_required
@permission_required(
    "passengers.change_baggage",
    raise_exception=True,
)
def baggage_update(request, baggage_id):
    baggage = get_object_or_404(
        Baggage,
        id=baggage_id,
    )

    if request.method == "POST":
        old_values = {
            "passenger": baggage.passenger,
            "baggage_tag": baggage.baggage_tag,
            "description": baggage.description,
            "weight": baggage.weight,
            "declared": baggage.declared,
        }

        post_data = request.POST.copy()
        post_data["passenger"] = baggage.passenger_id

        form = BaggageForm(
            post_data,
            instance=baggage,
        )

        if form.is_valid():
            updated_baggage = form.save()

            changes = []

            if old_values["passenger"] != updated_baggage.passenger:
                changes.append(
                    f"Passenger: "
                    f"{old_values['passenger'].reference_number} → "
                    f"{updated_baggage.passenger.reference_number}"
                )

            if old_values["baggage_tag"] != updated_baggage.baggage_tag:
                changes.append(
                    f"Baggage Tag: "
                    f"{old_values['baggage_tag']} → "
                    f"{updated_baggage.baggage_tag}"
                )

            if old_values["description"] != updated_baggage.description:
                changes.append(
                    f"Description: "
                    f"{old_values['description']} → "
                    f"{updated_baggage.description}"
                )

            if old_values["weight"] != updated_baggage.weight:
                changes.append(
                    f"Weight: "
                    f"{old_values['weight']} → "
                    f"{updated_baggage.weight}"
                )

            if old_values["declared"] != updated_baggage.declared:
                old_declared = (
                    "Declared"
                    if old_values["declared"]
                    else "Not Declared"
                )

                new_declared = (
                    "Declared"
                    if updated_baggage.declared
                    else "Not Declared"
                )

                changes.append(
                    f"Declared: {old_declared} → {new_declared}"
                )

            if changes:
                AuditLog.objects.create(
                    user=request.user,
                    action="update",
                    model_name="Baggage",
                    object_id=updated_baggage.id,
                    description=(
                        f"Updated baggage "
                        f"{updated_baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect("baggage_list")

    else:
        form = BaggageForm(
            instance=baggage,
        )

    return render(
        request,
        "passengers/baggage_form.html",
        {
            "form": form,
            "baggage": baggage,
        },
    )

@login_required
@permission_required(
    "passengers.view_inspection",
    raise_exception=True,
)
def inspection_list(request):
    inspections = Inspection.objects.select_related(
        "baggage",
        "baggage__passenger",
        "baggage__passenger__flight",
    ).all()

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    result = request.GET.get("result", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if search:
        inspections = inspections.filter(
            Q(baggage__baggage_tag__icontains=search)
            | Q(baggage__passenger__reference_number__icontains=search)
            | Q(baggage__passenger__first_name__icontains=search)
            | Q(baggage__passenger__last_name__icontains=search)
            | Q(findings__icontains=search)
        )

    if status:
        inspections = inspections.filter(
            status=status
        )

    if result:
        inspections = inspections.filter(
            result=result
        )

    if date_from:
        parsed_from = parse_date(date_from)

        if parsed_from:
            inspections = inspections.filter(
                created_at__date__gte=parsed_from
            )

    if date_to:
        parsed_to = parse_date(date_to)

        if parsed_to:
            inspections = inspections.filter(
                created_at__date__lte=parsed_to
            )

    inspections = inspections.order_by("-created_at")

    return render(
        request,
        "passengers/inspection_list.html",
        {
            "inspections": inspections,
            "search": search,
            "selected_status": status,
            "selected_result": result,
            "date_from": date_from,
            "date_to": date_to,
            "status_choices": Inspection.STATUS_CHOICES,
            "result_choices": Inspection.RESULT_CHOICES,
        },
    )

@login_required
@permission_required(
    "passengers.add_inspection",
    raise_exception=True,
)
def inspection_create(request):
    if request.method == "POST":
        form = InspectionForm(request.POST)

        if form.is_valid():
            inspection = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Inspection",
                object_id=inspection.id,
                description=(
                    f"Created inspection for baggage "
                    f"{inspection.baggage.baggage_tag}."
                ),
            )

            return redirect("inspection_list")

    else:
        form = InspectionForm()

    return render(
        request,
        "passengers/inspection_form.html",
        {"form": form},
    )

@login_required
@permission_required(
    "passengers.change_inspection",
    raise_exception=True,
)
def inspection_update(request, inspection_id):
    inspection = get_object_or_404(
        Inspection,
        id=inspection_id,
    )

    if request.method == "POST":
        old_status = inspection.status
        old_result = inspection.result
        old_findings = inspection.findings
        old_inspected_at = inspection.inspected_at

        post_data = request.POST.copy()
        post_data["baggage"] = inspection.baggage_id

        form = InspectionForm(
            post_data,
            instance=inspection,
        )

        if form.is_valid():
            updated_inspection = form.save()

            changes = []

            if old_status != updated_inspection.status:
                changes.append(
                    f"Status: "
                    f"{dict(Inspection.STATUS_CHOICES).get(old_status)} → "
                    f"{updated_inspection.get_status_display()}"
                )

            if old_result != updated_inspection.result:
                changes.append(
                    f"Result: "
                    f"{dict(Inspection.RESULT_CHOICES).get(old_result)} → "
                    f"{updated_inspection.get_result_display()}"
                )

            if old_findings != updated_inspection.findings:
                changes.append(
                    "Findings were updated."
                )

            if old_inspected_at != updated_inspection.inspected_at:
                changes.append(
                    "Inspection date/time was updated."
                )

            if changes:
                if (
                    old_status != updated_inspection.status
                    or old_result != updated_inspection.result
                ):
                    action = "status_change"
                else:
                    action = "update"

                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name="Inspection",
                    object_id=updated_inspection.id,
                    description=(
                        f"Updated inspection for baggage "
                        f"{updated_inspection.baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect("inspection_list")

    else:
        form = InspectionForm(
            instance=inspection,
        )

    return render(
        request,
        "passengers/inspection_form.html",
        {
            "form": form,
            "inspection": inspection,
        },
    )

@login_required
@permission_required(
    "passengers.view_inspection",
    raise_exception=True,
)
def inspection_detail(request, inspection_id):
    inspection = get_object_or_404(
        Inspection.objects.select_related(
            "baggage",
            "baggage__passenger",
            "baggage__passenger__flight",
        ),
        id=inspection_id,
    )

    assessment = getattr(inspection, "assessment", None)

    cases = inspection.baggage.cases.all().order_by("-created_at")

    clearance = getattr(
        inspection.baggage,
        "clearance",
        None,
    )

    return render(
        request,
        "passengers/inspection_detail.html",
        {
            "inspection": inspection,
            "assessment": assessment,
            "cases": cases,
            "clearance": clearance,
        },
    )

@login_required
@permission_required(
    "passengers.view_assessment",
    raise_exception=True,
)
def assessment_list(request):
    assessments = Assessment.objects.select_related(
        "inspection",
        "inspection__baggage",
        "inspection__baggage__passenger",
    ).order_by("-created_at")

    return render(
        request,
        "passengers/assessment_list.html",
        {
            "assessments": assessments,
        },
    )

@login_required
@permission_required(
    "passengers.add_assessment",
    raise_exception=True,
)
def assessment_create(request):

    inspection_id = request.GET.get("inspection")

    inspection = None

    if inspection_id:
        inspection = get_object_or_404(
            Inspection,
            id=inspection_id,
        )

    if request.method == "POST":
        post_data = request.POST.copy()

        if inspection:
            post_data["inspection"] = inspection.pk

        form = AssessmentForm(post_data)

        if form.is_valid():
            assessment = form.save(commit=False)

            if inspection:
                assessment.inspection = inspection

            assessment.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Assessment",
                object_id=assessment.id,
                description=(
                    f"Created assessment for baggage "
                    f"{assessment.inspection.baggage.baggage_tag}"
                ),
            )

            return redirect("assessment_list")

    else:
        form = AssessmentForm(
            initial={
                "inspection": inspection,
            }
        )

    return render(
        request,
        "passengers/assessment_form.html",
        {
            "form": form,
            "inspection": inspection,
        },
    )

@login_required
@permission_required(
    "passengers.change_assessment",
    raise_exception=True,
)
def assessment_update(request, assessment_id):
    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
    )

    if request.method == "POST":

        old_values = {
            "status": assessment.status,
            "declared_value": assessment.declared_value,
            "assessed_value": assessment.assessed_value,
            "duty_amount": assessment.duty_amount,
            "tax_amount": assessment.tax_amount,
            "remarks": assessment.remarks,
            "assessed_at": assessment.assessed_at,
        }

        post_data = request.POST.copy()
        post_data["inspection"] = assessment.inspection_id

        form = AssessmentForm(
            post_data,
            instance=assessment,
        )

        if form.is_valid():
            updated_assessment = form.save()

            changes = []

            if old_values["status"] != updated_assessment.status:
                changes.append(
                    f"Status: "
                    f"{old_values['status']} → "
                    f"{updated_assessment.status}"
                )

            if old_values["declared_value"] != updated_assessment.declared_value:
                changes.append(
                    f"Declared Value: "
                    f"{old_values['declared_value']} → "
                    f"{updated_assessment.declared_value}"
                )

            if old_values["assessed_value"] != updated_assessment.assessed_value:
                changes.append(
                    f"Assessed Value: "
                    f"{old_values['assessed_value']} → "
                    f"{updated_assessment.assessed_value}"
                )

            if old_values["duty_amount"] != updated_assessment.duty_amount:
                changes.append(
                    f"Duty Amount: "
                    f"{old_values['duty_amount']} → "
                    f"{updated_assessment.duty_amount}"
                )

            if old_values["tax_amount"] != updated_assessment.tax_amount:
                changes.append(
                    f"Tax Amount: "
                    f"{old_values['tax_amount']} → "
                    f"{updated_assessment.tax_amount}"
                )

            if old_values["remarks"] != updated_assessment.remarks:
                changes.append(
                    f"Remarks: "
                    f"{old_values['remarks']} → "
                    f"{updated_assessment.remarks}"
                )

            if old_values["assessed_at"] != updated_assessment.assessed_at:
                changes.append(
                    f"Assessed At: "
                    f"{old_values['assessed_at']} → "
                    f"{updated_assessment.assessed_at}"
                )

            if changes:
                action = (
                    "status_change"
                    if old_values["status"] != updated_assessment.status
                    else "update"
                )

                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name="Assessment",
                    object_id=updated_assessment.id,
                    description=(
                        f"Updated assessment for baggage "
                        f"{updated_assessment.inspection.baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect("assessment_list")

    else:
        form = AssessmentForm(
            instance=assessment,
        )

    return render(
        request,
        "passengers/assessment_form.html",
        {
            "form": form,
            "assessment": assessment,
        },
    )

@login_required
@permission_required(
    "passengers.view_assessment",
    raise_exception=True,
)
def assessment_detail(request, assessment_id):
    assessment = get_object_or_404(
        Assessment.objects.select_related(
            "inspection",
            "inspection__baggage",
            "inspection__baggage__passenger",
            "inspection__baggage__passenger__flight",
        ),
        id=assessment_id,
    )

    payment = getattr(assessment, "payment", None)

    clearance = getattr(
        assessment.inspection.baggage,
        "clearance",
        None,
    )

    return render(
        request,
        "passengers/assessment_detail.html",
        {
            "assessment": assessment,
            "payment": payment,
            "clearance": clearance,
        },
    )

@login_required
@permission_required(
    "passengers.view_payment",
    raise_exception=True,
)
def payment_list(request):
    payments = Payment.objects.select_related(
        "assessment",
        "assessment__inspection",
        "assessment__inspection__baggage",
        "assessment__inspection__baggage__passenger",
    ).order_by("-created_at")

    return render(
        request,
        "passengers/payment_list.html",
        {
            "payments": payments,
        },
    )

@login_required
@permission_required(
    "passengers.add_payment",
    raise_exception=True,
)
def payment_create(request):

    assessment_id = request.GET.get("assessment")

    assessment = None

    if assessment_id:
        assessment = get_object_or_404(
            Assessment,
            id=assessment_id,
        )

    if request.method == "POST":
        post_data = request.POST.copy()

        if assessment:
            post_data["assessment"] = assessment.pk

        form = PaymentForm(post_data)

        if form.is_valid():
            payment = form.save(commit=False)

            if assessment:
                payment.assessment = assessment

            payment.save()

            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Payment",
                object_id=payment.id,
                description=(
                    f"Created payment for baggage "
                    f"{payment.assessment.inspection.baggage.baggage_tag}"
                ),
            )

            return redirect("payment_list")

    else:
        form = PaymentForm(
            initial={
                "assessment": assessment,
            }
        )

    return render(
        request,
        "passengers/payment_form.html",
        {
            "form": form,
            "assessment": assessment,
        },
    )

@login_required
@permission_required(
    "passengers.view_payment",
    raise_exception=True,
)
def payment_detail(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related(
            "assessment",
            "assessment__inspection",
            "assessment__inspection__baggage",
            "assessment__inspection__baggage__passenger",
            "assessment__inspection__baggage__passenger__flight",
        ),
        id=payment_id,
    )

    assessment = payment.assessment
    inspection = assessment.inspection
    baggage = inspection.baggage
    clearance = getattr(baggage, "clearance", None)

    return render(
        request,
        "passengers/payment_detail.html",
        {
            "payment": payment,
            "assessment": assessment,
            "inspection": inspection,
            "baggage": baggage,
            "clearance": clearance,
        },
    )


@login_required
@permission_required(
    "passengers.change_payment",
    raise_exception=True,
)
def payment_update(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
    )

    if request.method == "POST":

        old_values = {
            "status": payment.status,
            "amount_due": payment.amount_due,
            "amount_paid": payment.amount_paid,
            "payment_method": payment.payment_method,
            "payment_reference": payment.payment_reference,
            "paid_at": payment.paid_at,
            "remarks": payment.remarks,
        }

        post_data = request.POST.copy()
        post_data["assessment"] = payment.assessment_id

        form = PaymentForm(
            post_data,
            instance=payment,
        )

        if form.is_valid():
            updated_payment = form.save()

            changes = []

            if old_values["status"] != updated_payment.status:
                changes.append(
                    f"Status: "
                    f"{old_values['status']} → "
                    f"{updated_payment.status}"
                )

            if old_values["amount_due"] != updated_payment.amount_due:
                changes.append(
                    f"Amount Due: "
                    f"{old_values['amount_due']} → "
                    f"{updated_payment.amount_due}"
                )

            if old_values["amount_paid"] != updated_payment.amount_paid:
                changes.append(
                    f"Amount Paid: "
                    f"{old_values['amount_paid']} → "
                    f"{updated_payment.amount_paid}"
                )

            if old_values["payment_method"] != updated_payment.payment_method:
                changes.append(
                    f"Payment Method: "
                    f"{old_values['payment_method']} → "
                    f"{updated_payment.payment_method}"
                )

            if old_values["payment_reference"] != updated_payment.payment_reference:
                changes.append(
                    f"Payment Reference: "
                    f"{old_values['payment_reference']} → "
                    f"{updated_payment.payment_reference}"
                )

            if old_values["paid_at"] != updated_payment.paid_at:
                changes.append(
                    f"Paid At: "
                    f"{old_values['paid_at']} → "
                    f"{updated_payment.paid_at}"
                )

            if old_values["remarks"] != updated_payment.remarks:
                changes.append(
                    f"Remarks: "
                    f"{old_values['remarks']} → "
                    f"{updated_payment.remarks}"
                )

            if changes:
                action = (
                    "status_change"
                    if old_values["status"] != updated_payment.status
                    else "update"
                )

                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name="Payment",
                    object_id=updated_payment.id,
                    description=(
                        f"Updated payment for baggage "
                        f"{updated_payment.assessment.inspection.baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect("payment_list")

    else:
        form = PaymentForm(
            instance=payment
        )

    return render(
        request,
        "passengers/payment_form.html",
        {
            "form": form,
            "payment": payment,
        },
    )

@login_required
@permission_required(
    "passengers.view_clearance",
    raise_exception=True,
)
def clearance_list(request):
    clearances = Clearance.objects.select_related(
        "baggage",
        "baggage__passenger",
    ).order_by("-created_at")

    return render(
        request,
        "passengers/clearance_list.html",
        {
            "clearances": clearances,
        },
    )

@login_required
@permission_required(
    "passengers.add_clearance",
    raise_exception=True,
)
def clearance_create(request):

    payment_id = request.GET.get("payment")

    payment = None
    baggage = None

    if payment_id:
        payment = get_object_or_404(
            Payment,
            id=payment_id,
        )

        baggage = payment.assessment.inspection.baggage

    if request.method == "POST":
        post_data = request.POST.copy()

        if baggage:
            post_data["baggage"] = baggage.pk

        form = ClearanceForm(post_data)

        if form.is_valid():
            clearance = form.save(commit=False)

            if baggage:
                clearance.baggage = baggage

            clearance.save()

            AuditLog.objects.create(
                user=request.user,
                action="clearance",
                model_name="Clearance",
                object_id=clearance.id,
                description=(
                    f"Created clearance for baggage "
                    f"{clearance.baggage.baggage_tag}"
                ),
            )

            return redirect("clearance_list")

    else:
        form = ClearanceForm(
            initial={
                "baggage": baggage,
            }
        )

    return render(
        request,
        "passengers/clearance_form.html",
        {
            "form": form,
            "payment": payment,
            "baggage": baggage,
        },
    )

@login_required
@permission_required(
    "passengers.change_clearance",
    raise_exception=True,
)
def clearance_update(request, clearance_id):
    clearance = get_object_or_404(
        Clearance,
        id=clearance_id,
    )

    if request.method == "POST":
        old_values = {
            "status": clearance.status,
            "clearance_reference": clearance.clearance_reference,
            "cleared_at": clearance.cleared_at,
            "remarks": clearance.remarks,
        }
        post_data = request.POST.copy()
        post_data["baggage"] = clearance.baggage_id

        form = ClearanceForm(
            post_data,
            instance=clearance,
        )

        if form.is_valid():
            updated_clearance = form.save()
            changes = []

            if old_values["status"] != updated_clearance.status:
                changes.append(
                    f"Status: "
                    f"{old_values['status']} → "
                    f"{updated_clearance.status}"
                )

            if old_values["clearance_reference"] != updated_clearance.clearance_reference:
                changes.append(
                    f"Clearance Reference: "
                    f"{old_values['clearance_reference']} → "
                    f"{updated_clearance.clearance_reference}"
                )

            if old_values["cleared_at"] != updated_clearance.cleared_at:
                changes.append(
                    f"Cleared At: "
                    f"{old_values['cleared_at']} → "
                    f"{updated_clearance.cleared_at}"
                )

            if old_values["remarks"] != updated_clearance.remarks:
                changes.append(
                    f"Remarks: "
                    f"{old_values['remarks']} → "
                    f"{updated_clearance.remarks}"
                )
            if changes:
                action = (
                    "status_change"
                    if old_values["status"] != updated_clearance.status
                    else "update"
                )

                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name="Clearance",
                    object_id=updated_clearance.id,
                    description=(
                        f"Updated clearance "
                        f"{updated_clearance.clearance_reference} "
                        f"for baggage "
                        f"{updated_clearance.baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )
            return redirect("clearance_list")

    else:
        form = ClearanceForm(
            instance=clearance,
        )

    return render(
        request,
        "passengers/clearance_form.html",
        {
            "form": form,
            "clearance": clearance,
        },
    )

@login_required
@permission_required(
    "passengers.view_clearance",
    raise_exception=True,
)
def clearance_detail(request, clearance_id):
    clearance = get_object_or_404(
        Clearance.objects.select_related(
            "baggage",
            "baggage__passenger",
            "baggage__passenger__flight",
        ),
        id=clearance_id,
    )

    baggage = clearance.baggage
    passenger = baggage.passenger
    inspection = getattr(baggage, "inspection", None)

    assessment = None
    payment = None

    if inspection:
        assessment = getattr(inspection, "assessment", None)

    if assessment:
        payment = getattr(assessment, "payment", None)

    cases = baggage.cases.all().order_by("-created_at")

    return render(
        request,
        "passengers/clearance_detail.html",
        {
            "clearance": clearance,
            "baggage": baggage,
            "passenger": passenger,
            "inspection": inspection,
            "assessment": assessment,
            "payment": payment,
            "cases": cases,
        },
    )

@login_required
@permission_required(
    "passengers.view_case",
    raise_exception=True,
)
def case_list(request):
    cases = Case.objects.select_related(
        "baggage",
        "baggage__passenger",
        "baggage__passenger__flight",
        "created_by",
        "resolved_by",
    ).all()

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    case_type = request.GET.get("case_type", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if search:
        cases = cases.filter(
            Q(case_reference__icontains=search)
            | Q(baggage__baggage_tag__icontains=search)
            | Q(baggage__passenger__reference_number__icontains=search)
            | Q(baggage__passenger__first_name__icontains=search)
            | Q(baggage__passenger__last_name__icontains=search)
            | Q(description__icontains=search)
            | Q(resolution__icontains=search)
        )

    if status:
        cases = cases.filter(status=status)

    if case_type:
        cases = cases.filter(case_type=case_type)

    if date_from:
        parsed_from = parse_date(date_from)

        if parsed_from:
            cases = cases.filter(
                created_at__date__gte=parsed_from
            )

    if date_to:
        parsed_to = parse_date(date_to)

        if parsed_to:
            cases = cases.filter(
                created_at__date__lte=parsed_to
            )

    cases = cases.order_by("-created_at")

    return render(
        request,
        "passengers/case_list.html",
        {
            "cases": cases,
            "search": search,
            "selected_status": status,
            "selected_case_type": case_type,
            "date_from": date_from,
            "date_to": date_to,
            "status_choices": Case.STATUS_CHOICES,
            "case_type_choices": Case.TYPE_CHOICES,
        },
    )

@login_required
@permission_required(
    "passengers.add_case",
    raise_exception=True,
)
def case_create(request):

    baggage_id = request.GET.get("baggage")

    baggage = None

    if baggage_id:
        baggage = get_object_or_404(
            Baggage,
            id=baggage_id,
        )

    if request.method == "POST":
        post_data = request.POST.copy()

        if baggage:
            post_data["baggage"] = baggage.pk

        form = CaseForm(post_data)

        if form.is_valid():
            case = form.save(commit=False)

            if baggage:
                case.baggage = baggage

            # Prevent accidentally creating another active case
            # for the same baggage through a direct URL request.
            if case.baggage and Case.objects.filter(
                baggage=case.baggage,
                status__in=["open", "under_review"],
            ).exists():
                form.add_error(
                    "baggage",
                    "This baggage already has an active case.",
                )
            else:
                case.created_by = request.user
                case.save()

                AuditLog.objects.create(
                    user=request.user,
                    action="create",
                    model_name="Case",
                    object_id=case.id,
                    description=(
                        f"Created case "
                        f"{case.case_reference} for baggage "
                        f"{case.baggage.baggage_tag}"
                    ),
                )

                return redirect("case_list")

    else:
        form = CaseForm(
            initial={
                "baggage": baggage,
            }
        )

    return render(
        request,
        "passengers/case_form.html",
        {
            "form": form,
            "baggage": baggage,
        },
    )

@login_required
@permission_required(
    "passengers.change_case",
    raise_exception=True,
)
def case_update(request, case_id):
    case = get_object_or_404(
        Case,
        id=case_id,
    )

    old_status = case.status

    if request.method == "POST":
        old_values = {
            "case_type": case.case_type,
            "status": case.status,
            "description": case.description,
            "resolution": case.resolution,
            "resolved_at": case.resolved_at,
        }
        post_data = request.POST.copy()
        post_data["baggage"] = case.baggage_id

        form = CaseForm(
            post_data,
            instance=case,
        )

        if form.is_valid():
            updated_case = form.save(commit=False)

            if (
                old_status != "resolved"
                and updated_case.status in ["resolved", "closed"]
            ):
                updated_case.resolved_by = request.user

            updated_case.save()
            changes = []

            if old_values["case_type"] != updated_case.case_type:
                changes.append(
                    f"Case Type: "
                    f"{old_values['case_type']} → "
                    f"{updated_case.case_type}"
                )

            if old_values["status"] != updated_case.status:
                changes.append(
                    f"Status: "
                    f"{old_values['status']} → "
                    f"{updated_case.status}"
                )

            if old_values["description"] != updated_case.description:
                changes.append(
                    f"Description: "
                    f"{old_values['description']} → "
                    f"{updated_case.description}"
                )

            if old_values["resolution"] != updated_case.resolution:
                changes.append(
                    f"Resolution: "
                    f"{old_values['resolution']} → "
                    f"{updated_case.resolution}"
                )

            if old_values["resolved_at"] != updated_case.resolved_at:
                changes.append(
                    f"Resolved At: "
                    f"{old_values['resolved_at']} → "
                    f"{updated_case.resolved_at}"
                )
            if changes:
                if old_values["status"] != updated_case.status:
                    if updated_case.status in ["resolved", "closed"]:
                        action = "case_resolution"
                    else:
                        action = "status_change"
                else:
                    action = "update"

                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name="Case",
                    object_id=updated_case.id,
                    description=(
                        f"Updated case {updated_case.case_reference} "
                        f"for baggage {updated_case.baggage.baggage_tag}: "
                        + "; ".join(changes)
                    ),
                )

            return redirect("case_list")

    else:
        form = CaseForm(
            instance=case,
        )

    return render(
        request,
        "passengers/case_form.html",
        {
            "form": form,
            "case": case,
        },
    )

@login_required
@permission_required(
    "passengers.view_case",
    raise_exception=True,
)
def case_detail(request, case_id):
    case = get_object_or_404(
        Case.objects.select_related(
            "baggage",
            "baggage__passenger",
            "baggage__passenger__flight",
            "created_by",
            "resolved_by",
        ),
        id=case_id,
    )

    baggage = case.baggage
    passenger = baggage.passenger
    inspection = getattr(baggage, "inspection", None)
    clearance = getattr(baggage, "clearance", None)

    assessment = None
    payment = None

    if inspection:
        assessment = getattr(inspection, "assessment", None)

    if assessment:
        payment = getattr(assessment, "payment", None)

    return render(
        request,
        "passengers/case_detail.html",
        {
            "case": case,
            "baggage": baggage,
            "passenger": passenger,
            "inspection": inspection,
            "assessment": assessment,
            "payment": payment,
            "clearance": clearance,
        },
    )

@login_required
@permission_required(
    "passengers.view_auditlog",
    raise_exception=True,
)
def audit_log_list(request):
    audit_logs = AuditLog.objects.select_related(
        "user"
    ).order_by("-created_at")

    search = request.GET.get("search", "").strip()
    action = request.GET.get("action", "")
    model_name = request.GET.get("model", "")
    date = request.GET.get("date", "")

    if search:
        audit_logs = audit_logs.filter(
            Q(user__username__icontains=search)
            | Q(description__icontains=search)
        )

    if action:
        audit_logs = audit_logs.filter(
            action=action
        )

    if model_name:
        audit_logs = audit_logs.filter(
            model_name=model_name
        )

    if date:
        audit_logs = audit_logs.filter(
            created_at__date=date
        )

    paginator = Paginator(
        audit_logs,
        20,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "audit_logs": page_obj,
        "page_obj": page_obj,
        "search": search,
        "selected_action": action,
        "selected_model": model_name,
        "selected_date": date,
        "action_choices": AuditLog.ACTION_CHOICES,
        "model_choices": AuditLog.objects.values_list(
            "model_name",
            flat=True,
        ).distinct().order_by(
            "model_name"
        ),
    }

    return render(
        request,
        "passengers/audit_log_list.html",
        context,
    )

@login_required
@permission_required(
    "passengers.view_auditlog",
    raise_exception=True,
)
def audit_log_detail(request, log_id):
    audit_log = get_object_or_404(
        AuditLog.objects.select_related("user"),
        id=log_id,
    )

    return render(
        request,
        "passengers/audit_log_detail.html",
        {
            "audit_log": audit_log,
        },
    )

@login_required
@permission_required(
    "passengers.view_baggage",
    raise_exception=True,
)
def baggage_detail(request, baggage_id):
    baggage = get_object_or_404(
        Baggage.objects.select_related(
            "passenger",
            "passenger__flight",
        ),
        id=baggage_id,
    )

    inspection = getattr(baggage, "inspection", None)

    assessment = None
    payment = None

    if inspection:
        assessment = getattr(inspection, "assessment", None)

    if assessment:
        payment = getattr(assessment, "payment", None)

    clearance = getattr(baggage, "clearance", None)

    cases = baggage.cases.all().order_by("-created_at")

    return render(
        request,
        "passengers/baggage_detail.html",
        {
            "baggage": baggage,
            "inspection": inspection,
            "assessment": assessment,
            "payment": payment,
            "clearance": clearance,
            "cases": cases,
        },
    )

@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    passengers = Passenger.objects.none()
    flights = Flight.objects.none()
    baggage = Baggage.objects.none()
    inspections = Inspection.objects.none()
    assessments = Assessment.objects.none()
    payments = Payment.objects.none()
    clearances = Clearance.objects.none()
    cases = Case.objects.none()

    if query:
        passengers = Passenger.objects.filter(
            Q(reference_number__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(passport_number__icontains=query)
        ).order_by("-arrival_datetime")[:10]

        flights = Flight.objects.filter(
            Q(flight_number__icontains=query)
            | Q(airline__icontains=query)
            | Q(origin__icontains=query)
        ).order_by("-arrival_datetime")[:10]

        baggage = Baggage.objects.select_related(
            "passenger"
        ).filter(
            Q(baggage_tag__icontains=query)
            | Q(description__icontains=query)
            | Q(passenger__reference_number__icontains=query)
            | Q(passenger__first_name__icontains=query)
            | Q(passenger__last_name__icontains=query)
        ).order_by("-created_at")[:10]

        inspections = Inspection.objects.select_related(
            "baggage",
            "baggage__passenger",
        ).filter(
            Q(baggage__baggage_tag__icontains=query)
            | Q(baggage__passenger__reference_number__icontains=query)
            | Q(findings__icontains=query)
            | Q(status__icontains=query)
            | Q(result__icontains=query)
        ).order_by("-created_at")[:10]

        assessments = Assessment.objects.select_related(
            "inspection",
            "inspection__baggage",
        ).filter(
            Q(inspection__baggage__baggage_tag__icontains=query)
            | Q(status__icontains=query)
            | Q(remarks__icontains=query)
        ).order_by("-created_at")[:10]

        payments = Payment.objects.select_related(
            "assessment",
            "assessment__inspection",
            "assessment__inspection__baggage",
        ).filter(
            Q(assessment__inspection__baggage__baggage_tag__icontains=query)
            | Q(status__icontains=query)
            | Q(payment_reference__icontains=query)
            | Q(payment_method__icontains=query)
        ).order_by("-created_at")[:10]

        clearances = Clearance.objects.select_related(
            "baggage",
            "baggage__passenger",
        ).filter(
            Q(clearance_reference__icontains=query)
            | Q(baggage__baggage_tag__icontains=query)
            | Q(status__icontains=query)
        ).order_by("-created_at")[:10]

        cases = Case.objects.select_related(
            "baggage",
            "baggage__passenger",
        ).filter(
            Q(case_reference__icontains=query)
            | Q(baggage__baggage_tag__icontains=query)
            | Q(case_type__icontains=query)
            | Q(status__icontains=query)
            | Q(description__icontains=query)
        ).order_by("-created_at")[:10]

    return render(
        request,
        "passengers/global_search.html",
        {
            "query": query,
            "passengers": passengers,
            "flights": flights,
            "baggage": baggage,
            "inspections": inspections,
            "assessments": assessments,
            "payments": payments,
            "clearances": clearances,
            "cases": cases,
        },
    )