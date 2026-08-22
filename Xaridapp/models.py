from django.db import models
from django.conf import settings


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name="Kategoriya nomi"
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="URL Slug"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


# ============================================================
# PRODUCT
# ============================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Kategoriyasi"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Mahsulot nomi"
    )

    description = models.TextField(
        verbose_name="Tavsifi"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Narxi"
    )

    image = models.ImageField(
        upload_to="products/%Y/%m/%d",
        blank=True,
        verbose_name="Rasmi"
    )

    stock = models.PositiveIntegerField(
        verbose_name="Ombordagi soni"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Sotuvda mavjudmi?"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]


# ============================================================
# ORDER
# ============================================================

class Order(models.Model):

    STATUS_CHOICES = [
        ("Kutilmoqda", "⏳ To'lov kutilmoqda"),
        ("To'langan", "✅ To'langan"),
        ("Qabul qilindi", "📦 Qabul qilindi"),
        ("Yuborildi", "🚚 Yuborildi"),
        ("Yetkazildi", "🎉 Yetkazildi"),
        ("Bekor qilindi", "❌ Bekor qilindi"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )

    mijoz_nomi = models.CharField(
        max_length=100,
        verbose_name="Mijoz nomi"
    )

    telefon_raqami = models.CharField(
        max_length=20,
        verbose_name="Telefon raqami"
    )

    manzil = models.TextField(
        verbose_name="Manzil"
    )

    umumiy_narx = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Umumiy narx"
    )

    maqom = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Kutilmoqda",
        verbose_name="Buyurtma holati"
    )

    yaratilgan_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )

    def __str__(self):
        ism = self.user.username if self.user else self.mijoz_nomi
        return f"Buyurtma #{self.id} - {ism}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-yaratilgan_at"]


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        default="info"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ["-created_at"]


# ============================================================
# PAYMENT
# ============================================================

class Tolov(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="tolov",
        verbose_name="Buyurtma"
    )

    summa = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="To'lov summasi"
    )

    tasdiqlangan = models.BooleanField(
        default=False,
        verbose_name="To'lov tasdiqlanganmi?"
    )

    yaratilgan_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="To'lov vaqti"
    )

    tasdiqlangan_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Tasdiqlangan vaqt"
    )

    def __str__(self):
        return f"To'lov #{self.id} - Buyurtma #{self.order.id}"

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ["-yaratilgan_at"]