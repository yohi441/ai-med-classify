from django.shortcuts import render

# Create your views here.
from django.views import View
from django.urls import reverse_lazy
from inventory.forms import MedicineClassificationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Notification, ChatSession, ChatMessage
from django.db.models import Q, Sum
from datetime import datetime
from openai import OpenAI
import markdown
<<<<<<< HEAD
from config.settings import HF_API_KEY
=======
from django.conf import settings
>>>>>>> 5750e87 (Update the hf api keys)


class MedicineClassificationView(LoginRequiredMixin, View):
    template_name = 'inventory/classify.html'
    login_url = 'login'
    CONFIDENCE_THRESHOLD = 10  # percent

    def generate_ai_reply(self, input_text):
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=settings.HF_API_KEY
        )

        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:cerebras",
            messages=[
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
        )

     
        return completion.choices[0].message.content

    def get(self, request):
        """Render the blank classification form."""
        form = MedicineClassificationForm()
        session, _ = ChatSession.objects.get_or_create(user=request.user)
        messages = session.messages.order_by("-created_at")
        context = {
            'form': form,
            'now': datetime.now(),
            "ai_messages": messages,
            "show_typing": False, 
            "notifications": Notification.objects.filter(is_read=False).order_by('-created_at'),
            "notification_count": Notification.objects.filter(counted=True).count(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Process the classification form submission."""
        form = MedicineClassificationForm(request.POST)
        ai_response = None
        user_question = None

        if form.is_valid():
            input_text = form.cleaned_data['input_text']
            # Call the AI service to get a response
            
            
            session, _ = ChatSession.objects.get_or_create(user=request.user)
            
            
            ai_response = self.generate_ai_reply(input_text)
            # Save user question
            ChatMessage.objects.create(
                session=session,
                sender="user",
                content=input_text
            )
            # Save AI reply
            ChatMessage.objects.create(
                session=session,
                sender="ai",
                content=ai_response
            )
            
            
            
        ai_response = markdown.markdown(ai_response)
        messages = session.messages.order_by("-created_at")
        form = MedicineClassificationForm()
        context = {
            'form': form,
            "ai_messages": messages,
            'ai_response': ai_response,
            "user_question": user_question,
            "show_typing": True,
            'now': datetime.now(),
            "notifications": Notification.objects.filter(is_read=False).order_by('-created_at'),
            "notification_count": Notification.objects.filter(counted=True).count(),
        }
        return render(request, self.template_name, context)
    



    


