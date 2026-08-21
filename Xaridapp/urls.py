from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Mahsulotning batafsil sahifasi
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'), 
    
    path('login/', views.custom_login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Savat va buyurtma yo'llari
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),  # Takrorlanadigani olib tashlandi, nomi cart_view qilindi
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.payment_page_view, name='payment_page'), # <-- Bu ham kerak bo'ladi
# Bosh sahifa (agar sizda nomi boshqacha bo'lsa, o'sha funksiya nomini yozing)
    path('', views.index, name='index'), 
    
    # Qidiruv sahifasi xatolikni yo'qotadigan asosiy qator:
    path('search/', views.search_view, name='search'),
    
    # To'lov sahifasi
    path('payment/<int:order_id>/', views.payment_page_view, name='payment_page'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('add-to-favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path("addresses/", views.addresses, name="addresses"),
    path("payment/", views.payment, name="payment"),
    path("notifications/", views.notifications, name="notifications"),
    path("help-center/", views.help_center, name="help_center"),
    path("returns/", views.returns, name="returns"),
    path('payment-methods/',views.payment_methods,name='payment_methods'),
    path("buyurtmalar/",views.orders,name="buyurtmalar"),
    path('buyurtmalar/<int:pk>/', views.order_detail, name='buyurtmalar_detail'),
]