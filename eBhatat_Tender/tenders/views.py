import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
import razorpay

from bids.models import TenderApplication
from accounts.models import UserProfile, Notification, AdminRequest, Department, Category
from accounts.utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site
from .utils import generate_award_pdf
from .models import Tenderss

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
# TENDER MANAGEMENT VIEWS
# ==============================================================================

# Handle admin permission requests
@login_required
def request_admin(request):
    if request.method == "POST":
        dept_name = request.POST.get("department_name")
        cat_name = request.POST.get("category_name")
        
        AdminRequest.objects.create(
            user=request.user,
            department_name=dept_name,
            category_name=cat_name
        )
        messages.success(request, "Your request has been submitted for admin approval.")
        return redirect("tenders:dashboard")

    requests = AdminRequest.objects.filter(user=request.user).order_by("-created_at")
    return render(request, 'admin_request.html', {
        'page_title': 'Request Admin Permission',
        'requests': requests
    })

# Manage administrative user requests
@login_required
def admin_view_requests(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect("tenders:dashboard")

    if request.method == "POST":
        req_id = request.POST.get("request_id")
        action = request.POST.get("action")
        remark = request.POST.get("remark")
        
        admin_req = get_object_or_404(AdminRequest, id=req_id)
        
        if action == "approve":
            admin_req.status = "approved"
            # Create Department and Category if they don't exist
            Department.objects.get_or_create(name=admin_req.department_name)
            Category.objects.get_or_create(name=admin_req.category_name)
            
            Notification.objects.create(
                user=admin_req.user,
                message=f"Your request for {admin_req.department_name} - {admin_req.category_name} has been approved.",
                link=reverse("tenders:tenderCreator")
            )
        elif action == "reject":
            admin_req.status = "rejected"
            Notification.objects.create(
                user=admin_req.user,
                message=f"Your request for {admin_req.department_name} has been rejected.",
            )
            
        admin_req.admin_remark = remark
        admin_req.save()
        messages.success(request, f"Request {action}ed successfully.")
        return redirect("tenders:admin_view_requests")
    


# ==============================================================================
# DASHBOARD & LIST VIEWS
# ==============================================================================

# Main dashboard for users
def dashboard(request):
    today = timezone.now().date()
    
    # Auto-close expired open tenders globally
    Tenderss.objects.filter(closing_date__lt=today, status='open').update(status='closed')

    tenders = Tenderss.objects.filter(created_by=request.user)

    total_tenders = tenders.count()
    active_tenders = tenders.filter(status="open").count()
    closed_tenders = tenders.filter(status="closed").count()

    total_applications = TenderApplication.objects.filter(
        tender__created_by=request.user
    ).count()

    # Recent 5 tenders with application count
    recent_tenders = tenders.annotate(
        application_count=Count("applications")
    ).order_by("-created_at")[:5]

    context = {
        "total_tenders": total_tenders,
        "active_tenders": active_tenders,
        "closed_tenders": closed_tenders,
        "total_applications": total_applications,
        "recent_tenders": recent_tenders,
        "page_title": "Dashboard",
    }
    return render(request, 'dashboard.html', context)

# Create your views here.
# Create and publish tenders
def tenderCreator(request):
    if request.method == "POST":
        tender = Tenderss.objects.create(
            title=request.POST.get("title"),
            department=request.POST.get("department"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            estimated_value=request.POST.get("estimated_value"),
            emd_amount=request.POST.get("emd_amount"),
            publish_date=request.POST.get("publish_date"),
            closing_date=request.POST.get("closing_date"),
            pre_bid_meeting=request.POST.get("pre_bid_meeting"),
            location=request.POST.get("location"),
            status=request.POST.get("status"),
            document=request.FILES.get("document"),
            created_by=request.user
        )
        
        # 📌 Notify all specific bidders about the new tender
        bidders = UserProfile.objects.filter(role='bidder')
        for bidder in bidders:
            Notification.objects.create(
                user=bidder.user,
                message=f"New Tender Published: {tender.title}",
                link=reverse("tenders:tenderDetails", kwargs={"tender_id": tender.id})
            )
                
        return redirect("tenders:mytenders")

    # Fetch approved departments and categories for this user
    approved_requests = AdminRequest.objects.filter(user=request.user, status='approved')
    approved_depts = sorted(list(set([r.department_name for r in approved_requests])))
    approved_cats = sorted(list(set([r.category_name for r in approved_requests])))

    return render(request, 'tenderCreator.html', {
        'page_title': 'Publish Tender',
        'approved_depts': approved_depts,
        'approved_cats': approved_cats
    })

# List user issued tenders
def mytenders(request):
   today = timezone.now().date()
   Tenderss.objects.filter(closing_date__lt=today, status='open').update(status='closed')
   
   tenders = Tenderss.objects.filter(created_by=request.user).order_by('-created_at')
   
   # Prefetch awarded application for each tender to show company name in list
   for t in tenders:
       app = t.applications.filter(status='awarded').first()
       if app:
           app.masked_gst = mask_id(app.gst_number)
           t.awarded_application = app
       
   return render(request, 'mytenders.html', {'tenders': tenders, 'page_title': 'Issued Tenders'})

# Update user profile details
def updateProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # 🔀 Redirect Vendors (Bidders) to their dedicated premium profile page
    if profile.role == 'bidder':
        return redirect("bids:vendor_profile_update")

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name")
        profile.mobile = request.POST.get("mobile")
        profile.address = request.POST.get("address")
        
        # Only allow setting designation if it's currently blank
        designation = request.POST.get("designation")
        if designation and not profile.designation:
            profile.designation = designation
        
        # Only update ID fields if they are actually in the POST data 
        # (they might be disabled in the HTML once verified, and thus not sent)
        gov_id_type = request.POST.get("gov_id_type")
        if gov_id_type:
            profile.gov_id_type = gov_id_type
            
        gov_id_number = request.POST.get("gov_id_number")
        if gov_id_number:
            profile.gov_id_number = gov_id_number

        # Profile picture upload
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")

        # Government ID upload
        if request.FILES.get("gov_id_upload"):
            profile.gov_id_upload = request.FILES.get("gov_id_upload")

        # 🔒 Role only set if not already assigned
        if not profile.role:
            role = request.POST.get("role")
            if role:
                profile.role = role

        profile.save()

        # 🔐 Password Change Logic
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if old_password or new_password or confirm_password:
            if not old_password or not new_password or not confirm_password:
                messages.error(request, "To change password, please fill in all password fields.")
                return redirect("tenders:updateProfile")
            
            if not request.user.check_password(old_password):
                messages.error(request, "Incorrect current password.")
                return redirect("tenders:updateProfile")
            
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect("tenders:updateProfile")
            
            if len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
                return redirect("tenders:updateProfile")

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully!")

        # Update first_name on User model for consistency
        full_name = request.POST.get("full_name")
        if full_name:
            User.objects.filter(id=request.user.id).update(first_name=full_name)

        messages.success(request, "Profile updated successfully!")
        return redirect("tenders:updateProfile")   # reload page after save

    profile_data = {
        'full_name': profile.full_name,
        'mobile': profile.mobile,
        'address': profile.address,
        'designation': profile.designation,
        'gov_id_type': profile.gov_id_type,
        'gov_id_number': mask_id(profile.gov_id_number),
        'role': profile.role,
        'profile_pic': profile.profile_pic,
        'gov_id_upload': profile.gov_id_upload,
    }

    return render(request, 'updateProfile.html', {'page_title': 'Profile Settings', 'profile': profile_data})

# Simple tender deletion view
def tender_delete(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id, created_by=request.user)
    tender.delete()
    return redirect('tenders:mytenders')

# Edit existing tender details
@login_required
def tender_edit(request, tender_id):
    tender = get_object_or_404(
        Tenderss,
        id=tender_id,
        created_by=request.user
    )

    if request.method == "POST":

        tender.title = request.POST.get("title")
        tender.department = request.POST.get("department")
        tender.category = request.POST.get("category")
        tender.description = request.POST.get("description")
        tender.estimated_value = request.POST.get("estimated_value")
        tender.emd_amount = request.POST.get("emd_amount")

        # Handle publish date
        publish_date = request.POST.get("publish_date")
        tender.publish_date = publish_date if publish_date else None

        # Handle closing date
        closing_date = request.POST.get("closing_date")
        tender.closing_date = closing_date if closing_date else None

        # ✅ SAFE DateTime Handling (Fix ValidationError)
        pre_bid = request.POST.get("pre_bid_meeting")

        if pre_bid:
            tender.pre_bid_meeting = parse_datetime(pre_bid)
        else:
            tender.pre_bid_meeting = None

        tender.location = request.POST.get("location")
        tender.status = request.POST.get("status")

        # Handle file upload
        if request.FILES.get("document"):
            tender.document = request.FILES.get("document")

        tender.save()

        return redirect("tenders:mytenders")

    return render(request, "tender_edit.html", {
        "tender": tender,
        "page_title": "Edit Tender",
    })
# View single tender details
def tenderDetails(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)

    is_expired = tender.closing_date < timezone.now().date()
    # Optional: Automatically close expired open tenders
    if is_expired and tender.status == "open":
        tender.status = "closed"
        tender.save()
        
    has_applied = False
    if request.user.is_authenticated:
        has_applied = TenderApplication.objects.filter(tender=tender, applicant=request.user).exists()

    applications = tender.applications.all().order_by('-applied_at')
    awarded_bid = applications.filter(status='awarded').first()

    if awarded_bid:
        awarded_bid.masked_gst = mask_id(awarded_bid.gst_number)

    # Fetch available funding for this tender (or general funding)
    from funding.models import Funding
    from django.db.models import Q
    available_fundings = Funding.objects.filter(Q(tender=tender) | Q(tender__isnull=True))
    
    # Check if user has applied for any of these fundings for THIS tender
    user_funding_apps = []
    applied_funding_ids = []
    if request.user.is_authenticated:
        from funding.models import FundingApplication
        user_funding_apps = FundingApplication.objects.filter(bidder=request.user, tender=tender)
        applied_funding_ids = list(user_funding_apps.values_list('funding_id', flat=True))

    context = {
        "tender": tender,
        "is_expired": is_expired,
        "has_applied": has_applied,
        "applications": applications,
        "awarded_bid": awarded_bid,
        "available_fundings": available_fundings,
        "applied_funding_ids": applied_funding_ids,
        "page_title": "Tender Details",
    }

    return render(request, 'tenderDetails.html', context)


# List vendor submitted bids
def bids(request):
    bids = TenderApplication.objects.filter(applicant=request.user).order_by('-applied_at') 
    return render(request, 'bids.html', {'bids': bids})

# View tender application status
def viewbids(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    is_expired = tender.closing_date < timezone.now().date()

    if is_expired and tender.status.lower() == "open":
        tender.status = "closed"
        tender.save()

    has_applied = False
    if request.user.is_authenticated:
        has_applied = tender.applications.filter(applicant=request.user).exists()

    context = {
        "tender": tender,
        "is_expired": is_expired,
        "has_applied": has_applied,
        "page_title": "View Bids",
    }
    return render(request, 'viewbids.html', context)

# See all tender applications
@login_required
def view_tender_bids(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id, created_by=request.user)

    bids = TenderApplication.objects.filter(
        tender=tender
    ).select_related("applicant").order_by("bid_amount")

    for bid in bids:
        bid.masked_gst = mask_id(bid.gst_number)
        
        # Transparency: Attach approved funding details
        from funding.models import FundingApplication
        bid.approved_funding = FundingApplication.objects.filter(
            bidder=bid.applicant,
            tender=tender,
            status='approved'
        ).first()

    total_emd = sum(bid.tender.emd_amount for bid in bids if bid.payment_status == 'paid')

    context = {
        "tender": tender,
        "bids": bids,
        "has_awarded_bid": bids.filter(status='awarded').exists(),
        "total_emd": total_emd,
        "page_title": "Tender Bids",
    }
    return render(request, "tender_bids.html", context)


# Update bid evaluation status
@login_required
def update_bid_status(request, bid_id):
    # Only tender creator can update bid
    bid = get_object_or_404(
        TenderApplication,
        id=bid_id,
        tender__created_by=request.user
    )

    if request.method == "POST":
        # Prevent changing status if already awarded
        if bid.tender.applications.filter(status="awarded").exists() and bid.status != "awarded":
            messages.error(request, "This tender has already been awarded to another bidder.")
            return redirect("tenders:view_tender_bids", tender_id=bid.tender.id)

        action = request.POST.get("action")
        remark = request.POST.get("remark")

        if action == "award":
            bid.status = "awarded"
            
            # Auto-reject and refund all other bids for this tender
            losing_bids = TenderApplication.objects.filter(tender=bid.tender).exclude(id=bid.id)
            for l_bid in losing_bids:
                l_bid.status = "rejected"
                if l_bid.payment_status == 'paid' and l_bid.razorpay_payment_id:
                    try:
                        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                        refund = client.payment.refund(l_bid.razorpay_payment_id, {
                            "amount": int(l_bid.tender.emd_amount * 100)
                        })
                        l_bid.payment_status = "refunded"
                    except Exception as e:
                        print(f"Refund failed for application {l_bid.id}: {e}")
                l_bid.save()
            
            # Close/Award the tender
            bid.tender.status = "awarded"
            bid.tender.save()
            
            # 📧 Send Official Award Email to Winner
            try:
                current_site = get_current_site(request)
                context = {
                    "bidder_name": bid.applicant.first_name or bid.applicant.username,
                    "company_name": bid.company_name,
                    "tender_title": bid.tender.title,
                    "tender_id": bid.tender.tender_id,
                    "department": bid.tender.department,
                    "location": bid.tender.location,
                    "bid_amount": bid.bid_amount,
                    "award_date": timezone.now().strftime("%d %B %Y"),
                    "gst_number": bid.gst_number,
                    "address": bid.registered_address,
                    "domain": current_site.domain,
                }
                
                pdf_content = generate_award_pdf(context)
                attachments = [{
                    'filename': f"Award_Letter_{bid.tender.tender_id}.pdf",
                    'content': pdf_content,
                    'mimetype': 'application/pdf'
                }]
                
                send_ebharat_email(
                    subject="Congratulations! Tender Awarded",
                    template_name="bid_awarded.html",
                    context=context,
                    recipient_list=[bid.applicant.email],
                    attachments=attachments
                )
            except Exception as e:
                print(f"Award Email failed: {e}")

            messages.success(request, f"Tender awarded to {bid.company_name} successfully!")

        elif action == "approve":
            bid.status = "approved"
            messages.success(request, "Bid approved successfully.")

        elif action == "reject":
            bid.status = "rejected"
            messages.error(request, "Bid rejected.")

        bid.remark = remark
        bid.save()

    return redirect("tenders:view_tender_bids", tender_id=bid.tender.id)
# View to display all bids across tenders for the logged-in user
# View consolidated bid applications
@login_required
def myBiddsApplications(request):

    bids = TenderApplication.objects.select_related(
        "tender", "applicant"
    ).filter(
        tender__created_by=request.user   # 🔥 important filter
    ).order_by("-applied_at")

    # Counts
    total_bids = bids.count()
    pending_count = bids.filter(status="pending").count()
    approved_count = bids.filter(status="approved").count()
    rejected_count = bids.filter(status="rejected").count()

    context = {
        "bids": bids,
        "total_bids": total_bids,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "page_title": "Bid Applications",
    }

    return render(request, "myBiddsApplications.html", context)