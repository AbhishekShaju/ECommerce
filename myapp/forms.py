# forms.py
from django import forms

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your email")

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile  # If you have a custom profile model

# Create a form for user profile edit
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # Make sure this model has address, phone number, pin code, and profile photo fields
        fields = ['address', 'phone_number', 'pin_code', 'profile_photo']
    
    # Adding some widgets for styling
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your address'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))
    pin_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your pin code'}))
    profile_photo = forms.ImageField(required=False)

