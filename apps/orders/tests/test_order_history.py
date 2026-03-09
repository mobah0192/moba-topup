from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.games.models import Game, GameCategory, GameItem
from apps.orders.models import Order

User = get_user_model()

class OrderHistoryTest(TestCase):
    """Test untuk riwayat order"""
    
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
        
        # Buat beberapa order dengan status berbeda
        self.order1 = Order.objects.create(
            user=self.user,
            game_item=self.item,
            game_id='111111',
            quantity=1,
            price=23000,
            total_amount=23000,
            status='pending',
            invoice_number='INV-001'
        )
        
        self.order2 = Order.objects.create(
            user=self.user,
            game_item=self.item,
            game_id='222222',
            quantity=2,
            price=23000,
            total_amount=46000,
            status='paid',
            invoice_number='INV-002'
        )
        
        self.order3 = Order.objects.create(
            user=self.user,
            game_item=self.item,
            game_id='333333',
            quantity=3,
            price=23000,
            total_amount=69000,
            status='completed',
            invoice_number='INV-003'
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_order_list_page(self):
        """Test 7: Halaman riwayat order"""
        response = self.client.get(reverse('orders:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')
        
        # Cek context
        self.assertIn('orders', response.context)
        self.assertIn('status_counts', response.context)
        
        # Hitung order (harus 3)
        self.assertEqual(len(response.context['orders']), 3)
    
    def test_order_list_filter_by_status(self):
        """Test 8: Filter status order"""
        # Filter pending
        response = self.client.get(reverse('orders:list') + '?status=pending')
        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].status, 'pending')
        
        # Filter paid
        response = self.client.get(reverse('orders:list') + '?status=paid')
        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].status, 'paid')
        
        # Filter completed
        response = self.client.get(reverse('orders:list') + '?status=completed')
        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].status, 'completed')
    
    def test_order_detail_page(self):
        """Test 9: Halaman detail order"""
        response = self.client.get(
            reverse('orders:detail', args=[self.order1.invoice_number])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')
        
        # Cek context
        self.assertIn('order', response.context)
        order = response.context['order']
        self.assertEqual(order.invoice_number, 'INV-001')
    
    def test_order_detail_unauthorized(self):
        """Test akses order orang lain"""
        # Buat user lain
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
        
        # Buat order milik user lain
        other_order = Order.objects.create(
            user=other_user,
            game_item=self.item,
            game_id='999999',
            quantity=1,
            price=23000,
            total_amount=23000,
            status='pending',
            invoice_number='INV-OTHER'
        )
        
        # Coba akses
        response = self.client.get(
            reverse('orders:detail', args=[other_order.invoice_number])
        )
        
        # Harus 404 atau forbidden
        self.assertEqual(response.status_code, 404)
    
    def test_cancel_order(self):
        """Test 10: Cancel order"""
        response = self.client.post(
            reverse('orders:cancel', args=[self.order1.invoice_number]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Cek status order berubah
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'expired')
    
    def test_cancel_order_not_pending(self):
        """Test cancel order yang sudah paid"""
        response = self.client.post(
            reverse('orders:cancel', args=[self.order2.invoice_number]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        self.assertFalse(data['success'])  # Harus gagal
        self.assertIn('error', data)
        
        # Status tidak berubah
        self.order2.refresh_from_db()
        self.assertEqual(self.order2.status, 'paid')