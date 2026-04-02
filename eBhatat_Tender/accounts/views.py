from django.contrib import messages
from django.shortcuts import redirect, render
from accounts.models import UserProfile, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from .utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site

# ==============================================================================
# AUTHENTICATION & NOTIFICATION VIEWS
# ==============================================================================

# View for user login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("password")

        # Allow login with email as well
        if username and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("coreadmin:deshbord")
            return redirect("public:home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("accounts:login")
    return render(request, "login.html")

# Mark notifications as read
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Clear all user notifications
@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

# View history of notifications
@login_required
def view_all_notifications(request):
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "all_notifications.html", {"all_notifications": all_notifications})


# ==============================================================================
# PROFILE MANAGEMENT VIEWS
# ==============================================================================

# Update role-based profile details
@login_required
def updateProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Note: Sensitive fields like gov_id_number are masked in templates 
    # using the profile.masked_id property for security.

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

        if not profile.role:
            role = request.POST.get("role")
            if role:
                profile.role = role

        profile.save()
        messages.success(request, "Profile Updated Successfully.")
        return redirect("accounts:updateProfile")

    if profile.role == 'bidder':
        return redirect("bids:vendor_profile_update")
    elif profile.role == 'creator':
        return redirect("tenders:updateProfile")
    
    # Fallback if no role is set yet
    template_name = 'vendorsProfileupdate.html' if profile.role == 'creator' else 'bidersProfileupdate.html'
    return render(request, template_name, {'profile': profile})

# View for user logout
def logout_view(request):
    logout(request)
    return redirect("accounts:login")
# =======================
# PROFILE VIEW
# =======================
# Manage personal KYC profile
@login_required
def my_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 🚩 Mandatory Onboarding Check (skip for superusers)
    if not request.user.is_superuser:
        if not profile.mobile or not profile.address or not profile.role:
            return redirect('accounts:complete_profile')

    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile.gov_id_type = request.POST.get('gov_id_type')
        profile.gov_id_number = request.POST.get('gov_id_number')

        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES.get('profile_pic')

        if request.FILES.get('gov_id_upload'):
            profile.gov_id_upload = request.FILES.get('gov_id_upload')

        # 🔒 Lock role after first selection
        if not profile.role:
            profile.role = request.POST.get('role')

        profile.status = "pending"
        profile.save()

        return redirect('accounts:myprofile')   # stay on profile until approved

    # 🔹 After admin approval → auto redirect
    if profile.status == "approved":
        if profile.role == "creator":
            return redirect("tenders:dashboard")
        elif profile.role == "bidder":
            return redirect("bids:bids_dashboard")

    return render(request, "myprofile.html", {"profile": profile})

@login_required
def complete_profile(request):
    if request.user.is_superuser:
        return redirect('coreadmin:base')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # If already completed, don't show this page again
    if profile.mobile and profile.address and profile.role:
        return redirect('accounts:myprofile')
        
    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.role = request.POST.get('role')
        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile.gov_id_type = request.POST.get('gov_id_type')
        profile.gov_id_number = request.POST.get('gov_id_number')
        
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES.get('profile_pic')
            
        if request.FILES.get('gov_id_upload'):
            profile.gov_id_upload = request.FILES.get('gov_id_upload')
            
        profile.status = 'pending'
        profile.save()

        # Update username if changed
        new_username = request.POST.get('username')
        if new_username and new_username != request.user.username:
            if not User.objects.filter(username=new_username).exists():
                request.user.username = new_username
                request.user.save()
            else:
                messages.error(request, f"Username '{new_username}' is already taken.")
                return redirect('accounts:complete_profile')
        
        # Add password if user doesn't have a usable one (e.g. from Google login)
        if not request.user.has_usable_password():
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and confirm_password:
                if password == confirm_password:
                    request.user.set_password(password)
                    request.user.save()
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, request.user)
                else:
                    messages.error(request, "Passwords do not match.")
                    return redirect('accounts:complete_profile')

        messages.success(request, "Profile submitted for verification!")
        return redirect('accounts:myprofile')
        
    return render(request, "complete_profile.html", {"profile": profile})

# ==============================================================================
# REGISTRATION VIEWS
# ==============================================================================
# View for user registration
def check_username(request):
    username = request.GET.get('username', None)
    if username:
        taken = User.objects.filter(username=username).exists()
        return JsonResponse({'taken': taken})
    return JsonResponse({'taken': False})

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        # Email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # 🔹 Update auto-created profile with registration data
        profile = user.userprofile
        profile.full_name = full_name
        profile.mobile = mobile
        profile.save()

        user.save()

        # 📧 Send Welcome Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Welcome to eBharat Tender Portal",
                template_name="welcome_email.html",
                context={
                    "full_name": full_name,
                    "username": username,
                    "email": email,
                    "mobile": mobile,
                    "domain": current_site.domain,
                },
                recipient_list=[email]
            )
        except Exception as e:
            # Log error but don't break registration
            print(f"Email failed: {e}")

        return redirect("accounts:login")

    return render(request, "register.html")