from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from .models import Product, Order, Notification
from .forms import SignUpForm, CustomLoginForm


# ============================================================
# BOSH SAHIFA
# ============================================================

def index(request):
    category_slug = request.GET.get("category")

    if category_slug:
        products = Product.objects.filter(
            category__slug=category_slug
        )
    else:
        products = Product.objects.all()

    return render(
        request,
        "Xaridapp/index.html",
        {
            "products": products
        }
    )


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "Xaridapp/product_detail.html",
        {
            "product": product
        }
    )


# ============================================================
# SIGN UP
# ============================================================

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("index")
    else:
        form = SignUpForm()

    return render(
        request,
        "Xaridapp/signup.html",
        {
            "form": form
        }
    )


# ============================================================
# LOGIN
# ============================================================

def custom_login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("index")
    else:
        form = CustomLoginForm()

    return render(
        request,
        "Xaridapp/login.html",
        {
            "form": form
        }
    )


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile_view(request):
    return render(
        request,
        "Xaridapp/profile.html"
    )


# ============================================================
# EDIT PROFILE
# ============================================================

@login_required
def edit_profile(request):
    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        request.user.username = username
        request.user.email = email

        request.user.save()

        return redirect("profile")

    return render(
        request,
        "Xaridapp/edit_profile.html"
    )


# ============================================================
# ADD TO CART
# ============================================================

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart
    request.session.modified = True

    Notification.objects.create(
        user=request.user,
        title="Savatga qo‘shildi 🛒",
        message=f"{product.name} savatingizga qo‘shildi.",
        notification_type="cart"
    )

    return redirect("index")


# ============================================================
# CART
# ============================================================

@login_required
def cart_view(request):

    cart = request.session.get(
        "cart",
        {}
    )

    products_in_cart = []
    total_price = 0

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(
                id=int(product_id)
            )

            subtotal = product.price * quantity
            total_price += subtotal

            products_in_cart.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

        except Product.DoesNotExist:
            pass

    return render(
        request,
        "Xaridapp/cart.html",
        {
            "items": products_in_cart,
            "total_price": total_price
        }
    )


# ============================================================
# UPDATE CART
# ============================================================

@login_required
def update_cart(request, product_id, action):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        if action == "increase":
            cart[product_id] += 1

        elif action == "decrease":

            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]

        elif action == "remove":
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart_view")


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout_view(request):

    cart = request.session.get(
        "cart",
        {}
    )

    if not cart:
        return redirect("cart_view")

    total_price = 0

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(
                id=int(product_id)
            )

            total_price += product.price * quantity

        except Product.DoesNotExist:
            pass

    if request.method == "POST":

        mijoz_nomi = request.POST.get(
            "customer_name",
            ""
        ).strip()

        telefon_raqami = request.POST.get(
            "phone_number",
            ""
        ).strip()

        manzil = request.POST.get(
            "address",
            ""
        ).strip()

        if not mijoz_nomi or not telefon_raqami or not manzil:

            return render(
                request,
                "Xaridapp/checkout.html",
                {
                    "total_price": total_price,
                    "error": "Iltimos, barcha ma'lumotlarni to'ldiring."
                }
            )

        order = Order.objects.create(
            user=request.user,
            mijoz_nomi=mijoz_nomi,
            telefon_raqami=telefon_raqami,
            manzil=manzil,
            umumiy_narx=total_price,
            maqom="To'lov kutilmoqda"
        )

        request.session["cart"] = {}
        request.session.modified = True

        return redirect(
            "payment_page",
            order_id=order.id
        )

    return render(
        request,
        "Xaridapp/checkout.html",
        {
            "total_price": total_price
        }
    )


# ============================================================
# PAYMENT PAGE
# ============================================================

@login_required
def payment_page_view(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "Xaridapp/payment.html",
        {
            "order": order,
            "card_number": "7777 0122 2402 7152",
            "card_holder": "AZIMJON J."
        }
    )


# ============================================================
# PAYMENT SUCCESS
# ============================================================

