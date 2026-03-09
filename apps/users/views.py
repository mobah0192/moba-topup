from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm, CustomUserChangeForm

def register_view(request):
    """Halaman registrasi user baru"""
    if request.user.is_authenticated:
        return redirect('games:list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # TAMBAHKAN 2 BARIS INI:
            from django.contrib.auth.backends import ModelBackend
            user.backend = f'{ModelBackend.__module__}.{ModelBackend.__name__}'
            
            login(request, user)
            messages.success(request, f'Selamat datang {user.username}! Akun Anda berhasil dibuat.')
            return redirect('games:list')
        else:
            messages.error(request, 'Ada kesalahan. Silakan periksa form Anda.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """Halaman login"""
    if request.user.is_authenticated:
        return redirect('games:list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang kembali, {username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('games:list')
            else:
                messages.error(request, 'Username atau password salah.')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('games:list')


@login_required
def profile_view(request):
    """Halaman profil user"""
    from apps.orders.models import Order
    from django.db.models import Sum
    
    orders = Order.objects.filter(user=request.user)
    recent_orders = orders.order_by('-created_at')[:5]
    total_orders = orders.count()
    total_spent = orders.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    success_orders = orders.filter(status='paid').count()
    pending_orders = orders.filter(status='pending').count()
    
    context = {
        'user': request.user,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'success_orders': success_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit_view(request):
    """Edit profil user"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Ada kesalahan. Silakan cek form Anda.')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})