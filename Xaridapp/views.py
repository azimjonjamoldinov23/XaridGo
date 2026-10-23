from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
from django.db import transaction

from .models import Product, Order, OrderItem, Notification, UserProfile, Category
from .forms import SignUpForm, CustomLoginForm, ProductForm


# ============================================================
# BOSH SAHIFA
# ============================================================

def index(request):
    category_slug = request.GET.get("category")

    products = Product.objects.select_related("category").all()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if request.GET.get("available") == "1":
        products = products.filter(is_available=True, stock__gt=0)
    sort = request.GET.get("sort", "newest")
    sort_fields = {"price_asc": "price", "price_desc": "-price", "name": "name", "newest": "-created_at"}
    products = products.order_by(sort_fields.get(sort, "-created_at"))

    return render(
        request,
        "Xaridapp/index.html",
        {
            "products": products,
            "selected_category": category_slug,
            "sort": sort,
            "available_only": request.GET.get("available") == "1",
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
            "product": product,
            "categories": Category.objects.all(),
            "gallery_images": product.gallery_images.all(),
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
            UserProfile.objects.get_or_create(user=user)
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
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
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
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    return render(
        request,
        "Xaridapp/profile.html",
        {"profile": profile},
    )


# ============================================================
# EDIT PROFILE
# ============================================================

@login_required
def edit_profile(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    values = {
        "username": request.user.username,
        "email": request.user.email,
        "phone": profile.phone,
        "age": profile.age or "",
    }

    if request.method == "POST":
        values.update({
            "username": request.POST.get("username", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "age": request.POST.get("age", "").strip(),
        })
        error = None
        age = None

        if not values["username"]:
            error = "Foydalanuvchi nomini kiriting."
        elif request.user.__class__.objects.exclude(pk=request.user.pk).filter(
            username__iexact=values["username"]
        ).exists():
            error = "Bu foydalanuvchi nomi band."
        elif values["email"]:
            try:
                validate_email(values["email"])
            except ValidationError:
                error = "Elektron pochta manzilini tekshiring."

        if error is None and len(values["phone"]) > 20:
            error = "Telefon raqami 20 ta belgidan oshmasin."
        elif error is None and values["age"]:
            try:
                age = int(values["age"])
                if not 1 <= age <= 120:
                    raise ValueError
            except ValueError:
                error = "Yoshni 1 dan 120 gacha kiriting."

        if error:
            return render(request, "Xaridapp/edit_profile.html", {
                "profile": profile,
                "values": values,
                "error": error,
            })

        request.user.username = values["username"]
        request.user.email = values["email"]
        request.user.save(update_fields=["username", "email"])
        profile.phone = values["phone"]
        profile.age = age
        profile.save(update_fields=["phone", "age"])
        return redirect("profile")

    return render(
        request,
        "Xaridapp/edit_profile.html",
        {"profile": profile, "values": values},
    )


# ============================================================
# ADD TO CART
# ============================================================

@login_required
@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get(
        "cart",
        {}
    )

    if not product.is_available or product.stock < 1:
        return redirect("product_detail", pk=product.id)

    product_id = str(product_id)

    if int(cart.get(product_id, 0) or 0) >= product.stock:
        return redirect("cart_view")

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
            product = Product.objects.filter(pk=product_id).first()
            if product and product.is_available and cart[product_id] < product.stock:
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
    cart_products = []

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(
                id=int(product_id)
            )
            cart_products.append((product, int(quantity)))
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

        with transaction.atomic():
            locked_products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(
                    id__in=[p.id for p, _qty in cart_products]
                )
            }
            unavailable = [
                product.name for product, quantity in cart_products
                if product.id not in locked_products
                or not locked_products[product.id].is_available
                or locked_products[product.id].stock < quantity
            ]
            if unavailable:
                return render(request, "Xaridapp/checkout.html", {
                    "total_price": total_price,
                    "error": "Omborda yetarli mahsulot qolmagan: " + ", ".join(unavailable),
                })
            for product, quantity in cart_products:
                locked = locked_products[product.id]
                locked.stock -= quantity
                if locked.stock == 0:
                    locked.is_available = False
                    locked.save(update_fields=["stock", "is_available"])
                else:
                    locked.save(update_fields=["stock"])
            order = Order.objects.create(
                user=request.user,
                mijoz_nomi=mijoz_nomi,
                telefon_raqami=telefon_raqami,
                manzil=manzil,
                umumiy_narx=total_price,
                maqom="Kutilmoqda"
            )
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=locked_products[product.id],
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=quantity,
                )
                for product, quantity in cart_products
            ])

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

