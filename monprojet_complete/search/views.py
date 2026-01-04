from django.db.models import Q
from django.contrib.auth import get_user_model
from apps.groups.models import Groupe
from apps.publications.models import Publication
from django.shortcuts import render

User = get_user_model()


def search_results(request):
    """Search for users, publications, and groups - accessible to everyone"""
    query = request.GET.get('q', '').strip()
    users = User.objects.none()
    publications = Publication.objects.none()
    groups = Groupe.objects.none()

    if query:
        # Search users
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(institution__icontains=query) |
            Q(bio__icontains=query)
        ).distinct()
        
        # Search publications
        publications = Publication.objects.filter(
            Q(title__icontains=query) |
            Q(abstract__icontains=query) |
            Q(keywords__icontains=query) |
            Q(journal__icontains=query) |
            Q(publisher__icontains=query) |
            Q(doi__icontains=query) |
            Q(authors__username__icontains=query) |
            Q(authors__first_name__icontains=query) |
            Q(authors__last_name__icontains=query),
            status='published'
        ).distinct()
        
        # Process keywords for each publication
        publications_with_keywords = []
        for pub in publications:
            pub.keyword_list = [kw.strip() for kw in pub.keywords.split(',') if kw.strip()] if pub.keywords else []
            publications_with_keywords.append(pub)
        publications = publications_with_keywords
        
        # Search groups
        groups = Groupe.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'users': users,
        'publications': publications,
        'groups': groups,
    }
    return render(request, 'search/results.html', context)
