from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Publication
from apps.users.models import Utilisateur
from .models import Publication, Citation
from .models import Publication, Citation, PublicationImage
from apps.recommendations.neo4j_queries import RecommendationEngine


def publication_list(request):
    """Liste de toutes les publications"""
    # This filters ONLY published
    publications = Publication.objects.filter(status='published').order_by('-publication_date', '-created_at')
    
    # User publications only if authenticated
    user_publications = Publication.objects.filter(main_author=request.user).order_by('-created_at') if request.user.is_authenticated else Publication.objects.none()

    recommended_publications = []
    if request.user.is_authenticated:
        try:
            engine = RecommendationEngine()
            recommended_ids = [rec['publication_id'] for rec in engine.recommend_publications(request.user.id)]
            
            # Fetch recommended publications from the database
            recommended_publications = Publication.objects.filter(id__in=recommended_ids)
            
        except Exception as e:
            messages.error(request, f"Could not retrieve recommendations: {e}")


    context = {
        'publications': publications,
        'user_publications': user_publications,
        'recommended_publications': recommended_publications,
    }
    return render(request, 'publications/list.html', context)

def publication_detail(request, pk):
    """Détails d'une publication - accessible à tous"""
    publication = get_object_or_404(Publication, pk=pk)
    
    # Increment view count
    publication.view_count += 1
    publication.save(update_fields=['view_count'])
    
    is_author = request.user.is_authenticated and publication.main_author == request.user
    is_coauthor = request.user.is_authenticated and request.user in publication.authors.all()
    
    # Get citations
    citations_made = publication.citations_made.select_related('cited_publication').all()
    citations_received = publication.citations_received.select_related('citing_publication').all()
    
    # Get images
    images = publication.images.all()
    
    # Process keywords
    publication.keyword_list = [kw.strip() for kw in publication.keywords.split(',') if kw.strip()] if publication.keywords else []

    # Get user recommendations
    recommended_users = []
    if request.user.is_authenticated:
        try:
            engine = RecommendationEngine()
            # Fetch user recommendations from Neo4j
            recommended_user_ids = [rec['user_id'] for rec in engine.recommend_users_for_publication(publication.id, request.user.id)]
            
            # Fetch recommended users from the database
            recommended_users = Utilisateur.objects.filter(id__in=recommended_user_ids)

        except Exception as e:
            messages.error(request, f"Could not retrieve user recommendations: {e}")

    # Get similar publications
    recommended_publications = []
    try:
        engine = RecommendationEngine()
        # Fetch similar publications from Neo4j
        recommended_ids = [rec['publication_id'] for rec in engine.recommend_similar_publications(publication.id, limit=3)]
        
        # Fetch recommended publications from the database
        recommended_publications = Publication.objects.filter(id__in=recommended_ids)

    except Exception as e:
        messages.error(request, f"Could not retrieve publication recommendations: {e}")
    
    context = {
        'publication': publication,
        'is_author': is_author,
        'is_coauthor': is_coauthor,
        'citations_made': citations_made,
        'citations_received': citations_received,
        'images': images,
        'recommended_users': recommended_users,
        'recommended_publications': recommended_publications,
    }
    return render(request, 'publications/detail.html', context)


@login_required
def add_images(request, pk):
    """Add images to a publication"""
    publication = get_object_or_404(Publication, pk=pk)
    
    is_author = publication.main_author == request.user
    is_coauthor = request.user in publication.authors.all()
    
    if not (is_author or is_coauthor):
        messages.error(request, 'Seuls les auteurs peuvent ajouter des images.')
        return redirect('publications:detail', pk=pk)
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        captions = request.POST.getlist('captions')
        
        if not images:
            messages.error(request, 'Veuillez sélectionner au moins une image.')
            return redirect('publications:add_images', pk=pk)
        
        # Get current max order
        max_order = publication.images.count()
        
        for idx, image in enumerate(images):
            caption = captions[idx] if idx < len(captions) else ''
            PublicationImage.objects.create(
                publication=publication,
                image=image,
                caption=caption,
                order=max_order + idx
            )
        
        messages.success(request, f'{len(images)} image(s) ajoutée(s) avec succès!')
        return redirect('publications:detail', pk=pk)
    
    context = {
        'publication': publication,
    }
    return render(request, 'publications/add_images.html', context)


