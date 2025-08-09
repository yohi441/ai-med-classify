from django import forms

class MedicineClassificationForm(forms.Form):
    input_text = forms.CharField(
        label='Enter Medicine Name or Description',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. paracetamol tablet 500mg'}),
    )
