#!/usr/bin/env python
"""
Test script to submit stocktaking surplus form like a normal user.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invproj.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from inventory import models

User = get_user_model()

# Create test client
client = Client()

# Login as a user (you may need to adjust this)
# Try to get first superuser or create one
try:
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found. Creating one...")
        user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    client.force_login(user)
    print(f"Logged in as: {user.username}")
except Exception as e:
    print(f"Error logging in: {e}")
    sys.exit(1)

# Set active company in session (if needed)
# You may need to adjust this based on your company setup
try:
    company = models.Company.objects.first()
    if company:
        session = client.session
        session['active_company_id'] = company.id
        session.save()
        print(f"Active company set to: {company.id}")
except Exception as e:
    print(f"Warning: Could not set active company: {e}")

# First, get the form page to get CSRF token
print("\n=== Step 1: Getting form page ===")
response = client.get('/fa/inventory/stocktaking/surplus/create/')
print(f"Status code: {response.status_code}")

if response.status_code != 200:
    print(f"Error: Could not get form page. Status: {response.status_code}")
    print(response.content[:500])
    sys.exit(1)

# Extract CSRF token from the response
from django.middleware.csrf import get_token
csrf_token = get_token(response.wsgi_request)
print(f"CSRF token: {csrf_token[:20]}...")

# Prepare form data (like a normal user would fill)
print("\n=== Step 2: Preparing form data ===")
form_data = {
    'csrfmiddlewaretoken': csrf_token,
    'document_code': '',  # Will be auto-generated
    'document_date': '2025-12-26',
    'stocktaking_session_id': '',  # Empty as per logs
    
    # Formset management form
    'lines-TOTAL_FORMS': '1',
    'lines-INITIAL_FORMS': '0',
    'lines-MIN_NUM_FORMS': '1',
    'lines-MAX_NUM_FORMS': '1000',
    
    # Line 0 data (the values you provided)
    'lines-0-item': '23',  # Item ID
    'lines-0-warehouse': '10',  # Warehouse ID
    'lines-0-unit': 'EA',  # Unit
    'lines-0-quantity_expected': '2762',
    'lines-0-quantity_counted': '2765',
    'lines-0-quantity_adjusted': '3.000000',  # Auto-calculated: 2765 - 2762 = 3
    'lines-0-id': '',
    'lines-0-document': '',
    'lines-0-adjustment_metadata': '{}',
    'lines-0-valuation_method': '',
    'lines-0-unit_cost': '',
    'lines-0-total_cost': '',
    'lines-0-reason_code': '',
    'lines-0-investigation_reference': '',
}

print("Form data prepared:")
for key, value in form_data.items():
    if 'lines-0' in key:
        print(f"  {key}: {value}")

# Submit the form
print("\n=== Step 3: Submitting form ===")
response = client.post('/fa/inventory/stocktaking/surplus/create/', data=form_data, follow=True)
print(f"Status code: {response.status_code}")

# Check if form was valid
if response.status_code == 200:
    # Check for form errors
    if hasattr(response, 'context') and 'form' in response.context:
        form = response.context['form']
        if form.errors:
            print("\n❌ Form has errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        
        if 'lines_formset' in response.context:
            formset = response.context['lines_formset']
            if formset.errors:
                print("\n❌ Formset has errors:")
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        print(f"  Line {i}: {form_errors}")
    
    # Check response content for error messages
    content = response.content.decode('utf-8')
    if 'این مقدار لازم است' in content or 'This field is required' in content:
        print("\n❌ Validation errors found in response")
    elif response.redirect_chain:
        print(f"\n✅ Form submitted successfully! Redirected to: {response.redirect_chain[-1][0]}")
    else:
        print("\n⚠️  Form submitted but no redirect (might have errors)")
        # Print first 1000 chars of response
        print("\nResponse content (first 1000 chars):")
        print(content[:1000])
else:
    print(f"\n❌ Error: Status code {response.status_code}")
    print(response.content[:1000])

print("\n=== Test completed ===")

