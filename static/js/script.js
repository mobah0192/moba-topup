// ===== GLOBAL VARIABLES =====
let selectedItem = null;
let currentOrderId = null;

// ===== DOCUMENT READY =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 MOBA TOPUP App Loaded');
    
    // Inisialisasi semua komponen
    initNavbar();
    initCartFunctions();
    initGameDetail();
    initPaymentMethods();
    initOrderForm();
    initCopyButtons();
    initCountdown();
    initCategoryFilters();
    initBackToTop();
});

// ===== NAVBAR FUNCTIONS =====
function initNavbar() {
    // Active link
    const currentUrl = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
    
    // Brand animation refresh
    const brandText = document.querySelector('.brand-text');
    const brandHighlight = document.querySelector('.brand-text-highlight');
    
    if (brandText && brandHighlight) {
        setInterval(() => {
            brandText.style.animation = 'none';
            brandHighlight.style.animation = 'none';
            
            void brandText.offsetWidth;
            void brandHighlight.offsetWidth;
            
            brandText.style.animation = 'gradientShift 5s ease infinite';
            brandHighlight.style.animation = 'gradientShift 3s ease infinite';
        }, 10000);
    }
}

// ===== CART FUNCTIONS =====
function initCartFunctions() {
    updateCartCount();
    
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart, .btn-add-cart, .btn-add-cart-modern').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const itemId = this.dataset.itemId || this.closest('[data-item-id]')?.dataset.itemId;
            if (!itemId) return;
            
            addToCart(itemId);
        });
    });
    
    // Quantity update in cart
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.closest('[data-item-id]')?.dataset.itemId;
            const change = this.classList.contains('btn-minus') ? -1 : 1;
            if (itemId) updateQuantity(itemId, change);
        });
    });
    
    // Remove item
    document.querySelectorAll('.remove-item, .remove-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.closest('[data-item-id]')?.dataset.itemId;
            if (itemId) removeItem(itemId);
        });
    });
}

