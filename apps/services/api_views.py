from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Service
from apps.professionals.models import ProviderProfile

class APICategoriesView(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        data = [{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'description': c.description,
            'icon_name': c.icon_name,
            'image': c.image.url if c.image else None,
            'services_count': c.services.filter(is_active=True).count()
        } for c in categories]
        return Response(data)

class APIServicesView(APIView):
    def get(self, request):
        category_slug = request.GET.get('category')
        services = Service.objects.filter(is_active=True)
        if category_slug:
            services = services.filter(category__slug=category_slug)
        data = [{
            'id': s.id,
            'name': s.name,
            'slug': s.slug,
            'category': s.category.name,
            'short_description': s.short_description,
            'base_price': str(s.base_price),
            'pricing_type': s.pricing_type,
            'estimated_duration_minutes': s.estimated_duration_minutes,
            'is_emergency_eligible': s.is_emergency_eligible,
            'image': s.image.url if s.image else None
        } for s in services]
        return Response(data)
