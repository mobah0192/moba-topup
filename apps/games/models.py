from django.utils import timezone
from django.db import models
from django.utils.text import slugify

class Game(models.Model):
    """
    MODEL: Game
    Fungsi: Menyimpan data game yang tersedia
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nama Game"
    )
    
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Deskripsi"
    )
    
    icon = models.ImageField(
        upload_to='games/icons/',
        blank=True,
        null=True,
        verbose_name="Icon Game"
    )
    
    banner = models.ImageField(
        upload_to='games/banners/',
        blank=True,
        null=True,
        verbose_name="Banner Game"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
        ordering = ['name']


class GameCategory(models.Model):
    """
    MODEL: GameCategory
    Fungsi: Kategori item dalam game
    """
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name="Game"
    )
    
    name = models.CharField(
        max_length=50,
        verbose_name="Nama Kategori"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Deskripsi"
    )
    
    def __str__(self):
        return f"{self.game.name} - {self.name}"
    
    class Meta:
        verbose_name = "Kategori Game"
        verbose_name_plural = "Kategori Game"
        unique_together = ['game', 'name']


class GameItem(models.Model):
    """
    MODEL: GameItem
    Fungsi: Item yang bisa dibeli user
    """
    
    category = models.ForeignKey(
        GameCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Kategori"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nama Item"
    )
    
    amount = models.IntegerField(
        verbose_name="Jumlah (dalam game)"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Harga"
    )
    
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Harga Diskon"
    )
    
    is_popular = models.BooleanField(
        default=False,
        verbose_name="Item Populer"
    )
    
    image = models.ImageField(
        upload_to='games/items/',
        blank=True,
        null=True,
        verbose_name="Gambar Item"
    )
    
    stock = models.IntegerField(
        default=0,
        verbose_name="Stok"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    def get_price_display(self):
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def __str__(self):
        return f"{self.category.game.name} - {self.name}"
    
    class Meta:
        verbose_name = "Item Game"
        verbose_name_plural = "Item Game"
        ordering = ['category__game', 'price']


class ArticleCategory(models.Model):
    """Kategori artikel (TULIS SEKALI SAJA)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=20, 
        default='#667eea',
        help_text='Warna kategori (contoh: #667eea)'
    )
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text='Icon Font Awesome (contoh: fas fa-newspaper)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kategori Artikel"
        verbose_name_plural = "Kategori Artikel"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Model untuk artikel berita game (TULIS SEKALI SAJA)"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        ArticleCategory, 
        on_delete=models.CASCADE, 
        related_name='articles'
    )
    game = models.ForeignKey(
        Game, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='articles'
    )
    
    # Konten
    image = models.ImageField(
        upload_to='articles/', 
        blank=True, 
        null=True,
        verbose_name="Gambar Artikel"
    )
    content = models.TextField()
    excerpt = models.TextField(
        max_length=300, 
        blank=True,
        help_text="Ringkasan artikel"
    )
    
    # Metadata
    author = models.CharField(max_length=100, default='Admin')
    views = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Judul untuk SEO (opsional)"
    )
    meta_description = models.TextField(
        max_length=300, 
        blank=True,
        help_text="Deskripsi untuk SEO (opsional)"
    )
    
    # Status
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...'
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('games:article_detail', args=[self.slug])