@login_required
def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order.maqom = "To'langan"
    order.save()

    Notification.objects.create(
        user=request.user,
        title="To'lov muvaffaqiyatli ✅",
        message=f"#{order.id}-buyurtmangiz uchun to'lov qabul qilindi.",
        notification_type="payment"
    )

    return redirect("orders")


# ============================================================
# SEARCH
# ============================================================

def search_view(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    products = Product.objects.none()

    if query:

        words = query.split()
        query_filter = Q()

        for word in words:

            if len(word) >= 2:

                query_filter |= (
                    Q(name__icontains=word)
                    | Q(description__icontains=word)
                    | Q(category__name__icontains=word)
                )

        if query_filter:

            products = Product.objects.filter(
                query_filter
            ).distinct()

    return render(
        request,
        "Xaridapp/search.html",
        {
            "query": query,
            "products": products
        }
    )


# ============================================================
# FAVORITES
# ============================================================

@login_required
def add_to_favorites(request, product_id):

    get_object_or_404(
        Product,
        id=product_id
    )

    favorites = request.session.get(
        "favorites",
        []
    )

    product_id = int(product_id)

    if product_id in favorites:
        favorites.remove(product_id)
    else:
        favorites.append(product_id)

    request.session["favorites"] = favorites
    request.session.modified = True

    return redirect(
        "product_detail",
        pk=product_id
    )


# ============================================================
# FAVORITES PAGE
# ============================================================

@login_required
def favorites_view(request):

    favorites = request.session.get(
        "favorites",
        []
    )

    product_ids = []

    for item in favorites:

        try:
            product_ids.append(
                int(item)
            )

        except (TypeError, ValueError):
            pass

    products = Product.objects.filter(
        id__in=product_ids
    )

    return render(
        request,
        "Xaridapp/favorites.html",
        {
            "products": products
        }
    )


# ============================================================
# ADDRESSES
# ============================================================

@login_required
def addresses(request):

    return render(
        request,
        "Xaridapp/addresses.html"
    )


# ============================================================
# PAYMENT
# ============================================================

@login_required
def payment(request):

    return render(
        request,
        "Xaridapp/payment.html"
    )


# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notifications(request):

    notifications_list = Notification.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "Xaridapp/notifications.html",
        {
            "notifications": notifications_list
        }
    )


# ============================================================
# HELP CENTER
# ============================================================

def help_center(request):

    return render(
        request,
        "Xaridapp/help_center.html"
    )


# ============================================================
# RETURNS
# ============================================================

def returns(request):

    return render(
        request,
        "Xaridapp/returns.html"
    )


# ============================================================
# PAYMENT METHODS
# ============================================================

@login_required
def payment_methods(request):

    return render(
        request,
        "Xaridapp/payment_methods.html"
    )


# ============================================================
# BUYURTMALAR
# ============================================================

@login_required
def orders(request):

    buyurtmalar = Order.objects.filter(
        user=request.user
    ).order_by(
        "-yaratilgan_at"
    )

    qidiruv = request.GET.get(
        "qidiruv",
        ""
    ).strip()

    if qidiruv:

        buyurtmalar = buyurtmalar.filter(
            mijoz_nomi__icontains=qidiruv
        )

    return render(
        request,
        "Xaridapp/buyurtmalar.html",
        {
            "buyurtmalar": buyurtmalar,
            "qidiruv": qidiruv
        }
    )


# ============================================================
# BUYURTMA DETAIL
# ============================================================

@login_required
def order_detail(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "Xaridapp/buyurtmalar_detail.html",
        {
            "order": order
        }
    )


# ============================================================
# CREATE ORDER
# ============================================================

