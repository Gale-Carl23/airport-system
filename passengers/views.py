from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q

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
def passenger_list(request):
    search_query = request.GET.get("q", "").strip()

    passengers = Passenger.objects.all().order_by("-arrival_datetime")

    if search_query:
        passengers = passengers.filter(
            Q(reference_number__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(passport_number__icontains=search_query)
        )

    return render(
        request,
        "passengers/passenger_list.html",
        {
            "passengers": passengers,
            "search_query": search_query,
        },
    )

@login_required
def passenger_detail(request, passenger_id):
    passenger = get_object_or_404(
        Passenger,
        id=passenger_id,
    )

    return render(
        request,
        "passengers/passenger_detail.html",
        {"passenger": passenger},
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
def flight_create(request):
    if request.method == "POST":
        form = FlightForm(request.POST)

        if form.is_valid():
            form.save()
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

        form = BaggageForm(
            request.POST,
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
    ).order_by("-created_at")

    return render(
        request,
        "passengers/inspection_list.html",
        {
            "inspections": inspections,
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

        form = InspectionForm(
            request.POST,
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
    if request.method == "POST":
        form = AssessmentForm(request.POST)

        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Assessment",
                object_id=assessment.id,
                description=(
                    f"Created assessment for baggage "
                    f"{assessment.inspection.baggage.baggage_tag}. "
                    f"Declared value: {assessment.declared_value}, "
                    f"Assessed value: {assessment.assessed_value}, "
                    f"Duty: {assessment.duty_amount}, "
                    f"Tax: {assessment.tax_amount}."
                ),
            )
            return redirect("assessment_list")
    else:
        form = AssessmentForm()

    return render(
        request,
        "passengers/assessment_form.html",
        {
            "form": form,
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
    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("payment_list")

    else:
        form = PaymentForm()

    return render(
        request,
        "passengers/payment_form.html",
        {
            "form": form,
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
        form = PaymentForm(
            request.POST,
            instance=payment,
        )

        if form.is_valid():
            form.save()
            return redirect(
                "payment_list"
            )

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
    if request.method == "POST":
        form = ClearanceForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("clearance_list")

    else:
        form = ClearanceForm()

    return render(
        request,
        "passengers/clearance_form.html",
        {
            "form": form,
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
        form = ClearanceForm(
            request.POST,
            instance=clearance,
        )

        if form.is_valid():
            form.save()
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
    "passengers.view_case",
    raise_exception=True,
)
def case_list(request):
    cases = Case.objects.select_related(
    "baggage",
    "baggage__passenger",
    "created_by",
    "resolved_by",
    ).order_by("-created_at")

    return render(
        request,
        "passengers/case_list.html",
        {
            "cases": cases,
        },
    )

@login_required
@permission_required(
    "passengers.add_case",
    raise_exception=True,
)
def case_create(request):
    if request.method == "POST":
        form = CaseForm(request.POST)

        if form.is_valid():
            case = form.save(commit=False)

            case.created_by = request.user

            case.save()

            return redirect("case_list")

    else:
        form = CaseForm()

    return render(
        request,
        "passengers/case_form.html",
        {
            "form": form,
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
        form = CaseForm(
            request.POST,
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