function addToCart(itemId) {
    const btn = event?.target.closest('button');
    const originalHtml = btn?.innerHTML;
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    fetch(`/orders/cart/add/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: 1 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item ditambahkan ke keranjang!', 'success');
            updateCartCount();
        } else {
            showNotification(data.error || 'Gagal menambahkan item', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Terjadi kesalahan', 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    });
}

function updateQuantity(itemId, change) {
    const item = document.querySelector(`[data-item-id="${itemId}"]`);
    const input = item?.querySelector('.quantity-input');
    if (!input) return;
    
    let quantity = parseInt(input.value) + change;
    if (quantity < 1) quantity = 1;
    
    const btn = event?.target;
    const originalHtml = btn?.innerHTML;
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    fetch(`/orders/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Jumlah berhasil diupdate', 'success');
            setTimeout(() => location.reload(), 500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Gagal mengupdate jumlah', 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    });
}

function removeItem(itemId) {
    if (!confirm('Hapus item ini dari keranjang?')) return;
    
    const btn = event?.target.closest('button');
    const originalHtml = btn?.innerHTML;
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    fetch(`/orders/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item dihapus dari keranjang', 'success');
            setTimeout(() => location.reload(), 500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Gagal menghapus item', 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    });
}

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (!cartCount) return;
    
    fetch('/orders/cart/count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                cartCount.textContent = data.count;
                cartCount.classList.remove('d-none');
                
                document.querySelectorAll('.cart-count-mobile').forEach(el => {
                    el.textContent = data.count;
                    el.classList.remove('d-none');
                });
            } else {
                cartCount.classList.add('d-none');
                document.querySelectorAll('.cart-count-mobile').forEach(el => {
                    el.classList.add('d-none');
                });
            }
        })
        .catch(error => console.error('Error updating cart count:', error));
}

// ===== GAME DETAIL PAGE FUNCTIONS =====
function initGameDetail() {
    const itemCards = document.querySelectorAll('.item-card, .item-card-modern');
    const selectedItemId = document.getElementById('selected-item-id');
    const submitBtn = document.getElementById('submit-order');
    const gameIdInput = document.querySelector('.game-id-input');
    const quantityInput = document.getElementById('quantity-input');
    
    // Item selection
    itemCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('button')) return;
            
            itemCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            if (selectedItemId) {
                selectedItemId.value = this.dataset.itemId;
                
                // Update preview if exists
                const previewName = document.getElementById('selectedItemName');
                const previewPrice = document.getElementById('selectedItemPrice');
                if (previewName && previewPrice) {
                    previewName.textContent = this.dataset.itemName;
                    previewPrice.textContent = `Rp ${formatNumber(this.dataset.itemPrice)}`;
                    
                    document.querySelector('.no-selection')?.style.display = 'none';
                    document.querySelector('.selected-item-detail')?.style.display = 'block';
                }
            }
            
            updateCheckoutButton();
            updateTotalPrice();
        });
    });
    
    // Game ID validation
    if (gameIdInput) {
        gameIdInput.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (value.length >= 5) {
                this.classList.add('valid');
                this.classList.remove('error');
            } else {
                this.classList.remove('valid');
                this.classList.add('error');
            }
            
            updateCheckoutButton();
        });
    }
    
    // Quantity buttons
    if (quantityInput) {
        document.querySelectorAll('.quantity-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const change = this.classList.contains('btn-minus') ? -1 : 1;
                let value = parseInt(quantityInput.value) + change;
                if (value < 1) value = 1;
                quantityInput.value = value;
                updateTotalPrice();
            });
        });
    }
    
    function updateCheckoutButton() {
        if (!submitBtn) return;
        
        const itemSelected = selectedItemId?.value;
        const gameIdValid = gameIdInput?.value.trim().length >= 5;
        
        submitBtn.disabled = !(itemSelected && gameIdValid);
    }
    
    function updateTotalPrice() {
        const totalElement = document.getElementById('totalPrice');
        if (!totalElement) return;
        
        const selectedCard = document.querySelector('.item-card.selected, .item-card-modern.selected');
        if (!selectedCard) return;
        
        const price = parseFloat(selectedCard.dataset.itemPrice);
        const quantity = parseInt(quantityInput?.value || 1);
        const total = price * quantity;
        
        totalElement.textContent = `Rp ${formatNumber(total)}`;
    }
}

// ===== PAYMENT METHODS =====
function initPaymentMethods() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (!radio) return;
            
            radio.checked = true;
            paymentMethods.forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
            
            const instructionsDiv = document.getElementById('payment-instructions');
            if (!instructionsDiv) return;
            
            let instructions = '';
            if (radio.value === 'midtrans') {
                instructions = `
                    <div class="payment-instructions fade-in">
                        <h5><i class="fas fa-credit-card me-2"></i>Pembayaran via Midtrans</h5>
                        <ol>
                            <li>Klik tombol "Bayar Sekarang"</li>
                            <li>Anda akan diarahkan ke halaman pembayaran Midtrans</li>
                            <li>Pilih metode pembayaran yang diinginkan</li>
                            <li>Selesaikan pembayaran sesuai instruksi</li>
                        </ol>
                    </div>
                `;
            } else if (radio.value === 'balance') {
                instructions = `
                    <div class="payment-instructions fade-in">
                        <h5><i class="fas fa-wallet me-2"></i>Pembayaran via Saldo</h5>
                        <ol>
                            <li>Pastikan saldo Anda mencukupi</li>
                            <li>Klik tombol "Bayar Sekarang"</li>
                            <li>Saldo akan langsung dipotong</li>
                        </ol>
                    </div>
                `;
            }
            
            instructionsDiv.innerHTML = instructions;
        });
    });
}

// ===== ORDER FORM =====
function initOrderForm() {
    const orderForm = document.getElementById('order-form');
    if (!orderForm) return;
    
    orderForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const gameId = document.getElementById('game_id')?.value;
        const selectedPayment = document.querySelector('input[name="payment_method"]:checked');
        const selectedItem = document.getElementById('selected-item-id')?.value;
        
        if (!gameId || gameId.length < 5) {
            showNotification('ID Game tidak valid', 'error');
            return;
        }
        
        if (!selectedPayment) {
            showNotification('Pilih metode pembayaran', 'error');
            return;
        }
        
        if (!selectedItem) {
            showNotification('Pilih item yang akan dibeli', 'error');
            return;
        }
        
        showLoading();
        
        setTimeout(() => {
            hideLoading();
            this.submit();
        }, 1000);
    });
}

// ===== COPY BUTTONS =====
function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const textToCopy = this.dataset.copyText || this.previousElementSibling?.textContent;
            if (!textToCopy) return;
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                showNotification('Berhasil disalin!', 'success');
                
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Tersalin!';
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });
}

// ===== COUNTDOWN TIMER =====
function initCountdown() {
    const hoursEl = document.getElementById('hours');
    const minutesEl = document.getElementById('minutes');
    const secondsEl = document.getElementById('seconds');
    
    if (!hoursEl || !minutesEl || !secondsEl) return;
    
    const endTime = new Date();
    endTime.setHours(endTime.getHours() + 24);
    
    function updateTimer() {
        const now = new Date();
        const diff = endTime - now;
        
        if (diff <= 0) {
            endTime.setHours(endTime.getHours() + 24);
        }
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        hoursEl.textContent = String(hours).padStart(2, '0');
        minutesEl.textContent = String(minutes).padStart(2, '0');
        secondsEl.textContent = String(seconds).padStart(2, '0');
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

// ===== CATEGORY FILTERS =====
function initCategoryFilters() {
    document.querySelectorAll('.category-filter, .category-pill').forEach(filter => {
        filter.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.querySelectorAll('.category-filter, .category-pill').forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            // Add filter logic here
            showNotification(`Filter: ${this.textContent}`, 'info');
        });
    });
}

// ===== BACK TO TOP =====
function initBackToTop() {
    const backToTop = document.getElementById('backToTop');
    if (!backToTop) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('show');
        } else {
            backToTop.classList.remove('show');
        }
    });
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ===== LOADING SPINNER =====
function showLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.classList.add('active');
    }
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.classList.remove('active');
    }
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'success') {
    // Try using toast notification first
    const toast = document.getElementById('toastNotification');
    if (toast) {
        const toastMessage = document.getElementById('toastMessage');
        if (toastMessage) toastMessage.textContent = message;
        
        toast.className = `toast-modern show ${type}`;
        
        setTimeout(() => {
            toast.className = 'toast-modern';
        }, 3000);
        return;
    }
    
    // Fallback to custom notification
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = `message-item message-${type}`;
    notification.innerHTML = `
        <div class="message-icon"><i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i></div>
        <div class="message-content">${message}</div>
        <button class="message-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// ===== UTILITY FUNCTIONS =====
function formatNumber(number) {
    return new Intl.NumberFormat('id-ID').format(number);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== CHECKOUT FUNCTION =====
function checkout() {
    const btn = document.querySelector('.btn-checkout');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';
    }
    
    setTimeout(() => {
        window.location.href = '/orders/checkout/';
    }, 500);
}

// ===== RELATED ITEMS ADD =====
document.querySelectorAll('.related-add').forEach(btn => {
    btn.addEventListener('click', function() {
        // Parse item info from card
        const game = this.closest('.related-card')?.querySelector('.related-game')?.textContent;
        const item = this.closest('.related-card')?.querySelector('.related-item')?.textContent;
        
        showNotification(`Menambahkan ${item} dari ${game}`, 'success');
        
        // Simulate add to cart
        setTimeout(() => {
            updateCartCount();
        }, 500);
    });
});

// ===== TOOLTIP INIT (for Bootstrap 5) =====
document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(tooltip => {
    new bootstrap.Tooltip(tooltip);
});

console.log('✅ All scripts initialized');


// Show payment category
function showPaymentCategory(category) {
    // Update active class on buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Hide all categories
    document.getElementById('bank-payments').classList.remove('active');
    document.getElementById('ewallet-payments').classList.remove('active');
    document.getElementById('qris-payments').classList.remove('active');
    
    // Show selected category
    if (category === 'all') {
        document.getElementById('bank-payments').classList.add('active');
        document.getElementById('ewallet-payments').classList.add('active');
        document.getElementById('qris-payments').classList.add('active');
    } else if (category === 'bank') {
        document.getElementById('bank-payments').classList.add('active');
    } else if (category === 'ewallet') {
        document.getElementById('ewallet-payments').classList.add('active');
    } else if (category === 'qris') {
        document.getElementById('qris-payments').classList.add('active');
    }
}

// Initialize - show all by default
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('bank-payments').classList.add('active');
    document.getElementById('ewallet-payments').classList.add('active');
    document.getElementById('qris-payments').classList.add('active');
});

function filterPayments(category) {
    // Update active class
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter cards
    const cards = document.querySelectorAll('.payment-card');
    cards.forEach(card => {
        if (category === 'all' || card.dataset.category === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}