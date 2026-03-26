# fix_credit_score.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_site.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

count = User.objects.all().update(credit_score=100)
print(f"✅ Updated {count} users to 100")