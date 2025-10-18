from django.shortcuts import render

# Create your views here.
from django.views import View
from django.urls import reverse_lazy
from inventory.forms import MedicineClassificationForm
from ai.classify import classify_medicine  # We'll make this next
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Medicine, Inventory, Classification
from django.db.models import Q, Sum
from datetime import datetime


class MedicineClassificationView(LoginRequiredMixin, View):
    template_name = 'inventory/classify.html'
    login_url = 'login'
    success_url = reverse_lazy('classify')
    CONFIDENCE_THRESHOLD = 10  # percent

    def get(self, request):
        """Render the blank classification form."""
        form = MedicineClassificationForm()
        context = {
            'form': form,
            'now': datetime.now(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle form submission, run AI classification, and return results."""
        form = MedicineClassificationForm(request.POST)
        if not form.is_valid():
            # Invalid form: redisplay with errors
            return render(request, self.template_name, {
                'form': form,
                'now': datetime.now(),
            })

        input_text = form.cleaned_data['input_text']

        # 1️⃣ Run AI classifier
        ai_result = classify_medicine(input_text)
        predicted_label = ai_result["label"]
        top_score = ai_result["score"]  # already in percentage

        medicines = Medicine.objects.none()
        classification = None

        # 2️⃣ Only proceed if confidence meets threshold
        if top_score >= self.CONFIDENCE_THRESHOLD:
            medicines = Medicine.objects.filter(
                classification__label__iexact=predicted_label
            ).annotate(total_stock=Sum("inventory__quantity"))

            classification = Classification.objects.create(
                label=predicted_label,
                ai_confidence_score=top_score,
                approved=False
            )

        # 3️⃣ Return rendered response (for HTMX or normal)
        context = {
            'form': form,
            'ai': ai_result,
            'medicines': medicines,
            'classification': classification,
            'confidence_threshold': self.CONFIDENCE_THRESHOLD,
            'now': datetime.now(),
        }
        if request.htmx:
            print("HTMX request detected.")
            return render(request, 'inventory/partials/classify/form_partials.html', context)
        return render(request, self.template_name, context)