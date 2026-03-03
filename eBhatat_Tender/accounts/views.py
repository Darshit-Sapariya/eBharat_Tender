from pyexpat.errors import messages
from django.shortcuts import redirect, render
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.

# =======================
# bidder profile update view
# =======================
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
        return redirect("accounts:updateProfile")   # reload page after save

    return render(request, 'bidersProfileupdate.html')

# =======================
# tender creation & management views
# =======================
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
        return redirect("accounts:updatemyprofile")   # reload page after save

    return render(request, 'vendorsProfileupdate.html')

# =======================
# LOGIN & LOGOUT VIEWS
# =======================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("public:home")  # create dashboard page
        else:
            return redirect("accounts:login")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("accounts:login")
# =======================
# PROFILE VIEW
# =======================
@login_required
def my_profile(request):
    profile = request.user.userprofile
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
            return redirect("tenders:dashboard") # replace with actual redirect

        elif profile.role == "bidder":
            return redirect("bids:bidsdeshboard")  # replace with actual redirect

    return render(request, "myprofile.html", {"profile": profile})

# =======================
# REGISTRATION VIEW
# =======================
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

        user.save()
        return redirect("accounts:login")

    return render(request, "register.html")