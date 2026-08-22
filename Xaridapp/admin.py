from django.contrib import admin

from .models import Category, Product, Order, Notification


# ============================================================
# CATEGORY
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


# ============================================================
# PRODUCT
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'is_available',
        'created_at',
    )

    list_filter = (
        'is_available',
        'category',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'price',
        'stock',
        'is_available',
    )


# ============================================================
# ORDER
# ============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'mijoz_nomi',
        'telefon_raqami',
        'umumiy_narx',
        'maqom',
        'yaratilgan_at',
    )

    list_filter = (
        'maqom',
        'yaratilgan_at',
    )

    search_fields = (
        'mijoz_nomi',
        'telefon_raqami',
        'manzil',
        'user__username',
    )

    list_editable = (
        'maqom',
    )

    ordering = (
        '-yaratilgan_at',
    )


# ============================================================
# NOTIFICATION
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'title',
        'notification_type',
        'is_read',
        'created_at',
    )

    list_filter = (
        'notification_type',
        'is_read',
        'created_at',
    )

    search_fields = (
        'user__username',
        'title',
        'message',
    )

    ordering = (
        '-created_at',
    )