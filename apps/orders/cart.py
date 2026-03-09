from decimal import Decimal
from django.conf import settings
from apps.games.models import GameItem

class Cart:
    def __init__(self, request):
        """Inisialisasi cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # Simpan cart kosong ke session
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    
    def add(self, item, quantity=1, update_quantity=False):
        item_id = str(item.id)

        if item_id not in self.cart:
            self.cart[item_id] = {
                'quantity': 0,
                'price': str(item.price)
            }

        if update_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity

        self.save()
    
    def save(self):
        """Simpan cart ke session"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
    
    def remove(self, item):
        """Hapus item dari cart"""
        item_id = str(item.id)
        
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()
    
    def __iter__(self):
        """Iterasi item di cart"""
        item_ids = self.cart.keys()
        items = GameItem.objects.filter(id__in=item_ids)
        
        cart = self.cart.copy()
        
        for item in items:
            cart[str(item.id)]['item'] = item
        
        for item_id, item_data in cart.items():
            if 'item' in item_data:
                item_data['total_price'] = Decimal(item_data['price']) * item_data['quantity']
                yield item_data
    
    # 🟢 SATU METHOD __len__ SAJA
    def __len__(self):
        """
        MENGEMBALIKAN JUMLAH ITEM UNIK DI CART
        """
        return len(self.cart.keys())
    
    def get_total_price(self):
        """Hitung total harga semua item di cart"""
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def clear(self):
        """Kosongkan cart"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    # ===== METHOD YANG DIBUTUHKAN =====
    def get_items(self):
        """
        Mengembalikan list item di cart dengan detail lengkap
        Method ini yang dipanggil di views.py
        """
        items = []
        item_ids = self.cart.keys()
        
        # Ambil data item dari database
        game_items = GameItem.objects.filter(id__in=item_ids).select_related('category__game')
        
        # Buat mapping untuk akses cepat
        item_map = {str(item.id): item for item in game_items}
        
        for item_id, item_data in self.cart.items():
            if item_id in item_map:
                item = item_map[item_id]
                items.append({
                    'item': item,
                    'quantity': item_data['quantity'],
                    'price': Decimal(item_data['price']),
                    'total_price': Decimal(item_data['price']) * item_data['quantity'],
                    'game_name': item.category.game.name,
                    'category_name': item.category.name,
                    'item_name': item.name,
                    'item_amount': item.amount
                })
        
        return items
    
    def get_item_total(self, item_id):
        """Hitung total harga untuk item tertentu"""
        item_id = str(item_id)
        if item_id in self.cart:
            return Decimal(self.cart[item_id]['price']) * self.cart[item_id]['quantity']
        return 0
    
def __len__(self):
    """
    Mengembalikan JUMLAH ITEM UNIK di cart
    """
    return len(self.cart.keys())  # <-- PASTIKAN INI