@login_required
def delete_image(request, pk, image_id):
    """Delete an image from publication"""
    publication = get_object_or_404(Publication, pk=pk)
    image = get_object_or_404(PublicationImage, id=image_id, publication=publication)
    
    is_author = publication.main_author == request.user
    is_coauthor = request.user in publication.authors.all()
    
    if not (is_author or is_coauthor):
        messages.error(request, 'Permission refusée.')
        return redirect('publications:detail', pk=pk)
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image supprimée.')
        return redirect('publications:detail', pk=pk)
    
    context = {
        'publication': publication,
        'image': image,
    }
    return render(request, 'publications/delete_image_confirm.html', context)

@login_required
def publication_create(request):
    """Créer une nouvelle publication"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        abstract = request.POST.get('abstract', '').strip()
        publication_type = request.POST.get('publication_type', 'article')
        status = request.POST.get('status', 'draft')
        journal = request.POST.get('journal', '').strip()
        publisher = request.POST.get('publisher', '').strip()
        publication_date_str = request.POST.get('publication_date')
        publication_date = None
        if publication_date_str:
            try:
                publication_date = date.fromisoformat(publication_date_str)
            except ValueError:
                messages.error(request, "Invalid date format for publication date. Please use YYYY-MM-DD.")
                return render(request, 'publications/create.html')
        
        doi = request.POST.get('doi', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        keywords = request.POST.get('keywords', '').strip()
        
        if not title:
            messages.error(request, 'Le titre est requis.')
            return render(request, 'publications/create.html')
        
        publication = Publication.objects.create(
            title=title,
            abstract=abstract,
            main_author=request.user,
            publication_type=publication_type,
            status=status,
            journal=journal,
            publisher=publisher,
            publication_date=publication_date,
            doi=doi,
            isbn=isbn,
            keywords=keywords,
        )
        
        # Add main author to authors
        publication.authors.add(request.user)
        
        # Handle cover image
        if 'cover_image' in request.FILES:
            publication.cover_image = request.FILES['cover_image']
        
        # Handle document
        if 'document' in request.FILES:
            publication.document = request.FILES['document']
        
        publication.save()
        
        # Handle additional images
        images = request.FILES.getlist('images')
        if images:
            for idx, image in enumerate(images):
                PublicationImage.objects.create(
                    publication=publication,
                    image=image,
                    order=idx
                )
        
        if status == 'published':
            messages.success(request, 'Publication publiée avec succès!')
        else:
            messages.success(request, 'Publication créée en tant que brouillon.')
        
        return redirect('publications:detail', pk=publication.pk)
    
    return render(request, 'publications/create.html')

@login_required
def publication_edit(request, pk):
    """Modifier une publication"""
    publication = get_object_or_404(Publication, pk=pk)
    
    if publication.main_author != request.user:
        messages.error(request, 'Vous ne pouvez modifier que vos propres publications.')
        return redirect('publications:detail', pk=publication.pk)
    
    if request.method == 'POST':
        publication.title = request.POST.get('title', '').strip()
        publication.abstract = request.POST.get('abstract', '').strip()
        publication.publication_type = request.POST.get('publication_type', 'article')
        publication.status = request.POST.get('status', 'draft')
        publication.journal = request.POST.get('journal', '').strip()
        publication.publisher = request.POST.get('publisher', '').strip()
        publication_date_str = request.POST.get('publication_date')
        if publication_date_str:
            try:
                publication.publication_date = date.fromisoformat(publication_date_str)
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD. Publication date was not updated.")
        else:
            publication.publication_date = None
        
        publication.doi = request.POST.get('doi', '').strip()
        publication.isbn = request.POST.get('isbn', '').strip()
        publication.keywords = request.POST.get('keywords', '').strip()
        
        if 'document' in request.FILES:
            publication.document = request.FILES['document']
        if 'cover_image' in request.FILES:
            publication.cover_image = request.FILES['cover_image']
        
        publication.save()
        
        messages.success(request, 'Publication mise à jour avec succès!')
        return redirect('publications:detail', pk=publication.pk)
    
    context = {
        'publication': publication,
    }
    return render(request, 'publications/edit.html', context)


@login_required
def publication_delete(request, pk):
    """Supprimer une publication"""
    publication = get_object_or_404(Publication, pk=pk)
    
    if publication.main_author != request.user:
        messages.error(request, 'Vous ne pouvez supprimer que vos propres publications.')
        return redirect('publications:detail', pk=publication.pk)
    
    if request.method == 'POST':
        publication.delete()
        messages.success(request, 'Publication supprimée avec succès!')
        return redirect('publications:list')
    
    context = {
        'publication': publication,
    }
    return render(request, 'publications/delete.html', context)


@login_required
def add_citation(request, pk):
    """Add a citation to a publication"""
    publication = get_object_or_404(Publication, pk=pk)
    
    # Check if user is author
    is_author = publication.main_author == request.user
    is_coauthor = request.user in publication.authors.all()
    
    if not (is_author or is_coauthor):
        messages.error(request, 'Seuls les auteurs peuvent ajouter des citations.')
        return redirect('publications:detail', pk=pk)
    
    if request.method == 'POST':
        cited_pub_id = request.POST.get('cited_publication')
        citation_text = request.POST.get('citation_text', '').strip()
        
        if not cited_pub_id:
            messages.error(request, 'Veuillez sélectionner une publication à citer.')
            return redirect('publications:add_citation', pk=pk)
        
        try:
            cited_pub = Publication.objects.get(id=cited_pub_id, status='published')
        except Publication.DoesNotExist:
            messages.error(request, 'Publication non trouvée.')
            return redirect('publications:add_citation', pk=pk)
        
        # Check if citation already exists
        if Citation.objects.filter(citing_publication=publication, cited_publication=cited_pub).exists():
            messages.error(request, 'Cette publication est déjà citée.')
            return redirect('publications:add_citation', pk=pk)
        
        # Create citation
        Citation.objects.create(
            citing_publication=publication,
            cited_publication=cited_pub,
            citation_text=citation_text
        )
        
        # Update citation count
        cited_pub.citation_count += 1
        cited_pub.save()
        
        messages.success(request, f'Citation ajoutée: {cited_pub.title}')
        return redirect('publications:detail', pk=pk)
    
    # Get all published publications except current one
    available_pubs = Publication.objects.filter(
        status='published'
    ).exclude(id=pk).order_by('-publication_date', '-created_at')
    
    # Get already cited publications
    cited_ids = Citation.objects.filter(
        citing_publication=publication
    ).values_list('cited_publication_id', flat=True)
    
    context = {
        'publication': publication,
        'available_publications': available_pubs,
        'cited_ids': list(cited_ids),
    }
    return render(request, 'publications/add_citation.html', context)


@login_required
def remove_citation(request, pk, citation_id):
    """Remove a citation"""
    publication = get_object_or_404(Publication, pk=pk)
    citation = get_object_or_404(Citation, id=citation_id, citing_publication=publication)
    
    is_author = publication.main_author == request.user
    is_coauthor = request.user in publication.authors.all()
    
    if not (is_author or is_coauthor):
        messages.error(request, 'Permission refusée.')
        return redirect('publications:detail', pk=pk)
    
    if request.method == 'POST':
        cited_pub = citation.cited_publication
        citation.delete()
        
        # Update citation count
        cited_pub.citation_count = max(0, cited_pub.citation_count - 1)
        cited_pub.save()
        
        messages.success(request, 'Citation supprimée.')
        return redirect('publications:detail', pk=pk)
    
    context = {
        'publication': publication,
        'citation': citation,
    }
    return render(request, 'publications/remove_citation_confirm.html', context)