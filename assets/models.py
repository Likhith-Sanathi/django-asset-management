"""
Models for Asset Management Application
"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.conf import settings


class Asset(models.Model):
    """
    Main Asset model for tracking various asset types
    """
    CATEGORY_CHOICES = [
        ('mutual_funds', 'Mutual Funds'),
        ('stocks', 'Stocks'),
        ('lands', 'Lands'),
        ('flats', 'Flats'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('medical_insurance', 'Medical Insurance'),
        ('life_insurance', 'Life Insurance'),
        ('gold', 'Gold'),
    ]
    
    # Area unit choices for land/flats
    AREA_UNIT_CHOICES = [
        ('sqft', 'Square Feet'),
        ('sqm', 'Square Meters'),
        ('acres', 'Acres'),
        ('hectares', 'Hectares'),
        ('cents', 'Cents'),
        ('guntha', 'Guntha'),
    ]
    
    # Gold purity choices
    GOLD_PURITY_CHOICES = [
        ('24k', '24 Karat (99.9%)'),
        ('22k', '22 Karat (91.6%)'),
        ('18k', '18 Karat (75%)'),
        ('14k', '14 Karat (58.3%)'),
    ]

    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assets'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES
    )
    value = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Current value of the asset"
    )
    description = models.TextField(blank=True, null=True)
    
    # Dates
    start_date = models.DateField(
        help_text="Purchase/Start date"
    )
    end_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Maturity/End date (if applicable)"
    )
    
    # Land/Flat specific fields
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Latitude for land assets"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Longitude for land assets"
    )
    area = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Area measurement for land/flat"
    )
    area_unit = models.CharField(
        max_length=20,
        choices=AREA_UNIT_CHOICES,
        blank=True,
        null=True,
        help_text="Unit of area measurement"
    )
    
    # Gold specific fields
    weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        help_text="Weight in grams for gold"
    )
    gold_purity = models.CharField(
        max_length=10,
        choices=GOLD_PURITY_CHOICES,
        blank=True,
        null=True,
        help_text="Gold purity/karat"
    )
    
    # Stocks/Mutual Funds specific fields
    units = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Number of units/shares"
    )
    purchase_price_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Purchase price per unit/share"
    )
    current_nav = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Current NAV/price per unit"
    )
    folio_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Folio number for mutual funds"
    )
    
    # Insurance specific fields
    sum_assured = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Sum assured for insurance"
    )
    premium_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Premium amount"
    )
    premium_frequency = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('half_yearly', 'Half Yearly'),
            ('yearly', 'Yearly'),
            ('one_time', 'One Time'),
        ],
        blank=True,
        null=True,
        help_text="Premium payment frequency"
    )
    nominee = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nominee name"
    )
    
    # Fixed Deposit specific fields
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Interest rate (%) for FD"
    )
    maturity_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Maturity amount for FD"
    )
    
    # Common additional fields
    policy_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Policy/Account number for insurance, FD, etc."
    )
    institution = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Bank, Insurance company, Broker, etc."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def is_active(self):
        """Check if asset is currently active (not past end_date)"""
        from django.utils import timezone
        if self.end_date:
            return self.end_date >= timezone.now().date()
        return True


def asset_document_path(instance, filename):
    """Generate upload path for asset documents"""
    return f'assets/{instance.asset.owner.id}/{instance.asset.id}/{filename}'


class AssetDocument(models.Model):
    """
    Model for storing documents directly in PostgreSQL database
    """
    ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'xls', 'xlsx']
    
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    # Store the actual file content in the database
    file_data = models.BinaryField(
        blank=True,
        null=True,
        help_text="Binary file content stored in database"
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original filename"
    )
    file_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="MIME type of the file"
    )
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="File size in bytes"
    )
    name = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Document name/description"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Asset Document'
        verbose_name_plural = 'Asset Documents'

    def __str__(self):
        return f"{self.name or self.file_name} - {self.asset.name}"

    @property
    def filename(self):
        return self.file_name

    @property
    def file_extension(self):
        return os.path.splitext(self.file_name)[1].lower() if self.file_name else ''

    def save(self, *args, **kwargs):
        # Auto-populate name from filename if not provided
        if not self.name and self.file_name:
            self.name = os.path.splitext(self.file_name)[0]
        super().save(*args, **kwargs)
    
    @classmethod
    def create_from_file(cls, asset, uploaded_file):
        """Create an AssetDocument from an uploaded file"""
        import mimetypes
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Read file content
        file_content = uploaded_file.read()
        
        return cls.objects.create(
            asset=asset,
            file_data=file_content,
            file_name=uploaded_file.name,
            file_type=mime_type,
            file_size=len(file_content)
        )


class ActivityLog(models.Model):
    """
    Activity log for auditing asset changes
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('upload', 'Document Uploaded'),
        ('download', 'Document Downloaded'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    asset_name = models.CharField(
        max_length=255,
        help_text="Asset name at time of action"
    )
    asset_category = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.asset_name}"

    @classmethod
    def log_action(cls, user, action, asset, details=None, ip_address=None):
        """Helper method to create activity log entries"""
        return cls.objects.create(
            user=user,
            action=action,
            asset_name=asset.name if hasattr(asset, 'name') else str(asset),
            asset_category=asset.category if hasattr(asset, 'category') else '',
            details=details,
            ip_address=ip_address
        )
