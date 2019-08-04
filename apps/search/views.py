from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from django.http import Http404
from django.db.models import Q

from . import models


@require_POST
def search(request):
    print(request)
    search_input = request.POST.get('search-input') or ''
    try:
        search_page = max(0, int(request.POST.get('search-page')))
    except Exception as e:
        search_page = 0
    search_limit = 20
    search_scope_left = search_page*search_limit
    search_scope_right = (search_page+1)*search_limit
    results = models.Item.objects.filter(Q(title__icontains=search_input)).all()[search_scope_left:search_scope_right]
    context = {
        'search_input': search_input,
        'search_page': search_page,
        'results': results,
    }
    return render(request, 'search/search.html', context=context)
