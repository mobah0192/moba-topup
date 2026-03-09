from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, JsonResponse
from .models import Article, ArticleCategory, Game, GameItem

# ===== GAME VIEWS =====

def game_list(request):
    """
    Halaman utama menampilkan semua game yang tersedia
    """
    # Ambil semua game yang aktif dengan optimasi query
    games = Game.objects.filter(is_active=True).annotate(
        items_count=Count('categories__items', filter=Q(categories__items__is_active=True))
    ).prefetch_related('categories')
    
    # Untuk setiap game, ambil 3 item populer (optimasi)
    game_ids = [game.id for game in games]
    popular_items = GameItem.objects.filter(
        category__game_id__in=game_ids,
        is_popular=True,
        is_active=True
    ).select_related('category__game')[:10]
    
    # Map popular items ke game (untuk efisiensi)
    popular_items_map = {}
    for item in popular_items:
        game_id = item.category.game_id
        if game_id not in popular_items_map:
            popular_items_map[game_id] = []
        if len(popular_items_map[game_id]) < 3:
            popular_items_map[game_id].append(item)
    
    # Assign popular items ke game
    for game in games:
        game.popular_items = popular_items_map.get(game.id, [])
    
    # Ambil 3 artikel terbaru untuk ditampilkan di halaman utama
    latest_articles = Article.objects.filter(
        is_published=True
    ).select_related('category').order_by('-published_at')[:3]
    
    context = {
        'games': games,
        'latest_articles': latest_articles,  # <-- TAMBAHKAN INI
        'total_games': games.count(),
        'total_users': '10K+',
        'total_transactions': '5K+',
        'title': 'Daftar Game - MOBA TOPUP',
        'meta_description': 'Top up game termurah dan terpercaya di Indonesia. Tersedia berbagai game populer seperti Mobile Legends, Free Fire, PUBG, dan lainnya.'
    }
    return render(request, 'games/game_list.html', context)


def game_detail(request, slug):
    """
    Halaman detail game dengan daftar item yang bisa dibeli
    """

     # 🔐 Validasi slug (hanya huruf, angka, dan strip)
    import re
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        raise Http404("Game tidak ditemukan")
    
    game = get_object_or_404(
        Game.objects.prefetch_related('categories'), 
        slug=slug, 
        is_active=True
    )
    
    # Ambil semua kategori dan itemnya dengan optimasi
    categories = game.categories.prefetch_related(
        Prefetch(
            'items', 
            queryset=GameItem.objects.filter(is_active=True).order_by('price'),
            to_attr='active_items'
        )
    ).all()
    
    # Item populer
    popular_items = GameItem.objects.filter(
        category__game=game,
        is_popular=True,
        is_active=True
    ).select_related('category')[:6]
    
    # Item dengan harga termurah (untuk rekomendasi)
    cheapest_items = GameItem.objects.filter(
        category__game=game,
        is_active=True
    ).order_by('price')[:4]
    
    context = {
        'game': game,
        'categories': categories,
        'popular_items': popular_items,
        'cheapest_items': cheapest_items,
        'title': f'{game.name} - MOBA TOPUP',
        'meta_description': game.description[:160],
        'og_image': game.icon.url if game.icon else None
    }
    return render(request, 'games/game_detail.html', context)


def search_games(request):
    """
    Pencarian game dengan pagination
    """
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    games = Game.objects.filter(is_active=True)
    
    if query:
        games = games.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).order_by('name')
    else:
        games = games.order_by('name')[:50]
    
    # Pagination
    paginator = Paginator(games, 12)
    
    try:
        games_page = paginator.page(page)
    except PageNotAnInteger:
        games_page = paginator.page(1)
    except EmptyPage:
        games_page = paginator.page(paginator.num_pages)
    
    # Untuk setiap game, ambil 2 item populer untuk preview
    for game in games_page:
        game.popular_items = GameItem.objects.filter(
            category__game=game,
            is_popular=True,
            is_active=True
        ).select_related('category')[:2]
    
    context = {
        'games': games_page,
        'query': query,
        'title': f'Hasil Pencarian: {query}' if query else 'Semua Game',
        'meta_description': f'Hasil pencarian untuk "{query}" di MOBA TOPUP'
    }
    return render(request, 'games/search.html', context)


# ===== ARTICLE VIEWS =====

def article_list(request):
    """
    Daftar semua artikel dengan pagination
    """
    page = request.GET.get('page', 1)
    category_slug = request.GET.get('category')
    
    articles = Article.objects.filter(is_published=True).select_related('category')
    
    # Filter by category
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    
    # Order by tanggal terbaru
    articles = articles.order_by('-published_at', '-created_at')
    
    # Pagination
    paginator = Paginator(articles, 9)
    
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    # Categories with counts
    categories = ArticleCategory.objects.annotate(
        article_count=Count('articles', filter=Q(articles__is_published=True))
    ).filter(article_count__gt=0)
    
    # Artikel terbaru (untuk sidebar)
    recent_articles = Article.objects.filter(is_published=True).order_by('-published_at')[:5]
    
    # Artikel populer (berdasarkan views)
    popular_articles = Article.objects.filter(is_published=True).order_by('-views')[:5]
    
    context = {
        'articles': articles_page,
        'categories': categories,
        'recent_articles': recent_articles,
        'popular_articles': popular_articles,
        'current_category': category_slug,
        'title': 'Berita & Artikel Game Terbaru - MOBA TOPUP',
        'meta_description': 'Dapatkan informasi terbaru seputar game, tips & trik, dan update patch note dari berbagai game populer.'
    }
    return render(request, 'games/article_list.html', context)


