/**
 * Duck Ops - Game Logic
 * Refactored to 2D Canvas with Lottie Support
 */

// --- Configuration & Constants ---
const CONFIG = {
    SPAWN_INTERVAL: 2000,
    GAME_DURATION: 90,
    MAX_AMMO: 3,
    MAX_LIVES: 3,
    DUCK_SIZE: 120,
    HIT_RADIUS: 60,
    DIFFICULTIES: {
        easy: { speedMult: 0.8, spawnRate: 2500, points: 10, sizeMin: 0.8, sizeMax: 1.2 },
        medium: { speedMult: 1.5, spawnRate: 1800, points: 20, sizeMin: 0.5, sizeMax: 0.9 },
        hard: { speedMult: 3.0, spawnRate: 900, points: 50, sizeMin: 0.2, sizeMax: 0.4 }
    }
};

// --- Game State ---
let gameState = {
    active: false,
    paused: false,
    score: 0,
    hits: 0,
    misses: 0,
    combo: 0,
    maxCombo: 0,
    timer: CONFIG.GAME_DURATION,
    lives: CONFIG.MAX_LIVES,
    ammo: CONFIG.MAX_AMMO,
    difficulty: 'medium',
    crosshair: { x: 0.5, y: 0.5 },
    lastShotTime: 0
};

let ducks = [];
let particles = [];
let animationFrameId = null;
let gameIntervals = [];

// --- DOM Elements ---
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score-value');
const timerEl = document.getElementById('timer-value');
const timerBox = document.getElementById('timer-box');
const livesEl = document.getElementById('lives-display');
const ammoEl = document.getElementById('ammo-display');
const comboEl = document.getElementById('combo-display');
const countdownEl = document.getElementById('countdown-display');
const countdownNum = document.getElementById('countdown-number');

// --- Initialization ---
function init() {
    // Set canvas size
    resize();
    window.addEventListener('resize', resize);

    // Get difficulty from URL
    const params = new URLSearchParams(window.location.search);
    gameState.difficulty = params.get('difficulty') || 'medium';
    
    // Initial HUD update
    updateHUD();

    // Set background based on difficulty
    const backgrounds = {
        easy: '../assets/images/anh1.png',
        medium: '../assets/images/anh2.png',
        hard: '../assets/images/anh3.png'
    };
    if (backgrounds[gameState.difficulty]) {
        document.body.style.backgroundImage = `url(${backgrounds[gameState.difficulty]})`;
    }

    // Input handling
    window.addEventListener('mousemove', (e) => {
        gameState.crosshair.x = e.clientX / window.innerWidth;
        gameState.crosshair.y = e.clientY / window.innerHeight;
    });
    window.addEventListener('mousedown', shoot);
    window.addEventListener('keydown', (e) => {
        if (e.code === 'Space') shoot();
        if (e.code === 'Escape') togglePause();
    });
    
    // Start rendering loop immediately
    animate();

    // Show Intro Crawl
    showIntroCrawl();
    
    // Start WebSocket tracking
    initTracking();
}

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

// --- Tracking (WebSocket) ---
function initTracking() {
    try {
        const host = window.location.hostname || 'localhost';
        const ws = new WebSocket(`ws://${host}:8000/ws/tracking`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.detected) {
                // Update crosshair position (invert X because webcam is usually mirrored)
                gameState.crosshair.x = 1 - data.x;
                gameState.crosshair.y = data.y;
                
                // Optional: Auto-shoot if backend provides a trigger signal
                if (data.trigger) shoot();
            }
        };
        
        ws.onclose = () => {
            console.warn("Tracking WebSocket closed. Falling back to mouse.");
        };

        ws.onerror = () => {
            console.error("WebSocket error. Tracking disabled.");
        };
    } catch (err) {
        console.error("Failed to initialize tracking:", err);
    }
}

// --- Game Intro ---
function showIntroCrawl() {
    const introScreen = document.getElementById('intro-screen');
    const skipBtn = document.getElementById('skip-intro');
    
    // Skip on button click
    skipBtn.addEventListener('click', skipIntro);
    
    // Skip on Space key
    const skipOnSpace = (e) => {
        if (e.code === 'Space') {
            skipIntro();
            window.removeEventListener('keydown', skipOnSpace);
        }
    };
    window.addEventListener('keydown', skipOnSpace);

    // Auto finish after animation ends
    setTimeout(() => {
        if (introScreen.parentNode) skipIntro();
    }, 45000); // Match animation duration
}

