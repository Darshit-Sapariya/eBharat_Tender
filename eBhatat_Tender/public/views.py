from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.http import HttpResponse
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from tenders.models import Tenderss
from django.db.models import Q


from django.db.models import Sum
from bids.models import TenderApplication
from accounts.models import UserProfile
from tenders.models import Tenderss
from datetime import date

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

# Mask sensitive ID numbers
def mask_id(value):
    if not value: return ""
    val = str(value)
    mask_count = max(7, len(val) - 4)
    return "*" * mask_count + val[-4:]

# ==============================================================================
# PUBLIC FACING VIEWS
# ==============================================================================

# Main portal landing page
def index(request):
    # Stats
    open_tenders_count = Tenderss.objects.filter(status='open').count()
    
    total_val = Tenderss.objects.aggregate(total=Sum('estimated_value'))['total'] or 0
    total_value_cr = float(total_val) / 10000000
    
    total_applications = TenderApplication.objects.count()
    approved_applications = TenderApplication.objects.filter(status='approved').count()
    success_rate = 0
    if total_applications > 0:
        success_rate = (approved_applications / total_applications) * 100
        
    registered_vendors = UserProfile.objects.filter(role='bidder').count()
    
    # Recent Tenders
    recent_tenders = Tenderss.objects.filter(status='open').order_by('-created_at')[:3]
    
    context = {
        'open_tenders_count': open_tenders_count,
        'total_value_cr': round(total_value_cr, 2),
        'success_rate': round(success_rate, 1),
        'registered_vendors': registered_vendors,
        'recent_tenders': recent_tenders,
    }
    return render(request, 'index.html', context)
# Funding information page
def funding(request):
    return render(request, 'funding.html')
# Explain procurement workflow
def workflow(request):
    return render(request, 'workflow.html')
# Portal policy guidelines
def guidelines(request):
    return render(request, 'guidelines.html')


# =======================
# TENDERS VIEW
# =======================


# Public tender listing page
def tenders(request):

    search_query = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()   # ✅ NEW

    tenders = Tenderss.objects.all()

    # 🔎 Search filter
    if search_query:
        tenders = tenders.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    #  Category filter
    if category and category != "all":
        tenders = tenders.filter(category__iexact=category)

    #  Status filter (NEW)
    if status:
        tenders = tenders.filter(status__iexact=status)

    tenders = tenders.order_by('-created_at')
    
    # Prefetch awarded application for each tender to show company name in list
    for t in tenders:
        app = t.applications.filter(status='awarded').first()
        if app:
            app.masked_gst = mask_id(app.gst_number)
            t.awarded_application = app

    # --- Metrics Calculations ---
    from django.db.models import Sum
    from datetime import date
    from bids.models import TenderApplication
    from accounts.models import UserProfile
    
    # 1. Active / Open Tenders (total)
    open_tenders = Tenderss.objects.filter(status='open').count()
    
    # 2. Total Value (in Crores)
    total_val = Tenderss.objects.aggregate(total=Sum('estimated_value'))['total'] or 0
    total_value_cr = float(total_val) / 10000000
    
    # 3. Success Rate
    total_applications = TenderApplication.objects.count()
    approved_applications = TenderApplication.objects.filter(status='approved').count()
    success_rate = 0
    if total_applications > 0:
        success_rate = (approved_applications / total_applications) * 100
        
    # 4. Closing Today
    today = date.today()
    closing_today = Tenderss.objects.filter(closing_date=today).count()
    
    # 5. Registered Vendors
    registered_vendors = UserProfile.objects.filter(role='bidder').count()

    # 6. Watchlist for current user
    
    context = {
        'tenders': tenders,
        'search_query': search_query,
        'selected_category': category,
        'selected_status': status,
        'open_tenders': open_tenders,
        'total_value_cr': total_value_cr,
        'success_rate': success_rate,
        'closing_today': closing_today,
        'registered_vendors': registered_vendors,
    }

    return render(request, 'tenders.html', context)
# =======================
# TENDER DETAIL VIEW
# =======================
# Public tender detail view
@login_required
def tenderDetails(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    applications = tender.applications.all()

    awarded_bid = applications.filter(status='awarded').first()
    if awarded_bid:
        awarded_bid.masked_gst = mask_id(awarded_bid.gst_number)
    
    # Check if in watchlist/applied
    is_in_watchlist = False
    has_applied = False
    if request.user.is_authenticated:
        try:
            if request.user.userprofile.role == 'bidder':
                from accounts.models import Watchlist
                is_in_watchlist = Watchlist.objects.filter(user=request.user, tender=tender).exists()
                has_applied = TenderApplication.objects.filter(applicant=request.user, tender=tender).exists()
        except:
            pass

    return render(request, "tenderDetails.html", {
        "tender": tender,
        "applications": applications,
        "awarded_bid": awarded_bid,
        "is_in_watchlist": is_in_watchlist,
        "has_applied": has_applied,
    })


# Procurement news board
def noticeboard(request):
    return render(request, 'noticeboard.html')



