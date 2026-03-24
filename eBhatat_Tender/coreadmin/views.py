from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from tenders.models import Tenderss
from bids.models import TenderApplication
from accounts.models import UserProfile, AdminRequest, Category, Department, Notification
from funding.models import Funding, FundingApplication
from .models import ActionLog, Notice
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from accounts.utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.
@staff_member_required
def coreadmin_dashboard(request):
    return render(request, 'coreadmin_base.html')

def calculate_delta(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100)

@staff_member_required
def coreadmin_deshbord(request):
    # --- STATISTICS ---
    now = timezone.now()
    prev_30_days = now - timedelta(days=30)
    
    # Total Tenders
    total_tenders = Tenderss.objects.count()
    prev_total_tenders = Tenderss.objects.filter(created_at__lt=prev_30_days).count()
    tenders_delta = calculate_delta(total_tenders, prev_total_tenders)
    active_tenders = Tenderss.objects.filter(status='open').count()
    
    # Total Disbursed (Awarded Bid Amounts)
    total_awarded_val = TenderApplication.objects.filter(status='awarded').aggregate(total=Sum('bid_amount'))['total'] or 0
    prev_awarded_val = TenderApplication.objects.filter(status='awarded', applied_at__lt=prev_30_days).aggregate(total=Sum('bid_amount'))['total'] or 0
    disbursed_delta = calculate_delta(float(total_awarded_val), float(prev_awarded_val))
    
    # Pending Reviews
    pending_user_approvals = UserProfile.objects.filter(status='pending').count()
    pending_app_approvals = TenderApplication.objects.filter(status='pending').count()
    total_pending = pending_user_approvals + pending_app_approvals
    
    prev_pending_users = UserProfile.objects.filter(status='pending', created_at__lt=prev_30_days).count()
    prev_pending_apps = TenderApplication.objects.filter(status='pending', applied_at__lt=prev_30_days).count()
    prev_total_pending = prev_pending_users + prev_pending_apps
    pending_delta = calculate_delta(total_pending, prev_total_pending)
    
    # Registered Vendors
    total_vendors = UserProfile.objects.filter(role='bidder').count()
    prev_total_vendors = UserProfile.objects.filter(role='bidder', created_at__lt=prev_30_days).count()
    vendors_delta = calculate_delta(total_vendors, prev_total_vendors)
    
    # Contracts Executed
    contracts_executed = Tenderss.objects.filter(status='awarded').count()
    prev_contracts_executed = Tenderss.objects.filter(status='awarded', created_at__lt=prev_30_days).count()
    contracts_delta = calculate_delta(contracts_executed, prev_contracts_executed)
    
    # Bids this month
    bids_this_month = TenderApplication.objects.filter(applied_at__month=now.month, applied_at__year=now.year).count()
    
    # EMD Escrow (Paid EMD for open tenders)
    emd_escrow = TenderApplication.objects.filter(tender__status='open', payment_status='paid').aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    prev_emd_escrow = TenderApplication.objects.filter(tender__status='open', payment_status='paid', applied_at__lt=prev_30_days).aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    emd_delta = calculate_delta(float(emd_escrow), float(prev_emd_escrow))
    active_holds = Tenderss.objects.filter(status='open').count() 
    
    # Approval Rate
    total_apps = TenderApplication.objects.count()
    approved_apps = TenderApplication.objects.filter(status='approved').count()
    approval_rate = round((approved_apps / total_apps * 100)) if total_apps > 0 else 0
    
    prev_total_apps = TenderApplication.objects.filter(applied_at__lt=prev_30_days).count()
    prev_approved_apps = TenderApplication.objects.filter(status='approved', applied_at__lt=prev_30_days).count()
    prev_approval_rate = round((prev_approved_apps / prev_total_apps * 100)) if prev_total_apps > 0 else 0
    approval_delta = calculate_delta(approval_rate, prev_approval_rate)
    
    # Audit Logs
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    
    audit_logs_today = ActionLog.objects.filter(timestamp__date=today).count()
    prev_audit_logs_today = ActionLog.objects.filter(timestamp__date=yesterday).count()
    audit_delta = calculate_delta(audit_logs_today, prev_audit_logs_today)
    
    recent_activity = ActionLog.objects.order_by('-timestamp')[:5]
    
    # Sidebar Badges
    pending_funding_count = FundingApplication.objects.filter(status='pending').count()
    pending_admin_req_count = AdminRequest.objects.filter(status='pending').count()

    # --- CHART DATA (Tenders by Category) ---
    categories_data = Tenderss.objects.values('category').annotate(count=Count('id')).order_by('-count')
    cat_labels = [item['category'] for item in categories_data]
    cat_counts = [item['count'] for item in categories_data]
    category_stats = list(zip(cat_labels, cat_counts))
    
    # --- COMBINED PENDING LIST ---
    combined_pending = []
    for u in UserProfile.objects.filter(status='pending').order_by('-created_at')[:5]:
        combined_pending.append({'type': 'user', 'obj': u, 'date': u.created_at})
    for a in TenderApplication.objects.filter(status='pending').order_by('-applied_at')[:5]:
        combined_pending.append({'type': 'bid', 'obj': a, 'date': a.applied_at})
    for f in FundingApplication.objects.filter(status='pending').order_by('-applied_at')[:5]:
        combined_pending.append({'type': 'funding', 'obj': f, 'date': f.applied_at})
    for r in AdminRequest.objects.filter(status='pending').order_by('-created_at')[:5]:
        combined_pending.append({'type': 'admin_req', 'obj': r, 'date': r.created_at})
    
    combined_pending.sort(key=lambda x: x['date'], reverse=True)

    # --- RECENT TENDERS ---
    recent_tenders_list = Tenderss.objects.order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Dashboard',
        'total_tenders': total_tenders,
        'tenders_delta': tenders_delta,
        'tenders_delta_abs': abs(tenders_delta),
        'active_tenders': active_tenders,
        'total_vendors': total_vendors,
        'vendors_delta': vendors_delta,
        'vendors_delta_abs': abs(vendors_delta),
        'total_awarded_val': total_awarded_val,
        'disbursed_delta': disbursed_delta,
        'disbursed_delta_abs': abs(disbursed_delta),
        'total_pending': total_pending,
        'pending_delta': pending_delta,
        'pending_delta_abs': abs(pending_delta),
        'pending_user_approvals': pending_user_approvals,
        'pending_app_approvals': pending_app_approvals,
        'pending_funding_count': pending_funding_count,
        'pending_admin_req_count': pending_admin_req_count,
        'bids_this_month': bids_this_month,
        'contracts_executed': contracts_executed,
        'contracts_delta': contracts_delta,
        'contracts_delta_abs': abs(contracts_delta),
        'emd_escrow': emd_escrow,
        'emd_delta': emd_delta,
        'emd_delta_abs': abs(emd_delta),
        'active_holds': active_holds,
        'approval_rate': approval_rate,
        'approval_delta': approval_delta,
        'approval_delta_abs': abs(approval_delta),
        'audit_logs_today': audit_logs_today,
        'audit_delta': audit_delta,
        'audit_delta_abs': abs(audit_delta),
        'recent_activity': recent_activity,
        'combined_pending': combined_pending,
        'category_stats': category_stats,
        'recent_tenders': recent_tenders_list,
    }
    
    return render(request, 'deshbord.html', context)

