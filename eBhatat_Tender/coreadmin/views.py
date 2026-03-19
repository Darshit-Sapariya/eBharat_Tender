from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from tenders.models import Tenderss
from bids.models import TenderApplication
from accounts.models import UserProfile, AdminRequest, Category, Department
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def coreadmin_dashboard(request):
    return render(request, 'coreadmin_base.html')

def coreadmin_deshbord(request):
    # --- STATISTICS ---
    total_tenders = Tenderss.objects.count()
    active_tenders = Tenderss.objects.filter(status='open').count()
    total_vendors = UserProfile.objects.filter(role='bidder').count()
    
    total_awarded_val = Tenderss.objects.filter(status='awarded').aggregate(total=Sum('estimated_value'))['total'] or 0
    
    pending_user_approvals = UserProfile.objects.filter(status='pending').count()
    pending_app_approvals = TenderApplication.objects.filter(status='pending').count()
    total_pending = pending_user_approvals + pending_app_approvals
    
    # Bids this month
    now = timezone.now()
    bids_this_month = TenderApplication.objects.filter(applied_at__month=now.month, applied_at__year=now.year).count()
    contracts_executed = Tenderss.objects.filter(status='awarded').count() 
    
    emd_escrow = Tenderss.objects.filter(status='open').aggregate(total=Sum('emd_amount'))['total'] or 0
    active_holds = Tenderss.objects.filter(status='open').count() 
    
    # --- CHART DATA (Tenders by Category) ---
    categories_data = Tenderss.objects.values('category').annotate(count=Count('id')).order_by('-count')
    cat_labels = [item['category'] for item in categories_data]
    cat_counts = [item['count'] for item in categories_data]
    category_stats = list(zip(cat_labels, cat_counts))
    
    # --- CHART DATA (Activity Over Months) ---
    months = []
    tender_activity = []
    bid_activity = []
    for i in range(5, -1, -1):
        target_date = now - timedelta(days=i*30)
        month_name = target_date.strftime('%b')
        months.append(month_name)
        t_count = Tenderss.objects.filter(created_at__month=target_date.month, created_at__year=target_date.year).count()
        b_count = TenderApplication.objects.filter(applied_at__month=target_date.month, applied_at__year=target_date.year).count()
        tender_activity.append(t_count)
        bid_activity.append(b_count)

    # --- RECENT TENDERS ---
    recent_tenders_list = Tenderss.objects.order_by('-created_at')[:5]
    
    # --- ALERTS & PENDING ---
    pending_users = UserProfile.objects.filter(status='pending').order_by('-created_at')[:5]
    pending_apps = TenderApplication.objects.filter(status='pending').order_by('-applied_at')[:5]
    
    context = {
        'total_tenders': total_tenders,
        'active_tenders': active_tenders,
        'total_vendors': total_vendors,
        'total_awarded_val': total_awarded_val,
        'total_pending': total_pending,
        'pending_user_approvals': pending_user_approvals,
        'pending_app_approvals': pending_app_approvals,
        'bids_this_month': bids_this_month,
        'contracts_executed': contracts_executed,
        'emd_escrow': emd_escrow,
        'active_holds': active_holds,
        
        'cat_labels': cat_labels,
        'cat_counts': cat_counts,
        'category_stats': category_stats,
        'months': months,
        'tender_activity': tender_activity,
        'bid_activity': bid_activity,
        
        'recent_tenders': recent_tenders_list,
        'pending_users': pending_users,
        'pending_apps': pending_apps,
    }
    
    return render(request, 'deshbord.html', context)

# --- APPROVAL SYSTEM VIEWS ---

def user_approvals(request):
    pending_users = UserProfile.objects.filter(status='pending').order_by('-created_at')
    approved_users = UserProfile.objects.filter(status='approved').order_by('-created_at')[:20]
    return render(request, 'approvals.html', {
        'pending_users': pending_users,
        'approved_users': approved_users,
        'type': 'users'
    })

def application_approvals(request):
    pending_apps = TenderApplication.objects.filter(status='pending').order_by('-applied_at')
    approved_apps = TenderApplication.objects.filter(status='approved').order_by('-applied_at')[:20]
    return render(request, 'approvals.html', {
        'pending_apps': pending_apps,
        'approved_apps': approved_apps,
        'type': 'applications'
    })

