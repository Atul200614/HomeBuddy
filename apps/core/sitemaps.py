from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.services.models import Category, Service


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'core:faq', 'core:contact',
                'core:terms', 'core:privacy', 'services:list']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('services:category_detail', args=[obj.slug])


class ServiceSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('services:detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.created_at if hasattr(obj, 'created_at') else None
