from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

User = get_user_model()

class UserAuthTest(TestCase):
    """Test untuk autentikasi user"""
    
    def setUp(self):
        self.client = Client()
        
        
        # TAMBAHKAN INI:
        # Buat Social App untuk testing
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider='google',
            name='Google Login',
            client_id='dummy-client-id',
            secret='dummy-secret',
            key=''
        )
        app.sites.add(site)
        
        # Buat user untuk test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123'
        )
    
    def test_register_page(self):
        """Test halaman register bisa diakses"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_success(self):
        """Test 11: Register dengan data valid"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        })
        
        # Harus redirect (ke games list)
        self.assertEqual(response.status_code, 302)
        
        # Cek user tersimpan
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_invalid_data(self):
        """Test 12: Register dengan data invalid"""
        # Password tidak match
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'pass123',
            'password2': 'pass456'
        })
        
        self.assertEqual(response.status_code, 200)  # Tetap di halaman register
        self.assertTemplateUsed(response, 'users/register.html')
        
        # Cek user tidak tersimpan
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_register_duplicate_username(self):
        """Test register dengan username yang sudah ada"""
        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',  # Username sudah ada
            'email': 'another@test.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        
        # Harus ada error
        self.assertContains(response, 'sudah ada')
    
    def test_login_page(self):
        """Test halaman login bisa diakses"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_success(self):
        """Test 13: Login berhasil"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        # Harus redirect
        self.assertEqual(response.status_code, 302)
        
        # Cek user terautentikasi
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_wrong_password(self):
        """Test 14: Login dengan password salah"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        self.assertEqual(response.status_code, 200)  # Tetap di halaman login
        self.assertTemplateUsed(response, 'users/login.html')
        
        # Cek user tidak terautentikasi
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_login_nonexistent_user(self):
        """Test login dengan user tidak ada"""
        response = self.client.post(reverse('users:login'), {
            'username': 'notexist',
            'password': 'TestPass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_logout(self):
        """Test 15: Logout"""
        # Login dulu
        self.client.login(username='testuser', password='TestPass123')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        response = self.client.get(reverse('users:logout'))
        
        # Harus redirect
        self.assertEqual(response.status_code, 302)
        
        # Cek session hilang
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_profile_page_authenticated(self):
        """Test 16: Halaman profile untuk user login"""
        self.client.login(username='testuser', password='TestPass123')
        
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        
        # Cek context
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'].username, 'testuser')
    
    def test_profile_page_unauthenticated(self):
        """Test halaman profile tanpa login"""
        response = self.client.get(reverse('users:profile'))
        
        # Harus redirect ke login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
    
    def test_edit_profile(self):
        """Test 17: Edit profile"""
        self.client.login(username='testuser', password='TestPass123')
        
        response = self.client.post(reverse('users:profile_edit'), {
            'username': 'testuser',
            'email': 'updated@test.com',
            'phone': '081234567890'
        })
        
        # Harus redirect ke profile
        self.assertEqual(response.status_code, 302)
        
        # Cek data berubah
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')