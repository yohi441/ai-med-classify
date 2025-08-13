from django.db import models
from django.contrib.auth.models import User

class Classification(models.Model):
    medicine = models.ForeignKey("Medicine", on_delete=models.CASCADE, null=True, blank=True, related_name="classifications")
    label = models.CharField(max_length=100)
    ai_confidence_score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} ({'Approved' if self.approved else 'Pending'})"

class Medicine(models.Model):
    generic_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255, blank=True)
    dosage_form = models.CharField(max_length=100)
    strength = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255, blank=True)
    classification = models.ForeignKey(Classification, on_delete=models.SET_NULL, null=True, blank=True, related_name="medicines")

    def __str__(self):
        return f"{self.generic_name} ({self.brand_name})"

class Inventory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine.generic_name} - Batch {self.batch_number}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity_dispensed = models.PositiveIntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("dispensed", "Dispensed"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )
    classification = models.ForeignKey(
        "Classification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    request_id = models.CharField(max_length=100, blank=True, null=True) #NOSONAR
    stock_before = models.PositiveIntegerField(null=True, blank=True)
    stock_after = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.quantity_dispensed} of {self.medicine} by {self.user}"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} @ {self.timestamp}"
