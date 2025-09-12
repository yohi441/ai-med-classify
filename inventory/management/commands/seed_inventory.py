import random
from django.core.management.base import BaseCommand
from inventory.models import Medicine, Classification, Inventory, Transaction
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Seed the database with fresh test medicines, classifications, and inventory data."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🚨 Deleting old data..."))

        Transaction.objects.all().delete()
        Inventory.objects.all().delete()
        Medicine.objects.all().delete()
        Classification.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("✅ Old data cleared."))

        # Common classification labels
        labels = [
            "antibiotic",
            "antiviral",
            "antifungal",
            "antipyretic",
            "painkiller",
            "anti-inflammatory",
            "antihistamine",
            "cough suppressant",
            "expectorant",
            "antihypertensive",
            "antidiabetic",
            "antidepressant",
            "antiseptic",
            "vitamin supplement",
            "proton pump inhibitor",
        ]

        classification_objs = {}
        for label in labels:
            obj, _ = Classification.objects.get_or_create(label=label)
            classification_objs[label] = obj

        # Example medicines with manufacturers
        medicines_data = [
            ("Paracetamol", "Biogesic", "Tablet", "500mg", "Unilab", ["antipyretic", "painkiller"]),
            ("Ibuprofen", "Advil", "Tablet", "200mg", "Pfizer", ["painkiller", "anti-inflammatory"]),
            ("Amoxicillin", "Amoxil", "Capsule", "500mg", "GSK", ["antibiotic"]),
            ("Acyclovir", "Zovirax", "Ointment", "5%", "GSK", ["antiviral"]),
            ("Cetirizine", "Zyrtec", "Tablet", "10mg", "UCB Pharma", ["antihistamine"]),
            ("Metformin", "Glucophage", "Tablet", "500mg", "Merck", ["antidiabetic"]),
            ("Losartan", "Cozaar", "Tablet", "50mg", "Merck", ["antihypertensive"]),
            ("Fluoxetine", "Prozac", "Capsule", "20mg", "Eli Lilly", ["antidepressant"]),
            ("Omeprazole", "Prilosec", "Capsule", "20mg", "AstraZeneca", ["proton pump inhibitor"]),
            ("Ascorbic Acid", "Cecon", "Tablet", "500mg", "Unilab", ["vitamin supplement"]),
            ("Clotrimazole", "Canesten", "Cream", "1%", "Bayer", ["antifungal", "antiseptic"]),
            ("Salbutamol", "Ventolin", "Inhaler", "100mcg", "GSK", ["expectorant"]),
            ("Dextromethorphan", "Robitussin DM", "Syrup", "15mg/5ml", "Pfizer", ["cough suppressant"]),
        ]

        # Expand dataset (~100 medicines)
        expanded_data = []
        for i in range(1, 9):  # 8 variations
            for med in medicines_data:
                generic, brand, form, strength, manufacturer, clfs = med
                expanded_data.append((
                    f"{generic} {i}",
                    f"{brand} {i}",
                    form,
                    strength,
                    manufacturer,
                    clfs
                ))

        self.stdout.write(self.style.WARNING("📦 Seeding medicines and inventory..."))

        # Create medicines & link classifications
        for med in expanded_data:
            generic, brand, form, strength, manufacturer, clfs = med
            medicine = Medicine.objects.create(
                generic_name=generic,
                brand_name=brand,
                dosage_form=form,
                strength=strength,
                manufacturer=manufacturer,
            )
            medicine.classification.set([classification_objs[c] for c in clfs])

            # Add random inventory batches
            for _ in range(random.randint(1, 3)):
                Inventory.objects.create(
                    medicine=medicine,
                    batch_number=f"BN{random.randint(1000,9999)}",
                    quantity=random.randint(10, 200),
                    expiration_date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
                )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully with ~100 medicines."))