function skipIntro() {
    const introScreen = document.getElementById('intro-screen');
    if (!introScreen || introScreen.classList.contains('fade-out')) return;

    introScreen.classList.add('fade-out');
    setTimeout(() => {
        if (introScreen.parentNode) document.body.removeChild(introScreen);
        startCountdown();
    }, 1000);
}

// --- Game Loop ---
function startCountdown() {
    countdownEl.classList.add('active');
    let count = 3;
    countdownNum.innerText = count;
    
    const timer = setInterval(() => {
        count--;
        if (count > 0) {
            countdownNum.innerText = count;
        } else if (count === 0) {
            countdownNum.innerText = "GO!";
        } else {
            clearInterval(timer);
            countdownEl.classList.remove('active');
            startGame();
        }
    }, 1000);
}

function startGame() {
    gameState.active = true;
    gameState.timer = CONFIG.GAME_DURATION;
    
    // Spawn Ducks
    const spawnTimer = setInterval(() => {
        if (gameState.active && !gameState.paused) spawnDuck();
    }, CONFIG.DIFFICULTIES[gameState.difficulty].spawnRate);
    gameIntervals.push(spawnTimer);
    
    // Game Clock
    const clockTimer = setInterval(() => {
        if (gameState.active && !gameState.paused) {
            gameState.timer--;
            updateHUD();
            if (gameState.timer <= 0) endGame();
            if (gameState.timer <= 10) timerBox.classList.add('warning');
        }
    }, 1000);
    gameIntervals.push(clockTimer);
}

function endGame() {
    gameState.active = false;
    // Do NOT cancel the animation frame so the crosshair remains visible
    gameIntervals.forEach(clearInterval);
    
    // Show Game Over Screen
    document.getElementById('gameover-screen').classList.add('active');
    document.getElementById('final-score').innerText = gameState.score;
    document.getElementById('final-hits').innerText = gameState.hits;
    document.getElementById('final-accuracy').innerText = 
        gameState.hits + gameState.misses > 0 
        ? Math.round((gameState.hits / (gameState.hits + gameState.misses)) * 100) + '%' 
        : '0%';
    document.getElementById('final-combo').innerText = gameState.maxCombo;
}

// --- Duck Management ---
class Duck {
    constructor() {
        const diff = CONFIG.DIFFICULTIES[gameState.difficulty];
        this.id = Math.random().toString(36).substr(2, 9);
        
        // Size based on difficulty
        const sizeMult = diff.sizeMin + Math.random() * (diff.sizeMax - diff.sizeMin);
        this.size = CONFIG.DUCK_SIZE * sizeMult;
        
        // Random entry point
        this.side = Math.random() > 0.5 ? 'left' : 'right';
        this.x = this.side === 'left' ? -this.size : canvas.width + this.size;
        this.y = canvas.height * (0.2 + Math.random() * 0.5);
        
        // Movement
        this.speedX = (this.side === 'left' ? 1 : -1) * (2 + Math.random() * 3) * diff.speedMult;
        this.speedY = (Math.random() - 0.5) * 2;
        this.wavy = Math.random() > 0.5;
        this.waveFreq = 0.02 + Math.random() * 0.05;
        this.waveAmp = 20 + Math.random() * 30;
        this.time = 0;
        
        this.dead = false;
        
        // Lottie Player Element (DOM for best quality)
        this.element = document.createElement('div');
        this.element.className = 'game-duck';
        this.element.style.width = `${this.size}px`;
        this.element.style.height = `${this.size}px`;
        this.element.style.position = 'fixed';
        this.element.style.zIndex = '10';
        this.element.style.pointerEvents = 'none';
        
        if (this.side === 'left') this.element.style.transform = 'scaleX(-1)';
        
        // Use Blob URL to avoid file:// protocol loading issues and ensure compatibility
        if (!window.duckLottieUrl) {
            const blob = new Blob([JSON.stringify(DUCK_LOTTIE_JSON)], { type: 'application/json' });
            window.duckLottieUrl = URL.createObjectURL(blob);
        }

        const player = document.createElement('dotlottie-player');
        player.setAttribute('src', window.duckLottieUrl);
        player.setAttribute('background', 'transparent');
        player.setAttribute('speed', '1');
        player.setAttribute('loop', '');
        player.setAttribute('autoplay', '');
        player.style.width = '100%';
        player.style.height = '100%';
        
        this.element.appendChild(player);
        document.body.appendChild(this.element);
    }

