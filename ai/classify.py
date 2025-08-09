# ai/classify.py

from transformers import pipeline

# Load the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the labels your app will recognize
CANDIDATE_LABELS = [
    "antibiotic",
    "painkiller",
    "antipyretic",
    "antiseptic",
    "antiviral",
    "antifungal",
    "vitamin supplement",
    "cough suppressant",
    "antihistamine",
]

def classify_medicine(text):
    result = classifier(text, CANDIDATE_LABELS)
    
    top_label = result['labels'][0]
    top_score = round(result['scores'][0] * 100, 2)

    return {
        "label": top_label,
        "score": top_score,
        "all": list(zip(result['labels'], [round(s * 100, 2) for s in result['scores']]))
    }
