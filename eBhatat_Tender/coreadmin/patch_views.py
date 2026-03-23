import os

views_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\views.py"
urls_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\urls.py"

with open(views_path, "r", encoding="utf-8") as f:
    v = f.read()

# 1. Add model
v = v.replace("from funding.models import Funding, FundingApplication", "from funding.models import Funding, FundingApplication\nfrom .models import ActionLog")

# 2. approve_user
replace_2 = """        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_APPROVAL",
            target_user=profile.user,
            description=f"Approved user {profile.user.username} with role {profile.get_role_display() or 'None'}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"User {profile.user.username} approved successfully.")
    return redirect('coreadmin:user_approvals')"""
v = v.replace("        messages.success(request, f\"User {profile.user.username} approved successfully.\")\n    return redirect('coreadmin:user_approvals')", replace_2)

# 3. reject_user
replace_3 = """        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_REJECTION",
            target_user=profile.user,
            description=f"Rejected user {profile.user.username}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"User {profile.user.username} rejected.")
    return redirect('coreadmin:user_approvals')"""
v = v.replace("        messages.warning(request, f\"User {profile.user.username} rejected.\")\n    return redirect('coreadmin:user_approvals')", replace_3)

# 4. approve dev request
replace_4 = """        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_APPROVAL",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Approved department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"Request for {admin_req.department_name} approved.")
    return redirect('coreadmin:admin_request_approvals')"""
v = v.replace("        messages.success(request, f\"Request for {admin_req.department_name} approved.\")\n    return redirect('coreadmin:admin_request_approvals')", replace_4)

# 5. reject dev request
replace_5 = """        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_REJECTION",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Rejected department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"Request for {admin_req.department_name} rejected.")
    return redirect('coreadmin:admin_request_approvals')"""
v = v.replace("        messages.warning(request, f\"Request for {admin_req.department_name} rejected.\")\n    return redirect('coreadmin:admin_request_approvals')", replace_5)

# 6. Add endpoints
endpoints = """
@login_required
def allocate_user_role(request, profile_id):
    if request.method == 'POST':
        from accounts.models import UserProfile
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
            
            from accounts.models import Notification
            Notification.objects.create(
                user=profile.user,
                message=f"Your account role has been updated to {new_role} by an Administrator."
            )
            from django.contrib import messages
            messages.success(request, f"Role updated successfully for {profile.user.username}.")
        else:
            from django.contrib import messages
            messages.error(request, "No valid role selected.")
    return redirect('coreadmin:user_list')

@login_required
def action_history(request):
    logs = ActionLog.objects.all().order_by('-timestamp')
    return render(request, 'action_history.html', {'logs': logs})
"""
v = v + "\n" + endpoints

with open(views_path, "w", encoding="utf-8") as f:
    f.write(v)

# URLs patch
with open(urls_path, "r", encoding="utf-8") as f:
    u = f.read()

urls_add = """
    # History & Roles
    path('history/', views.action_history, name='action_history'),
    path('allocate/user/<int:profile_id>/', views.allocate_user_role, name='allocate_user_role'),
"""
u = u.replace("    path('analytics/', views.analytics, name='analytics'),", urls_add + "\n    path('analytics/', views.analytics, name='analytics'),")

with open(urls_path, "w", encoding="utf-8") as f:
    f.write(u)

print("Views and URLs updated!")
