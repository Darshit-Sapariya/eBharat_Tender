from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from  bids.models import TenderApplication
from accounts.models import UserProfile
from tenders.models import Tenderss
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from tenders.models import Tenderss
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Tenderss, TenderApplication

def updateProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name")
        profile.mobile = request.POST.get("mobile")
        profile.address = request.POST.get("address")
        profile.gov_id_type = request.POST.get("gov_id_type")
        profile.gov_id_number = request.POST.get("gov_id_number")
        profile.save()
        messages.success(request, "Profile Updated Successfully.")
        return redirect("bids:updateprofile")

    return render(request, 'updateProfile.html')    





@login_required
def bidsdeshboard(request):

    today = timezone.now()

    # Open tenders (not expired)
    open_tenders = Tenderss.objects.filter(
        closing_date__gte=today,
        status='open'
    ).order_by("closing_date")

    # User's applied tenders
    applied_tenders = TenderApplication.objects.filter(
        applicant=request.user
    )

    # Pending bids
    pending_tenders = applied_tenders.filter(status='pending')

    # Approved bids
    approved_tenders = applied_tenders.filter(status='approved')
    # Rejected bids
    rejected_tenders = applied_tenders.filter(status='rejected')

    context = {
        "open_tenders": open_tenders,
        "applied_tenders": applied_tenders,
        "pending_tenders": pending_tenders,
        "approved_tenders": approved_tenders,
        "rejected_tenders": rejected_tenders,

        # Counts (very useful for dashboard cards)
        "open_count": open_tenders.count(),
        "applied_count": applied_tenders.count(),
        "pending_count": pending_tenders.count(),
        "approved_count": approved_tenders.count(),
        "rejected_count": rejected_tenders.count(),
    }

    return render(request, 'bidsdeshboard.html', context)


def applybid(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)

    # Prevent owner from bidding
    if tender.created_by == request.user:
        return redirect("tenders:tenderDetails", tender_id=tender.id)

    if request.method == "POST":
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
            bid_amount=request.POST.get("bid_amount"),
            technical_document=request.FILES.get("technical_document"),
            financial_document=request.FILES.get("financial_document"),
            other_document=request.FILES.get("other_document"),
        )

        messages.success(request, "Tender Application Submitted Successfully.")
        return redirect("tenders:tenderDetails", tender_id=tender.id)

    return render(request, "applybid.html", {"tender": tender})


@login_required
def tender_applications(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)

    # Only creator can see applications
    if tender.created_by != request.user:
        messages.error(request, "You are not authorized to view applications.")
        return redirect("dashboard")

    applications = tender.applications.all()

    return render(request, "tender_applications.html", {
        "tender": tender,
        "applications": applications
    })

@login_required
def mybids(request):
    bids = TenderApplication.objects.filter(applicant=request.user)

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

@login_required
def bid_detail(request, bid_id):
    bid = get_object_or_404(TenderApplication,id=bid_id,applicant=request.user)
    return render(request, "bid_detail.html", {"bid": bid}) 



from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable
from django.utils.timezone import now


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