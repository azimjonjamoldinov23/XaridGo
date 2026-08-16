from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import SignUpForm, CustomLoginForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
from django.shortcuts import get_object_or_404
from .models import Order

def index(request):
    category_slug = request.GET.get('category')
    if category_slug:
        # Agar modelingizdagi kategoriya maydoni slug yoki foreign key bo'lsa, moslang:
        # Masalan, agar kategoriya nom bo'yicha filter qilinsa:
        products = Product.objects.filter(category__name=category_slug)
        # Yoki agar category o'zi to'g'ridan-to'g'ri matn (CharField) bo'lsa:
        # products = Product.objects.filter(category=category_slug)
    else:
        products = Product.objects.all()
        
    return render(request, 'Xaridapp/index.html', {'products': products})
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'Xaridapp/product_detail.html', {'product': product})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # Foydalanuvchini bazaga saqlash
            login(request, user)        # Avtomatik tizimga kirish
            return redirect('index')    # Bosh sahifaga yo'naltirish
    else:
        form = SignUpForm()
    return render(request, 'Xaridapp/signup.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = CustomLoginForm()
    return render(request, 'Xaridapp/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'Xaridapp/profile.html')



from django.shortcuts import get_object_or_404, redirect
from .models import Product

from django.shortcuts import get_object_or_404, redirect
from .models import Product # Modelingiz nomini tekshiring!

def add_to_cart(request, product_id):
    # Mahsulotni topish
    product = get_object_or_404(Product, id=product_id)
    
    # Sessiyadan savatni olish
    cart = request.session.get('cart', {})
    
    # Mahsulot ID sini string formatga o'tkazish
    str_id = str(product_id)
    
    # Savatga qo'shish yoki sonini oshirish
    if str_id in cart:
        cart[str_id] += 1
    else:
        cart[str_id] = 1
        
    # Sessiyani yangilash
    request.session['cart'] = cart
    request.session.modified = True # BU QATOR MUHIM!
    
    return redirect('index')

def cart_view(request):
    return render(request, 'Xaridapp/cart.html') # Yoki o'zingizning savat shabloningiz nomi
def cart_view(request):
    # Sessiyadan savatni olamiz
    cart = request.session.get('cart', {})
    
    # Savatdagi mahsulotlar ID lari bo'yicha bazadan mahsulotlarni qidirib olamiz
    products_in_cart = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = product.price * quantity
            total_price += subtotal
            products_in_cart.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass

    context = {
        'items': products_in_cart,
        'total_price': total_price
    }
    return render(request, 'Xaridapp/cart.html', context)
from django.shortcuts import get_object_or_404, redirect

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    str_id = str(product_id)

    if str_id in cart:
        if action == 'increase':
            cart[str_id] += 1
        elif action == 'decrease':
            if cart[str_id] > 1:
                cart[str_id] -= 1
            else:
                del cart[str_id] # Agar 1 bo'lsa, o'chirib tashlaymiz
        elif action == 'remove':
            del cart[str_id]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_view') # 'cart_view' - bu savat sahifangizning URL nomi
from .models import Product, Order  # Agar Order modeli hali import qilinmagan bo'lsa

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_view')
    
    total_price = 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            total_price += product.price * quantity
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Modelingizdagi aniq maydon nomlariga mosladik:
        order = Order.objects.create(
            customer_name=first_name,   # <-- 'customer_name'
            phone_number=phone,         # <-- 'phone_number'
            address=address,
            total_price=total_price
        )
        
        # Savatni tozalash
        request.session['cart'] = {}
        request.session.modified = True
        
        return redirect('payment_page', order_id=order.id)

    return render(request, 'Xaridapp/checkout.html', {'total_price': total_price})



def payment_page_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'Xaridapp/payment.html', {'order': order})



from django.shortcuts import redirect, get_object_or_404
from .models import Order

# ... sizdagi boshqa sahifalar (home, product_detail) kodlari shu yerda turaveradi ...

from django.shortcuts import render, get_object_or_404
from .models import Order

def payment_page_view(request, order_id):
    # Buyurtmani bazadan olamiz
    order = get_object_or_404(Order, id=order_id)
    
    # O'zingizning Paynet karta ma'lumotlaringiz
    context = {
        'order': order,
        'card_number': '7777 0122 2402 7152',  # Paynet karta raqamingizni yozing
        'card_holder': 'AZIMJON J.',          # Ism-familiyangizni yozing
    }
    
    # Click'ga REDIRECT QILMAYMIZ, o'zimizning HTML sahifamizni ochamiz
    return render(request, 'Xaridapp/payment.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Order

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Order

def search_view(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    
    if query:
        # Kiritilgan matnni alohida so'zlarga bo'lib olamiz
        words = query.split()
        
        # Har bir so'z uchun moslikni tekshiruvchi filtimizni shakllantiramiz
        query_filter = Q()
        for word in words:
            # Agar so'z kamida 2 ta harfdan iborat bo'lsa qidiruvga qo'shamiz
            if len(word) >= 2:
                query_filter |= Q(name__icontains=word) | \
                               Q(description__icontains=word) | \
                               Q(category__name__icontains=word)
        
        # Bazadan mos keluvchi mahsulotlarni olamiz
        if query_filter:
            products = Product.objects.filter(query_filter).distinct()

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'Xaridapp/search.html', context)