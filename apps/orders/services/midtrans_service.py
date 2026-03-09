import midtransclient
import uuid
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

class MidtransService:
    """
    Service class untuk menangani semua interaksi dengan Midtrans
    """
    
    def __init__(self):
        """Inisialisasi koneksi ke Midtrans"""
        self.is_production = settings.MIDTRANS_IS_PRODUCTION
        self.server_key = settings.MIDTRANS_SERVER_KEY
        self.client_key = settings.MIDTRANS_CLIENT_KEY
        self.merchant_id = settings.MIDTRANS_MERCHANT_ID
        
        # Inisialisasi Snap client
        self.snap = midtransclient.Snap(
            is_production=self.is_production,
            server_key=self.server_key,
            client_key=self.client_key
        )
    
    def create_transaction(self, order, request):
        """
        Membuat transaksi Midtrans untuk order tertentu
        """
        # Generate order_id unik untuk Midtrans
        midtrans_order_id = f"ORDER-{order.invoice_number}-{uuid.uuid4().hex[:8]}"
        
        # Simpan ke order
        order.midtrans_order_id = midtrans_order_id
        order.save()
        
        # Hitung gross amount (total pembayaran)
        gross_amount = int(order.total_amount)  # Midtrans pake integer
        
        # Buat parameter transaksi
        transaction_params = {
            "transaction_details": {
                "order_id": midtrans_order_id,
                "gross_amount": gross_amount
            },
            "credit_card": {
                "secure": True
            },
            "customer_details": {
                "first_name": order.user.username,
                "email": order.user.email,
                "phone": order.user.phone_number or ""
            },
            "item_details": [
                {
                    "id": str(order.game_item.id),
                    "price": int(order.price),
                    "quantity": order.quantity,
                    "name": f"{order.game_item.name} ({order.game_item.category.game.name})"
                }
            ],
            "callbacks": {
                "finish": request.build_absolute_uri(
                    reverse('orders:payment_finish', args=[order.invoice_number])
                ),
                "unfinish": request.build_absolute_uri(
                    reverse('orders:payment_unfinish', args=[order.invoice_number])
                ),
                "error": request.build_absolute_uri(
                    reverse('orders:payment_error', args=[order.invoice_number])
                )
            },
            "expiry": {
                "start_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S %z"),
                "unit": "minutes",
                "duration": 30  # 30 menit expiry
            }
        }
        
        try:
            # Buat transaksi di Midtrans
            response = self.snap.create_transaction(transaction_params)
            
            # Simpan response ke order
            order.payment_details = response
            order.payment_url = response.get('redirect_url')
            order.save()
            
            return {
                'success': True,
                'token': response.get('token'),
                'redirect_url': response.get('redirect_url'),
                'order_id': midtrans_order_id
            }
            
        except Exception as e:
            # Log error
            print(f"Midtrans Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_transaction_status(self, order_id):
        """
        Mengecek status transaksi dari Midtrans
        """
        try:
            # Gunakan API client untuk cek status
            api_client = midtransclient.CoreApi(
                is_production=self.is_production,
                server_key=self.server_key,
                client_key=self.client_key
            )
            
            response = api_client.transaction.status(order_id)
            return {
                'success': True,
                'data': response
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook_notification(self, notification_body):
        """
        Menangani notifikasi webhook dari Midtrans
        """
        try:
            # Langsung ambil data dari notifikasi
            order_id = notification_body['order_id']
            transaction_status = notification_body['transaction_status']
            fraud_status = notification_body.get('fraud_status', 'accept')
            
            print(f"Processing webhook for order: {order_id}")
            print(f"Transaction status: {transaction_status}")
            print(f"Fraud status: {fraud_status}")
            
            # Mapping status Midtrans ke status Order
            status_mapping = {
                'capture': 'paid',
                'settlement': 'paid',
                'pending': 'pending',
                'deny': 'failed',
                'cancel': 'failed',
                'expire': 'expired',
                'failure': 'failed'
            }
            
            # Jika fraud_status = 'challenge', status tetap pending sampai accept
            if fraud_status == 'challenge':
                new_status = 'pending'
            else:
                new_status = status_mapping.get(transaction_status, 'pending')
            
            return {
                'success': True,
                'order_id': order_id,
                'transaction_status': transaction_status,
                'fraud_status': fraud_status,
                'new_status': new_status
            }
            
        except Exception as e:
            print(f"Error in handle_webhook_notification: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }