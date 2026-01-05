"""
Forms for Asset Management Application
"""

import os
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Asset, AssetDocument


class CustomUserCreationForm(UserCreationForm):
    """Extended signup form with email"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm your password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styling"""
    remember_me = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })


class AssetForm(forms.ModelForm):
    """Form for creating and editing assets"""
    
    class Meta:
        model = Asset
        fields = [
            'name', 'category', 'value', 'description',
            'start_date', 'end_date', 
            # Land/Flat fields
            'latitude', 'longitude', 'area', 'area_unit',
            # Gold fields
            'weight_grams', 'gold_purity',
            # Stocks/MF fields
            'units', 'purchase_price_per_unit', 'current_nav', 'folio_number',
            # Insurance fields
            'sum_assured', 'premium_amount', 'premium_frequency', 'nominee',
            # FD fields
            'interest_rate', 'maturity_amount',
            # Common fields
            'policy_number', 'institution'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Asset name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            # Land/Flat fields
            'latitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Latitude',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Longitude',
                'step': 'any'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Area',
                'step': '0.01'
            }),
            'area_unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            # Gold fields
            'weight_grams': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Weight in grams',
                'step': '0.001'
            }),
            'gold_purity': forms.Select(attrs={
                'class': 'form-select'
            }),
            # Stocks/MF fields
            'units': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Number of units',
                'step': '0.0001'
            }),
            'purchase_price_per_unit': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Purchase price per unit',
                'step': '0.0001'
            }),
            'current_nav': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Current NAV/price',
                'step': '0.0001'
            }),
            'folio_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Folio number'
            }),
            # Insurance fields
            'sum_assured': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Sum assured',
                'step': '0.01'
            }),
            'premium_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Premium amount',
                'step': '0.01'
            }),
            'premium_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nominee': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nominee name'
            }),
            # FD fields
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Interest rate %',
                'step': '0.01'
            }),
            'maturity_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Maturity amount',
                'step': '0.01'
            }),
            # Common fields
            'policy_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Policy/Account number'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Bank/Institution name'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)
        
        # Pre-select category if provided
        if self.category:
            self.fields['category'].initial = self.category
        
        # Get the current category (from instance or from provided category)
        current_category = self.category or (self.instance.category if self.instance and self.instance.pk else None)
        
        # Hide/show fields based on category
        self._setup_category_fields(current_category)

    def _setup_category_fields(self, category):
        """Setup field visibility and requirements based on category"""
        # Define which fields are relevant for each category
        category_fields = {
            'lands': ['latitude', 'longitude', 'area', 'area_unit'],
            'flats': ['area', 'area_unit'],
            'gold': ['weight_grams', 'gold_purity'],
            'stocks': ['units', 'purchase_price_per_unit', 'current_nav', 'institution'],
            'mutual_funds': ['units', 'purchase_price_per_unit', 'current_nav', 'folio_number', 'institution'],
            'fixed_deposit': ['interest_rate', 'maturity_amount', 'policy_number', 'institution'],
            'medical_insurance': ['sum_assured', 'premium_amount', 'premium_frequency', 'nominee', 'policy_number', 'institution'],
            'life_insurance': ['sum_assured', 'premium_amount', 'premium_frequency', 'nominee', 'policy_number', 'institution'],
        }
        
        # All category-specific fields
        all_special_fields = [
            'latitude', 'longitude', 'area', 'area_unit',
            'weight_grams', 'gold_purity',
            'units', 'purchase_price_per_unit', 'current_nav', 'folio_number',
            'sum_assured', 'premium_amount', 'premium_frequency', 'nominee',
            'interest_rate', 'maturity_amount'
        ]
        
        # Get relevant fields for current category
        relevant_fields = category_fields.get(category, [])
        
        # Mark fields as not required if not relevant
        for field_name in all_special_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
                # Add data attribute for JS to show/hide
                self.fields[field_name].widget.attrs['data-category-field'] = field_name
        
        # Make coordinates required for lands
        if category == 'lands':
            self.fields['latitude'].required = True
            self.fields['longitude'].required = True

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate dates
        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")
        
        # Validate coordinates for land assets
        if category == 'lands':
            latitude = cleaned_data.get('latitude')
            longitude = cleaned_data.get('longitude')
            if not latitude or not longitude:
                raise ValidationError("Latitude and Longitude are required for land assets.")
        
        return cleaned_data


class MultiFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file uploads"""
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    """Custom field for multiple file uploads"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.xls,.xlsx'
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)] if data else []
        return result


class AssetDocumentForm(forms.Form):
    """Form for uploading multiple documents"""
    files = MultiFileField(
        required=False,
        label="Upload Documents"
    )

    def clean_files(self):
        files = self.cleaned_data.get('files', [])
        
        for f in files:
            if f:
                # Validate file extension
                ext = os.path.splitext(f.name)[1].lower()
                if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
                    raise ValidationError(
                        f"File type '{ext}' is not allowed. Allowed types: {', '.join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}"
                    )
                
                # Validate file size
                if f.size > settings.MAX_DOCUMENT_SIZE:
                    max_size_mb = settings.MAX_DOCUMENT_SIZE / (1024 * 1024)
                    raise ValidationError(
                        f"File '{f.name}' exceeds maximum size of {max_size_mb}MB."
                    )
        
        return files


class AssetWithDocumentsForm(forms.Form):
    """Combined form for asset and documents"""
    # This is used for validation in views
    pass


class AssetFilterForm(forms.Form):
    """Form for filtering assets"""
    CATEGORY_CHOICES = [('', 'All Categories')] + list(Asset.CATEGORY_CHOICES)
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search assets...'
        })
    )
    min_value = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Min value'
        })
    )
    max_value = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Max value'
        })
    )