    update() {
        if (this.dead) return;
        
        this.time++;
        this.x += this.speedX;
        
        if (this.wavy) {
            this.y += Math.sin(this.time * this.waveFreq) * 2 + this.speedY;
        } else {
            this.y += this.speedY;
        }
        
        // Update DOM element
        this.element.style.left = `${this.x - this.size/2}px`;
        this.element.style.top = `${this.y - this.size/2}px`;
        
        // Remove if out of bounds
        if (this.side === 'left' && this.x > canvas.width + this.size) this.remove(false);
        if (this.side === 'right' && this.x < -this.size) this.remove(false);
    }

    remove(wasHit) {
        if (this.dead) return;
        this.dead = true;
        
        if (wasHit) {
            this.element.classList.add('hit');
            // Flash effect
            setTimeout(() => {
                if (this.element.parentNode) document.body.removeChild(this.element);
            }, 300);
        } else {
            if (this.element.parentNode) document.body.removeChild(this.element);
            if (gameState.active) {
                gameState.lives--;
                updateHUD();
                if (gameState.lives <= 0) endGame();
            }
        }
        
        ducks = ducks.filter(d => d.id !== this.id);
    }
}

function spawnDuck() {
    ducks.push(new Duck());
}

// --- Combat Logic ---
function shoot() {
    if (!gameState.active || gameState.paused) return;
    
    // Ammo check
    if (gameState.ammo <= 0) {
        // Play click sound?
        return;
    }
    
    gameState.ammo--;
    updateHUD();
    
    // Hit detection
    const cx = gameState.crosshair.x * canvas.width;
    const cy = gameState.crosshair.y * canvas.height;
    
    let hit = false;
    for (let i = ducks.length - 1; i >= 0; i--) {
        const duck = ducks[i];
        const dist = Math.sqrt((cx - duck.x)**2 + (cy - duck.y)**2);
        
        if (dist < CONFIG.HIT_RADIUS) {
            duck.remove(true);
            onDuckHit();
            hit = true;
            break;
        }
    }
    
    if (!hit) {
        gameState.misses++;
        gameState.combo = 0;
        updateHUD();
    }
    
    // Visual feedback for shot
    createShotEffect(cx, cy, hit);
    
    // Auto reload after a delay if empty
    if (gameState.ammo === 0) {
        setTimeout(reload, 800);
    }
}

function reload() {
    gameState.ammo = CONFIG.MAX_AMMO;
    updateHUD();
}

function onDuckHit() {
    gameState.hits++;
    gameState.combo++;
    if (gameState.combo > gameState.maxCombo) gameState.maxCombo = gameState.combo;
    
    const diff = CONFIG.DIFFICULTIES[gameState.difficulty];
    const points = diff.points * (gameState.combo > 1 ? Math.min(gameState.combo, 5) : 1);
    gameState.score += points;
    
    updateHUD();
    
    // Show floating score
    createFloatingText(`+${points}`, gameState.crosshair.x * canvas.width, gameState.crosshair.y * canvas.height);
}

// --- Visual Effects ---
function createShotEffect(x, y, hit) {
    particles.push({
        x, y,
        size: hit ? 40 : 20,
        opacity: 1,
        color: hit ? '#FFD700' : '#ffffff',
        life: 1
    });
}

function createFloatingText(text, x, y) {
    particles.push({
        x, y,
        text,
        size: 24,
        opacity: 1,
        color: '#FFD700',
        life: 1,
        type: 'text'
    });
}