@login_required
def create_order(request):

    if request.method == "POST":

        mijoz_nomi = request.POST.get(
            "customer_name",
            ""
        ).strip()

        telefon_raqami = request.POST.get(
            "phone_number",
            ""
        ).strip()

        manzil = request.POST.get(
            "address",
            ""
        ).strip()

        total_price = request.POST.get(
            "total_price",
            "0"
        ).strip()

        order = Order.objects.create(
            user=request.user,
            mijoz_nomi=mijoz_nomi,
            telefon_raqami=telefon_raqami,
            manzil=manzil,
            umumiy_narx=total_price,
            maqom="Kutilmoqda"
        )

        return redirect(
            "payment_page",
            order_id=order.id
        )

    return render(
        request,
        "Xaridapp/create_order.html"
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# ============================================================
# XARIDGO ADMIN LOGIN
# ============================================================

def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("admin_dashboard")

        return render(
            request,
            "Xaridapp/admin_login.html",
            {
                "error": "Login yoki parol noto'g'ri!"
            }
        )

    return render(
        request,
        "Xaridapp/admin_login.html"
    )


# ============================================================
# XARIDGO ADMIN PANEL
# ============================================================

@login_required
def admin_dashboard(request):

    # Oddiy foydalanuvchi admin panelga kira olmaydi
    if not request.user.is_staff:
        return redirect("admin_login")

    orders = Order.objects.all().order_by(
        "-yaratilgan_at"
    )

    products = Product.objects.all().order_by(
        "-created_at"
    )

    pending_orders = Order.objects.filter(
        maqom__in=[
            "Kutilmoqda",
            "To'lov kutilmoqda",
            "pending"
        ]
    ).count()

    paid_orders = Order.objects.filter(
        maqom__in=[
            "To'langan",
            "paid"
        ]
    ).count()

    delivered_orders = Order.objects.filter(
        maqom__in=[
            "Yetkazildi",
            "delivered"
        ]
    ).count()

    cancelled_orders = Order.objects.filter(
        maqom="Bekor qilindi"
    ).count()

    context = {

        # Ro'yxatlar
        "orders": orders,
        "products": products,

        # Statistika
        "orders_count": orders.count(),
        "products_count": products.count(),

        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,

        # Admin user
        "admin_user": request.user,
    }

    return render(
        request,
        "Xaridapp/admin_dashboard.html",
        context
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@login_required
def admin_logout(request):

    logout(request)

    return redirect("admin_login")


# ============================================================
# ADMIN ORDERS
# ============================================================

@staff_member_required(login_url="/admin-login/")
def admin_orders(request):

    orders = Order.objects.all().order_by(
        "-yaratilgan_at"
    )

    return render(
        request,
        "Xaridapp/admin_orders.html",
        {
            "orders": orders
        }
    )


# ============================================================
# ADMIN ORDER DETAIL
# ============================================================

@staff_member_required(login_url="/admin-login/")
def admin_order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        yangi_maqom = request.POST.get(
            "maqom"
        )

        allowed_statuses = [
            "Kutilmoqda",
            "To'lov kutilmoqda",
            "To'langan",
            "Qabul qilindi",
            "Yuborildi",
            "Yetkazildi",
            "Bekor qilindi",
        ]

        if yangi_maqom in allowed_statuses:

            order.maqom = yangi_maqom
            order.save()

        return redirect(
            "admin_order_detail",
            order_id=order.id
        )

    return render(
        request,
        "Xaridapp/admin_order_detail.html",
        {
            "order": order,
            "status_choices": Order.STATUS_CHOICES,
        }
    )

from django.shortcuts import render
from .models import Order, Product


def admin_panel(request):
    products_count = Product.objects.count()
    orders_count = Order.objects.count()

    pending_orders = Order.objects.filter(
        status="Kutilmoqda"
    ).count()

    delivered_orders = Order.objects.filter(
        status="Yetkazildi"
    ).count()

    orders = Order.objects.all().order_by("-created_at")[:10]

    return render(request, "admin-panel.html", {
        "products_count": products_count,
        "orders_count": orders_count,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "orders": orders,
    })


def admin_orders(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        maqom = request.POST.get("maqom")

        order = get_object_or_404(Order, id=order_id)
        order.maqom = maqom
        order.save()

        return redirect("admin_orders")

    orders = Order.objects.all().order_by("-yaratilgan_at")

    return render(request, "Xaridapp/orders.html", {
        "orders": orders
    })
def order_status_update(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        new_status = request.POST.get("status")

        order.status = new_status
        order.save()

    return redirect("admin_orders")