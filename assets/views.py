"""
Views for Asset Management Application
All views protected with LoginRequiredMixin for authenticated access only
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from decimal import Decimal

from .models import Asset, AssetDocument, ActivityLog
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    AssetForm, AssetDocumentForm, AssetFilterForm
)


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================
# AUTHENTICATION VIEWS
# ============================================

class CustomLoginView(LoginView):
    """Custom login view with persistent session support"""
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', True)
        
        if not remember_me:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        # else: uses SESSION_COOKIE_AGE from settings (30 days)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'login'


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


# ============================================
# DASHBOARD VIEW
# ============================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard with asset overview and charts"""
    template_name = 'dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's assets
        assets = Asset.objects.filter(owner=user)
        
        # Total value
        total_value = assets.aggregate(
            total=Coalesce(Sum('value'), Decimal('0'))
        )['total']
        
        # Breakdown by category
        category_breakdown = assets.values('category').annotate(
            total=Sum('value'),
            count=Count('id')
        ).order_by('-total')
        
        # Format for charts
        chart_data = {
            'labels': [],
            'values': [],
            'colors': []
        }
        
        # Color palette for categories
        colors = {
            'mutual_funds': '#3B82F6',
            'stocks': '#10B981',
            'lands': '#8B5CF6',
            'flats': '#F59E0B',
            'fixed_deposit': '#EF4444',
            'medical_insurance': '#EC4899',
            'life_insurance': '#06B6D4',
            'gold': '#F97316',
        }
        
        category_labels = dict(Asset.CATEGORY_CHOICES)
        
        for item in category_breakdown:
            chart_data['labels'].append(category_labels.get(item['category'], item['category']))
            chart_data['values'].append(float(item['total']))
            chart_data['colors'].append(colors.get(item['category'], '#6B7280'))
        
        # Recent assets
        recent_assets = assets[:5]
        
        # Recent activity
        recent_activity = ActivityLog.objects.filter(user=user)[:10]
        
        # Asset counts by category
        category_counts = {cat[0]: 0 for cat in Asset.CATEGORY_CHOICES}
        for item in category_breakdown:
            category_counts[item['category']] = item['count']
        
        context.update({
            'total_value': total_value,
            'total_assets': assets.count(),
            'category_breakdown': category_breakdown,
            'chart_data': chart_data,
            'recent_assets': recent_assets,
            'recent_activity': recent_activity,
            'category_choices': Asset.CATEGORY_CHOICES,
            'category_counts': category_counts,
            'category_labels': category_labels,
        })
        
        return context


# ============================================
# ASSET CRUD VIEWS
# ============================================

