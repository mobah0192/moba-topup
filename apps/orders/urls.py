from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # ===== CART URLS =====
    path('cart/count/', views.cart_count, name='cart_count'),
    path('cart/add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    
    # ===== CHECKOUT URLS =====
    path('checkout/', views.checkout, name='checkout'),
    path('guest-checkout/', views.guest_checkout, name='guest_checkout'),
    
    # ===== ORDER CREATE =====
    path('create/<slug:game_slug>/', views.order_create, name='create'),
    
    # ===== PAYMENT URLS =====
    path('payment/<str:invoice_number>/', views.order_payment, name='payment'),
    path('payment/<str:invoice_number>/finish/', views.payment_finish, name='payment_finish'),
    path('payment/<str:invoice_number>/unfinish/', views.payment_unfinish, name='payment_unfinish'),
    path('payment/<str:invoice_number>/error/', views.payment_error, name='payment_error'),
    
    # ===== ORDER LIST =====
    path('', views.order_list, name='list'),
    
    # ===== ORDER DETAIL & ACTIONS (PALING AKHIR - KARENA PAKAI PARAMETER INVOICE) =====
    path('<str:invoice_number>/cancel/', views.order_cancel, name='cancel'),
    path('<str:invoice_number>/confirm/', views.order_confirm, name='confirm'),
    path('<str:invoice_number>/', views.order_detail, name='detail'),  # HARUS PALING BAWAH!
    
    # ===== API URLS =====
    path('api/<str:invoice_number>/status/', views.get_order_status, name='api_status'),
    path('api/<str:invoice_number>/check-payment/', views.check_payment_status, name='check_payment_status'),

]

# ===== WEBHOOK URLS (TIDAK PERLU CSRF) =====
urlpatterns += [
    path('webhook/midtrans/', views.midtrans_webhook, name='midtrans_webhook'),
]