# --- APPROVAL SYSTEM VIEWS ---

@staff_member_required
def user_approvals(request):
    pending_users = UserProfile.objects.filter(status='pending').order_by('-created_at')
    approved_users = UserProfile.objects.filter(status='approved').order_by('-created_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'User Approvals',
        'pending_users': pending_users,
        'approved_users': approved_users,
        'type': 'users'
    })

@staff_member_required
def application_approvals(request):
    pending_apps = TenderApplication.objects.filter(status='pending').order_by('-applied_at')
    approved_apps = TenderApplication.objects.filter(status='approved').order_by('-applied_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'Tender Approvals',
        'pending_apps': pending_apps,
        'approved_apps': approved_apps,
        'type': 'applications'
    })

@staff_member_required
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
        Notification.objects.create(
            user=profile.user,
            message=f"Your account has been approved as {profile.get_role_display()}."
        )
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_APPROVAL",
            target_user=profile.user,
            description=f"Approved user {profile.user.username} with role {profile.get_role_display() or 'None'}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"User {profile.user.username} approved successfully.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Account Approved",
                template_name="status_update_notification.html",
                context={
                    "user_name": profile.user.first_name or profile.user.username,
                    "activity_name": "Account Registration",
                    "item_name": f"Verification as {profile.get_role_display()}",
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[profile.user.email]
            )
        except Exception as e:
            print(f"User Approval Email failed: {e}")
    return redirect('coreadmin:user_approvals')

