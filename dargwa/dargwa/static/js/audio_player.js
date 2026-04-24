var audioCache = {};

function playSound(url) {
    if (!url) {
        console.warn('Sound URL is empty');
        return;
    }

    try {
        if (!audioCache[url]) {
            audioCache[url] = new Audio(url);
            audioCache[url].preload = 'auto';
        }

        audioCache[url].currentTime = 0;

        var playPromise = audioCache[url].play();

        if (playPromise !== undefined) {
            playPromise.catch(function(error) {
                console.warn('Audio playback failed:', error);
            });
        }
    } catch (error) {
        console.error('Error playing sound:', error);
    }
}

function handleSoundClick(event) {
    event.stopPropagation();
    var url = this.getAttribute('data-sound-url');
    if (url) {
        playSound(url);
    }
}

function initAudioPlayers(container) {
    var buttons = (container || document).querySelectorAll('.play-sound');
    buttons.forEach(function(btn) {
        btn.removeEventListener('click', handleSoundClick);
        btn.addEventListener('click', handleSoundClick);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initAudioPlayers();
});
