from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomLoginForm, CustomRegisterForm

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('blog_app:posts')
    else:
        form = CustomRegisterForm()
        
    return render(request, 'registration/register.html', {'form': form})