// --- HUD Updates ---
function updateHUD() {
    scoreEl.innerText = gameState.score;
    timerEl.innerText = gameState.timer;
    
    // Update Lives
    livesEl.innerHTML = '';
    for (let i = 0; i < CONFIG.MAX_LIVES; i++) {
        const heart = document.createElement('span');
        heart.innerText = i < gameState.lives ? '❤️' : '🖤';
        livesEl.appendChild(heart);
    }
    
    // Update Ammo
    const bullets = ammoEl.querySelectorAll('.ammo-bullet');
    bullets.forEach((b, i) => {
        if (i < gameState.ammo) b.classList.remove('empty');
        else b.classList.add('empty');
    });
    
    // Update Combo
    if (gameState.combo >= 2) {
        comboEl.innerText = `🔥 COMBO x${gameState.combo}`;
        comboEl.classList.add('active');
    } else {
        comboEl.classList.remove('active');
    }
}

// --- Animation ---
let isLooping = false;
function animate() {
    if (isLooping) return;
    isLooping = true;
    
    function loop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update ducks and particles only when playing
        if (gameState.active && !gameState.paused) {
            ducks.forEach(duck => duck.update());
            
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.life -= 0.05;
                if (p.life <= 0) {
                    particles.splice(i, 1);
                    continue;
                }
                drawParticle(p);
            }
        } else {
            // Draw particles even when paused (static)
            particles.forEach(p => drawParticle(p));
        }
        
        // Always draw crosshair
        drawCrosshair();
        
        animationFrameId = requestAnimationFrame(loop);
    }
    
    loop();
}

function drawParticle(p) {
    ctx.globalAlpha = p.life;
    if (p.type === 'text') {
        ctx.fillStyle = p.color;
        ctx.font = `bold ${p.size}px Outfit`;
        ctx.textAlign = 'center';
        ctx.fillText(p.text, p.x, p.y - (1 - p.life) * 50);
    } else {
        ctx.strokeStyle = p.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * (1 - p.life), 0, Math.PI * 2);
        ctx.stroke();
    }
    ctx.globalAlpha = 1;
}

function drawCrosshair() {
    const cx = gameState.crosshair.x * canvas.width;
    const cy = gameState.crosshair.y * canvas.height;
    
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 2;
    
    // Outer circle
    ctx.beginPath();
    ctx.arc(cx, cy, 25, 0, Math.PI * 2);
    ctx.stroke();
    
    // Inner dot
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fill();
    
    // Lines
    ctx.beginPath();
    ctx.moveTo(cx - 35, cy); ctx.lineTo(cx - 15, cy);
    ctx.moveTo(cx + 35, cy); ctx.lineTo(cx + 15, cy);
    ctx.moveTo(cx, cy - 35); ctx.lineTo(cx, cy - 15);
    ctx.moveTo(cx, cy + 35); ctx.lineTo(cx, cy + 15);
    ctx.stroke();
    
    // Glow effect
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#FFD700';
    ctx.stroke();
    ctx.shadowBlur = 0;
}

// --- Pause / Resume ---
function togglePause() {
    if (!gameState.active) return;
    gameState.paused = !gameState.paused;
    const pauseScreen = document.getElementById('pause-screen');
    
    if (gameState.paused) {
        pauseScreen.classList.add('active');
    } else {
        pauseScreen.classList.remove('active');
        // No need to call animate() here as it's already looping
    }
}

function resumeGame() {
    if (gameState.paused) togglePause();
}

function restartGame() {
    // Clean up current ducks
    ducks.forEach(d => {
        if (d.element.parentNode) document.body.removeChild(d.element);
    });
    ducks = [];
    particles = [];
    gameIntervals.forEach(clearInterval);
    gameIntervals = [];
    
    // Reset State
    gameState = {
        ...gameState,
        active: false,
        paused: false,
        score: 0,
        hits: 0,
        misses: 0,
        combo: 0,
        timer: CONFIG.GAME_DURATION,
        lives: CONFIG.MAX_LIVES,
        ammo: CONFIG.MAX_AMMO
    };
    
    document.getElementById('gameover-screen').classList.remove('active');
    timerBox.classList.remove('warning');
    
    updateHUD();
    startCountdown();
}

// Expose functions for buttons
window.resumeGame = resumeGame;
window.restartGame = restartGame;

// --- Start the game ---
init();
