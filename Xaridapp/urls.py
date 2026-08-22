from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("product/<int:pk>/", views.product_detail_view, name="product_detail"),

    path("login/", views.custom_login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/update/<int:product_id>/<str:action>/", views.update_cart, name="update_cart"),

    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/<int:order_id>/", views.payment_page_view, name="payment_page"),
    path("payment/success/<int:order_id>/", views.payment_success, name="payment_success"),
    path("payment/", views.payment, name="payment"),
    path("payment-methods/", views.payment_methods, name="payment_methods"),

    path("search/", views.search_view, name="search"),

    path("add-to-favorites/<int:product_id>/", views.add_to_favorites, name="add_to_favorites"),
    path("favorites/", views.favorites_view, name="favorites"),

    path("addresses/", views.addresses, name="addresses"),
    path("notifications/", views.notifications, name="notifications"),
    path("help-center/", views.help_center, name="help_center"),
    path("returns/", views.returns, name="returns"),

    path("buyurtmalar/", views.orders, name="buyurtmalar"),
    path("buyurtmalar/<int:pk>/", views.order_detail, name="buyurtmalar_detail"),
    path("create-order/", views.create_order, name="create_order"),

    path("admin-panel/login/", views.admin_login, name="admin_login"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/logout/", views.admin_logout, name="admin_logout"),
    path("admin-panel/orders/", views.admin_orders, name="admin_orders"),
    path("admin-panel/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("orders/", views.orders, name="orders"),
    path("admin-panel/orders/",views.admin_orders,name="admin_orders"),
    path("admin-panel/orders/status/<int:order_id>/",views.order_status_update,name="order_status_update"),
]