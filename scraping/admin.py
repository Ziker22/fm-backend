from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import ScrapedPlace, ScrapedPost

@admin.register(ScrapedPost)
class ScrapedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'third_party_type', 'probability')
    search_fields = ('title', 'content')

class ScrapedPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'processed')
    ordering = ('name',)
    list_filter = ('processed',)
    search_fields = ('name',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['review_button_html'] = format_html(
            '<a href="{}" class="button">Review Places</a>',
            reverse("admin:scraping_scrapedplace_review")
        )
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('review/', self.admin_site.admin_view(self.review_view), name='scraping_scrapedplace_review'),
            path('mark_processed/<int:place_id>/', self.admin_site.admin_view(self.mark_processed), name='scraping_scrapedplace_mark_processed'),
        ]
        return custom_urls + urls

    def review_view(self, request):
        """View to review ScrapedPlace entries one by one"""
        # Get the first unprocessed ScrapedPlace
        place = ScrapedPlace.objects.filter(processed=False).order_by("name").first()
        if not place:
            self.message_user(request, "No unprocessed places found.")
            return HttpResponseRedirect(reverse('admin:scraping_scrapedplace_changelist'))

        context = {
            'place': place,
            'post': place.post,
            'opts': self.model._meta,
            'title': 'Review Scraped Place',
            'app_label': self.model._meta.app_label,
            'original': place,
            'has_view_permission': self.has_view_permission(request, place),
        }

        return TemplateResponse(request, 'admin/scraping/scrapedplace/review.html', context)

    def mark_processed(self, request, place_id):
        """Mark a ScrapedPlace as processed and redirect to the next one"""
        place = get_object_or_404(ScrapedPlace, id=place_id)
        place.processed = True
        place.save()

        self.message_user(request, f"Place '{place.name}' marked as processed.")
        return HttpResponseRedirect(reverse('admin:scraping_scrapedplace_review'))

admin.site.register(ScrapedPlace, ScrapedPlaceAdmin)
