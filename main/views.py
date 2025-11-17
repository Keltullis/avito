from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, FormView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Category, Product, Size, BlogPost
from .forms import ContactForm
from django.db.models import Q
from moderator.models import ModerationStatus
from django.contrib import messages
from django.core.paginator import Paginator


class IndexView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)

    

class CatalogView(TemplateView):
    template_name = 'main/base.html'

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__icontains=value),
        'size': lambda queryset, value: queryset.filter(product_sizes__size__name=value),
        'material': lambda queryset, value: queryset.filter(material__icontains=value),
        'brand': lambda queryset, value: queryset.filter(brand__icontains=value),
        'condition': lambda queryset, value: queryset.filter(condition=value),
        'category': lambda queryset, value: queryset.filter(category__slug=value),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        
        products = Product.objects.filter(
            is_active=True,
            moderation__status=ModerationStatus.APPROVED
        ).order_by('-created_at')
        
        current_category = None
        current_category_name = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)
            current_category_name = current_category.name

        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                if param == 'category' and category_slug:
                    filter_params[param] = value
                    continue
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''

        filter_params['q'] = query or ''

        context.update({
            'categories': categories,
            'products': products,
            'current_category': category_slug,
            'current_category_name': current_category_name,
            'filter_params': filter_params,
            'sizes': Size.objects.all(),
            'search_query': query or ''
        })

        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True
        
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            if context.get('show_search'):
                return TemplateResponse(request, 'main/search_input.html', context)
            elif context.get('reset_search'):
                return TemplateResponse(request, 'main/search_button.html', {})
            template = 'main/filter_modal.html' if request.GET.get('show_filters') == 'true' else (
                'main/main_catalog_content.html' if not context['current_category'] else 'main/catalog_content.html'
            )
            return TemplateResponse(request, template, context)
        if context['current_category']:
            return TemplateResponse(request, 'main/catalog.html', context)
        return TemplateResponse(request, 'main/main_catalog.html', context)
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True,
            moderation__status=ModerationStatus.APPROVED
        ).exclude(id=product.id)[:4]
        
        context['related_products'] = related_products
        context['current_category'] = product.category.slug
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_detail_content.html', context)
        return TemplateResponse(request, 'main/product_detail.html', context)


class AboutView(TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/about_content.html', context)
        return TemplateResponse(request, self.template_name, context)


class BlogView(TemplateView):
    template_name = 'main/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        
        # Get published blog posts
        posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(posts, 6)  # 6 posts per page
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['posts'] = page_obj
        context['paginator'] = paginator
        
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            # If requesting a specific post modal
            if request.GET.get('post_slug'):
                post_slug = request.GET.get('post_slug')
                post = get_object_or_404(BlogPost, slug=post_slug, is_published=True)
                return TemplateResponse(request, 'main/blog_post_modal.html', {'post': post})
            return TemplateResponse(request, 'main/blog_content.html', context)
        return TemplateResponse(request, self.template_name, context)


class ContactView(FormView):
    template_name = 'main/contact_us.html'
    form_class = ContactForm
    success_url = '/contact/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        return context

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('HX-Request'):
            return TemplateResponse(
                self.request, 
                'main/contact_success.html',
                {'categories': Category.objects.all()}
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.request.headers.get('HX-Request'):
            return TemplateResponse(self.request, 'main/contact_form.html', context)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/contact_content.html', context)
        return TemplateResponse(request, self.template_name, context)
