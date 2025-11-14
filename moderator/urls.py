from django.urls import path
from . import views

app_name = 'moderator'

urlpatterns = [
    path('', views.moderator_dashboard, name='moderator_dashboard'),
    path('pending/', views.pending_listings, name='pending_listings'),
    path('approved/', views.approved_listings, name='approved_listings'),
    path('rejected/', views.rejected_listings, name='rejected_listings'),
    path('approve/<int:product_id>/', views.approve_listing, name='approve_listing'),
    path('reject/<int:product_id>/', views.reject_listing, name='reject_listing'),
    path('listing/<int:product_id>/', views.listing_detail, name='listing_detail'),
]
