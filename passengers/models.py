from django.db import models


class Passenger(models.Model):
    reference_number = models.CharField(max_length=20, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    passport_number = models.CharField(max_length=30)
    nationality = models.CharField(max_length=100)
    flight = models.ForeignKey(
        "Flight",
        on_delete=models.PROTECT,
        related_name="passengers",
        null=True, blank=True
        )   
    arrival_datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    airline = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    arrival_datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.flight_number} - {self.airline}"


class Baggage(models.Model):
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="baggage",
    )

    baggage_tag = models.CharField(
        max_length=30,
        unique=True,
    )

    description = models.CharField(
        max_length=255,
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    declared = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.baggage_tag

class Inspection(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    RESULT_CHOICES = [
        ("not_set", "Not Set"),
        ("cleared", "Cleared"),
        ("for_assessment", "For Assessment"),
        ("held", "Held"),
        ("seized", "Seized"),
    ]

    baggage = models.OneToOneField(
        Baggage,
        on_delete=models.PROTECT,
        related_name="inspection",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    result = models.CharField(
        max_length=30,
        choices=RESULT_CHOICES,
        default="not_set",
    )

    findings = models.TextField(
        blank=True,
    )

    inspected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Inspection - {self.baggage.baggage_tag}"

class Assessment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]

    inspection = models.OneToOneField(
        Inspection,
        on_delete=models.PROTECT,
        related_name="assessment",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    declared_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    assessed_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    duty_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    remarks = models.TextField(
        blank=True,
    )

    assessed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Assessment - {self.inspection.baggage.baggage_tag}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("other", "Other"),
    ]

    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.PROTECT,
        related_name="payment",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        blank=True,
    )

    payment_reference = models.CharField(
        max_length=50,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Payment - {self.assessment.inspection.baggage.baggage_tag}"