class AssetListView(LoginRequiredMixin, ListView):
    """List all user's assets with filtering"""
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 12
    login_url = 'login'
    
    def get_queryset(self):
        queryset = Asset.objects.filter(owner=self.request.user)
        
        # Apply filters
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        min_value = self.request.GET.get('min_value')
        max_value = self.request.GET.get('max_value')
        
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(name__icontains=search)
        if min_value:
            queryset = queryset.filter(value__gte=min_value)
        if max_value:
            queryset = queryset.filter(value__lte=max_value)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AssetFilterForm(self.request.GET)
        context['current_category'] = self.request.GET.get('category', '')
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    """View single asset details"""
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'
    login_url = 'login'
    
    def get_queryset(self):
        # Only allow viewing own assets
        return Asset.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        
        # Log view action
        ActivityLog.log_action(
            user=self.request.user,
            action='view',
            asset=self.object,
            ip_address=get_client_ip(self.request)
        )
        
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    """Create new asset"""
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('asset_list')
    login_url = 'login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.request.GET.get('category')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_form'] = AssetDocumentForm()
        context['is_edit'] = False
        category = self.request.GET.get('category')
        if category:
            context['category_label'] = dict(Asset.CATEGORY_CHOICES).get(category, '')
        return context
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Handle file uploads - store in database as binary
        files = self.request.FILES.getlist('files')
        for f in files:
            AssetDocument.create_from_file(asset=self.object, uploaded_file=f)
        
        # Log creation
        ActivityLog.log_action(
            user=self.request.user,
            action='create',
            asset=self.object,
            details=f"Created asset with value {self.object.value}",
            ip_address=get_client_ip(self.request)
        )
        
        messages.success(self.request, f'Asset "{self.object.name}" created successfully!')
        return response


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing asset"""
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    login_url = 'login'
    
    def get_queryset(self):
        # Only allow editing own assets
        return Asset.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_form'] = AssetDocumentForm()
        context['documents'] = self.object.documents.all()
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle file uploads - store in database as binary
        files = self.request.FILES.getlist('files')
        for f in files:
            AssetDocument.create_from_file(asset=self.object, uploaded_file=f)
            ActivityLog.log_action(
                user=self.request.user,
                action='upload',
                asset=self.object,
                details=f"Uploaded document: {f.name}",
                ip_address=get_client_ip(self.request)
            )
        
        # Log update
        ActivityLog.log_action(
            user=self.request.user,
            action='update',
            asset=self.object,
            details=f"Updated asset",
            ip_address=get_client_ip(self.request)
        )
        
        messages.success(self.request, f'Asset "{self.object.name}" updated successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('asset_detail', kwargs={'pk': self.object.pk})


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    """Delete asset"""
    model = Asset
    template_name = 'assets/asset_confirm_delete.html'
    success_url = reverse_lazy('asset_list')
    login_url = 'login'
    
    def get_queryset(self):
        # Only allow deleting own assets
        return Asset.objects.filter(owner=self.request.user)
    
    def form_valid(self, form):
        asset_name = self.object.name
        
        # Log deletion before deleting
        ActivityLog.log_action(
            user=self.request.user,
            action='delete',
            asset=self.object,
            details=f"Deleted asset with value {self.object.value}",
            ip_address=get_client_ip(self.request)
        )
        
        messages.success(self.request, f'Asset "{asset_name}" deleted successfully!')
        return super().form_valid(form)


# ============================================
# DOCUMENT VIEWS
# ============================================

@login_required
def download_document(request, pk):
    """Download a document from the database"""
    document = get_object_or_404(AssetDocument, pk=pk)
    
    # Ownership check
    if document.asset.owner != request.user:
        return HttpResponseForbidden("You don't have permission to download this document.")
    
    # Create response with binary data
    response = HttpResponse(document.file_data, content_type=document.file_type)
    response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
    response['Content-Length'] = document.file_size
    
    return response


@login_required
def delete_document(request, pk):
    """Delete a document from an asset"""
    document = get_object_or_404(AssetDocument, pk=pk)
    
    # Ownership check
    if document.asset.owner != request.user:
        return HttpResponseForbidden("You don't have permission to delete this document.")
    
    asset = document.asset
    doc_name = document.file_name
    document.delete()
    
    ActivityLog.log_action(
        user=request.user,
        action='delete',
        asset=asset,
        details=f"Deleted document: {doc_name}",
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'Document "{doc_name}" deleted successfully!')
    return redirect('asset_detail', pk=asset.pk)


# ============================================
# ACTIVITY LOG VIEW
# ============================================

class ActivityLogView(LoginRequiredMixin, ListView):
    """View activity logs"""
    model = ActivityLog
    template_name = 'activity_log.html'
    context_object_name = 'logs'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)


# ============================================
# API VIEWS (for charts)
# ============================================

@login_required
def chart_data_api(request):
    """API endpoint for chart data"""
    assets = Asset.objects.filter(owner=request.user)
    
    category_breakdown = assets.values('category').annotate(
        total=Sum('value')
    ).order_by('-total')
    
    category_labels = dict(Asset.CATEGORY_CHOICES)
    colors = {
        'mutual_funds': '#3B82F6',
        'stocks': '#10B981',
        'lands': '#8B5CF6',
        'flats': '#F59E0B',
        'fixed_deposit': '#EF4444',
        'medical_insurance': '#EC4899',
        'life_insurance': '#06B6D4',
        'gold': '#F97316',
    }
    
    data = {
        'labels': [category_labels.get(item['category'], item['category']) for item in category_breakdown],
        'values': [float(item['total']) for item in category_breakdown],
        'colors': [colors.get(item['category'], '#6B7280') for item in category_breakdown],
    }
    
    return JsonResponse(data)
