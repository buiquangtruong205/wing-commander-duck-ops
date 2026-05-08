/**
 * Duck Ops Landing Page Logic
 */

// Staggered menu animation on load
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.menu-btn');
    buttons.forEach((btn, i) => {
        btn.style.animationDelay = `${0.6 + i * 0.12}s`;
    });

    // Add ripple effect on click
    buttons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            const rect = btn.getBoundingClientRect();
            ripple.style.left = `${e.clientX - rect.left}px`;
            ripple.style.top = `${e.clientY - rect.top}px`;
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// ---- Flying Ducks System ----
function spawnFlyingDucks() {
    const duckEmojis = ['🦆'];
    const minDucks = 3;
    const maxDucks = 8;
    const duckCount = Math.floor(Math.random() * (maxDucks - minDucks + 1)) + minDucks;

    for (let i = 0; i < duckCount; i++) {
        createFlyingDuck(duckEmojis, i);
    }

    // Periodically add/remove ducks to keep it dynamic
    setInterval(() => {
        const existingDucks = document.querySelectorAll('.flying-duck');
        // Remove oldest duck if too many
        if (existingDucks.length > 10) {
            existingDucks[0].remove();
        }
        // Randomly spawn a new duck
        if (Math.random() > 0.5 && existingDucks.length < 10) {
            createFlyingDuck(duckEmojis, Math.floor(Math.random() * 100));
        }
    }, 4000);
}

function createFlyingDuck(emojis, index) {
    const duck = document.createElement('div');
    duck.className = 'flying-duck';

    const body = document.createElement('dotlottie-player');
    body.className = 'duck-body';
    body.setAttribute('src', '../assets/animations/duck.json');
    body.setAttribute('background', 'transparent');
    body.setAttribute('speed', (Math.random() * 0.5 + 0.75).toFixed(2));
    body.setAttribute('loop', '');
    body.setAttribute('autoplay', '');
    duck.appendChild(body);

    // Random direction
    const direction = Math.random() > 0.5 ? 'rtl' : 'ltr';
    duck.classList.add(direction);

    // Random vertical position (5% - 85%)
    const topPos = Math.random() * 80 + 5;
    duck.style.top = `${topPos}%`;

    // Random flight duration (6s - 14s)
    const duration = (Math.random() * 8 + 6).toFixed(1);
    duck.style.setProperty('--fly-duration', `${duration}s`);

    // Staggered start delay
    const delay = (Math.random() * 5).toFixed(1);
    duck.style.setProperty('--fly-delay', `${delay}s`);

    // Random bob amount for wavy flight path
    const bobAmount = -(Math.random() * 20 + 10);
    duck.style.setProperty('--bob-amount', `${bobAmount.toFixed(0)}px`);

    // Random size (1.8rem - 3.5rem)
    const size = (Math.random() * 1.7 + 1.8).toFixed(1);
    duck.style.fontSize = `${size}rem`;

    // Opacity variation for depth
    const opacity = (Math.random() * 0.4 + 0.6).toFixed(2);
    duck.style.opacity = opacity;

    // Wing flap speed variation
    const flapSpeed = (Math.random() * 0.2 + 0.25).toFixed(2);
    body.style.animationDuration = `${flapSpeed}s`;

    document.body.appendChild(duck);
}

// Start the flying ducks
spawnFlyingDucks();

function startGame() {
    // Show difficulty selection modal
    const modal = document.getElementById('difficulty-modal');
    modal.classList.add('active');
    // Trigger card entrance animations
    setTimeout(() => {
        document.getElementById('modal-content').classList.add('show');
    }, 50);
}

function closeDifficultyModal() {
    const modal = document.getElementById('difficulty-modal');
    const content = document.getElementById('modal-content');
    content.classList.remove('show');
    setTimeout(() => {
        modal.classList.remove('active');
    }, 350);
}

function openAboutModal() {
    const modal = document.getElementById('about-modal');
    modal.classList.add('active');
    setTimeout(() => {
        document.getElementById('about-modal-content').classList.add('show');
    }, 50);
}

function closeAboutModal() {
    const modal = document.getElementById('about-modal');
    const content = document.getElementById('about-modal-content');
    content.classList.remove('show');
    setTimeout(() => {
        modal.classList.remove('active');
    }, 350);
}

function selectDifficulty(level) {
    // Animate the selected card
    const card = document.getElementById(`diff-${level}`);
    card.classList.add('selected');
    
    setTimeout(() => {
        window.location.href = `../duck/index.html?difficulty=${level}`;
    }, 500);
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeDifficultyModal();
        closeAboutModal();
    }
});
