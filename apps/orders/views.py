import json
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.paginator import Paginator
from urllib3 import request

from apps.games.models import Game, GameItem
from .models import Order
from .forms import OrderForm, GuestCheckoutForm
from .cart import Cart
from .services.midtrans_service import MidtransService
from .models import PaymentMethod


# ===== CART VIEWS =====

def cart_detail(request):
    """
    Menampilkan isi keranjang
    """
    cart = Cart(request)
    
    context = {
        'cart': cart,
        'cart_items': cart.get_items(),
        'cart_total': cart.get_total_price(),
        'title': 'Keranjang Belanja - MOBA TOPUP'
    }
    return render(request, 'orders/cart_detail.html', context)


@require_http_methods(["POST"])
def cart_add(request, item_id):
    """
    Tambah item ke cart via AJAX
    """
    try:
        # 🔐 VALIDASI TIPE DATA item_id
        try:
            item_id = int(item_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'ID item tidak valid'
            }, status=400)
        
        item = get_object_or_404(GameItem, id=item_id, is_active=True)
        
        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Data tidak valid'
            }, status=400)
        
        if quantity < 1 or quantity > 99:  # 🔐 Batasi quantity maksimal
            return JsonResponse({
                'success': False,
                'error': 'Quantity harus antara 1-99'
            }, status=400)
        
        # Get or create cart
        cart = Cart(request)
        
        # Add item to cart
        cart.add(
            item=item,
            quantity=quantity,
            update_quantity=data.get('update_quantity', False)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{item.name} ditambahkan ke keranjang',
            'cart_count': len(cart),
            'cart_total': float(cart.get_total_price())
        })
        
    except Http404:
        return JsonResponse({
            'success': False,
            'error': 'Item tidak ditemukan'
        }, status=404)
    except Exception as e:
        # 🔐 Jangan expose error details ke user
        print(f"Cart add error: {e}")  # Log untuk debugging
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan internal'
        }, status=500)

    
@require_http_methods(["POST"])
def cart_update(request, item_id):
    """
    Update quantity item di cart
    """
    try:
        # 🔐 VALIDASI TIPE DATA item_id
        try:
            item_id = int(item_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'ID item tidak valid'
            }, status=400)
        
        item = get_object_or_404(GameItem, id=item_id)
        cart = Cart(request)
        
        # 🔐 Get quantity with validation
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                quantity = int(data.get('quantity', 1))
            else:
                quantity = int(request.POST.get('quantity', 1))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Quantity tidak valid'
            }, status=400)
        
        # 🔐 Validate quantity range
        if quantity < 0 or quantity > 99:
            return JsonResponse({
                'success': False,
                'error': 'Quantity harus antara 0-99'
            }, status=400)
        
        if quantity <= 0:
            cart.remove(item)
            message = 'Item dihapus dari keranjang'
        else:
            cart.add(item=item, quantity=quantity, update_quantity=True)
            message = 'Jumlah berhasil diupdate'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': len(cart),
            'cart_total': float(cart.get_total_price()),
            'item_total': float(cart.get_item_total(item_id))
        })
        
    except GameItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item tidak ditemukan'
        }, status=404)
    except Exception as e:
        print(f"Cart update error: {e}")  # Log internal
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan internal'
        }, status=500)

@require_http_methods(["POST"])
def cart_remove(request, item_id):
    """
    Menghapus item dari cart
    """
    try:
        # 🔐 VALIDASI TIPE DATA item_id
        try:
            item_id = int(item_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'ID item tidak valid'
            }, status=400)
        
        item = get_object_or_404(GameItem, id=item_id)
        cart = Cart(request)
        
        cart.remove(item)
        
        return JsonResponse({
            'success': True,
            'message': 'Item dihapus dari keranjang',
            'cart_count': len(cart),
            'cart_total': float(cart.get_total_price())
        })
        
    except GameItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item tidak ditemukan'
        }, status=404)
    except Exception as e:
        print(f"Cart remove error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan internal'
        }, status=500)

def cart_count(request):
    """
    Mengembalikan jumlah item di cart (untuk AJAX)
    """
    cart = Cart(request)
    return JsonResponse({
        'count': len(cart),
        'total': cart.get_total_price()
    })


# ===== CHECKOUT VIEWS =====

