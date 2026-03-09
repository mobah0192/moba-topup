document.addEventListener('DOMContentLoaded', function() {
    console.log('Music.js loaded');
    
    const bgMusic = document.getElementById('bgMusic');
    const musicIcon = document.getElementById('musicIcon');
    const musicStatus = document.getElementById('musicStatus');
    const volumeControl = document.getElementById('volumeControl');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumePercent = document.getElementById('volumePercent');
    
    // CEK APAKAH ELEMEN DITEMUKAN
    console.log('bgMusic element:', bgMusic);
    console.log('musicIcon element:', musicIcon);
    
    if (!bgMusic) {
        console.error('Elemen audio tidak ditemukan!');
        return;
    }
    
    // CEK SOURCE AUDIO
    const sources = bgMusic.getElementsByTagName('source');
    console.log('Audio sources:', sources.length);
    for (let i = 0; i < sources.length; i++) {
        console.log(`Source ${i}:`, sources[i].src);
    }
    
    // Set initial volume
    bgMusic.volume = volumeSlider ? volumeSlider.value : 0.3;
    bgMusic.loop = true;
    
    // Fungsi untuk play musik
    function playMusic() {
        console.log('Mencoba memutar musik...');
        
        // Cek apakah audio siap
        console.log('Audio readyState:', bgMusic.readyState);
        console.log('Audio paused:', bgMusic.paused);
        
        // Promise play
        const playPromise = bgMusic.play();
        
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    console.log('✓ Musik berhasil diputar');
                    if (musicIcon) musicIcon.className = 'fas fa-pause';
                    if (musicStatus) musicStatus.textContent = 'Jeda Musik';
                    if (volumeControl) volumeControl.classList.add('show');
                    
                    // Tambah class playing
                    const musicControl = document.querySelector('.music-control');
                    if (musicControl) musicControl.classList.add('playing');
                    
                    localStorage.setItem('music_playing', 'true');
                })
                .catch(error => {
                    console.error('✗ Gagal memutar musik:', error);
                    console.log('Alasan:', error.name, error.message);
                    
                    if (musicStatus) {
                        musicStatus.textContent = 'Klik untuk putar';
                    }
                });
        }
    }
    
    // Fungsi untuk pause musik
    function pauseMusic() {
        bgMusic.pause();
        console.log('Musik dijeda');
        if (musicIcon) musicIcon.className = 'fas fa-music';
        if (musicStatus) musicStatus.textContent = 'Putar Musik';
        if (volumeControl) volumeControl.classList.remove('show');
        
        const musicControl = document.querySelector('.music-control');
        if (musicControl) musicControl.classList.remove('playing');
        
        localStorage.setItem('music_playing', 'false');
    }
    
    // Toggle music function (global)
    window.toggleMusic = function() {
        console.log('Toggle music clicked');
        if (bgMusic.paused) {
            playMusic();
        } else {
            pauseMusic();
        }
        localStorage.setItem('music_interacted', 'true');
    };
    
    // Volume control
    if (volumeSlider && bgMusic) {
        volumeSlider.addEventListener('input', function() {
            bgMusic.volume = this.value;
            if (volumePercent) {
                volumePercent.textContent = Math.round(this.value * 100) + '%';
            }
            console.log('Volume:', this.value);
            localStorage.setItem('music_volume', this.value);
        });
        
        // Load volume dari localStorage
        const savedVolume = localStorage.getItem('music_volume');
        if (savedVolume) {
            volumeSlider.value = savedVolume;
            bgMusic.volume = savedVolume;
            if (volumePercent) {
                volumePercent.textContent = Math.round(savedVolume * 100) + '%';
            }
        }
    }
    
    // Show/hide volume control
    const musicControl = document.querySelector('.music-control');
    if (musicControl && volumeControl) {
        musicControl.addEventListener('mouseenter', function() {
            if (!bgMusic.paused) {
                volumeControl.classList.add('show');
            }
        });
        
        musicControl.addEventListener('mouseleave', function() {
            setTimeout(() => {
                if (volumeControl && !volumeControl.matches(':hover')) {
                    volumeControl.classList.remove('show');
                }
            }, 1000);
        });
        
        volumeControl.addEventListener('mouseleave', function() {
            this.classList.remove('show');
        });
    }
    
    // CEK LOKAL STORAGE
    const wasPlaying = localStorage.getItem('music_playing') === 'true';
    console.log('Was playing before:', wasPlaying);
    
    // Attempt autoplay
    setTimeout(() => {
        console.log('Mencoba autoplay...');
        
        // Coba play
        playMusic();
        
        // Jika gagal, tunggu interaksi user
        setTimeout(() => {
            if (bgMusic.paused) {
                console.log('Autoplay gagal, menunggu interaksi user');
                
                // Tambah event listener untuk interaksi pertama
                function firstInteraction() {
                    console.log('First interaction detected');
                    if (bgMusic.paused) {
                        playMusic();
                    }
                    document.removeEventListener('click', firstInteraction);
                    document.removeEventListener('touchstart', firstInteraction);
                }
                
                document.addEventListener('click', firstInteraction);
                document.addEventListener('touchstart', firstInteraction);
            }
        }, 1000);
    }, 500);
    
    // Handle video autoplay
    const bgVideo = document.getElementById('bgVideo');
    if (bgVideo) {
        bgVideo.play()
            .then(() => console.log('Video berhasil diputar'))
            .catch(e => console.log('Video autoplay prevented:', e));
    }
});