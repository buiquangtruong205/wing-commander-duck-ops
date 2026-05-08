// Wing Commander - Game Logic
const plane = document.getElementById('plane');
const altEl = document.getElementById('alt');
const distEl = document.getElementById('dist');
const webcam = document.getElementById('webcam-view');
let altitude = 5000;
let distance = 0;
let planeY = 50; // Percentage

// Read difficulty from URL
const urlParams = new URLSearchParams(window.location.search);
const difficulty = urlParams.get('difficulty') || 'medium';

// Difficulty settings
const DIFFICULTY_CONFIG = {
    easy:   { enemyRate: 0.85, enemySpeed: 5000, spawnInterval: 150 },
    medium: { enemyRate: 0.70, enemySpeed: 3000, spawnInterval: 100 },
    hard:   { enemyRate: 0.50, enemySpeed: 1800, spawnInterval: 70 }
};

const config = DIFFICULTY_CONFIG[difficulty] || DIFFICULTY_CONFIG.medium;

// Background images per difficulty
const DIFFICULTY_BG = {
    easy:   '../assets/images/anh1.png',
    medium: '../assets/images/anh2.png',
    hard:   '../assets/images/anh3.png'
};

// Apply background
const gameContainer = document.getElementById('game-container');
const bgUrl = DIFFICULTY_BG[difficulty] || DIFFICULTY_BG.medium;
gameContainer.style.backgroundImage = `url('${bgUrl}')`;
gameContainer.style.backgroundSize = 'cover';
gameContainer.style.backgroundPosition = 'center';
gameContainer.style.backgroundRepeat = 'no-repeat';

// WebSocket Connection
const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/tracking`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.detected) {
        // Update plane position based on hand height
        planeY = data.y * 100;
        plane.style.top = `${planeY}%`;
        
        // Update HUD
        altitude = Math.round((1 - data.y) * 10000);
        altEl.innerText = altitude;
    }
};

// Scrolling Background & Gameplay
function initGame() {
    setInterval(() => {
        distance += 0.1;
        distEl.innerText = distance.toFixed(1);
        spawnCloud();
        if (Math.random() > config.enemyRate) spawnEnemy();
    }, config.spawnInterval);
}

function spawnCloud() {
    const cloud = document.createElement('div');
    cloud.className = 'cloud';
    const size = Math.random() * 100 + 50;
    cloud.style.width = `${size}px`;
    cloud.style.height = `${size/2}px`;
    cloud.style.top = `${Math.random() * 100}%`;
    cloud.style.left = '100vw';
    cloud.style.transition = 'left 5s linear';
    
    document.getElementById('game-container').appendChild(cloud);
    
    setTimeout(() => cloud.style.left = '-200px', 50);
    setTimeout(() => cloud.remove(), 5000);
}

function spawnEnemy() {
    const enemy = document.createElement('div');
    enemy.className = 'enemy';
    enemy.innerText = '🦆';
    enemy.style.fontSize = '40px';
    enemy.style.top = `${Math.random() * 100}%`;
    enemy.style.left = '100vw';
    enemy.style.transition = `left ${config.enemySpeed / 1000}s linear`;
    
    document.getElementById('game-container').appendChild(enemy);
    
    setTimeout(() => enemy.style.left = '-100px', 50);
    
    // Simple collision check
    const checkInterval = setInterval(() => {
        const pRect = plane.getBoundingClientRect();
        const eRect = enemy.getBoundingClientRect();
        
        if (pRect.left < eRect.right && pRect.right > eRect.left &&
            pRect.top < eRect.bottom && pRect.bottom > eRect.top) {
            enemy.innerText = '💥';
            setTimeout(() => enemy.remove(), 200);
            clearInterval(checkInterval);
        }
    }, 50);

    setTimeout(() => {
        enemy.remove();
        clearInterval(checkInterval);
    }, config.enemySpeed);
}

// Webcam handling
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcam.srcObject = stream;
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 320;
        canvas.height = 240;
        
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL('image/jpeg', 0.5);
                ws.send(dataUrl);
            }
        }, 100);
        
    } catch (err) {
        console.error("Webcam error:", err);
    }
}

initGame();
startWebcam();
