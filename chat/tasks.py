from celery import shared_task
from .ai_model import generate_reply

@shared_task(queue='ai')
def generate_ai_reply(messages):
    try:
        return generate_reply(messages)
    except Exception as e:
        return f"⚠️ Error generating reply: {str(e)}"