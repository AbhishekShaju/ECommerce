from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),  # The contact URL path
    path('profile/', views.profile, name='profile'),  # Profile page route
    path('index/', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:category_id>/', views.product_list, name='product_list_category'),  # This pattern should match
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_item, name='remove_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_success', views.order_success, name='order_success'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('orders/', views.order_list, name='orders'),

  
]
