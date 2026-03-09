from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from apps.games.models import Game, GameCategory, GameItem
from apps.orders.models import Order
import json

User = get_user_model()

class PaymentTest(TestCase):
    """Test untuk fitur pembayaran"""

    def setUp(self):
        self.client = Client()

        # Buat user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        # Buat game & item
        self.game = Game.objects.create(name="Mobile Legends", slug="mobile-legends")
        self.category = GameCategory.objects.create(game=self.game, name="Diamond")
        self.item = GameItem.objects.create(
            category=self.category,
            name="86 Diamonds",
            amount=86,
            price=23000,
            is_active=True
        )

        # Buat order dengan midtrans_order_id
        self.order = Order.objects.create(
            user=self.user,
            game_item=self.item,
            game_id='12345678',
            quantity=2,
            price=23000,
            total_amount=46000,
            status='pending',
            invoice_number='INV-TEST-12345',
            midtrans_order_id='ORDER-TEST-123'  # <-- TAMBAHKAN INI
        )

        self.client.login(username='testuser', password='testpass123')

    @patch('apps.orders.services.midtrans_service.MidtransService.create_transaction')
    def test_payment_page(self, mock_create_transaction):
        """Test halaman pembayaran"""
        # Mock response dari Midtrans
        mock_create_transaction.return_value = {
            'success': True,
            'token': 'dummy-snap-token',
            'redirect_url': 'https://app.sandbox.midtrans.com/snap/v2/vtweb/dummy',
            'order_id': 'ORDER-TEST-123'
        }

        # Buka halaman payment
        response = self.client.get(
            reverse('orders:payment', args=[self.order.invoice_number])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_payment.html')

        # Cek context
        self.assertIn('order', response.context)
        self.assertIn('midtrans_client_key', response.context)

    def test_payment_page_already_paid(self):
        """Test halaman payment untuk order yang sudah dibayar"""
        self.order.status = 'paid'
        self.order.save()

        response = self.client.get(
            reverse('orders:payment', args=[self.order.invoice_number])
        )

        # Harus redirect ke detail
        self.assertEqual(response.status_code, 302)
        # 🔴 UBAH: jangan cari 'detail', langsung cek redirect ke URL yang benar
        self.assertEqual(response.url, reverse('orders:detail', args=[self.order.invoice_number]))

    def test_payment_finish_redirect(self):
        """Test redirect setelah payment finish"""
        response = self.client.get(
            reverse('orders:payment_finish', args=[self.order.invoice_number])
        )

        self.assertEqual(response.status_code, 302)
        # 🔴 UBAH: langsung cek redirect ke URL yang benar
        self.assertEqual(response.url, reverse('orders:detail', args=[self.order.invoice_number]))

    def test_payment_unfinish_redirect(self):
        """Test redirect saat payment belum selesai"""
        response = self.client.get(
            reverse('orders:payment_unfinish', args=[self.order.invoice_number])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('orders:payment', args=[self.order.invoice_number]))

    def test_payment_error_redirect(self):
        """Test redirect saat payment error"""
        response = self.client.get(
            reverse('orders:payment_error', args=[self.order.invoice_number])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('orders:payment', args=[self.order.invoice_number]))

    @patch('apps.orders.services.midtrans_service.MidtransService.check_transaction_status')
    def test_check_payment_status(self, mock_check_status):
        """Test API cek status payment"""
        # Mock response dari Midtrans
        mock_check_status.return_value = {
            'success': True,
            'data': {
                'transaction_status': 'pending',
                'order_id': self.order.midtrans_order_id
            }
        }

        response = self.client.get(
            reverse('orders:check_payment_status', args=[self.order.invoice_number])
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'pending')  # Masih pending karena mock

    def test_webhook_midtrans(self):
        """Test 9: Webhook Midtrans jalan"""
    # Simulasi webhook dari Midtrans
        webhook_data = {
            'order_id': self.order.midtrans_order_id,
            'transaction_status': 'settlement',
            'fraud_status': 'accept',
            'status_code': '200',
            'gross_amount': '46000.00'
            }

        response = self.client.post(
            reverse('orders:midtrans_webhook'),
            data=json.dumps(webhook_data),
            content_type='application/json'
     )

    # 🔴 DEBUG PRINT
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
    
        self.assertEqual(response.status_code, 200)
    
    # Cek status order berubah jadi 'paid'
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')