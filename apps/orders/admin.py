from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'game_item', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['invoice_number', 'user__username', 'game_id']
    readonly_fields = ['invoice_number', 'created_at']
    
    fieldsets = (
        ('Informasi Order', {
            'fields': ('invoice_number', 'user', 'status', 'payment_method')
        }),
        ('Detail Game', {
            'fields': ('game_item', 'game_id', 'game_server', 'quantity')
        }),
        ('Keuangan', {
            'fields': ('price', 'total_amount')
        }),
        ('Midtrans', {
            'fields': ('midtrans_order_id', 'payment_url', 'payment_details'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

from .models import PaymentMethod

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_active', 'sort_order']
    list_filter = ['category', 'is_active']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['name', 'code']
    prepopulated_fields = {'code': ('name',)}
    
    fieldsets = (
        ('Informasi Metode', {
            'fields': ('name', 'code', 'category', 'description')
        }),
        ('Logo', {
            'fields': ('logo',),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'sort_order')
        }),
    )