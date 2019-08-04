from django.shortcuts import render
from django.conf import settings
from django.http import Http404
from django.db.models import Q


def index(request):
    return render(request, 'index.html')