@staff_member_required
def reject_user(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        remark = request.POST.get('remark', '')
        
        profile.status = 'rejected'
        profile.admin_remark = remark
        profile.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_REJECTION",
            target_user=profile.user,
            description=f"Rejected user {profile.user.username}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"User {profile.user.username} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Account Verification Status Update",
                template_name="status_update_notification.html",
                context={
                    "user_name": profile.user.first_name or profile.user.username,
                    "activity_name": "Account Registration",
                    "item_name": "Profile Verification",
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[profile.user.email]
            )
        except Exception as e:
            print(f"User Rejection Email failed: {e}")
    return redirect('coreadmin:user_approvals')

@staff_member_required
def approve_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'approved'
        application.remark = remark
        application.save()
        
        messages.success(request, f"Application for {application.tender.title} approved.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Bid Approved - {application.tender.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": application.user.first_name or application.user.username,
                    "activity_name": "Tender Bid Application",
                    "item_name": application.tender.title,
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[application.user.email]
            )
        except Exception as e:
            print(f"Bid Approval Email failed: {e}")
    return redirect('coreadmin:application_approvals')

@staff_member_required
def reject_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'rejected'
        application.remark = remark
        
        # PROMPT: reject bit = return payment
        if application.payment_status == 'paid':
            application.payment_status = 'refunded'
            messages.info(request, f"Payment for {application.company_name} has been marked for refund.")
            
        application.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="BID_REJECTION",
            description=f"Rejected bid from {application.company_name} for tender {application.tender.tender_id}. Payment Status: {application.payment_status}"
        )
        
        messages.warning(request, f"Application for {application.tender.title} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Bid Application Status Update - {application.tender.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": application.user.first_name or application.user.username,
                    "activity_name": "Tender Bid Application",
                    "item_name": application.tender.title,
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[application.user.email]
            )
        except Exception as e:
            print(f"Bid Rejection Email failed: {e}")
    return redirect('coreadmin:application_approvals')

@staff_member_required
def funding_approvals(request):
    pending_apps = FundingApplication.objects.filter(status='pending').order_by('-applied_at')
    approved_apps = FundingApplication.objects.filter(status='approved').order_by('-applied_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'Funding Approvals',
        'pending_funding': pending_apps,
        'approved_funding': approved_apps,
        'type': 'funding'
    })

@staff_member_required
def approve_funding_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(FundingApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        app.status = 'approved'
        app.admin_remark = remark
        app.save()
        
        Notification.objects.create(
            user=app.bidder,
            message=f"Your Funding Application for {app.funding.title} has been APPROVED."
        )
        
        messages.success(request, f"Funding application from {app.bidder.username} approved.")

        # 📧 Send Status Email + PDF Attach
        try:
            from funding.utils import generate_funding_award_pdf
            pdf_content = generate_funding_award_pdf(app)
            pdf_attachment = {
                'filename': f'eBharat_Funding_Approval_{app.id}.pdf',
                'content': pdf_content,
                'mimetype': 'application/pdf'
            }
            
            from django.utils import timezone
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Funding Approved - {app.funding.title}",
                template_name="funding_awarded.html",
                context={
                    "bidder_name": app.bidder.first_name or app.bidder.username,
                    "funding_title": app.funding.title,
                    "amount_requested": app.amount_requested,
                    "tender_title": app.tender.title,
                    "tender_id": app.tender.tender_id,
                    "approval_date": timezone.now().strftime("%d %B %Y"),
                    "domain": current_site.domain,
                },
                recipient_list=[app.bidder.email],
                attachments=[pdf_attachment]
            )
        except Exception as e:
            print(f"Funding Approval Email failed: {e}")
    return redirect('coreadmin:funding_approvals')

