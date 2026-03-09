from django import forms
from .models import Order, PaymentMethod

class OrderForm(forms.Form):
    """Form untuk checkout (user login)"""
    game_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan ID Game'
        }),
        label='Game ID',
        required=True
    )
    game_server = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan Server (opsional)'
        }),
        label='Server'
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1
        }),
        label='Jumlah',
        required=True
    )
    
    # 🔴 PERBAIKI BAGIAN INI
    payment_method = forms.ChoiceField(
        choices=[],  # Akan diisi di __init__
        widget=forms.RadioSelect,
        required=True,
        label='Metode Pembayaran'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ambil metode pembayaran aktif dari database
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        choices = [(method.code, method.name) for method in payment_methods]
        self.fields['payment_method'].choices = choices
        print("=== PAYMENT METHOD CHOICES ===")  # Debug
        print(choices)  # Debug
    

class GuestCheckoutForm(forms.Form):
    """Form untuk checkout tanpa login (guest)"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan email Anda'
        }),
        label='Email'
    )
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nama (opsional)'
        }),
        label='Nama'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nomor telepon (opsional)'
        }),
        label='Nomor Telepon'
    )
    game_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan ID Game'
        }),
        label='Game ID'
    )
    game_server = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan Server (opsional)'
        }),
        label='Server'
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1
        }),
        label='Jumlah'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('midtrans', 'Midtrans'),
        ],
        widget=forms.RadioSelect,
        initial='midtrans',
        label='Metode Pembayaran'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email harus diisi')
        return email


class OrderStatusForm(forms.Form):
    """Form untuk cek status order"""
    invoice_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nomor invoice'
        }),
        label='Nomor Invoice'
    )