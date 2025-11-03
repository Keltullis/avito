from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('account-details/', views.account_details, name='account_details'),
    path('edit-account-details/', views.edit_account_details, name='edit_account_details'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    path('logout/', views.logout_view, name='logout'),
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<slug:product_slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/check/<slug:product_slug>/', views.check_wishlist_status, name='check_wishlist_status'),
    path('create-listing/', views.create_listing_view, name='create_listing'),
    path('my-listings/', views.my_listings_view, name='my_listings'),
    path('listing/delete/<int:product_id>/', views.delete_listing, name='delete_listing'),
    path('listing/toggle/<int:product_id>/', views.toggle_listing_status, name='toggle_listing_status'),
]