@staff_member_required
def reject_funding_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(FundingApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        app.status = 'rejected'
        app.admin_remark = remark
        app.save()
        
        Notification.objects.create(
            user=app.bidder,
            message=f"Your Funding Application for {app.funding.title} has been REJECTED."
        )
        
        messages.warning(request, f"Funding application from {app.bidder.username} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Funding Application Status Update - {app.funding.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": app.bidder.first_name or app.bidder.username,
                    "activity_name": "Funding Application",
                    "item_name": app.funding.title,
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[app.bidder.email]
            )
        except Exception as e:
            print(f"Funding Rejection Email failed: {e}")
    return redirect('coreadmin:funding_approvals')

# --- USER LIST MANAGEMENT ---

@staff_member_required
def user_list(request):
    role = request.GET.get('role', 'all')
    if role == 'bidder':
        profiles = UserProfile.objects.filter(role='bidder')
    elif role == 'creator':
        profiles = UserProfile.objects.filter(role='creator')
    else:
        profiles = UserProfile.objects.all()
    
    return render(request, 'user_list.html', {
        'page_title': 'User Management',
        'profiles': profiles,
        'current_role': role
    })

@user_passes_test(lambda u: u.is_superuser)
def create_staff(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.first_name = full_name # Use first_name for the full name instead of profile
            user.save()
            
            ActionLog.objects.create(
                admin_user=request.user,
                action_type="STAFF_CREATION",
                target_user=user,
                description=f"Created staff account for {full_name} ({username})."
            )
            
            messages.success(request, f"Staff account for {full_name} created successfully.")

            # 📧 Send Welcome/Staff Creation Email
            try:
                current_site = get_current_site(request)
                send_ebharat_email(
                    subject="Your Staff Account has been Created",
                    template_name="welcome_email.html",
                    context={
                        "full_name": full_name,
                        "username": username,
                        "email": email,
                        "mobile": "N/A", # Staff creation doesn't capture mobile by default
                        "domain": current_site.domain,
                    },
                    recipient_list=[email]
                )
            except Exception as e:
                print(f"Staff Email failed: {e}")
            return redirect('coreadmin:user_list')
            
    return render(request, 'create_staff.html', {'page_title': 'Create Staff Account'})

# --- TENDER LIST MANAGEMENT ---

@staff_member_required
def tender_list(request):
    all_tenders = Tenderss.objects.all().order_by('-created_at')
    
    # We want to show which tender who public and how many bid who awards
    tenders_data = []
    for tender in all_tenders:
        applications = tender.applications.all()
        bid_count = applications.count()
        awardee = applications.filter(status='awarded').first()
        tenders_data.append({
            'obj': tender,
            'bid_count': bid_count,
            'applications': applications,
            'awardee': awardee,
            # We also pass formatted awardee name for quick reference
            'awardee_name': awardee.company_name if awardee else "None",
            'publisher': tender.created_by.username # WHO publish
        })
    
    return render(request, 'tender_list.html', {
        'page_title': 'Tender Directory',
        'tenders': tenders_data
    })

@staff_member_required
def tender_bidders(request, tender_id):
    from django.shortcuts import get_object_or_404 # Ensure it's imported just in case
    tender = get_object_or_404(Tenderss, id=tender_id)
    applications = tender.applications.all().order_by('-applied_at')
    
    return render(request, 'tender_bidders.html', {
        'page_title': f'Bidders for TND-{tender.id:04d}',
        'tender': tender,
        'applications': applications,
        'bid_count': applications.count(),
        'awardee': applications.filter(status='awarded').first()
    })

# --- FUNDING MANAGEMENT ---

@login_required
def funding_list(request):
    fundings = Funding.objects.all().order_by('-created_at')
    return render(request, 'funding_list.html', {'page_title': 'Manage Funding Schemes', 'fundings': fundings})

@login_required
def create_funding(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        max_amount = request.POST.get('max_amount')
        interest_rate = request.POST.get('interest_rate')
        tender_id = request.POST.get('tender_id')
        
        tender = None
        if tender_id:
            try:
                tender = Tenderss.objects.get(id=tender_id)
            except Tenderss.DoesNotExist:
                messages.error(request, "Selected Tender does not exist.")
                return redirect('coreadmin:create_funding')
                
        Funding.objects.create(
            title=title,
            description=description,
            max_amount=max_amount,
            interest_rate=interest_rate,
            tender=tender
        )
        messages.success(request, f"Funding scheme '{title}' created successfully.")
        return redirect('coreadmin:funding_list')
        
    tenders = Tenderss.objects.filter(status='open')
    return render(request, 'create_funding.html', {'page_title': 'Create Funding Scheme', 'tenders': tenders})

# --- ADMIN REQUESTS (Department/Category Approval) ---

@staff_member_required
def admin_request_approvals(request):
    pending_requests = AdminRequest.objects.filter(status='pending').order_by('-created_at')
    approved_requests = AdminRequest.objects.filter(status='approved').order_by('-created_at')[:10]
    return render(request, 'approvals.html', {
        'page_title': 'Administrative Requests',
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'type': 'admin_requests'
    })

@staff_member_required
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
        
        Notification.objects.create(
            user=admin_req.user,
            message=f"Your request for {admin_req.department_name} department has been approved."
        )
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_APPROVAL",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Approved department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"Request for {admin_req.department_name} approved.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Administrative Request Approved",
                template_name="status_update_notification.html",
                context={
                    "user_name": admin_req.user.first_name or admin_req.user.username,
                    "activity_name": "Department/Category Creation Request",
                    "item_name": f"{admin_req.department_name} / {admin_req.category_name}",
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[admin_req.user.email]
            )
        except Exception as e:
            print(f"Admin Req Approval Email failed: {e}")
    return redirect('coreadmin:admin_request_approvals')

@staff_member_required
def reject_admin_request(request, request_id):
    if request.method == 'POST':
        admin_req = get_object_or_404(AdminRequest, id=request_id)
        remark = request.POST.get('remark', '')
        
        admin_req.status = 'rejected'
        admin_req.admin_remark = remark
        admin_req.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_REJECTION",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Rejected department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"Request for {admin_req.department_name} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Administrative Request Update",
                template_name="status_update_notification.html",
                context={
                    "user_name": admin_req.user.first_name or admin_req.user.username,
                    "activity_name": "Department/Category Creation Request",
                    "item_name": f"{admin_req.department_name} / {admin_req.category_name}",
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[admin_req.user.email]
            )
        except Exception as e:
            print(f"Admin Req Rejection Email failed: {e}")
    return redirect('coreadmin:admin_request_approvals')

@staff_member_required
def system_reports(request):
    filter_type = request.GET.get('filter_type', 'all')
    date_val = request.GET.get('date')
    fy_val = request.GET.get('fy')
    
    tenders = Tenderss.objects.all()
    bids = TenderApplication.objects.all()
    
    import datetime
    
    if filter_type == 'date' and date_val:
        filter_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
        tenders = tenders.filter(created_at__date=filter_date)
        bids = bids.filter(applied_at__date=filter_date)
    elif filter_type == 'fy' and fy_val:
        start_year = int(fy_val)
        start_date = datetime.date(start_year, 4, 1)
        end_date = datetime.date(start_year + 1, 3, 31)
        tenders = tenders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        bids = bids.filter(applied_at__date__gte=start_date, applied_at__date__lte=end_date)
        
    tenders = tenders.order_by('-created_at')
    
    total_tenders = tenders.count()
    total_bids = bids.count()
    total_disbursed = bids.filter(status='awarded').aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0
    
    return render(request, 'reports.html', {
        'page_title': 'System Reports',
        'tenders': tenders[:50], # Performance limit on preview
        'total_tenders': total_tenders,
        'total_bids': total_bids,
        'total_disbursed': total_disbursed,
        'filter_type': filter_type,
        'date_val': date_val,
        'fy_val': fy_val
    })

@staff_member_required
def download_report_pdf(request):
    filter_type = request.GET.get('filter_type', 'all')
    date_val = request.GET.get('date')
    fy_val = request.GET.get('fy')
    
    tenders = Tenderss.objects.all()
    bids = TenderApplication.objects.all()
    
    import datetime
    report_subtitle = "Overall System Data"
    
    if filter_type == 'date' and date_val:
        filter_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
        tenders = tenders.filter(created_at__date=filter_date)
        bids = bids.filter(applied_at__date=filter_date)
        report_subtitle = f"For specific date: {filter_date.strftime('%d %b %Y')}"
    elif filter_type == 'fy' and fy_val:
        start_year = int(fy_val)
        start_date = datetime.date(start_year, 4, 1)
        end_date = datetime.date(start_year + 1, 3, 31)
        tenders = tenders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        bids = bids.filter(applied_at__date__gte=start_date, applied_at__date__lte=end_date)
        report_subtitle = f"For Financial Year: {start_year}-{start_year+1}"
        
    tenders = tenders.order_by('-created_at')
    
    total_tenders = tenders.count()
    total_bids = bids.count()
    total_disbursed = bids.filter(status='awarded').aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0
    
    # Generate PDF
    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Canvas for Header/Footer (Landscape adapted)
    def header_footer(canvas, doc):
        canvas.saveState()
        width, height = landscape(A4)
        # Header Logo & Text
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#0f2a5e'))
        canvas.drawString(30, height - 30, "eBHARAT TENDER")
        # Header Subtitle
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawRightString(width - 30, height - 30, report_subtitle)
        # Decorative Line under header
        canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
        canvas.line(30, height - 35, width - 30, height - 35)
        
        # Footer text (Page No)
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor('#1e293b'))
        canvas.drawRightString(width - 30, 20, f"Page No. {page_num}")
        # Line above footer
        canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
        canvas.line(30, 35, width - 30, 35)
        canvas.restoreState()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.HexColor('#0f2a5e'), alignment=1)
    elements.append(Paragraph("Official System Data Report", title_style))
    
    # Meta Summary Table
    summary_data = [
        ["Total Tenders", "Total Bids Received", "Total Disbursed (INR)"],
        [str(total_tenders), str(total_bids), f"{float(total_disbursed):,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[150, 150, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0,1), (-1,1), 14),
        ('TOPPADDING', (0,1), (-1,1), 12),
        ('BOTTOMPADDING', (0,1), (-1,1), 12),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Main Data Table
    data = [["ID", "Title", "Category", "Status", "Date", "Est. Value (INR)"]]
    for t in tenders:
        data.append([
            f"TND-{t.id:04d}",
            t.title[:45] + "..." if len(t.title) > 45 else t.title,
            t.category if t.category else "N/A",
            t.status.upper(),
            t.created_at.strftime("%d %b %Y"),
            f"{t.estimated_value:,.2f}"
        ])
        
    if len(data) > 1:
        # repeatRows=1 forces the header row to appear on every new page!
        t_table = Table(data, colWidths=[60, 250, 120, 80, 80, 120], repeatRows=1)
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2a5e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (5,0), (5,-1), 'RIGHT'), # Values right
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8faff')]),
        ]))
        elements.append(t_table)
    else:
        elements.append(Paragraph("No tenders found for the selected period.", styles['Italic']))

    # ── Awarded Bids details Section ──
    awarded_bids = bids.filter(status='awarded')
    if awarded_bids.exists():
        elements.append(PageBreak()) # Send details to a fresh page cleanly
        elements.append(Paragraph("Awarded Company Details", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        for ab in awarded_bids:
            details_data = [
                ["Tender", ab.tender.title[:65] + "..." if len(ab.tender.title) > 65 else ab.tender.title],
                ["Company Name", ab.company_name],
                ["Authorized Bidder", ab.bidder_name],
                ["Contact Info", f"{ab.official_email}  |  Mobile: {ab.mobile_number}"],
                ["Address", f"{ab.registered_address}, {ab.city}, {ab.state} - {ab.pin_code}"],
                ["Awarded Amount", f"INR {ab.bid_amount:,.2f}"]
            ]
            detail_table = Table(details_data, colWidths=[130, 450])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8faff')),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1e293b')),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            # KeepTogether ensures the specific company table is not split across multiple pages
            elements.append(KeepTogether([detail_table, Spacer(1, 15)]))
            
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    import time
    stamp = int(time.time())
    response['Content-Disposition'] = f'attachment; filename="eBharat_Report_{stamp}.pdf"'
    return response

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out from the Control Center.")
    return redirect('accounts:login')

