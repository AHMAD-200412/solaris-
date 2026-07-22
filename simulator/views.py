
from django.shortcuts import render, redirect
# Create your views here.
def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == "company":
            return redirect("/dashboard/company/")
        return redirect("/user/home/")

    return render(request, "home.html")