def article_detail(request, slug):
    """
    Detail artikel dengan related articles
    """
    article = get_object_or_404(
        Article.objects.select_related('category'), 
        slug=slug, 
        is_published=True
    )
    
    # Increment views
    from django.db.models import F
    Article.objects.filter(id=article.id).update(views=F('views') + 1)
    article.refresh_from_db()
    
    # Artikel terkait (berdasarkan kategori)
    related_articles = Article.objects.filter(
        category=article.category, 
        is_published=True
    ).exclude(id=article.id).order_by('-published_at')[:3]
    
    # Artikel populer (untuk sidebar)
    popular_articles = Article.objects.filter(
        is_published=True
    ).exclude(id=article.id).order_by('-views')[:5]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'popular_articles': popular_articles,
        'title': f'{article.title} - MOBA TOPUP',
        'meta_description': article.excerpt or article.content[:160],
        'og_image': article.image.url if article.image else None
    }
    return render(request, 'games/article_detail.html', context)


def article_by_category(request, slug):
    """
    Artikel berdasarkan kategori
    """
    category = get_object_or_404(ArticleCategory, slug=slug)
    articles = Article.objects.filter(category=category, is_published=True)
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'games/article_by_category.html', context)


# ===== API ENDPOINTS (AJAX) =====

def get_game_items_api(request, game_id):
    """
    API endpoint untuk mendapatkan items game (untuk AJAX)
    """
    try:
        # 🔐 VALIDASI game_id
        try:
            game_id = int(game_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'ID game tidak valid'
            }, status=400)
        
        game = Game.objects.get(id=game_id, is_active=True)
        categories = game.categories.prefetch_related(
            Prefetch('items', queryset=GameItem.objects.filter(is_active=True))
        ).all()
        
        data = {
            'success': True,
            'game': {
                'id': game.id,
                'name': game.name,
                'slug': game.slug
            },
            'categories': []
        }
        
        for category in categories:
            cat_data = {
                'id': category.id,
                'name': category.name,
                'items': []
            }
            
            for item in category.items.all():
                cat_data['items'].append({
                    'id': item.id,
                    'name': item.name,
                    'amount': item.amount,
                    'price': str(item.price),
                    'is_popular': item.is_popular
                })
            
            data['categories'].append(cat_data)
        
        return JsonResponse(data)
        
    except Game.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Game tidak ditemukan'
        }, status=404)
    except Exception as e:
        # 🔐 Jangan expose error
        print(f"API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan internal'
        }, status=500)


def check_game_id_api(request):
    """
    API endpoint untuk validasi Game ID
    """
    game_id = request.GET.get('game_id', '').strip()
    game_type = request.GET.get('game_type', '').strip()
    
    # 🔐 Validasi input tidak kosong
    if not game_id or not game_type:
        return JsonResponse({
            'success': False,
            'error': 'Parameter tidak lengkap'
        }, status=400)
    
    # 🔐 Batasi panjang input
    if len(game_id) > 50 or len(game_type) > 50:
        return JsonResponse({
            'success': False,
            'error': 'Input terlalu panjang'
        }, status=400)
    
    # 🔐 Whitelist game_type
    allowed_game_types = ['mobile_legends', 'free_fire', 'pubg', 'others']
    if game_type not in allowed_game_types:
        return JsonResponse({
            'success': False,
            'error': 'Tipe game tidak valid'
        }, status=400)
    
    # Validasi berdasarkan jenis game
    is_valid = False
    message = ''
    
    if game_type == 'mobile_legends':
        is_valid = len(game_id) >= 8 and game_id.isdigit()
        message = 'ID Mobile Legends minimal 8 digit angka'
    elif game_type == 'free_fire':
        is_valid = len(game_id) >= 8 and game_id.isdigit()
        message = 'ID Free Fire minimal 8 digit angka'
    elif game_type == 'pubg':
        is_valid = len(game_id) >= 5
        message = 'ID PUBG minimal 5 karakter'
    else:
        is_valid = len(game_id) >= 5
        message = 'ID minimal 5 karakter'
    
    return JsonResponse({
        'success': True,
        'is_valid': is_valid,
        'message': message if not is_valid else 'ID valid'
    })


# ===== LEGACY / REDIRECT VIEWS =====

def garena_store(request):
    """
    Halaman khusus Garena Official Store
    """
    # Ambil game-game Garena
    garena_games = Game.objects.filter(
        name__icontains='garena',
        is_active=True
    ) | Game.objects.filter(
        name__in=['Free Fire', 'Delta Force']
    )
    
    context = {
        'title': 'Garena Official Store - MOBA TOPUP',
        'games': garena_games,
        'store_banner': True
    }
    return render(request, 'games/garena_store.html', context)