@login_required
def allocate_user_role(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        role = request.POST.get('role')
        if role:
            old_role = profile.get_role_display() if profile.role else 'None'
            profile.role = role
            profile.save()
            new_role = profile.get_role_display()
            
            ActionLog.objects.create(
                admin_user=request.user,
                action_type="ROLE_ALLOCATION",
                target_user=profile.user,
                description=f"Changed role from {old_role} to {new_role}."
            )
            
            Notification.objects.create(
                user=profile.user,
                message=f"Your account role has been updated to {new_role} by an Administrator."
            )

            # 📧 Send Role Update Email
            try:
                current_site = get_current_site(request)
                send_ebharat_email(
                    subject="Account Role Updated",
                    template_name="status_update_notification.html",
                    context={
                        "user_name": profile.user.first_name or profile.user.username,
                        "activity_name": "Account Profile Update",
                        "item_name": f"Role Allocation to {new_role}",
                        "status": "approved", # Role change is considered an administrative approval
                        "remark": f"Your role has been updated from {old_role} to {new_role}.",
                        "domain": current_site.domain,
                    },
                    recipient_list=[profile.user.email]
                )
            except Exception as e:
                print(f"Role Update Email failed: {e}")

            messages.success(request, f"Role updated successfully for {profile.user.username}.")
        else:
            messages.error(request, "No valid role selected.")
    return redirect('coreadmin:user_list')

@login_required
def action_history(request):
    logs = ActionLog.objects.all().order_by('-timestamp')
    return render(request, 'action_history.html', {'page_title': 'System Audit Log', 'logs': logs})

# --- NOTICE MANAGEMENT ---

@login_required
def notice_list(request):
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'manage_notices.html', {'page_title': 'Manage Noticeboard', 'notices': notices})

