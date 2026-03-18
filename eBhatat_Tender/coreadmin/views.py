from django.shortcuts import render

# Create your views here.
def coreadmin_dashboard(request):
    return render(request, 'coreadmin_base.html')