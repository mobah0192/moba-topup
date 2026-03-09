from django.contrib.auth.models import AbstractUser
from django.conf import settings 
from django.db import models

class CustomUser(AbstractUser):
    """
    MODEL: CustomUser
    Fungsi: Menyimpan data user dengan field tambahan
    Mengapa: AbstractUser sudah punya username, password, email. Kita tambah field khusus
    """
    
    # Field untuk nomor telepon
    phone_number = models.CharField(
        max_length=15,           # Maksimal 15 karakter (cukup untuk +628xxx)
        blank=True,              # Boleh dikosongkan
        null=True,               # Boleh NULL di database
        verbose_name="Nomor Telepon"  # Nama yang tampil di admin
    )
    
    # Field untuk saldo user
    balance = models.DecimalField(
        max_digits=12,            # Total digit (12 digit = sampai miliaran)
        decimal_places=2,         # 2 angka di belakang koma (Rp 1.000,50)
        default=0,                # Default 0 saat register
        verbose_name="Saldo"
    )
    
    # Field untuk verifikasi
    is_verified = models.BooleanField(
        default=False,            # Default belum terverifikasi
        verbose_name="Terverifikasi"
    )
    
    # Field untuk created_at (otomatis terisi saat pertama dibuat)
    created_at = models.DateTimeField(
        auto_now_add=True,        # Otomatis diisi waktu sekarang saat create
        verbose_name="Dibuat Pada"
    )
    
    # Field untuk updated_at (otomatis update setiap kali diubah)
    updated_at = models.DateTimeField(
        auto_now=True,            # Otomatis update setiap kali diubah
        verbose_name="Diupdate Pada"
    )
    
    def __str__(self):
        """
        Fungsi: Representasi string dari object
        Contoh: Di admin panel akan tampil "admin" bukan "CustomUser object(1)"
        """
        return self.username
    
    class Meta:
        """
        Meta class: Konfigurasi tambahan untuk model
        """
        verbose_name = "User"              # Nama singular
        verbose_name_plural = "Users"      # Nama plural
        ordering = ['-date_joined']        # Urutan default (terbaru pertama)


class Reward(models.Model):
    """Model untuk menyimpan poin reward user"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rewards'
    )
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reward"
        verbose_name_plural = "Rewards"

class Voucher(models.Model):
    """Model untuk voucher diskon"""
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code

class UserVoucher(models.Model):
    """Relasi user dengan voucher yang dimiliki"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)