@login_required
def checkout(request):
    """
    Halaman checkout untuk user yang sudah login
    """
    cart = Cart(request)
    
    # CEK APAKAH ADA PARAMETER ITEM_ID (UNTUK BELI LANGSUNG)
    item_id = request.GET.get('item_id')
    game_id_param = request.GET.get('game_id')
    quantity_param = request.GET.get('quantity', 1)
    
    if item_id and game_id_param:
        try:  # ← TRY PERTAMA
            # 🔐 VALIDASI item_id
            try:  # ← TRY KEDUA (untuk konversi)
                item_id_int = int(item_id)
                quantity = int(quantity_param)
            except (ValueError, TypeError):
                messages.error(request, 'Parameter tidak valid')
                return redirect('orders:cart_detail')
            
            # 🔐 Batasi quantity
            if quantity < 1 or quantity > 99:
                messages.error(request, 'Quantity harus antara 1-99')
                return redirect('orders:cart_detail')
            
            item = get_object_or_404(GameItem, id=item_id_int, is_active=True)
            cart.add(item=item, quantity=quantity)
            
            # Simpan game_id ke session untuk pre-fill
            request.session['last_game_id'] = game_id_param
            request.session['last_quantity'] = quantity
            
            messages.info(request, 'Item ditambahkan ke keranjang. Silakan lanjutkan checkout.')
            
        except Exception as e:  # ← EXCEPT UNTUK TRY PERTAMA
            print(f"Error adding item to cart: {e}")
            messages.error(request, 'Terjadi kesalahan. Silakan coba lagi.')
            return redirect('orders:cart_detail')
    
    if len(cart) == 0:
        messages.warning(request, 'Keranjang belanja Anda kosong')
        return redirect('games:list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            return _process_checkout(request, cart, form.cleaned_data)
        else:
            messages.error(request, 'Ada kesalahan dalam form. Silakan cek kembali.')
    else:
        # Pre-fill form dengan data dari session
        initial_data = {
            'game_id': request.session.get('last_game_id', ''),
            'game_server': request.session.get('last_game_server', ''),
            'quantity': request.session.get('last_quantity', 1),
        }
        form = OrderForm(initial=initial_data)
    
    payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('sort_order')
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.get_items(),
        'cart_total': cart.get_total_price(),
        'payment_methods': payment_methods,
        'title': 'Checkout - MOBA TOPUP'
    }
    return render(request, 'orders/checkout.html', context)

def guest_checkout(request):
    """
    Checkout tanpa login
    """
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Keranjang belanja Anda kosong')
        return redirect('games:list')
    
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        if form.is_valid():
            # Simpan email guest ke session
            request.session['guest_email'] = form.cleaned_data['email']
            request.session['guest_name'] = form.cleaned_data.get('name', 'Guest')
            
            return _process_checkout(
                request, 
                cart, 
                form.cleaned_data,
                is_guest=True
            )
        else:
            messages.error(request, 'Ada kesalahan dalam form. Silakan cek kembali.')
    else:
        form = GuestCheckoutForm()
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.get_items(),
        'cart_total': cart.get_total_price(),
        'title': 'Guest Checkout - MOBA TOPUP'
    }
    return render(request, 'orders/guest_checkout.html', context)



def _process_checkout(request, cart, data, is_guest=False):
    """
    Proses checkout (internal function)
    """
    try:
        # 🔐 VALIDASI DATA SEBELUM DIPROSES
        # Pastikan tidak ada field mencurigakan
        allowed_fields = ['game_id', 'game_server', 'quantity', 'payment_method', 'email', 'name', 'phone']
        for key in data.keys():
            if key not in allowed_fields:
                print(f"⚠️ PERINGATAN: Field tidak dikenal dalam checkout: {key}")
                messages.error(request, 'Data tidak valid')
                return redirect('orders:cart_detail')
        
        # 🔐 VALIDASI quantity
        if data.get('quantity', 1) < 1 or data.get('quantity', 1) > 99:
            messages.error(request, 'Quantity tidak valid')
            return redirect('orders:cart_detail')
        
        # 🔐 VALIDASI game_id (hanya alfanumerik)
        import re
        game_id = data.get('game_id', '')
        if not re.match(r'^[a-zA-Z0-9_\-]+$', game_id):
            messages.error(request, 'Game ID mengandung karakter tidak valid')
            return redirect('orders:cart_detail')
        
        print("="*50)
        print("🚀 MEMULAI PROCESS CHECKOUT")
        print(f"Data: {data}")
        print(f"Cart items: {len(cart.get_items())}")
        print("="*50)
        
        with transaction.atomic():
            orders = []
            
            for idx, cart_item in enumerate(cart.get_items()):
                item = cart_item['item']
                
                print(f"🔄 Memproses item ke-{idx+1}: {item.name} (ID: {item.id})")
                print(f"   Quantity: {cart_item['quantity']}")
                print(f"   Price: {item.price}")
                
                # Buat order
                order = Order(
                    user=None if is_guest else request.user,
                    game_item=item,
                    game_id=data['game_id'],
                    game_server=data.get('game_server', ''),
                    quantity=cart_item['quantity'],
                    price=Decimal(str(item.price)),
                    total_amount=Decimal(str(item.price)) * cart_item['quantity'],
                    payment_method=data.get('payment_method', 'midtrans'),
                    status='pending',
                    #customer_email=data.get('email') if is_guest else request.user.email,
                    #customer_name=data.get('name', request.user.username) if not is_guest else data.get('name', 'Guest'),
                    #customer_phone=data.get('phone', '')
                )
                order.save()
                orders.append(order)
                print(f"✅ Order created: {order.invoice_number}")
            
            # Simpan game_id terakhir ke session
            request.session['last_game_id'] = data['game_id']
            if data.get('game_server'):
                request.session['last_game_server'] = data['game_server']
            
            # Kosongkan cart
            cart.clear()
            print("✅ Cart cleared")
            
            messages.success(
                request, 
                f'Berhasil membuat {len(orders)} order! Silakan lakukan pembayaran.'
            )
            
            # Redirect ke pembayaran
            if len(orders) == 1:
                redirect_url = reverse('orders:payment', args=[orders[0].invoice_number])
                print(f"✅ Redirect ke: {redirect_url}")
                return redirect('orders:payment', invoice_number=orders[0].invoice_number)
            else:
                print(f"✅ Redirect ke order list")
                return redirect('orders:list')
                
    except Exception as e:
        print("="*50)
        print("💥 EXCEPTION TERJADI:")
        import traceback
        traceback.print_exc()
        print("="*50)
        
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('orders:cart_detail')

