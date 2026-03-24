from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Funding, FundingApplication
from tenders.models import Tenderss
from django.db.models import Sum
from accounts.utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site

@login_required
def apply_funding(request, funding_id, tender_id):
    funding = get_object_or_404(Funding, id=funding_id)
    tender = get_object_or_404(Tenderss, id=tender_id)
    
    # Check if already applied
    if FundingApplication.objects.filter(bidder=request.user, funding=funding, tender=tender).exists():
        messages.info(request, "You have already applied for this funding.")
        return redirect('tenders:tenderDetails', tender_id=tender.id)

    if request.method == "POST":
        try:
            amount = request.POST.get('amount_requested')
            purpose = request.POST.get('purpose')
            document = request.FILES.get('supporting_document')
            
            if not amount or not purpose or not document:
                messages.error(request, "All fields are required.")
                return render(request, 'funding/apply_funding.html', {'funding': funding, 'tender': tender})

            FundingApplication.objects.create(
                bidder=request.user,
                funding=funding,
                tender=tender,
                amount_requested=amount,
                purpose=purpose,
                supporting_document=document
            )

            # 📧 Send Funding Application Confirmation Email
            try:
                current_site = get_current_site(request)
                send_ebharat_email(
                    subject=f"Funding Request Confirmation - {funding.title}",
                    template_name="funding_application_confirmation.html",
                    context={
                        "bidder_name": request.user.first_name or request.user.username,
                        "funding_title": funding.title,
                        "tender_title": tender.title,
                        "amount_requested": amount,
                        "purpose": purpose,
                        "domain": current_site.domain,
                    },
                    recipient_list=[request.user.email]
                )
            except Exception as e:
                print(f"Funding Email failed: {e}")

            messages.success(request, "Funding application submitted successfully!")
            return redirect('public:tenders')

        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
            return render(request, 'funding/apply_funding.html', {'funding': funding, 'tender': tender})


    return render(request, 'funding/apply_funding.html', {'funding': funding, 'tender': tender})

@login_required
def my_funding_requests(request):
    applications = FundingApplication.objects.filter(bidder=request.user).order_by('-applied_at')
    
    wallet_balance = applications.filter(status='approved').aggregate(
        total=Sum('amount_requested'))['total'] or 0
        
    pending_amount = applications.filter(status='pending').aggregate(
        total=Sum('amount_requested'))['total'] or 0

    return render(request, 'funding/my_funding_requests.html', {
        'applications': applications,
        'wallet_balance': wallet_balance,
        'pending_amount': pending_amount
    })