@staff_member_required(login_url="admin_login")
@require_POST
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.maqom = "To'langan"
    order.save(update_fields=["maqom"])
    return redirect("admin_order_detail", order_id=order.id)


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

    if request.GET.get("available") == "1":
        products = products.filter(is_available=True, stock__gt=0)
    sort = request.GET.get("sort", "newest")
    sort_fields = {"price_asc": "price", "price_desc": "-price", "name": "name", "newest": "-created_at"}
    products = products.order_by(sort_fields.get(sort, "-created_at"))

    return render(
        request,
        "Xaridapp/search.html",
        {
            "query": query,
            "products": products,
            "sort": sort,
            "available_only": request.GET.get("available") == "1",
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
    return redirect("orders")


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


def order_tracking(request):
    order = None
    error = None
    if request.method == "POST":
        raw_id = request.POST.get("order_id", "").strip().lstrip("#")
        phone = "".join(ch for ch in request.POST.get("phone", "") if ch.isdigit())
        if raw_id.isdigit() and phone:
            candidate = Order.objects.filter(pk=int(raw_id)).first()
            saved_phone = "".join(ch for ch in (candidate.telefon_raqami if candidate else "") if ch.isdigit())
            if candidate and phone == saved_phone:
                order = candidate
        if order is None:
            error = "Buyurtma topilmadi. Raqam va telefonni tekshiring."
    return render(request, "Xaridapp/order_tracking.html", {"order": order, "error": error})


# ============================================================
# CREATE ORDER
# ============================================================

@login_required
def create_order(request):
    # Legacy URL: checkout calculates and validates the order server-side.
    return redirect("checkout")


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

@staff_member_required(login_url="admin_login")
def admin_dashboard(request):
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
        "product_count": products.count(),
        "order_count": orders.count(),
        "pending_count": pending_orders,
        "delivered_count": delivered_orders,

        # Admin user
        "admin_user": request.user,
    }

    return render(
        request,
        "Xaridapp/admin_dashboard.html",
        context
    )


@staff_member_required(login_url="admin_login")
def admin_products(request):
    return render(request, "Xaridapp/admin_products.html", {
        "products": Product.objects.select_related("category").order_by("name"),
    })


@staff_member_required(login_url="admin_login")
def admin_product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        _save_gallery_images(form, product)
        return redirect("admin_products")
    return render(request, "Xaridapp/admin_product_form.html", {"form": form, "title": "Mahsulot qo‘shish"})


@staff_member_required(login_url="admin_login")
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        saved_product = form.save()
        _save_gallery_images(form, saved_product)
        return redirect("admin_products")
    return render(request, "Xaridapp/admin_product_form.html", {
        "form": form,
        "title": "Mahsulotni tahrirlash",
        "product": product,
        "gallery_images": product.gallery_images.all(),
    })


def _save_gallery_images(form, product):
    from .models import ProductImage
    ProductImage.objects.bulk_create([
        ProductImage(product=product, image=image)
        for image in form.cleaned_data.get("gallery_images", [])
    ])


@staff_member_required(login_url="admin_login")
@require_POST
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return redirect("admin_products")


# ============================================================
# ADMIN LOGOUT
# ============================================================

@staff_member_required(login_url="admin_login")
def admin_logout(request):

    logout(request)

    return redirect("admin_login")


# ============================================================
# ADMIN ORDERS
# ============================================================

@staff_member_required(login_url="admin_login")
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

@staff_member_required(login_url="admin_login")
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
            _update_order_status(order, yangi_maqom)

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


def _update_order_status(order, new_status):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if new_status == "Bekor qilindi" and not order.inventory_restored:
            for item in order.items.select_related("product"):
                if item.product_id:
                    item.product.stock += item.quantity
                    item.product.is_available = True
                    item.product.save(update_fields=["stock", "is_available"])
            order.inventory_restored = True
        order.maqom = new_status
        order.save(update_fields=["maqom", "inventory_restored"])
    return order

@staff_member_required(login_url="admin_login")
@require_POST
def order_status_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("maqom") or request.POST.get("status")
    allowed_statuses = {value for value, _label in Order.STATUS_CHOICES}

    if new_status in allowed_statuses:
        _update_order_status(order, new_status)

    return redirect("admin_order_detail", order_id=order.id)
