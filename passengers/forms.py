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


# ==========================================================
# PASSENGER
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }


# ==========================================================
# FLIGHT
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }


# ==========================================================
# BAGGAGE
# ==========================================================

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

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")

        if weight is not None and weight < 0:
            raise forms.ValidationError(
                "Baggage weight cannot be negative."
            )

        return weight


# ==========================================================
# INSPECTION
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        result = cleaned_data.get("result")
        inspected_at = cleaned_data.get("inspected_at")

        # --------------------------------------------------
        # Pending / In Progress
        # --------------------------------------------------

        if status in ["pending", "in_progress"]:

            if result != "not_set":
                self.add_error(
                    "result",
                    "The inspection result must be 'Not Set' "
                    "while the inspection is not completed.",
                )

            if inspected_at:
                self.add_error(
                    "inspected_at",
                    "An inspection date and time should only be "
                    "provided when the inspection is completed.",
                )

        # --------------------------------------------------
        # Completed
        # --------------------------------------------------

        if status == "completed":

            if result == "not_set":
                self.add_error(
                    "result",
                    "A completed inspection must have a result.",
                )

            if not inspected_at:
                self.add_error(
                    "inspected_at",
                    "A completed inspection must have an "
                    "inspection date and time.",
                )

        return cleaned_data


# ==========================================================
# ASSESSMENT
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }

    def clean_declared_value(self):
        value = self.cleaned_data.get("declared_value")

        if value is not None and value < 0:
            raise forms.ValidationError(
                "Declared value cannot be negative."
            )

        return value

    def clean_assessed_value(self):
        value = self.cleaned_data.get("assessed_value")

        if value is not None and value < 0:
            raise forms.ValidationError(
                "Assessed value cannot be negative."
            )

        return value

    def clean_duty_amount(self):
        value = self.cleaned_data.get("duty_amount")

        if value is not None and value < 0:
            raise forms.ValidationError(
                "Duty amount cannot be negative."
            )

        return value

    def clean_tax_amount(self):
        value = self.cleaned_data.get("tax_amount")

        if value is not None and value < 0:
            raise forms.ValidationError(
                "Tax amount cannot be negative."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        inspection = cleaned_data.get("inspection")
        status = cleaned_data.get("status")
        assessed_at = cleaned_data.get("assessed_at")

        # --------------------------------------------------
        # Inspection validation
        # --------------------------------------------------

        if inspection:

            if inspection.status != "completed":
                self.add_error(
                    "inspection",
                    "The inspection must be completed "
                    "before assessment.",
                )

            if inspection.result != "for_assessment":
                self.add_error(
                    "inspection",
                    "An assessment can only be created for "
                    "an inspection with the result "
                    "'For Assessment'.",
                )

        # --------------------------------------------------
        # Assessment completion
        # --------------------------------------------------

        if status == "completed":

            if not assessed_at:
                self.add_error(
                    "assessed_at",
                    "A completed assessment must have an "
                    "assessment date and time.",
                )

        # --------------------------------------------------
        # Pending assessment
        # --------------------------------------------------

        if status == "pending" and assessed_at:

            self.add_error(
                "assessed_at",
                "An assessment date should only be provided "
                "when the assessment is completed.",
            )

        return cleaned_data


# ==========================================================
# PAYMENT
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }

    def clean_amount_due(self):
        amount = self.cleaned_data.get("amount_due")

        if amount is not None and amount < 0:
            raise forms.ValidationError(
                "Amount due cannot be negative."
            )

        return amount

    def clean_amount_paid(self):
        amount = self.cleaned_data.get("amount_paid")

        if amount is not None and amount < 0:
            raise forms.ValidationError(
                "Amount paid cannot be negative."
            )

        return amount

    def clean(self):
        cleaned_data = super().clean()

        assessment = cleaned_data.get("assessment")
        status = cleaned_data.get("status")
        amount_due = cleaned_data.get("amount_due")
        amount_paid = cleaned_data.get("amount_paid")
        payment_method = cleaned_data.get("payment_method")
        payment_reference = cleaned_data.get("payment_reference")
        paid_at = cleaned_data.get("paid_at")

        # --------------------------------------------------
        # Assessment validation
        # --------------------------------------------------

        if assessment:

            if assessment.status != "completed":
                self.add_error(
                    "assessment",
                    "A payment can only be created for "
                    "a completed assessment.",
                )

        # --------------------------------------------------
        # Paid payment
        # --------------------------------------------------

        if status == "paid":

            if not paid_at:
                self.add_error(
                    "paid_at",
                    "A paid payment must have a payment "
                    "date and time.",
                )

            if amount_paid is None or amount_paid <= 0:
                self.add_error(
                    "amount_paid",
                    "A paid payment must have an amount "
                    "greater than zero.",
                )

            if (
                amount_due is not None
                and amount_paid is not None
                and amount_paid < amount_due
            ):
                self.add_error(
                    "amount_paid",
                    "The amount paid cannot be less "
                    "than the amount due.",
                )

            if not payment_method:
                self.add_error(
                    "payment_method",
                    "A payment method is required "
                    "when the payment is marked as paid.",
                )

            if not payment_reference:
                self.add_error(
                    "payment_reference",
                    "A payment reference is required "
                    "when the payment is marked as paid.",
                )

        # --------------------------------------------------
        # Pending payment
        # --------------------------------------------------

        if status == "pending":

            if paid_at:
                self.add_error(
                    "paid_at",
                    "A pending payment cannot have a "
                    "payment date.",
                )

        # --------------------------------------------------
        # Cancelled payment
        # --------------------------------------------------

        if status == "cancelled":

            if paid_at:
                self.add_error(
                    "paid_at",
                    "A cancelled payment cannot have a "
                    "payment date.",
                )

        return cleaned_data


