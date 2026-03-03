from time import timezone
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from bids.models import TenderApplication
from accounts.models import UserProfile
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Tenderss


# Create your views here.
def tenderCreator(request):
    return render(request, 'tenderCreator.html')
def updateProfile(request):
    if request.method == 'POST':
        # Handle form submission and update profile logic here
        pass
    return render(request, 'updateProfile.html')
def deshboard(request):
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
    }
    return render(request, 'dashboard.html', context)
def mytenders(request):
    return render(request, 'mytenders.html')

# Create your views here.
def tenderCreator(request):
    if request.method == "POST":
        Tenderss.objects.create(
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
        return redirect("tenders:mytenders")

    return render(request, 'tenderCreator.html')

def mytenders(request):
   tenders = Tenderss.objects.filter(created_by=request.user).order_by('-created_at')
   return render(request, 'mytenders.html', {'tenders': tenders})

def updateProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name")
        profile.mobile = request.POST.get("mobile")
        profile.address = request.POST.get("address")
        profile.gov_id_type = request.POST.get("gov_id_type")
        profile.gov_id_number = request.POST.get("gov_id_number")

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
        return redirect("tenders:updateProfile")   # reload page after save

    return render(request, 'updateProfile.html')

def tender_delete(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id, created_by=request.user)
    tender.delete()
    return redirect('tenders:mytenders')

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
        "tender": tender
    })

def tenderDetails(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)

    is_expired = tender.closing_date < timezone.now().date()
    # Optional: Automatically close expired open tenders
    if is_expired and tender.status == "open":
        tender.status = "closed"
        tender.save()

    context = {
        "tender": tender,
        "is_expired": is_expired
    }
    return render(request, 'tenderDetails.html', context)

def bids(request):
    bids = TenderApplication.objects.filter(applicant=request.user).order_by('-applied_at') 
    return render(request, 'bids.html', {'bids': bids})

def bidsinfo(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    is_expired = tender.closing_date < timezone.now().date()

    if is_expired and tender.status == "Open":
        tender.status = "Closed"
        tender.save()

    context = {
        "tender": tender,
        "is_expired": is_expired
    }
    return render(request, 'bidsinfo.html', context)

@login_required
def view_tender_bids(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id, created_by=request.user)

    bids = TenderApplication.objects.filter(
        tender=tender
    ).select_related("applicant").order_by("bid_amount")

    context = {
        "tender": tender,
        "bids": bids
    }
    return render(request, "tender_bids.html", context)

login_required
def update_bid_status(request, bid_id):
    # Only tender creator can update bid
    bid = get_object_or_404(
        TenderApplication,
        id=bid_id,
        tender__created_by=request.user
    )

    if request.method == "POST":

        # Prevent changing status again
        if bid.status != "pending":
            messages.warning(request, "This bid has already been reviewed.")
            return redirect("tenders:view_tender_bids", tender_id=bid.tender.id)

        action = request.POST.get("action")
        remark = request.POST.get("remark")

        if action == "approve":
            bid.status = "approved"

            # OPTIONAL: auto reject all other bids
            TenderApplication.objects.filter(
                tender=bid.tender
            ).exclude(id=bid.id).update(status="rejected")

            messages.success(request, "Bid approved successfully.")

        elif action == "reject":
            bid.status = "rejected"
            messages.error(request, "Bid rejected.")

        # Save remark
        bid.remark = remark
        bid.save()

    return redirect("tenders:view_tender_bids", tender_id=bid.tender.id)
# View to display all bids across tenders for the logged-in user
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
    }

    return render(request, "myBiddsApplications.html", context)