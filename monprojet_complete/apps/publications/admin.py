from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Publication, Citation, PublicationImage


@admin.register(Publication)
class PublicationAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'main_author', 'publication_type', 'status', 'publication_date', 'view_count']
    list_filter = ['publication_type', 'status', 'publication_date']
    search_fields = ['title', 'abstract', 'journal', 'keywords']
    filter_horizontal = ['authors']
    date_hierarchy = 'publication_date'
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'citation_count']

@admin.register(Citation)
class CitationAdmin(SimpleHistoryAdmin):
    list_display = ('citing_publication', 'cited_publication', 'created_at')
    search_fields = ('citing_publication__title', 'cited_publication__title')
    autocomplete_fields = ('citing_publication', 'cited_publication')

@admin.register(PublicationImage)
class PublicationImageAdmin(SimpleHistoryAdmin):
    list_display = ('publication', 'caption', 'order', 'uploaded_at')
    search_fields = ('publication__title', 'caption')
    autocomplete_fields = ('publication',)
