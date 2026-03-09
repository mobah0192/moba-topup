from django.utils import timezone
import random
import string

def format_rupiah(amount):
    """Format angka ke Rupiah (Rp 1.000.000)"""
    if amount is None:
        return "Rp 0"
    return f"Rp {amount:,.0f}".replace(',', '.')

def generate_invoice_number():
    """Generate nomor invoice unik"""
    today = timezone.now().strftime('%Y%m%d')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"INV-{today}-{random_chars}"