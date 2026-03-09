from django.urls import path
from . import views

urlpatterns = [
    path('status/<str:invoice_number>/', views.get_order_status, name='api_status'),
    path('webhook/midtrans/', views.midtrans_webhook, name='midtrans_webhook'),
]