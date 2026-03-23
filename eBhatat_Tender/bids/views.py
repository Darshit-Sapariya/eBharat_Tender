from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import razorpay
from .models import TenderApplication
from tenders.models import Tenderss
from accounts.models import UserProfile, Notification, Watchlist
from funding.models import Funding, FundingApplication
from funding.models import Funding, FundingApplication
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# ==============================================================================
# BIDDER DASHBOARD & MANAGEMENT VIEWS
# ==============================================================================

# View personal bidder dashboard
@login_required
def bids_dashboard(request):
    today = timezone.now().date()
    
    # Auto-close expired tenders globally
    Tenderss.objects.filter(closing_date__lt=today, status='open').update(status='closed')

    # Open tenders (not expired)
    open_tenders = Tenderss.objects.filter(
        closing_date__gte=today,
        status='open'
    ).order_by("closing_date")

    # User's applied tenders
    applied_tenders = TenderApplication.objects.filter(
        applicant=request.user
    ).order_by('-applied_at')

    # Pending bids
    pending_tenders = applied_tenders.filter(status='pending')

    # Approved bids
    approved_tenders = applied_tenders.filter(status='approved')
    # Rejected bids
    rejected_tenders = applied_tenders.filter(status='rejected')
    # Awarded bids
    awarded_tenders = applied_tenders.filter(status='awarded')

    # Calculate success rate
    total_applied = applied_tenders.count()
    awarded_count = awarded_tenders.count()
    success_rate = (awarded_count / total_applied * 100) if total_applied > 0 else 0

    # Recent Open Tenders (Latest 5)
    recent_tenders = Tenderss.objects.filter(status='open').order_by('-created_at')[:5]

    # Recent Notifications (Latest 5)
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Watchlist Count
    watchlist_count = Watchlist.objects.filter(user=request.user).count()

    # Funding Application Count
    from funding.models import FundingApplication as FA
    funding_count = FA.objects.filter(bidder=request.user).count()

    # User Profile for status
    profile = getattr(request.user, 'userprofile', None)


    context = {
        "open_tenders": open_tenders,
        "applied_tenders": applied_tenders,
        "awarded_tenders": awarded_tenders,
        "success_rate": round(success_rate, 1),
        "pending_tenders": pending_tenders,
        "approved_tenders": approved_tenders,
        "rejected_tenders": rejected_tenders,
        "recent_tenders": recent_tenders,
        "recent_notifications": recent_notifications,
        "profile": profile,

        # Counts
        "open_count": open_tenders.count(),
        "applied_count": applied_tenders.count(),
        "pending_count": pending_count if (pending_count := pending_tenders.count()) else 0, # usingWalrus for fun, wait no, let's keep it simple
        "pending_count": pending_tenders.count(),
        "approved_count": approved_tenders.count(),
        "rejected_count": rejected_tenders.count(),
        "watchlist_count": watchlist_count,
        "funding_count": funding_count,
    }

    return render(request, 'bids_dashboard.html', context)


