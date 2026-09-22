from django import forms

from .models import (
    Passenger,
    Flight, 
    Baggage,
    Inspection
    )


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger

        fields = [
            "reference_number",
            "first_name",
            "last_name",
            "passport_number",
            "nationality",
            "flight",
            "arrival_datetime",
        ]

        widgets = {
            "arrival_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight

        fields = [
            "flight_number",
            "airline",
            "origin",
            "arrival_datetime",
        ]

        widgets = {
            "arrival_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

class BaggageForm(forms.ModelForm):
    class Meta:
        model = Baggage

        fields = [
            "passenger",
            "baggage_tag",
            "description",
            "weight",
            "declared",
        ]

class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection

        fields = [
            "baggage",
            "status",
            "result",
            "findings",
            "inspected_at",
        ]

        widgets = {
            "inspected_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        result = cleaned_data.get("result")
        inspected_at = cleaned_data.get("inspected_at")

        if status in ["pending", "in_progress"]:
            if result != "not_set":
                self.add_error(
                    "result",
                    "The inspection result must be 'Not Set' while the inspection is not completed.",
                )

        if status == "completed":
            if result == "not_set":
                self.add_error(
                    "result",
                    "A completed inspection must have a result.",
                )

            if not inspected_at:
                self.add_error(
                    "inspected_at",
                    "A completed inspection must have an inspection date and time.",
                )

        return cleaned_data

