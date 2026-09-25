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
def passenger_create(request):

    if request.method == "POST":
        form = PassengerForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("passenger_list")

    else:
        form = PassengerForm()

    return render(
        request,
        "passengers/passenger_form.html",
        {"form": form},
    )

@login_required
def passenger_update(request, passenger_id):
    passenger = get_object_or_404(
        Passenger,
        id=passenger_id,
    )

    if request.method == "POST":
        form = PassengerForm(
            request.POST,
            instance=passenger,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "passenger_detail",
                passenger_id=passenger.id,
            )

    else:
        form = PassengerForm(instance=passenger)

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
def baggage_create(request):
    if request.method == "POST":
        form = BaggageForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("baggage_list")
    else:
        form = BaggageForm()

    return render(
        request,
        "passengers/baggage_form.html",
        {
            "form": form,
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
            form.save()
            return redirect("inspection_list")
    else:
        form = InspectionForm()

    return render(
        request,
        "passengers/inspection_form.html",
        {
            "form": form,
        },
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
        form = InspectionForm(
            request.POST,
            instance=inspection,
        )

        if form.is_valid():
            form.save()
            return redirect(
                "inspection_list"
            )
    else:
        form = InspectionForm(
            instance=inspection
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