# ==========================================================
# CLEARANCE
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        baggage = cleaned_data.get("baggage")
        status = cleaned_data.get("status")
        cleared_at = cleaned_data.get("cleared_at")

        if not baggage:
            return cleaned_data

        # --------------------------------------------------
        # 1. Baggage must have an inspection
        # --------------------------------------------------

        try:
            inspection = baggage.inspection

        except Inspection.DoesNotExist:

            self.add_error(
                "baggage",
                "This baggage does not have an inspection.",
            )

            return cleaned_data

        # --------------------------------------------------
        # 2. Inspection must be completed
        # --------------------------------------------------

        if inspection.status != "completed":

            self.add_error(
                "baggage",
                "The inspection must be completed "
                "before clearance.",
            )

        # --------------------------------------------------
        # 3. Held / Seized cannot be cleared
        # --------------------------------------------------

        if inspection.result in ["held", "seized"]:

            self.add_error(
                "baggage",
                "This baggage requires further action "
                "and cannot be cleared.",
            )

        # --------------------------------------------------
        # 4. Result must allow clearance
        # --------------------------------------------------

        if inspection.result not in [
            "cleared",
            "for_assessment",
        ]:

            self.add_error(
                "baggage",
                "This inspection result does not "
                "allow clearance.",
            )

        # --------------------------------------------------
        # 5. Assessment and payment
        # --------------------------------------------------

        if inspection.result == "for_assessment":

            try:
                assessment = inspection.assessment

            except Assessment.DoesNotExist:

                self.add_error(
                    "baggage",
                    "This baggage requires an "
                    "assessment before clearance.",
                )

                return cleaned_data

            if assessment.status != "completed":

                self.add_error(
                    "baggage",
                    "The assessment must be completed "
                    "before clearance.",
                )

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
                    "The payment must be completed "
                    "before clearance.",
                )

        # --------------------------------------------------
        # 6. Cleared status
        # --------------------------------------------------

        if status == "cleared":

            if not cleared_at:

                self.add_error(
                    "cleared_at",
                    "A cleared baggage record must have "
                    "a clearance date and time.",
                )

        # --------------------------------------------------
        # 7. Non-cleared status
        # --------------------------------------------------

        if status != "cleared" and cleared_at:

            self.add_error(
                "cleared_at",
                "Only cleared baggage can have a "
                "clearance date and time.",
            )

        return cleaned_data


# ==========================================================
# CASE
# ==========================================================

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
                attrs={
                    "type": "datetime-local",
                }
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

        # --------------------------------------------------
        # 1. Baggage must have an inspection
        # --------------------------------------------------

        try:
            inspection = baggage.inspection

        except Inspection.DoesNotExist:

            self.add_error(
                "baggage",
                "This baggage does not have an inspection.",
            )

            return cleaned_data

        # --------------------------------------------------
        # 2. Case must originate from Held / Seized
        # --------------------------------------------------

        if inspection.result not in [
            "held",
            "seized",
        ]:

            self.add_error(
                "baggage",
                "A case can only be created for baggage "
                "with a Held or Seized inspection result.",
            )

        # --------------------------------------------------
        # 3. New cases must start as Open
        # --------------------------------------------------

        if not self.instance.pk:

            if status != "open":

                self.add_error(
                    "status",
                    "A new case must start with "
                    "the status 'Open'.",
                )

        # --------------------------------------------------
        # 4. Existing case status transitions
        # --------------------------------------------------

        else:

            old_status = self.instance.status

            allowed_transitions = {
                "open": [
                    "under_review",
                ],

                "under_review": [
                    "resolved",
                ],

                "resolved": [
                    "closed",
                ],

                "closed": [],
            }

            if status != old_status:

                allowed_next_statuses = (
                    allowed_transitions.get(
                        old_status,
                        [],
                    )
                )

                if status not in allowed_next_statuses:

                    self.add_error(
                        "status",
                        f"A case with status "
                        f"'{self.instance.get_status_display()}' "
                        f"cannot be changed directly to "
                        f"'{dict(Case.STATUS_CHOICES).get(status, status)}'.",
                    )

        # --------------------------------------------------
        # 5. Resolution requirements
        # --------------------------------------------------

        if status in [
            "resolved",
            "closed",
        ]:

            if not resolution:

                self.add_error(
                    "resolution",
                    "A resolved or closed case must "
                    "have a resolution.",
                )

            if not resolved_at:

                self.add_error(
                    "resolved_at",
                    "A resolved or closed case must have "
                    "a resolution date and time.",
                )

        # --------------------------------------------------
        # 6. Open / Under Review
        # --------------------------------------------------

        if status in [
            "open",
            "under_review",
        ]:

            if resolved_at:

                self.add_error(
                    "resolved_at",
                    "An open or under-review case cannot "
                    "have a resolution date.",
                )

        return cleaned_data

