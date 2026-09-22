from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q


from .models import Passenger, Flight, Baggage
from .forms import PassengerForm, FlightForm, BaggageForm


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