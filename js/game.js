class UltimateTicTacToe {
    constructor() {
        // Game constants
        this.EMPTY = null;
        this.PLAYER_X = 'X';
        this.PLAYER_O = 'O';
        
        // Game state
        this.board = this.createBoard();
        this.metaBoard = this.createMetaBoard();
        this.currentPlayer = this.PLAYER_X;
        this.activeSubRow = null;
        this.activeSubCol = null;
        this.winner = null;
        this.gameOver = false;
        this.aiEnabled = true;
        this.isAnimating = false;
        this.isDarkTheme = true;
        
        // Timing constants
        this.AI_THINKING_TIME = 1000;  // Time before AI makes a move
        this.MARK_ANIMATION_TIME = 500; // Time for mark animation
        
        // DOM elements
        this.mainBoardElement = document.getElementById('mainBoard');
        this.metaBoardElement = document.getElementById('metaBoard');
        this.statusElement = document.getElementById('gameStatus');
        this.restartButton = document.getElementById('restartBtn');
        this.toggleThemeButton = document.getElementById('toggleAIBtn');
        this.difficultySelect = document.getElementById('difficultySelect');
        this.difficultyModal = document.getElementById('difficultyModal');
        
        // Add overlay element
        this.overlayElement = document.getElementById('gameOverlay');
        
        // Debug buttons
        this.debugWinButton = document.getElementById('debugWinBtn');
        this.debugLoseButton = document.getElementById('debugLoseBtn');
        
        // Initialize the game
        this.initializeBoard();
        this.setupEventListeners();
        this.updateThemeButton();
    }

    createBoard() {
        return Array(9).fill(null).map(() => Array(9).fill(null));
    }

    createMetaBoard() {
        return Array(3).fill(null).map(() => Array(3).fill(null));
    }

    initializeBoard() {
        // Clear main board
        this.mainBoardElement.innerHTML = '';
        
        // Create sub-boards and cells
        for (let sr = 0; sr < 3; sr++) {
            for (let sc = 0; sc < 3; sc++) {
                const subBoard = document.createElement('div');
                subBoard.className = 'sub-board';
                subBoard.dataset.subRow = sr;
                subBoard.dataset.subCol = sc;
                
                for (let r = 0; r < 3; r++) {
                    for (let c = 0; c < 3; c++) {
                        const cell = document.createElement('div');
                        cell.className = 'cell';
                        cell.dataset.row = sr * 3 + r;
                        cell.dataset.col = sc * 3 + c;
                        subBoard.appendChild(cell);
                    }
                }
                
                this.mainBoardElement.appendChild(subBoard);
            }
        }

        // Initialize meta board
        this.metaBoardElement.innerHTML = '';
        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                const cell = document.createElement('div');
                cell.className = 'meta-cell';
                this.metaBoardElement.appendChild(cell);
            }
        }

        this.updateDisplay();
    }

    setupEventListeners() {
        // Cell click handler
        this.mainBoardElement.addEventListener('click', (e) => {
            if (this.gameOver || (this.currentPlayer === this.PLAYER_O && this.aiEnabled)) return;
            
            const cell = e.target.closest('.cell');
            if (!cell) return;
            
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            
            this.makeMove(row, col);
        });

        // Restart button handler
        this.restartButton.addEventListener('click', () => {
            this.restart();
        });

        // Theme toggle handler
        this.toggleThemeButton.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Difficulty select handler
        this.difficultySelect.addEventListener('change', (e) => {
            const difficulty = e.target.value;
            if (difficulty !== 'easy') {
                this.difficultyModal.style.display = 'flex';
                e.target.value = 'easy';
            }
        });

        // Debug button handlers
        this.debugWinButton.addEventListener('click', () => {
            this.forceGameEnd(this.PLAYER_X);
        });

        this.debugLoseButton.addEventListener('click', () => {
            this.forceGameEnd(this.PLAYER_O);
        });
    }

    async makeMove(row, col) {
        if (!this.isValidMove(row, col) || this.isAnimating) return false;
        
        this.isAnimating = true;
        
        // Make the move
        this.board[row][col] = this.currentPlayer;
        
        // Update active sub-board
        this.activeSubRow = row % 3;
        this.activeSubCol = col % 3;
        
        // Update display with animation
        await this.updateDisplayWithAnimation(row, col);
        
        // Update meta board
        this.updateMetaBoard();
        
        // Check for winner
        this.winner = this.checkGlobalWinner();
        if (this.winner) {
            this.gameOver = true;
        } else if (this.checkForDraw()) {
            this.gameOver = true;
        }
        
        // Switch player
        this.currentPlayer = this.currentPlayer === this.PLAYER_X ? this.PLAYER_O : this.PLAYER_X;
        
        // Update status and complete the move
        this.updateDisplay();
        this.isAnimating = false;
        
        // AI move if enabled
        if (this.currentPlayer === this.PLAYER_O && this.aiEnabled && !this.gameOver) {
            setTimeout(() => this.aiMove(), this.AI_THINKING_TIME);
        }
        
        return true;
    }

    isValidMove(row, col) {
        // Check if cell is empty
        if (this.board[row][col] !== this.EMPTY) return false;
        
        // Check if move is in active sub-board
        if (this.activeSubRow !== null && this.activeSubCol !== null) {
            const subRow = Math.floor(row / 3);
            const subCol = Math.floor(col / 3);
            
            // If the target sub-board is full, allow move anywhere
            if (this.isSubBoardFull(this.activeSubRow, this.activeSubCol)) {
                return true;
            }
            
            return subRow === this.activeSubRow && subCol === this.activeSubCol;
        }
        
        return true;
    }

    isSubBoardFull(subRow, subCol) {
        const rows = this.getSubBoardIndices(subRow);
        const cols = this.getSubBoardIndices(subCol);
        
        for (let r of rows) {
            for (let c of cols) {
                if (this.board[r][c] === this.EMPTY) {
                    return false;
                }
            }
        }
        
        return true;
    }

    getSubBoardIndices(index) {
        const start = index * 3;
        return [start, start + 1, start + 2];
    }

    checkSubBoardWinner(subRow, subCol) {
        const rows = this.getSubBoardIndices(subRow);
        const cols = this.getSubBoardIndices(subCol);
        
        // Extract sub-board
        const sub = [];
        for (let r of rows) {
            const subRow = [];
            for (let c of cols) {
                subRow.push(this.board[r][c]);
            }
            sub.push(subRow);
        }
        
        // Check rows
        for (let r = 0; r < 3; r++) {
            if (sub[r][0] && sub[r][0] === sub[r][1] && sub[r][0] === sub[r][2]) {
                return sub[r][0];
            }
        }
        
        // Check columns
        for (let c = 0; c < 3; c++) {
            if (sub[0][c] && sub[0][c] === sub[1][c] && sub[0][c] === sub[2][c]) {
                return sub[0][c];
            }
        }
        
        // Check diagonals
        if (sub[0][0] && sub[0][0] === sub[1][1] && sub[0][0] === sub[2][2]) {
            return sub[0][0];
        }
        if (sub[0][2] && sub[0][2] === sub[1][1] && sub[0][2] === sub[2][0]) {
            return sub[0][2];
        }
        
        return null;
    }

    updateMetaBoard() {
        for (let sr = 0; sr < 3; sr++) {
            for (let sc = 0; sc < 3; sc++) {
                this.metaBoard[sr][sc] = this.checkSubBoardWinner(sr, sc);
            }
        }
    }

    checkGlobalWinner() {
        // Check rows
        for (let r = 0; r < 3; r++) {
            if (this.metaBoard[r][0] && 
                this.metaBoard[r][0] === this.metaBoard[r][1] && 
                this.metaBoard[r][0] === this.metaBoard[r][2]) {
                return this.metaBoard[r][0];
            }
        }
        
        // Check columns
        for (let c = 0; c < 3; c++) {
            if (this.metaBoard[0][c] && 
                this.metaBoard[0][c] === this.metaBoard[1][c] && 
                this.metaBoard[0][c] === this.metaBoard[2][c]) {
                return this.metaBoard[0][c];
            }
        }
        
        // Check diagonals
        if (this.metaBoard[0][0] && 
            this.metaBoard[0][0] === this.metaBoard[1][1] && 
            this.metaBoard[0][0] === this.metaBoard[2][2]) {
            return this.metaBoard[0][0];
        }
        if (this.metaBoard[0][2] && 
            this.metaBoard[0][2] === this.metaBoard[1][1] && 
            this.metaBoard[0][2] === this.metaBoard[2][0]) {
            return this.metaBoard[0][2];
        }
        
        return null;
    }

    checkForDraw() {
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (this.board[r][c] === this.EMPTY) {
                    return false;
                }
            }
        }
        return true;
    }

    async updateDisplayWithAnimation(row, col) {
        // Update the specific cell that was just played
        const cells = this.mainBoardElement.getElementsByClassName('cell');
        for (let cell of cells) {
            if (parseInt(cell.dataset.row) === row && parseInt(cell.dataset.col) === col) {
                cell.textContent = this.board[row][col];
                cell.className = `cell ${this.board[row][col].toLowerCase()}`;
                break;
            }
        }

        // Wait for the animation to complete
        await new Promise(resolve => setTimeout(resolve, this.MARK_ANIMATION_TIME));
    }

    updateDisplay() {
        // Update main board cells (except the one that was just animated)
        const cells = this.mainBoardElement.getElementsByClassName('cell');
        for (let cell of cells) {
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            const value = this.board[row][col];
            
            if (value && !cell.classList.contains(value.toLowerCase())) {
                cell.textContent = value;
                cell.className = `cell ${value.toLowerCase()}`;
            } else if (!value) {
                cell.textContent = '';
                cell.className = 'cell';
            }
        }
        
        // Update sub-board highlighting
        const subBoards = this.mainBoardElement.getElementsByClassName('sub-board');
        for (let subBoard of subBoards) {
            const sr = parseInt(subBoard.dataset.subRow);
            const sc = parseInt(subBoard.dataset.subCol);
            
            // Remove active class from all sub-boards first
            subBoard.classList.remove('active-board');
            
            if (!this.gameOver) {
                // If it's the first move
                if (this.activeSubRow === null && this.activeSubCol === null) {
                    if (!this.isSubBoardFull(sr, sc)) {
                        subBoard.classList.add('active-board');
                    }
                }
                // If the active sub-board is full
                else if (this.isSubBoardFull(this.activeSubRow, this.activeSubCol)) {
                    if (!this.isSubBoardFull(sr, sc)) {
                        subBoard.classList.add('active-board');
                    }
                }
                // If this is the active sub-board and it's not full
                else if (sr === this.activeSubRow && sc === this.activeSubCol && 
                         !this.isSubBoardFull(sr, sc)) {
                    subBoard.classList.add('active-board');
                }
            }
        }
        
        // Update meta board
        const metaCells = this.metaBoardElement.getElementsByClassName('meta-cell');
        let metaIndex = 0;
        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                const value = this.metaBoard[r][c];
                const cell = metaCells[metaIndex++];
                
                // Reset the cell's classes and data
                cell.className = 'meta-cell';
                cell.removeAttribute('data-symbol');
                
                // If there's a value, add the appropriate class and symbol
                if (value) {
                    cell.classList.add(value.toLowerCase());
                    cell.setAttribute('data-symbol', value);
                }
            }
        }
        
        // Update status
        this.updateStatus();
    }

    updateStatus() {
        const statusBar = document.getElementById('statusBar');
        statusBar.classList.remove('win', 'lose');
        this.overlayElement.classList.remove('win', 'lose');

        if (this.gameOver) {
            if (this.winner) {
                if (this.winner === this.PLAYER_X) {
                    this.statusElement.textContent = "You win!";
                    this.celebrateWin();
                } else {
                    this.statusElement.textContent = "AI wins!";
                    this.showLoseEffect();
                }
            } else {
                this.statusElement.textContent = "Game ended in a draw!";
            }
        } else {
            this.statusElement.textContent = `Player ${this.currentPlayer}'s turn` +
                (this.currentPlayer === this.PLAYER_O && this.aiEnabled ? " (AI thinking...)" : "");
        }
    }

    celebrateWin() {
        // Add winning effects to UI
        document.getElementById('statusBar').classList.add('win');
        this.overlayElement.classList.add('win');

        // Create confetti
        const duration = 3000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1001 };

        const randomInRange = (min, max) => Math.random() * (max - min) + min;

        const interval = setInterval(() => {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);

            // Create confetti from both sides
            confetti({
                ...defaults,
                particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
            });
            confetti({
                ...defaults,
                particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
            });
        }, 250);

        // Create final celebratory burst
        setTimeout(() => {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
                zIndex: 1001
            });
        }, duration - 1000);
    }

    showLoseEffect() {
        // Add losing effects to UI
        document.getElementById('statusBar').classList.add('lose');
        this.overlayElement.classList.add('lose');
        
        // Add screen shake effect
        document.body.style.animation = 'none';
        document.body.offsetHeight; // Trigger reflow
        document.body.style.animation = 'shake 0.5s ease-in-out';
    }

    aiMove() {
        if (this.gameOver || this.currentPlayer !== this.PLAYER_O || !this.aiEnabled || this.isAnimating) return;
        
        // Get valid moves
        const validMoves = [];
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (this.isValidMove(r, c)) {
                    validMoves.push([r, c]);
                }
            }
        }
        
        // Make random move
        if (validMoves.length > 0) {
            const [row, col] = validMoves[Math.floor(Math.random() * validMoves.length)];
            this.makeMove(row, col);
        }
    }

    restart() {
        // Clear all effects
        document.getElementById('statusBar').classList.remove('win', 'lose');
        this.overlayElement.classList.remove('win', 'lose');
        document.body.style.animation = '';
        
        // Reset game state
        this.board = this.createBoard();
        this.metaBoard = this.createMetaBoard();
        this.currentPlayer = this.PLAYER_X;
        this.activeSubRow = null;
        this.activeSubCol = null;
        this.winner = null;
        this.gameOver = false;
        this.initializeBoard();
    }

    toggleTheme() {
        this.isDarkTheme = !this.isDarkTheme;
        document.body.classList.toggle('light-theme', !this.isDarkTheme);
        this.updateThemeButton();
    }

    updateThemeButton() {
        this.toggleThemeButton.textContent = this.isDarkTheme ? 'Light Mode' : 'Dark Mode';
    }

    forceGameEnd(winner) {
        if (this.gameOver) return;
        
        // Set winner and game over state
        this.winner = winner;
        this.gameOver = true;
        
        // Fill the meta board for visual effect
        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                this.metaBoard[r][c] = winner;
            }
        }
        
        // Fill the main board
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (!this.board[r][c]) {
                    this.board[r][c] = winner;
                }
            }
        }
        
        // Update display and show effects
        this.updateDisplay();
    }
}

// Add this to your existing CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}
`;
document.head.appendChild(style);

// Start the game when the page loads
window.addEventListener('load', () => {
    new UltimateTicTacToe();
}); 