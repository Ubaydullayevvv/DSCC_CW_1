from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


def index(request: HttpRequest) -> HttpResponse:
    """Landing page for /users/ with helpful navigation."""
    return render(request, 'users/index.html')


def register(request: HttpRequest) -> HttpResponse:
    """Allow visitors to create an account."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('users:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """Authenticate a user via username and password."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('users:dashboard')
    else:
        form = AuthenticationForm(request)
    return render(request, 'users/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Log out the current user."""
    auth_logout(request)
    return redirect('/')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Simple protected dashboard stub."""
    return render(request, 'users/dashboard.html')
