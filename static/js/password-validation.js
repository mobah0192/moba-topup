document.addEventListener('DOMContentLoaded', function() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    
    if (!password1) return;
    
    function validatePassword() {
        const password = password1.value;
        
        // Length check
        const lengthReq = document.getElementById('req-length');
        if (lengthReq) {
            if (password.length >= 8) {
                lengthReq.className = 'valid';
                lengthReq.innerHTML = '<i class="fas fa-check-circle"></i> Minimal 8 karakter ✓';
            } else {
                lengthReq.className = 'invalid';
                lengthReq.innerHTML = '<i class="fas fa-times-circle"></i> Minimal 8 karakter';
            }
        }
        
        // Numbers only check
        const numberReq = document.getElementById('req-number');
        if (numberReq) {
            if (/^\d+$/.test(password) && password.length > 0) {
                numberReq.className = 'invalid';
                numberReq.innerHTML = '<i class="fas fa-times-circle"></i> Tidak boleh hanya angka';
            } else if (password.length > 0) {
                numberReq.className = 'valid';
                numberReq.innerHTML = '<i class="fas fa-check-circle"></i> Tidak boleh hanya angka ✓';
            } else {
                numberReq.className = '';
                numberReq.innerHTML = '<i class="fas fa-circle"></i> Tidak boleh hanya angka';
            }
        }
        
        // Common password check
        const commonReq = document.getElementById('req-common');
        if (commonReq) {
            const commonPasswords = ['password', '12345678', 'qwerty123', 'admin123', 'password123'];
            if (commonPasswords.includes(password.toLowerCase()) && password.length > 0) {
                commonReq.className = 'invalid';
                commonReq.innerHTML = '<i class="fas fa-times-circle"></i> Tidak boleh password umum';
            } else if (password.length > 0) {
                commonReq.className = 'valid';
                commonReq.innerHTML = '<i class="fas fa-check-circle"></i> Tidak boleh password umum ✓';
            } else {
                commonReq.className = '';
                commonReq.innerHTML = '<i class="fas fa-circle"></i> Tidak boleh password umum';
            }
        }
        
        // Update confirm password validation
        if (password2 && password2.value) {
            validateConfirmPassword();
        }
    }
    
    function validateConfirmPassword() {
        if (!password2) return;
        
        if (password1.value !== password2.value) {
            password2.setCustomValidity('Password tidak cocok');
            password2.classList.add('error');
            password2.classList.remove('valid');
        } else {
            password2.setCustomValidity('');
            password2.classList.remove('error');
            password2.classList.add('valid');
        }
    }
    
    // Event listeners
    password1.addEventListener('input', validatePassword);
    password1.addEventListener('keyup', validatePassword);
    
    if (password2) {
        password2.addEventListener('input', validateConfirmPassword);
        password2.addEventListener('keyup', validateConfirmPassword);
    }
    
    // Initial validation
    validatePassword();
});