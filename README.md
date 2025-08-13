# 🐥 AI Med Classify (Prototype)


---

## 📦 Requirements
- Python 3.12+
- pip
- Virtualenv (recommended)
- Django 5.2.4

---
Create & activate a virtual environment

python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate 

Install dependencies

pip install -r requirements.txt
Apply database migrations

python manage.py migrate
Create a superuser

python manage.py createsuperuser
Run the development server

python manage.py runserver
