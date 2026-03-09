document.addEventListener('DOMContentLoaded', function() {
    const gameVideos = [
        { src: '/static/images/games/ml_loop.mp4', name: 'Mobile Legends' },
        { src: '/static/images/games/freefire_loop.mp4', name: 'Free Fire' },
        { src: '/static/images/games/genshin_loop.mp4', name: 'Genshin Impact' }
    ];
    
    const heroVideo = document.getElementById('heroVideo');
    const videoIndicator = document.getElementById('videoIndicator');
    let currentVideoIndex = 0;
    
    if (!heroVideo) return;
    
    // Fungsi untuk ganti video
    function changeVideo() {
        currentVideoIndex = (currentVideoIndex + 1) % gameVideos.length;
        const newVideo = gameVideos[currentVideoIndex];
        
        // Update indicator
        if (videoIndicator) {
            videoIndicator.innerHTML = `<i class="fas fa-play-circle"></i> Now playing: ${newVideo.name}`;
        }
        
        // Fade out
        heroVideo.style.opacity = '0';
        
        setTimeout(() => {
            heroVideo.src = newVideo.src;
            heroVideo.load();
            heroVideo.play()
                .then(() => {
                    // Fade in
                    heroVideo.style.opacity = '1';
                    console.log(`Playing: ${newVideo.name}`);
                })
                .catch(e => {
                    console.log('Video play failed:', e);
                    // Jika gagal, coba video berikutnya
                    setTimeout(changeVideo, 2000);
                });
        }, 500);
    }
    
    // Event listener untuk video ended
    heroVideo.addEventListener('ended', function() {
        changeVideo();
    });
    
    // Error handling
    heroVideo.addEventListener('error', function(e) {
        console.log('Video error:', e);
        changeVideo(); // Coba video berikutnya
    });
    
    // Set video pertama (acak)
    const randomIndex = Math.floor(Math.random() * gameVideos.length);
    heroVideo.src = gameVideos[randomIndex].src;
    heroVideo.load();
    
    // Coba play
    heroVideo.play()
        .then(() => {
            heroVideo.style.opacity = '1';
            if (videoIndicator) {
                videoIndicator.innerHTML = `<i class="fas fa-play-circle"></i> Now playing: ${gameVideos[randomIndex].name}`;
            }
            console.log(`Playing: ${gameVideos[randomIndex].name}`);
        })
        .catch(e => {
            console.log('Initial play failed:', e);
            heroVideo.style.opacity = '1';
            // Tetap tampilkan video meski autoplay gagal (user bisa play manual)
        });
    
    // Tambahkan CSS transition untuk fade
    heroVideo.style.transition = 'opacity 0.5s ease';
});