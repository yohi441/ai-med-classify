from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from inventory.forms import MedicineClassificationForm
from ai.classify import classify_medicine  # We'll make this next
from django.contrib.auth.mixins import LoginRequiredMixin


class MedicineClassificationView(LoginRequiredMixin, FormView):
    template_name = 'inventory/classify.html'
    form_class = MedicineClassificationForm
    success_url = reverse_lazy('inventory:classify')  # stays on the same page
    login_url = 'login'

    def form_valid(self, form):
        input_text = form.cleaned_data['input_text']
        result = classify_medicine(input_text)

        # Add prediction result to the context
        return self.render_to_response(self.get_context_data(
            form=form,
            result=result
        ))
