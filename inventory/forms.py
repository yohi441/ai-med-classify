from django import forms

from .models import Transaction, Medicine
from django.db.models import Sum
from django.forms import modelformset_factory

class MedicineClassificationForm(forms.Form):
    input_text = forms.CharField(
        label='Enter AI Question',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Enter you question here...',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm mt-10'
                         'focus:ring-2 focus:ring-blue-500 focus:border-blue-500 '
                         'text-sm resize-none',
            }
        ),
    )



class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ["medicine", "quantity_dispensed", ]
        widgets = {
            "medicine": forms.Select(attrs={
                "id": "medicine-select",
                "class": "cursor-pointer w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }),
            "quantity_dispensed": forms.NumberInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }),
           
        }
    

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
