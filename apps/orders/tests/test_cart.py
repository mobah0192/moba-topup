from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.games.models import Game, GameCategory, GameItem
from apps.orders.models import Order
import json

User = get_user_model()

class CartTest(TestCase):
    """Test untuk fitur keranjang"""
    
    def setUp(self):
        """Data awal sebelum test"""
        self.client = Client()
        
        # Buat game
        self.game = Game.objects.create(
            name="Mobile Legends",
            slug="mobile-legends",
            description="Game Mobile Legends"
        )
        
        # Buat kategori
        self.category = GameCategory.objects.create(
            game=self.game,
            name="Diamond"
        )
        
        # Buat item
        self.item = GameItem.objects.create(
            category=self.category,
            name="86 Diamonds",
            amount=86,
            price=23000,
            is_active=True
        )
        
        self.item2 = GameItem.objects.create(
            category=self.category,
            name="172 Diamonds",
            amount=172,
            price=46000,
            is_active=True
        )
    
    def test_add_to_cart(self):
        """Test 1: Tambah item ke cart"""
        response = self.client.post(
            reverse('orders:cart_add', args=[self.item.id]),
            data=json.dumps({'quantity': 2}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)  # 1 item unik
        
        # Cek session cart
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.item.id), cart)
        self.assertEqual(cart[str(self.item.id)]['quantity'], 2)
    
    def test_add_to_cart_invalid_item(self):
        """Test tambah item yang tidak ada"""
        response = self.client.post(
            reverse('orders:cart_add', args=[9999]),  # ID tidak ada
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_cart_quantity(self):
        """Test 2: Update quantity di cart"""
        # Tambah item dulu
        self.client.post(
            reverse('orders:cart_add', args=[self.item.id]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Update quantity
        response = self.client.post(
            reverse('orders:cart_update', args=[self.item.id]),
            data=json.dumps({'quantity': 5}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Cek quantity
        cart = self.client.session.get('cart', {})
        self.assertEqual(cart[str(self.item.id)]['quantity'], 5)
    
    def test_update_cart_invalid_quantity(self):
        """Test update dengan quantity 0 (harusnya hapus)"""
        # Tambah item dulu
        self.client.post(
            reverse('orders:cart_add', args=[self.item.id]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Update quantity jadi 0
        response = self.client.post(
            reverse('orders:cart_update', args=[self.item.id]),
            data=json.dumps({'quantity': 0}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.item.id), cart)  # Item harus ilang
    
    def test_remove_from_cart(self):
        """Test 3: Remove item dari cart"""
        # Tambah item dulu
        self.client.post(
            reverse('orders:cart_add', args=[self.item.id]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Hapus item
        response = self.client.post(
            reverse('orders:cart_remove', args=[self.item.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Cek cart kosong
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.item.id), cart)
    
    def test_cart_detail_page(self):
        """Test halaman cart detail"""
        # Tambah item
        self.client.post(
            reverse('orders:cart_add', args=[self.item.id]),
            data=json.dumps({'quantity': 2}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Buka halaman cart
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/cart_detail.html')
        
        # Cek context
        self.assertIn('cart', response.context)
        cart = response.context['cart']
        self.assertEqual(len(cart), 1)  # 1 item unik


class CheckoutTest(TestCase):
    """Test untuk fitur checkout"""
    
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
        
        # Tambah item ke cart
        session = self.client.session
        session['cart'] = {
            str(self.item.id): {
                'quantity': 2,
                'price': float(self.item.price)
            }
        }
        session.save()
    
    def test_checkout_page_login_required(self):
        """Test halaman checkout harus login"""
        response = self.client.get(reverse('orders:checkout'))
        
        # Harus redirect ke login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
    
    def test_checkout_page_authenticated(self):
        """Test 4: Checkout sebagai user login"""
        # Login dulu
        self.client.login(username='testuser', password='testpass123')
        
        # Buka halaman checkout
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')
        
        # Cek context
        self.assertIn('cart', response.context)
        self.assertIn('form', response.context)
    
    def test_checkout_process(self):
        """Test proses checkout berhasil"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('orders:checkout'), {
            'game_id': '12345678',
            'game_server': 'Asia',
            'payment_method': 'midtrans',
            'quantity': 1,
        })
        
        # Harus redirect
        self.assertEqual(response.status_code, 302)
        
        # Cek apakah redirect ke payment (cek URLnya mengandung 'payment')
        self.assertIn('payment', response.url)
        
        # Cek order dibuat
        orders = Order.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 1)
        
        order = orders.first()
        self.assertEqual(order.game_id, '12345678')
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.total_amount, 46000)
        self.assertEqual(order.status, 'pending')
    
    def test_checkout_with_invalid_data(self):
        """Test 6: Validasi form checkout"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit dengan game_id kosong
        response = self.client.post(reverse('orders:checkout'), {
            'game_id': '',
            'payment_method': 'midtrans'
        })
        
        # Harus tetap di halaman checkout (status 200, bukan redirect)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')
        
        # Cek order tidak dibuat
        self.assertEqual(Order.objects.count(), 0)
    
    def test_guest_checkout_page(self):
        """Test 5: Guest checkout"""
        # Akses halaman guest checkout
        response = self.client.get(reverse('orders:guest_checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/guest_checkout.html')
    
    def test_guest_checkout_process(self):
        """Test proses guest checkout berhasil"""
        response = self.client.post(reverse('orders:guest_checkout'), {
            'email': 'guest@test.com',
            'name': 'Guest User',
            'game_id': '87654321',
            'payment_method': 'midtrans',
            'quantity': 1,
        })
        
        # Harus redirect
        self.assertEqual(response.status_code, 302)
        
        # Cek apakah redirect ke payment (cek URLnya mengandung 'payment')
        self.assertIn('payment', response.url)
        
        # Cek order dibuat tanpa user
        orders = Order.objects.filter(user__isnull=True)
        self.assertEqual(orders.count(), 1)
        
        order = orders.first()
        self.assertEqual(order.game_id, '87654321')
        #self.assertEqual(order.customer_email, 'guest@test.com')
    
    def test_checkout_empty_cart(self):
        """Test checkout dengan cart kosong"""
        self.client.login(username='testuser', password='testpass123')
        
        # Kosongkan cart
        session = self.client.session
        session['cart'] = {}
        session.save()
        
        # Coba checkout
        response = self.client.get(reverse('orders:checkout'))
        
        # Harus redirect ke games list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('games:list'))