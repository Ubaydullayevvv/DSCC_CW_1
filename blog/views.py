from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def home(request: HttpRequest) -> HttpResponse:
    """Render a placeholder landing page for the blog."""
    return render(request, 'blog/home.html')