def approve_user(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        role = request.POST.get('role')
        remark = request.POST.get('remark', '')
        
        profile.status = 'approved'
        if role:
            profile.role = role
        profile.admin_remark = remark
        profile.save()
        
        # Also create a notification
        from accounts.models import Notification
        Notification.objects.create(
            user=profile.user,
            message=f"Your account has been approved as {profile.get_role_display()}."
        )
        
        messages.success(request, f"User {profile.user.username} approved successfully.")
    return redirect('coreadmin:user_approvals')

def reject_user(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        remark = request.POST.get('remark', '')
        
        profile.status = 'rejected'
        profile.admin_remark = remark
        profile.save()
        
        messages.warning(request, f"User {profile.user.username} rejected.")
    return redirect('coreadmin:user_approvals')

def approve_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'approved'
        application.remark = remark
        application.save()
        
        messages.success(request, f"Application for {application.tender.title} approved.")
    return redirect('coreadmin:application_approvals')

def reject_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'rejected'
        application.remark = remark
        application.save()
        
        messages.warning(request, f"Application for {application.tender.title} rejected.")
    return redirect('coreadmin:application_approvals')

# --- USER LIST MANAGEMENT ---

def user_list(request):
    role = request.GET.get('role', 'all')
    if role == 'vendor':
        profiles = UserProfile.objects.filter(role='bidder')
    elif role == 'creator':
        profiles = UserProfile.objects.filter(role='creator')
    else:
        profiles = UserProfile.objects.all()
    
    return render(request, 'user_list.html', {
        'profiles': profiles,
        'current_role': role
    })

# --- TENDER LIST MANAGEMENT ---

def tender_list(request):
    all_tenders = Tenderss.objects.all().order_by('-created_at')
    
    # We want to show which tender who public and how many bid who awards
    tenders_data = []
    for tender in all_tenders:
        bid_count = tender.applications.count()
        awardee = tender.applications.filter(status='awarded').first()
        tenders_data.append({
            'obj': tender,
            'bid_count': bid_count,
            'awardee': awardee.company_name if awardee else "None",
            'publisher': tender.created_by.username # WHO publish
        })
    
    return render(request, 'tender_list.html', {
        'tenders': tenders_data
    })

# --- ADMIN REQUESTS (Department/Category Approval) ---

def admin_request_approvals(request):
    pending_requests = AdminRequest.objects.filter(status='pending').order_by('-created_at')
    approved_requests = AdminRequest.objects.filter(status='approved').order_by('-created_at')[:10]
    return render(request, 'approvals.html', {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'type': 'admin_requests'
    })

def approve_admin_request(request, request_id):
    if request.method == 'POST':
        admin_req = get_object_or_404(AdminRequest, id=request_id)
        remark = request.POST.get('remark', '')
        
        # Actually create the Department/Category if they don't exist
        Department.objects.get_or_create(name=admin_req.department_name)
        Category.objects.get_or_create(name=admin_req.category_name)
        
        admin_req.status = 'approved'
        admin_req.admin_remark = remark
        admin_req.save()
        
        from accounts.models import Notification
        Notification.objects.create(
            user=admin_req.user,
            message=f"Your request for {admin_req.department_name} department has been approved."
        )
        
        messages.success(request, f"Request for {admin_req.department_name} approved.")
    return redirect('coreadmin:admin_request_approvals')

def reject_admin_request(request, request_id):
    if request.method == 'POST':
        admin_req = get_object_or_404(AdminRequest, id=request_id)
        remark = request.POST.get('remark', '')
        
        admin_req.status = 'rejected'
        admin_req.admin_remark = remark
        admin_req.save()
        
        messages.warning(request, f"Request for {admin_req.department_name} rejected.")
    return redirect('coreadmin:admin_request_approvals')

def analytics(request):
    now = timezone.now()
    months = []
    tender_trend = []
    bid_trend = []
    reg_trend = []
    
    # Last 6 months trend
    for i in range(5, -1, -1):
        target_date = now - timedelta(days=i*30)
        months.append(target_date.strftime('%b %Y'))
        
        t_count = Tenderss.objects.filter(created_at__month=target_date.month, created_at__year=target_date.year).count()
        b_count = TenderApplication.objects.filter(applied_at__month=target_date.month, applied_at__year=target_date.year).count()
        r_count = UserProfile.objects.filter(created_at__month=target_date.month, created_at__year=target_date.year).count()
        
        tender_trend.append(t_count)
        bid_trend.append(b_count)
        reg_trend.append(r_count)

    # Category Distribution
    cat_data = Tenderss.objects.values('category').annotate(count=Count('id')).order_by('-count')
    cat_labels = [c['category'] or "Uncategorized" for c in cat_data]
    cat_counts = [c['count'] for c in cat_data]

    # Status Distribution
    status_data = Tenderss.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'].upper() for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # TOP Publishers (Creator Roles)
    top_publishers = Tenderss.objects.values('created_by__username').annotate(total=Count('id')).order_by('-total')[:5]
    pub_labels = [p['created_by__username'] for p in top_publishers]
    pub_counts = [p['total'] for p in top_publishers]

    context = {
        'months': months,
        'tender_trend': tender_trend,
        'bid_trend': bid_trend,
        'reg_trend': reg_trend,
        'cat_labels': cat_labels,
        'cat_counts': cat_counts,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'pub_labels': pub_labels,
        'pub_counts': pub_counts,
    }
    return render(request, 'analytics.html', context)