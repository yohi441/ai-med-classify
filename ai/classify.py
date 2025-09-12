# ai/classify.py

from transformers import pipeline

# Load the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the labels your app will recognize
CANDIDATE_LABELS = [
    "antibiotic",          # fights bacterial infections
    "antiviral",           # fights viral infections
    "antifungal",          # fights fungal infections
    "antipyretic",         # reduces fever
    "painkiller",          # relieves pain (general analgesics)
    "anti-inflammatory",   # reduces inflammation
    "antihistamine",       # treats allergies
    "cough suppressant",   # relieves cough
    "expectorant",         # helps clear mucus
    "antihypertensive",    # lowers blood pressure
    "antidiabetic",        # controls blood sugar
    "antidepressant",      # treats depression
    "antiseptic",          # prevents infection (external use)
    "vitamin supplement",  # supports nutrition
    "proton pump inhibitor" # reduces stomach acid (e.g., GERD)
]
   



def classify_medicine(text):
    result = classifier(text, CANDIDATE_LABELS)
    
    top_label = result['labels'][0]
    top_score = round(result['scores'][0] * 100, 2)
    print(result['labels'])
    print(result['scores'])

    # return top_label, top_score
    
    return {
        "label": top_label,
        "score": top_score,
        # "all": list(zip(result['labels'], [round(s * 100, 2) for s in result['scores']]))
    }
