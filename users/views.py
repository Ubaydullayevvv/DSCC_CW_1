from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(request: HttpRequest) -> HttpResponse:
    """Placeholder landing page for the users app."""
    return render(request, 'users/index.html')
