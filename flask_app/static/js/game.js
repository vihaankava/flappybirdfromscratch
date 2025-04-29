document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    
    const startScreen = document.getElementById('start-screen');
    const gameOverScreen = document.getElementById('game-over');
    const leaderboardScreen = document.getElementById('leaderboard-screen');
    
    const finalScoreElement = document.getElementById('final-score');
    const playerNameInput = document.getElementById('player-name');
    const submitScoreButton = document.getElementById('submit-score');
    const playAgainButton = document.getElementById('play-again');
    const continueButton = document.getElementById('continue-btn');
    const leaderboardEntries = document.getElementById('leaderboard-entries');
    
    const jumpButton = document.getElementById('jump-btn');
    const fireButton = document.getElementById('fire-btn');
    
    const CANVAS_WIDTH = canvas.width;
    const CANVAS_HEIGHT = canvas.height;
    const GRAVITY = 0.5;
    const JUMP_FORCE = -10;
    const PIPE_WIDTH = 80;
    const PIPE_GAP = 200;
    const PIPE_SPEED = 3;
    const BIRD_WIDTH = 40;
    const BIRD_HEIGHT = 30;
    const FIREBALL_SPEED = 7;
    const FIREBALL_SIZE = 15;
    const ENEMY_SIZE = 40;
    const ENEMY_SPEED = 2;
    
    let gameState = 'START'; // START, PLAYING, OVER, LEADERBOARD
    let score = 0;
    let highScore = 0;
    let frames = 0;
    
    let bird = {
        x: CANVAS_WIDTH / 4,
        y: CANVAS_HEIGHT / 2,
        width: BIRD_WIDTH,
        height: BIRD_HEIGHT,
        velocity: 0,
        color: '#FFFF00'
    };
    
    let pipes = [];
    let fireballs = [];
    let enemies = [];
    
    function init() {
        showScreen('START');
        
        document.addEventListener('keydown', handleKeyDown);
        jumpButton.addEventListener('click', handleJump);
        fireButton.addEventListener('click', handleFire);
        submitScoreButton.addEventListener('click', handleSubmitScore);
        playAgainButton.addEventListener('click', handlePlayAgain);
        continueButton.addEventListener('click', handleContinue);
        
        const savedHighScore = localStorage.getItem('flappyBirdHighScore');
        if (savedHighScore) {
            highScore = parseInt(savedHighScore);
        }
        
        requestAnimationFrame(gameLoop);
    }
    
    function handleKeyDown(event) {
        if (event.code === 'Space') {
            event.preventDefault();
            handleJump();
        } else if (event.code === 'KeyA') {
            event.preventDefault();
            handleFire();
        }
    }
    
    function handleJump() {
        if (gameState === 'START') {
            startGame();
        } else if (gameState === 'PLAYING') {
            bird.velocity = JUMP_FORCE;
        }
    }
    
    function handleFire() {
        if (gameState === 'PLAYING') {
            fireballs.push({
                x: bird.x + bird.width,
                y: bird.y + bird.height / 2,
                size: FIREBALL_SIZE,
                color: '#FF4500'
            });
        }
    }
    
    function startGame() {
        gameState = 'PLAYING';
        showScreen('PLAYING');
        resetGame();
    }
    
    function resetGame() {
        bird = {
            x: CANVAS_WIDTH / 4,
            y: CANVAS_HEIGHT / 2,
            width: BIRD_WIDTH,
            height: BIRD_HEIGHT,
            velocity: 0,
            color: '#FFFF00'
        };
        pipes = [];
        fireballs = [];
        enemies = [];
        score = 0;
        frames = 0;
    }
    
    function gameOver() {
        gameState = 'OVER';
        finalScoreElement.textContent = score;
        
        if (score > highScore) {
            highScore = score;
            localStorage.setItem('flappyBirdHighScore', highScore);
        }
        
        showScreen('OVER');
    }
    
    function handleSubmitScore() {
        const playerName = playerNameInput.value.trim();
        if (playerName.length < 3) {
            showMessage('Please enter a name with at least 3 characters');
            return;
        }
        
        fetch('/api/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: playerName,
                score: score
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadLeaderboard();
                showScreen('LEADERBOARD');
            } else {
                showMessage('Error submitting score: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            showMessage('Error submitting score: ' + error.message);
        });
    }
    
    function handlePlayAgain() {
        gameState = 'START';
        showScreen('START');
    }
    
    function handleContinue() {
        gameState = 'START';
        showScreen('START');
    }
    
    function loadLeaderboard() {
        fetch('/api/leaderboard')
            .then(response => response.json())
            .then(data => {
                leaderboardEntries.innerHTML = '';
                
                if (data.length === 0) {
                    leaderboardEntries.innerHTML = '<p>No scores yet. Be the first!</p>';
                } else {
                    const list = document.createElement('ol');
                    data.forEach(entry => {
                        const item = document.createElement('li');
                        item.textContent = `${entry.name}: ${entry.score}`;
                        list.appendChild(item);
                    });
                    leaderboardEntries.appendChild(list);
                }
            })
            .catch(error => {
                console.error('Error loading leaderboard:', error);
                leaderboardEntries.innerHTML = '<p>Error loading leaderboard</p>';
            });
    }
    
    function gameLoop() {
        update();
        render();
        requestAnimationFrame(gameLoop);
    }
    
    function update() {
        if (gameState !== 'PLAYING') return;
        
        frames++;
        
        bird.velocity += GRAVITY;
        bird.y += bird.velocity;
        
        if (bird.y + bird.height >= CANVAS_HEIGHT || bird.y <= 0) {
            gameOver();
            return;
        }
        
        if (frames % 100 === 0) {
            const pipeHeight = Math.floor(Math.random() * (CANVAS_HEIGHT - PIPE_GAP - 100)) + 50;
            
            pipes.push({
                x: CANVAS_WIDTH,
                y: 0,
                width: PIPE_WIDTH,
                height: pipeHeight,
                passed: false,
                color: '#00FF00'
            });
            
            pipes.push({
                x: CANVAS_WIDTH,
                y: pipeHeight + PIPE_GAP,
                width: PIPE_WIDTH,
                height: CANVAS_HEIGHT - pipeHeight - PIPE_GAP,
                passed: false,
                color: '#00FF00'
            });
        }
        
        if (frames % 200 === 0) {
            enemies.push({
                x: CANVAS_WIDTH,
                y: Math.random() * (CANVAS_HEIGHT - ENEMY_SIZE),
                size: ENEMY_SIZE,
                color: '#FF0000'
            });
        }
        
        for (let i = 0; i < pipes.length; i++) {
            const pipe = pipes[i];
            pipe.x -= PIPE_SPEED;
            
            if (!pipe.passed && pipe.x + pipe.width < bird.x) {
                pipe.passed = true;
                if (i % 2 === 0) {
                    score++;
                }
            }
            
            if (
                bird.x + bird.width > pipe.x &&
                bird.x < pipe.x + pipe.width &&
                bird.y + bird.height > pipe.y &&
                bird.y < pipe.y + pipe.height
            ) {
                gameOver();
                return;
            }
        }
        
        pipes = pipes.filter(pipe => pipe.x + pipe.width > 0);
        
        for (let i = 0; i < fireballs.length; i++) {
            fireballs[i].x += FIREBALL_SPEED;
        }
        
        fireballs = fireballs.filter(fireball => fireball.x < CANVAS_WIDTH);
        
        for (let i = 0; i < enemies.length; i++) {
            const enemy = enemies[i];
            enemy.x -= ENEMY_SPEED;
            
            if (
                bird.x + bird.width > enemy.x &&
                bird.x < enemy.x + enemy.size &&
                bird.y + bird.height > enemy.y &&
                bird.y < enemy.y + enemy.size
            ) {
                gameOver();
                return;
            }
            
            for (let j = 0; j < fireballs.length; j++) {
                const fireball = fireballs[j];
                if (
                    fireball.x + fireball.size > enemy.x &&
                    fireball.x < enemy.x + enemy.size &&
                    fireball.y + fireball.size > enemy.y &&
                    fireball.y < enemy.y + enemy.size
                ) {
                    enemies.splice(i, 1);
                    fireballs.splice(j, 1);
                    score += 2; // Bonus points for killing enemy
                    i--; // Adjust index after removing enemy
                    break;
                }
            }
        }
        
        enemies = enemies.filter(enemy => enemy.x + enemy.size > 0);
    }
    
    function render() {
        ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        if (gameState === 'PLAYING' || gameState === 'OVER') {
            for (const pipe of pipes) {
                ctx.fillStyle = pipe.color;
                ctx.fillRect(pipe.x, pipe.y, pipe.width, pipe.height);
            }
            
            for (const fireball of fireballs) {
                ctx.fillStyle = fireball.color;
                ctx.beginPath();
                ctx.arc(fireball.x, fireball.y, fireball.size, 0, Math.PI * 2);
                ctx.fill();
            }
            
            for (const enemy of enemies) {
                ctx.fillStyle = enemy.color;
                ctx.fillRect(enemy.x, enemy.y, enemy.size, enemy.size);
            }
            
            ctx.fillStyle = bird.color;
            ctx.fillRect(bird.x, bird.y, bird.width, bird.height);
            
            ctx.fillStyle = 'black';
            ctx.font = '24px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(`Score: ${score}`, 10, 30);
            
            if (highScore > 0) {
                ctx.fillText(`High Score: ${highScore}`, 10, 60);
            }
        }
    }
    
    function showScreen(screen) {
        startScreen.classList.add('hidden');
        gameOverScreen.classList.add('hidden');
        leaderboardScreen.classList.add('hidden');
        
        switch (screen) {
            case 'START':
                startScreen.classList.remove('hidden');
                break;
            case 'PLAYING':
                break;
            case 'OVER':
                gameOverScreen.classList.remove('hidden');
                break;
            case 'LEADERBOARD':
                leaderboardScreen.classList.remove('hidden');
                break;
        }
    }
    
    function showMessage(message) {
        alert(message);
    }
    
    init();
});