# ===== ORDER VIEWS =====

@login_required
def order_list(request):
    """
    Halaman daftar order user
    """
    # Filter orders
    status = request.GET.get('status', '')
    
    orders = Order.objects.filter(user=request.user)
    
    if status:
        orders = orders.filter(status=status)
    
    # Order by newest first
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)
    
    # Count by status
    status_counts = {
        'pending': Order.objects.filter(user=request.user, status='pending').count(),
        'paid': Order.objects.filter(user=request.user, status='paid').count(),
        'processing': Order.objects.filter(user=request.user, status='processing').count(),
        'completed': Order.objects.filter(user=request.user, status='completed').count(),
        'failed': Order.objects.filter(user=request.user, status='failed').count(),
    }
    
    context = {
        'orders': orders_page,
        'status_counts': status_counts,
        'current_status': status,
        'title': 'Riwayat Topup - MOBA TOPUP'
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, invoice_number):
    """
    Halaman detail order
    """
    order = get_object_or_404(
        Order.objects.select_related('game_item__category__game'),
        invoice_number=invoice_number,
        user=request.user
    )
    
    context = {
        'order': order,
        'title': f'Order {order.invoice_number} - MOBA TOPUP'
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_cancel(request, invoice_number):
    """
    Batalkan order (hanya jika masih pending)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        order = Order.objects.get(invoice_number=invoice_number)
        
        # Cek akses
        if order.user and order.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        if order.status == 'pending':
            order.status = 'expired'
            order.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False, 
                'error': f'Order tidak dapat dibatalkan karena status {order.get_status_display()}'
            })
            
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)

@login_required
def order_confirm(request, invoice_number):
    """
    Konfirmasi order (misal untuk topup manual)
    """
    if request.method != 'POST':
        return redirect('orders:detail', invoice_number=invoice_number)
    
    order = get_object_or_404(
        Order,
        invoice_number=invoice_number,
        user=request.user
    )
    
    if order.status == 'paid':
        order.status = 'completed'
        order.save()
        messages.success(request, 'Order dikonfirmasi. Terima kasih!')
    else:
        messages.error(request, 'Order belum dibayar.')
    
    return redirect('orders:detail', invoice_number=order.invoice_number)


# ===== PAYMENT VIEWS =====

@login_required
def order_payment(request, invoice_number):
    """
    Halaman pembayaran order dengan Midtrans
    """
    order = get_object_or_404(
        Order.objects.select_related('game_item__category__game'),
        invoice_number=invoice_number,
        user=request.user
    )
    
    # Jika order sudah dibayar, redirect ke detail
    if order.status != 'pending':
        messages.warning(request, f'Order ini sudah {order.get_status_display()}.')
        return redirect('orders:detail', invoice_number=order.invoice_number)
    
    # Inisialisasi Midtrans
    midtrans = MidtransService()
    
    # Cek apakah sudah punya payment_url
    if not order.payment_url:
        # Buat transaksi baru
        result = midtrans.create_transaction(order, request)
        
        if result['success']:
            # Update order dengan payment_url
            order.payment_url = result['redirect_url']
            order.midtrans_order_id = result['order_id']
            order.save()
        else:
            messages.error(request, f'Gagal membuat pembayaran: {result.get("error")}')
            return redirect('orders:detail', invoice_number=order.invoice_number)
    
    context = {
        'order': order,
        'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY,
        'midtrans_snap_url': settings.MIDTRANS_SNAP_URL,
        'title': f'Pembayaran - {order.invoice_number}'
    }
    return render(request, 'orders/order_payment.html', context)


@login_required
def payment_finish(request, invoice_number):
    """
    Halaman setelah pembayaran selesai (redirect dari Midtrans)
    """
    order = get_object_or_404(Order, invoice_number=invoice_number, user=request.user)
    messages.success(request, 'Pembayaran berhasil! Pesanan sedang diproses.')
    return redirect('orders:detail', invoice_number=order.invoice_number)


@login_required
def payment_unfinish(request, invoice_number):
    """
    Halaman jika pembayaran belum selesai (redirect dari Midtrans)
    """
    order = get_object_or_404(Order, invoice_number=invoice_number, user=request.user)
    messages.warning(request, 'Pembayaran belum selesai. Silakan coba lagi.')
    return redirect('orders:payment', invoice_number=order.invoice_number)


@login_required
def payment_error(request, invoice_number):
    """
    Halaman jika terjadi error pembayaran (redirect dari Midtrans)
    """
    order = get_object_or_404(Order, invoice_number=invoice_number, user=request.user)
    messages.error(request, 'Terjadi kesalahan dalam pembayaran. Silakan coba lagi.')
    return redirect('orders:payment', invoice_number=order.invoice_number)


# ===== API VIEWS =====

@login_required
def get_order_status(request, invoice_number):
    """
    API untuk cek status order (via AJAX)
    """
    try:
        order = Order.objects.get(
            invoice_number=invoice_number,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'status': order.status,
            'status_display': order.get_status_display(),
            'invoice_number': order.invoice_number,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None,
            'payment_url': order.payment_url
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order tidak ditemukan'
        }, status=404)


@login_required
def check_payment_status(request, invoice_number):
    """
    API untuk mengecek status pembayaran via AJAX
    """
    try:
        order = Order.objects.get(
            invoice_number=invoice_number,
            user=request.user
        )
        
        # Jika status masih pending, cek ke Midtrans
        if order.status == 'pending' and order.midtrans_order_id:
            midtrans = MidtransService()
            result = midtrans.check_transaction_status(order.midtrans_order_id)
            
            if result['success']:
                # Update status berdasarkan response Midtrans
                transaction_status = result['data']['transaction_status']
                
                if transaction_status in ['capture', 'settlement']:
                    order.status = 'paid'
                    order.paid_at = timezone.now()
                    order.save()
                elif transaction_status in ['deny', 'expire', 'cancel']:
                    order.status = 'failed'
                    order.save()
        
        return JsonResponse({
            'success': True,
            'status': order.status,
            'status_display': order.get_status_display(),
            'invoice_number': order.invoice_number,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None,
            'payment_url': order.payment_url
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order tidak ditemukan'
        }, status=404)


# ===== WEBHOOK VIEWS =====

@csrf_exempt
@require_http_methods(["POST"])
def midtrans_webhook(request):
    """
    Webhook untuk notifikasi pembayaran dari Midtrans
    Tidak perlu login karena dipanggil oleh Midtrans
    """
    try:
        # Parse JSON body
        notification_body = json.loads(request.body)
        
        # 🔴 DEBUG PRINT
        print("="*50)
        print("WEBHOOK RECEIVED:")
        print(notification_body)
        print("="*50)
        
        # Handle notifikasi
        midtrans = MidtransService()
        result = midtrans.handle_webhook_notification(notification_body)
        
        # 🔴 DEBUG PRINT
        print("MIDTRANS SERVICE RESULT:")
        print(result)
        print("="*50)
        
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result.get('error')
            }, status=400)
        
        # Cari order berdasarkan midtrans_order_id
        order_id = result['order_id']
        
        try:
            # Cari order
            order = Order.objects.get(midtrans_order_id=order_id)
            
            # Update status order
            order.status = result['new_status']
            if result['new_status'] == 'paid':
                order.paid_at = timezone.now()
            
            order.save()
            
            print(f"✅ Order {order.invoice_number} updated to {order.status}")
            
            return JsonResponse({
                'success': True,
                'status': 'ok'
            })
            
        except Order.DoesNotExist:
            print(f"❌ Order with midtrans_order_id {order_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Order not found'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ===== LEGACY VIEWS (untuk backward compatibility) =====

def order_create(request, game_slug): 
    """
    Legacy view - redirect ke halaman game detail
    """
    from apps.games.models import Game
    
    # Ambil game berdasarkan slug
    game = get_object_or_404(Game, slug=game_slug)
    
    messages.info(request, 'Silakan gunakan tombol "Keranjang" atau "Beli Langsung" untuk menambah item')
    
    # Redirect ke halaman detail game
    return redirect('games:detail', slug=game.slug)