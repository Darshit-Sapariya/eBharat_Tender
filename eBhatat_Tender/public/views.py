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


# Create your views here.
def index(request):
    return render(request, 'index.html')
def funding(request):
    return render(request, 'funding.html')
def workflow(request):
    return render(request, 'workflow.html')
def guidelines(request):
    return render(request, 'guidelines.html')


# =======================
# TENDERS VIEW
# =======================
def tenders(request):

    search_query = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    tenders = Tenderss.objects.all()

    # Search filter
    if search_query:
        tenders = tenders.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Category filter
    if category and category != "all":
        tenders = tenders.filter(category__iexact=category)

    tenders = tenders.order_by('-created_at')

    context = {
        'tenders': tenders,
        'search_query': search_query,
        'selected_category': category,
    }

    return render(request, 'tenders.html', context)
# =======================
# TENDER DETAIL VIEW
# =======================
@login_required
def tenderDetails(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    applications = tender.applications.all()

    return render(request, "tenderDetails.html", {
        "tender": tender,
        "applications": applications
    })




