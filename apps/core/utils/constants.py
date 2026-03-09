ORDER_STATUS = {
    'PENDING': 'pending',
    'PAID': 'paid',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'EXPIRED': 'expired',
}

ORDER_STATUS_CHOICES = [
    ('pending', 'Menunggu Pembayaran'),
    ('paid', 'Sudah Dibayar'),
    ('processing', 'Sedang Diproses'),
    ('completed', 'Selesai'),
    ('failed', 'Gagal'),
    ('expired', 'Kadaluarsa'),
]

PAYMENT_METHODS = [
    ('balance', 'Saldo'),
    ('midtrans', 'Midtrans'),
]