@login_required
def vendor_profile_update(request):
    """Premium profile update view for Vendors."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Secure Display: Sensitive ID numbers are masked via the profile.masked_id property
    # in templates. The full ID is only shown when toggled by the user.
    
    # Strictly enforce vendor role if already set
    if profile.role and profile.role != 'bidder':
        messages.error(request, "Access denied. This portal is for vendors only.")
        return redirect("tenders:dashboard")

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")
        profile.mobile = request.POST.get("mobile")
        profile.address = request.POST.get("address")
        profile.gov_id_type = request.POST.get("gov_id_type")
        profile.gov_id_number = request.POST.get("gov_id_number")

        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")
        if request.FILES.get("gov_id_upload"):
            profile.gov_id_upload = request.FILES.get("gov_id_upload")

        # Auto-assign 'bidder' role if not already set (since they are in this view)
        if not profile.role:
            profile.role = 'bidder'

        profile.save()
        messages.success(request, "Your vendor profile has been updated successfully.")
        return redirect("bids:vendor_profile_update")

    return render(request, "vendor_profile_update.html", {"profile": profile})


# Handle new bid submission
@login_required
def applybid(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    fundings = Funding.objects.filter(tender=tender)

    # Prevent owner from bidding
    if tender.created_by == request.user:
        messages.warning(request, "You cannot bid on your own tender.")
        return redirect("tenders:tenderDetails", tender_id=tender.id)

    # Prevent bidding on closed/expired tenders
    if tender.status != 'open' or tender.closing_date < timezone.now().date():
        messages.error(request, "This tender is no longer open for bidding.")
        return redirect("tenders:tenderDetails", tender_id=tender.id)

    # Prevent duplicate bidding
    if TenderApplication.objects.filter(tender=tender, applicant=request.user).exists():
        messages.info(request, "You have already applied for this tender.")
        return redirect("tenders:tenderDetails", tender_id=tender.id)

    # Only bidders can apply
    try:
        if request.user.userprofile.role != 'bidder':
            messages.error(request, "Only verified bidders can apply for tenders.")
            return redirect("tenders:tenderDetails", tender_id=tender.id)
    except:
        return redirect("accounts:login")

    if request.method == "POST":
        try:
            bid_amount = request.POST.get("bid_amount")
            if not bid_amount:
                raise ValueError("Bid amount is required.")

            razorpay_payment_id = request.POST.get("razorpay_payment_id")
            if tender.emd_amount > 0 and not razorpay_payment_id:
                raise ValueError("EMD Payment is required to apply for this tender.")

            application = TenderApplication.objects.create(
                tender=tender,
                applicant=request.user,

                # Company Details
                company_name=request.POST.get("company_name"),
                gst_number=request.POST.get("gst_number"),
                registered_address=request.POST.get("registered_address"),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                pin_code=request.POST.get("pin_code"),
                gst_document=request.FILES.get("gst_document"),

                # Bidder Details
                bidder_name=request.POST.get("bidder_name"),
                designation=request.POST.get("designation"),
                official_email=request.POST.get("email"),
                mobile_number=request.POST.get("mobile"),

                # Financial
                financial_statement=request.FILES.get("financial_statement"),

                # Bidding Details
                bid_amount=bid_amount,
                technical_document=request.FILES.get("technical_document"),
                financial_document=request.FILES.get("financial_document"),
                other_document=request.FILES.get("other_document"),
                
                # Payment Details
                payment_status='paid' if tender.emd_amount > 0 else 'pending',
                razorpay_payment_id=razorpay_payment_id,
            )
            
            # Handle Funding Application if selected
            if request.POST.get("apply_funding") == "on":
                funding_id = request.POST.get("funding_id")
                amount_requested = request.POST.get("amount_requested")
                purpose = request.POST.get("purpose")
                supporting_doc = request.FILES.get("funding_document")
                
                if funding_id and amount_requested and purpose:
                    funding_obj = get_object_or_404(Funding, id=funding_id)
                    FundingApplication.objects.create(
                        bidder=request.user,
                        funding=funding_obj,
                        tender=tender,
                        amount_requested=amount_requested,
                        purpose=purpose,
                        supporting_document=supporting_doc
                    )
            
            # 📌 Notify the Tender Creator about the new bid
            Notification.objects.create(
                user=tender.created_by,
                message=f"New bid received from {application.company_name} for {tender.title}",
                link=reverse("tenders:view_tender_bids", kwargs={"tender_id": tender.id})
            )

            messages.success(request, "Tender Application Submitted Successfully! Your bid has been recorded.")
            return redirect("tenders:tenderDetails", tender_id=tender.id)
            
        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
            return render(request, "applybid.html", {
                "tender": tender, 
                "fundings": fundings,
                "error": str(e), 
                "razorpay_key": settings.RAZORPAY_KEY_ID
            })

    return render(request, "applybid.html", {
        "tender": tender,
        "fundings": fundings,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })


# View applications for tender
@login_required
def tender_applications(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)

    # Only creator can see applications
    if tender.created_by != request.user:
        messages.error(request, "You are not authorized to view applications.")
        return redirect("dashboard")

    applications = tender.applications.all().order_by('-id')
    total_emd = sum(app.tender.emd_amount for app in applications if app.payment_status == 'paid')

    return render(request, "tender_applications.html", {
        "tender": tender,
        "applications": applications,
        "total_emd": total_emd
    })

# List user submitted bids
@login_required
def mybids(request):
    bids = TenderApplication.objects.filter(applicant=request.user).order_by('-id')

    search = request.GET.get("search")
    status = request.GET.get("status")

    if search:
        bids = bids.filter(tender__title__icontains=search) | bids.filter(company_name__icontains=search)

    if status:
        bids = bids.filter(status=status)

    context = {
        "bids": bids,
        "pending_count": bids.filter(status="pending").count(),
        "approved_count": bids.filter(status="approved").count(),
        "rejected_count": bids.filter(status="rejected").count(),
    }

    return render(request, "mybids.html", context)

# View submitted bid details
@login_required
def bid_detail(request, bid_id):
    bid = get_object_or_404(TenderApplication,id=bid_id,applicant=request.user)
    return render(request, "bid_detail.html", {"bid": bid}) 

@login_required
def withdraw_bid(request, bid_id):
    """Allow bidder to withdraw a pending bid."""
    bid = get_object_or_404(TenderApplication, id=bid_id, applicant=request.user)
    
    if bid.status != 'pending':
        messages.error(request, "You can only withdraw bids that are still pending.")
        return redirect("bids:bid_detail", bid_id=bid.id)
        
    if bid.tender.closing_date < timezone.now().date():
        messages.error(request, "Closing date has passed. You cannot withdraw this bid.")
        return redirect("bids:bid_detail", bid_id=bid.id)

    bid.delete()
    messages.success(request, "Bid withdrawn successfully.")
    return redirect("bids:mybids")

@login_required
def toggle_watchlist(request, tender_id):
    """Add or remove a tender from user's watchlist."""
    tender = get_object_or_404(Tenderss, id=tender_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, tender=tender)

    if watchlist_item.exists():
        watchlist_item.delete()
        messages.info(request, f"Removed {tender.title} from watchlist.")
    else:
        Watchlist.objects.create(user=request.user, tender=tender)
        messages.success(request, f"Added {tender.title} to watchlist.")

    return redirect(request.META.get('HTTP_REFERER', 'public:home'))

