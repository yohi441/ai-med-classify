import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from inventory.models import Classification, Medicine, Inventory, Transaction, AuditLog


class Command(BaseCommand):
    help = "Populate the database with sample data for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding database with test data..."))

        # --- 1. Create Users ---
        if not User.objects.exists():
            for i in range(5):
                User.objects.create_user(
                    username=f"user{i+1}",
                    email=f"user{i+1}@example.com",
                    password="password123"
                )
        users = list(User.objects.all())

        # --- 2. Create Classifications ---
        Classification.objects.all().delete()
        classification_labels = [
            "Antibiotic", "Analgesic", "Antipyretic", "Antihistamine",
            "Antidepressant", "Antifungal", "Antiviral", "Antihypertensive"
        ]
        classifications = []
        for label in classification_labels:
            c = Classification.objects.create(
                label=label,
                ai_confidence_score=round(random.uniform(0.6, 0.99), 2),
                notes=f"Auto-classified as {label}",
                approved=random.choice([True, False])
            )
            classifications.append(c)

        # --- 3. Create Medicines ---
        Medicine.objects.all().delete()
        med_names = [
            ("Paracetamol", "Biogesic", "Tablet", "500mg", "Unilab"),
            ("Amoxicillin", "Amoxil", "Capsule", "250mg", "GSK"),
            ("Ibuprofen", "Advil", "Tablet", "200mg", "Pfizer"),
            ("Cetirizine", "Zyrtec", "Tablet", "10mg", "UCB"),
            ("Fluconazole", "Diflucan", "Capsule", "150mg", "Pfizer"),
            ("Losartan", "Cozaar", "Tablet", "50mg", "Merck"),
            ("Metformin", "Glucophage", "Tablet", "500mg", "Bristol-Myers Squibb"),
            ("Acyclovir", "Zovirax", "Ointment", "5%", "GSK")
        ]
        medicines = []
        for _ in range(20):  # generate 20 different medicines
            generic, brand, form, strength, manufacturer = random.choice(med_names)
            m = Medicine.objects.create(
                generic_name=generic,
                brand_name=brand,
                dosage_form=form,
                strength=strength,
                manufacturer=manufacturer,
                classification=random.choice(classifications)
            )
            medicines.append(m)

        # --- 4. Create Inventory ---
        Inventory.objects.all().delete()
        inventories = []
        for med in medicines:
            for _ in range(random.randint(2, 5)):  # multiple batches
                inv = Inventory.objects.create(
                    medicine=med,
                    batch_number=f"BN{random.randint(1000, 9999)}",
                    quantity=random.randint(5, 200),
                    expiration_date=timezone.now().date() + timedelta(days=random.randint(10, 400))
                )
                inventories.append(inv)

        # --- 5. Create Transactions ---
        Transaction.objects.all().delete()
        for _ in range(50):
            inv = random.choice(inventories)
            user = random.choice(users)
            qty = random.randint(1, min(10, inv.quantity))
            stock_before = inv.quantity
            stock_after = max(0, stock_before - qty)
            inv.quantity = stock_after
            inv.save()

            Transaction.objects.create(
                user=user,
                medicine=inv.medicine,
                quantity_dispensed=qty,
                transaction_date=timezone.now() - timedelta(days=random.randint(0, 60)),
                remarks="Test transaction",
                status=random.choice(["pending", "approved", "dispensed", "rejected"]),
                classification=inv.medicine.classification,
                request_id=f"REQ-{random.randint(1000, 9999)}",
                stock_before=stock_before,
                stock_after=stock_after
            )

        # --- 6. Create Audit Logs ---
        AuditLog.objects.all().delete()
        actions = ["Added medicine", "Updated inventory", "Approved request", "Rejected request", "Dispensed medicine"]
        for _ in range(30):
            AuditLog.objects.create(
                user=random.choice(users),
                action_type=random.choice(actions),
                timestamp=timezone.now() - timedelta(days=random.randint(0, 60))
            )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully with test data!"))
