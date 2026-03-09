from django.db import models
from django.conf import settings
import uuid

class Order(models.Model):
    """
    MODEL: Order
    Fungsi: Menyimpan transaksi topup
    """
    
    # Status order (pilihan)
    STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('paid', 'Sudah Dibayar'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
        ('expired', 'Kadaluarsa'),
    ]
    
    # Metode pembayaran
    PAYMENT_METHODS = [
        ('balance', 'Saldo'),
        ('midtrans', 'Midtrans'),
    ]
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nomor Invoice"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Mengacu ke CustomUser
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="User",
        null=True,  
        blank=True  
    )
    
    game_item = models.ForeignKey(
        'games.GameItem',
        on_delete=models.PROTECT,  # PROTECT = tidak bisa hapus item jika masih ada order
        related_name='orders',
        verbose_name="Item Game"
    )
    
    game_id = models.CharField(
        max_length=50,
        verbose_name="ID Game"
    )
    
    game_server = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Server Game"
    )
    
    quantity = models.IntegerField(
        default=1,
        verbose_name="Jumlah"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Harga Satuan"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Total Harga"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='midtrans',
        verbose_name="Metode Pembayaran"
    )
    
    # Untuk Midtrans
    midtrans_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    midtrans_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL Pembayaran"
    )
    
    payment_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detail Pembayaran"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Catatan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """
        Otomatis generate invoice number jika belum ada
        """
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """
        Format: INV-20250302-ABC12
        """
        from django.utils import timezone
        import random
        import string
        
        today = timezone.now().strftime('%Y%m%d')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"INV-{today}-{random_chars}"
    
    def __str__(self):
        return self.invoice_number
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

class PaymentMethod(models.Model):
    """Model untuk metode pembayaran"""
    
    PAYMENT_CATEGORIES = [
        ('bank', 'Transfer Bank'),
        ('ewallet', 'E-Wallet'),
        ('qris', 'QRIS'),
    ]
    
    name = models.CharField(
        max_length=50,
        verbose_name="Nama Metode"
    )
    
    code = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Kode (contoh: bca, gopay)"
    )
    
    category = models.CharField(
        max_length=20,
        choices=PAYMENT_CATEGORIES,
        default='bank',
        verbose_name="Kategori"
    )
    
    logo = models.ImageField(
        upload_to='payments/',
        verbose_name="Logo",
        help_text="Upload logo (format SVG/PNG)"
    )
    
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Deskripsi"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Urutan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Metode Pembayaran"
        verbose_name_plural = "Metode Pembayaran"
        ordering = ['sort_order', 'name']