@login_required
def create_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        Notice.objects.create(
            title=title,
            description=description,
            category=category,
            is_pinned=is_pinned,
            created_by=request.user
        )
        messages.success(request, f"Notice '{title}' published successfully.")
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="NOTICE_CREATION",
            description=f"Created a new notice: {title} ({category})"
        )
        
    return redirect('coreadmin:notice_list')

@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        notice.title = request.POST.get('title')
        notice.description = request.POST.get('description')
        notice.category = request.POST.get('category')
        notice.is_pinned = request.POST.get('is_pinned') == 'on'
        notice.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="NOTICE_UPDATED",
            description=f"Updated notice: {notice.title}"
        )
        messages.info(request, f"Notice '{notice.title}' updated.")
    return redirect('coreadmin:notice_list')

@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    title = notice.title
    notice.delete()
    
    ActionLog.objects.create(
        admin_user=request.user,
        action_type="NOTICE_DELETION",
        description=f"Deleted notice: {title}"
    )
    
    messages.warning(request, f"Notice '{title}' deleted.")
    return redirect('coreadmin:notice_list')


@staff_member_required
def admin_profile(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('coreadmin:admin_profile')
            
        elif action == 'change_password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                # Maintain session so the user is not automatically logged out
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated.")
                return redirect('coreadmin:admin_profile')
            else:
                for error_list in form.errors.values():
                    for error in error_list:
                        messages.error(request, error)
                    
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'admin_profile.html', {
        'page_title': 'Profile Settings',
        'password_form': form,
    })
