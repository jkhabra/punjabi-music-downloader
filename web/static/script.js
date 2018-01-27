var playingAudio = window = null;

var playAudio = function(event) {
    const target = event.currentTarget;
    const url = target.dataset.mp3;

    // When clicked different song from playingAudio
    if (playingAudio && playingAudio.src !== url) {
        playingAudio.pause();
        playingAudio.target.querySelector(".status-icon").classList.remove('paused');
        playingAudio = null;
    }

    // For same song
    if (playingAudio) {
        if (playingAudio.paused) {
            playingAudio.play();

            target.querySelector(".status-icon").classList.remove('playing');
            target.querySelector(".status-icon").classList.add('paused');
        }
        else {
            playingAudio.pause();

            target.querySelector(".status-icon").classList.remove('paused');
            target.querySelector(".status-icon").classList.add('playing');
        }
    } else {
        playingAudio = new Audio(url);
        playingAudio.target = target;
        playingAudio.play();

        target.querySelector(".status-icon").classList.remove('playing');
        target.querySelector(".status-icon").classList.add('paused');
    }
};

var showPlayIcon = function(event) {
    var target = event.target;

    if (playingAudio && !playingAudio.paused && target.dataset.mp3 === playingAudio.src) {
        return;
    }

    target.querySelector(".status-icon").classList.add('playing');
};

var showPauseIcon = function(event) {
    var target = event.target;

    target.querySelector(".status-icon").classList.add('paused');
};

var hidePlayIcon = function(event) {
    var target = event.target;

    target.querySelector(".status-icon").classList.remove('playing');
};

var hidePauseIcon = function(event) {
    var target = event.target;

    target.querySelector(".status-icon").classList.remove('paused');
};

document.addEventListener('DOMContentLoaded', () => {
    document
        .querySelectorAll('.song')
        .forEach((el) => {
            el.addEventListener('click', playAudio, true);
            el.addEventListener('mouseenter', showPlayIcon);
            el.addEventListener('mouseleave', hidePlayIcon);
        });
}, false);
