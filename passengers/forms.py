from django import forms

from .models import (
    Passenger,
    Flight, 
    Baggage,
    Inspection,
    Assessment,
    Payment,
    Clearance,
    Case,
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

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment

        fields = [
            "inspection",
            "status",
            "declared_value",
            "assessed_value",
            "duty_amount",
            "tax_amount",
            "remarks",
            "assessed_at",
        ]

        widgets = {
            "assessed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

        def clean(self):
            cleaned_data = super().clean()

            inspection = cleaned_data.get("inspection")
            status = cleaned_data.get("status")
            assessed_at = cleaned_data.get("assessed_at")

            if inspection:
                if inspection.result != "for_assessment":
                    self.add_error(
                        "inspection",
                        "An assessment can only be created for an inspection with the result 'For Assessment'.",
                    )

            if status == "completed":
                if not assessed_at:
                    self.add_error(
                        "assessed_at",
                        "A completed assessment must have an assessment date and time.",
                    )
            return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "assessment",
            "status",
            "amount_due",
            "amount_paid",
            "payment_method",
            "payment_reference",
            "paid_at",
            "remarks",
        ]

        widgets = {
            "paid_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        assessment = cleaned_data.get("assessment")
        status = cleaned_data.get("status")
        amount_due = cleaned_data.get("amount_due")
        amount_paid = cleaned_data.get("amount_paid")
        paid_at = cleaned_data.get("paid_at")

        # Payment can only be created for a completed assessment.
        if assessment:
            if assessment.status != "completed":
                self.add_error(
                    "assessment",
                    "A payment can only be created for a completed assessment.",
                )

        # Amounts cannot be negative.
        if amount_due is not None and amount_due < 0:
            self.add_error(
                "amount_due",
                "Amount due cannot be negative.",
            )

        if amount_paid is not None and amount_paid < 0:
            self.add_error(
                "amount_paid",
                "Amount paid cannot be negative.",
            )

        # A paid payment must have a payment date.
        if status == "paid":
            if not paid_at:
                self.add_error(
                    "paid_at",
                    "A paid payment must have a payment date and time.",
                )

            if amount_paid is None or amount_paid <= 0:
                self.add_error(
                    "amount_paid",
                    "A paid payment must have an amount greater than zero.",
                )

            elif amount_due is not None and amount_paid < amount_due:
                self.add_error(
                    "amount_paid",
                    "The amount paid cannot be less than the amount due.",
                )

        return cleaned_data

class ClearanceForm(forms.ModelForm):
    class Meta:
        model = Clearance
        fields = [
            "baggage",
            "status",
            "clearance_reference",
            "cleared_at",
            "remarks",
        ]

        widgets = {
            "cleared_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        baggage = cleaned_data.get("baggage")
        status = cleaned_data.get("status")
        cleared_at = cleaned_data.get("cleared_at")

        if not baggage:
            return cleaned_data

        # Get the inspection belonging to this baggage.
        try:
            inspection = baggage.inspection
        except Inspection.DoesNotExist:
            self.add_error(
                "baggage",
                "This baggage does not have an inspection.",
            )
            return cleaned_data

        # A baggage cannot be cleared while inspection is incomplete.
        if inspection.status != "completed":
            self.add_error(
                "baggage",
                "The inspection must be completed before clearance.",
            )

        # Held or seized inspection results cannot be cleared.
        if inspection.result in ["held", "seized"]:
            self.add_error(
                "baggage",
                "This baggage cannot be cleared because the inspection result requires further action.",
            )

        # If assessment is required, it must be completed.
        if inspection.result == "for_assessment":

            try:
                assessment = inspection.assessment
            except Assessment.DoesNotExist:
                self.add_error(
                    "baggage",
                    "This baggage requires an assessment before clearance.",
                )
                return cleaned_data

            if assessment.status != "completed":
                self.add_error(
                    "baggage",
                    "The assessment must be completed before clearance.",
                )

            # Payment must exist and be paid.
            try:
                payment = assessment.payment
            except Payment.DoesNotExist:
                self.add_error(
                    "baggage",
                    "Payment is required before clearance.",
                )
                return cleaned_data

            if payment.status != "paid":
                self.add_error(
                    "baggage",
                    "The payment must be completed before clearance.",
                )

        # A cleared record must have a date/time.
        if status == "cleared" and not cleared_at:
            self.add_error(
                "cleared_at",
                "A cleared baggage record must have a clearance date and time.",
            )

        return cleaned_data

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            "baggage",
            "case_reference",
            "case_type",
            "status",
            "description",
            "resolution",
            "resolved_at",
        ]

        widgets = {
            "resolved_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        baggage = cleaned_data.get("baggage")
        status = cleaned_data.get("status")
        resolution = cleaned_data.get("resolution")
        resolved_at = cleaned_data.get("resolved_at")

        if not baggage:
            return cleaned_data

        # A case should have an inspection.
        try:
            inspection = baggage.inspection
        except Inspection.DoesNotExist:
            self.add_error(
                "baggage",
                "This baggage does not have an inspection.",
            )
            return cleaned_data

        # A case should normally originate from a held or seized inspection.
        if inspection.result not in ["held", "seized"]:
            self.add_error(
                "baggage",
                "A case can only be created for baggage with a Held or Seized inspection result.",
            )

        # Resolved and closed cases require a resolution.
        if status in ["resolved", "closed"]:
            if not resolution:
                self.add_error(
                    "resolution",
                    "A resolved or closed case must have a resolution.",
                )

            if not resolved_at:
                self.add_error(
                    "resolved_at",
                    "A resolved or closed case must have a resolution date and time.",
                )

        # Open and under-review cases should not have a resolution date.
        if status in ["open", "under_review"]:
            if resolved_at:
                self.add_error(
                    "resolved_at",
                    "An open or under-review case cannot have a resolution date.",
                )

        return cleaned_data