@login_required
def my_watchlist(request):
    """View saved tenders."""
    items = Watchlist.objects.filter(user=request.user).select_related('tender').order_by('-created_at')
    return render(request, 'watchlist.html', {'watchlist': items})





# ==============================================================================
# DOCUMENT GENERATION VIEWS
# ==============================================================================

# Generate bid summary PDF
@login_required
def download_bid_pdf(request, bid_id):
    bid = get_object_or_404(TenderApplication, id=bid_id, applicant=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="eBharat_Bid_{bid.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # ---------------- HEADER ----------------
    header_style = ParagraphStyle(
        'header_style',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=18,
        spaceAfter=10
    )

    sub_header_style = ParagraphStyle(
        'sub_header_style',
        parent=styles['Normal'],
        alignment=1,
        fontSize=11,
        textColor=colors.grey
    )

    elements.append(Paragraph("eBharat Tender Portal", header_style))
    elements.append(Paragraph("Official Procurement Submission Record", sub_header_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- SECTION 1 ----------------
    elements.append(Paragraph("<b>1. Tender Information</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    tender_data = [
        ["Tender Title", bid.tender.title],
        ["Category", str(bid.tender.category)],
        ["Issued By", str(bid.tender.created_by)],
        ["Closing Date", bid.tender.closing_date.strftime("%d %B %Y")],
        ["Estimated Value", f"₹ {bid.tender.estimated_value}"],
        
    ]

    tender_table = Table(tender_data, colWidths=[170, 300])
    tender_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(tender_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- SECTION 2 ----------------
    elements.append(Paragraph("<b>2. Company Information</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    company_data = [
        ["Company Name", bid.company_name],
        ["GST Number", bid.gst_number],
        ["City", bid.city],
        ["State", bid.state],
        ["Pin Code", bid.pin_code],
    ]

    company_table = Table(company_data, colWidths=[170, 300])
    company_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(company_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- SECTION 3 ----------------
    elements.append(Paragraph("<b>3. Bid Submission Details</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    submission_data = [
        ["Authorized Representative", bid.bidder_name],
        ["Designation", bid.designation],
        ["Email", bid.official_email],
        ["Mobile", bid.mobile_number],
        ["Bid Amount", f"₹ {bid.bid_amount}"],
        ["Status", bid.status.capitalize()],
        ["Submitted On", bid.applied_at.strftime("%d %B %Y")],
    ]

    submission_table = Table(submission_data, colWidths=[170, 300])
    submission_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(submission_table)
    elements.append(Spacer(1, 0.6 * inch))

    # ---------------- SIGNATURE AREA ----------------
    sign_data = [
        ["__________________________", "__________________________"],
        ["Authorized Signatory", "Procurement Officer"],
    ]

    sign_table = Table(sign_data, colWidths=[250, 250])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(sign_table)
    elements.append(Spacer(1, 0.5 * inch))
    # Build PDF
    doc.build(elements)

    return response