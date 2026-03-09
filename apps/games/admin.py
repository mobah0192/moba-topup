from django.contrib import admin
from .models import Game, GameCategory, GameItem, Article, ArticleCategory

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Informasi Game', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('icon', 'banner'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['game', 'name']
    list_filter = ['game']
    search_fields = ['name']


@admin.register(GameItem)
class GameItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'amount', 'price', 'discount_price', 'is_popular', 'is_active']
    list_filter = ['category__game', 'is_popular', 'is_active']
    search_fields = ['name']
    list_editable = ['price', 'discount_price', 'is_popular']
    fieldsets = (
        ('Informasi Item', {
            'fields': ('category', 'name', 'amount')
        }),
        ('Harga', {
            'fields': ('price', 'discount_price')
        }),
        ('Status', {
            'fields': ('is_popular', 'is_active', 'stock')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('wide',)
        }),
    )


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'created_at']  # SEKARANG FIELD INI ADA
    list_filter = ['color']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'views', 'is_published', 'published_at']
    list_filter = ['category', 'is_published', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Artikel', {
            'fields': ('title', 'slug', 'category', 'game', 'image', 'content', 'excerpt', 'author')
        }),
        ('Status', {
            'fields': ('is_published', 'published_at', 'views')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),  # SEKARANG FIELD INI ADA
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )