from django import forms

from .models import Transaction, Medicine
from django.db.models import Sum
from django.forms import modelformset_factory

class MedicineClassificationForm(forms.Form):
    input_text = forms.CharField(
        label='Enter Medicine Name or Description',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'e.g. paracetamol tablet 500mg',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm '
                         'focus:ring-2 focus:ring-blue-500 focus:border-blue-500 '
                         'text-sm resize-none',
            }
        ),
    )



class TransactionForm(forms.ModelForm):
  
    class Meta:
        model = Transaction
        fields = ["medicine", "quantity_dispensed", "dosage", "remarks"]
        widgets = {
            "medicine": forms.Select(attrs={
                "class": "cursor-pointer w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }),
            "quantity_dispensed": forms.NumberInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }),
           "dosage": forms.Select(attrs={
                "class": "cursor-pointer w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }),
            "remarks": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only include medicines that have stock > 0
        medicines_with_stock = (
            Medicine.objects.annotate(total_stock=Sum("inventory__quantity"))
            .filter(total_stock__gt=0)
        )
        self.fields["medicine"].queryset = medicines_with_stock
        self.fields["dosage"].required = True

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get("medicine")
        qty = cleaned_data.get("quantity_dispensed")

        

        if medicine and qty:
            total_stock = medicine.inventory.aggregate(total=Sum("quantity"))["total"] or 0
            if qty > total_stock:
                self.add_error("quantity_dispensed", f"Not enough stock. Available: {total_stock}")

        return cleaned_data
    

TransactionFormSet = modelformset_factory(
    Transaction,
    form=TransactionForm,
    extra=0,
    can_delete=True  # allows deleting rows
)
