from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from inventory.forms import MedicineClassificationForm
from ai.classify import classify_medicine  # We'll make this next
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Medicine, Inventory, Classification
from django.db.models import Q, Sum
from datetime import datetime


class MedicineClassificationView(LoginRequiredMixin, FormView):
    template_name = 'inventory/classify.html'
    form_class = MedicineClassificationForm
    success_url = reverse_lazy('classify')
    login_url = 'login'

    def form_valid(self, form):
        input_text = form.cleaned_data['input_text']

        # 1. Run AI classifier
        ai_result = classify_medicine(input_text)
        predicted_label = ai_result["label"]
        top_score = ai_result["score"]  # Already in percentage

         # 2. Only proceed if confidence is above threshold
        CONFIDENCE_THRESHOLD = 10  # percent
        medicines = Medicine.objects.none()
        classification = None

        if top_score >= CONFIDENCE_THRESHOLD:
            # Find medicines in DB that match the predicted category
            medicines = Medicine.objects.filter(
                classification__label__iexact=predicted_label
            ).annotate(total_stock=Sum("inventory__quantity"))

            # Store classification
            classification = Classification.objects.create(
                label=predicted_label,
                ai_confidence_score=top_score,
                approved=False
            )

        return self.render_to_response(self.get_context_data(
            form=form,
            ai=ai_result,
            medicines=medicines,
            classification=classification,
            confidence_threshold=CONFIDENCE_THRESHOLD
        ))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = datetime.now()

        return context
