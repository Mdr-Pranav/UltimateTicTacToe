import pygame
import sys
import random

# --- Constants and settings ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
BOARD_SIZE = 600
META_BOARD_SIZE = 150
MARGIN = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
CYAN = (0, 200, 255)
ACTIVE_SUBBOARD_COLOR = (220, 240, 255)
HIGHLIGHT_COLOR = (255, 255, 200)
GRID_COLOR = (150, 150, 150)
THICK_LINE_COLOR = (50, 50, 50)

# Game markers
EMPTY = None
PLAYER_X = "X"
PLAYER_O = "O"

class UltimateTicTacToe:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set up the window
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ultimate Tic-Tac-Toe")
        
        # Set up fonts
        self.big_font = pygame.font.SysFont("Arial", 40)
        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 18)
        
        # Game state
        self.board = self.create_board()
        self.meta_board = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = PLAYER_X
        self.active_sub_row = None
        self.active_sub_col = None
        self.winner = None
        self.game_over = False
        
        # For highlighting the last move
        self.last_move = None
        
        # AI settings
        self.ai_enabled = True
        self.ai_delay = 0
        self.ai_timer = 0

    def create_board(self):
        """Initialize a 9x9 Ultimate Tic-Tac-Toe board filled with empty cells."""
        return [[EMPTY for _ in range(9)] for _ in range(9)]

    def get_sub_board_indices(self, sub_row, sub_col):
        """Get the range of rows and cols in the main board for a sub-board."""
        row_start = sub_row * 3
        col_start = sub_col * 3
        return range(row_start, row_start + 3), range(col_start, col_start + 3)

    def check_sub_board_winner(self, board, sub_row, sub_col):
        """Check if there's a winner in the specified 3x3 sub-board."""
        rows, cols = self.get_sub_board_indices(sub_row, sub_col)
        
        # Extract the sub-board
        sub = []
        for r in rows:
            sub_row_vals = []
            for c in cols:
                sub_row_vals.append(board[r][c])
            sub.append(sub_row_vals)

        # Check rows
        for r in range(3):
            if sub[r][0] == sub[r][1] == sub[r][2] and sub[r][0] is not EMPTY:
                return sub[r][0]

        # Check columns
        for c in range(3):
            if sub[0][c] == sub[1][c] == sub[2][c] and sub[0][c] is not EMPTY:
                return sub[0][c]

        # Check diagonals
        if sub[0][0] == sub[1][1] == sub[2][2] and sub[0][0] is not EMPTY:
            return sub[0][0]
        if sub[0][2] == sub[1][1] == sub[2][0] and sub[0][2] is not EMPTY:
            return sub[0][2]

        return None  # No winner

    def check_global_winner(self):
        """Check if there's a winner on the meta-board."""
        # Update the meta-board first
        self.update_meta_board()
        
        # Check rows
        for r in range(3):
            if self.meta_board[r][0] == self.meta_board[r][1] == self.meta_board[r][2] and self.meta_board[r][0] is not None:
                return self.meta_board[r][0]

        # Check columns
        for c in range(3):
            if self.meta_board[0][c] == self.meta_board[1][c] == self.meta_board[2][c] and self.meta_board[0][c] is not None:
                return self.meta_board[0][c]

        # Check diagonals
        if self.meta_board[0][0] == self.meta_board[1][1] == self.meta_board[2][2] and self.meta_board[0][0] is not None:
            return self.meta_board[0][0]
        if self.meta_board[0][2] == self.meta_board[1][1] == self.meta_board[2][0] and self.meta_board[0][2] is not None:
            return self.meta_board[0][2]

        return None  # No global winner yet

    def update_meta_board(self):
        """Update the meta-board with sub-board winners."""
        for sr in range(3):
            for sc in range(3):
                self.meta_board[sr][sc] = self.check_sub_board_winner(self.board, sr, sc)

    def get_valid_moves(self):
        """Return valid moves based on the active sub-board."""
        valid_moves = []
        
        if self.active_sub_row is None or self.active_sub_col is None:
            # First move or no valid sub-board - can play anywhere
            for r in range(9):
                for c in range(9):
                    if self.board[r][c] is EMPTY:
                        valid_moves.append((r, c))
        else:
            # Normal play - must play in the active sub-board if it has empty cells
            rows, cols = self.get_sub_board_indices(self.active_sub_row, self.active_sub_col)
            for r in rows:
                for c in cols:
                    if self.board[r][c] is EMPTY:
                        valid_moves.append((r, c))
            
            # If the active sub-board is full, can play anywhere on the board
            if not valid_moves:
                for r in range(9):
                    for c in range(9):
                        if self.board[r][c] is EMPTY:
                            valid_moves.append((r, c))
        
        return valid_moves

    def make_move(self, row, col):
        """Make a move at the given position if valid."""
        valid_moves = self.get_valid_moves()
        
        if (row, col) in valid_moves:
            self.board[row][col] = self.current_player
            self.last_move = (row, col)
            
            # Update active sub-board for next turn
            self.active_sub_row = row % 3
            self.active_sub_col = col % 3
            
            # Update meta-board
            self.update_meta_board()
            
            # Check for winner
            self.winner = self.check_global_winner()
            if self.winner:
                self.game_over = True
            
            # Switch player
            self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
            return True
        return False

    def ai_move(self):
        """Make a random AI move."""
        if self.game_over or self.current_player != PLAYER_O or not self.ai_enabled:
            return
        
        valid_moves = self.get_valid_moves()
        if valid_moves:
            move = random.choice(valid_moves)
            self.make_move(move[0], move[1])

    def draw_x(self, surface, x, y, size, thickness=2, color=BLUE):
        """Draw an X marker."""
        margin = size * 0.2
        pygame.draw.line(surface, color, (x + margin, y + margin), 
                         (x + size - margin, y + size - margin), thickness)
        pygame.draw.line(surface, color, (x + size - margin, y + margin), 
                         (x + margin, y + size - margin), thickness)

    def draw_o(self, surface, x, y, size, thickness=2, color=RED):
        """Draw an O marker."""
        margin = size * 0.2
        pygame.draw.circle(surface, color, (x + size // 2, y + size // 2), 
                          size // 2 - margin, thickness)

    def draw_grid(self, surface, x, y, size, cell_size):
        """Draw a 3x3 grid."""
        for i in range(4):  # Draw 4 lines for 3x3 grid
            # Horizontal lines
            line_thickness = 3 if i % 3 == 0 else 1
            pygame.draw.line(surface, GRID_COLOR, (x, y + i * cell_size), 
                            (x + size, y + i * cell_size), line_thickness)
            # Vertical lines
            pygame.draw.line(surface, GRID_COLOR, (x + i * cell_size, y), 
                            (x + i * cell_size, y + size), line_thickness)

    def draw_big_grid(self, surface, x, y, size):
        """Draw the main 3x3 grid with thick lines."""
        for i in range(4):  # Draw 4 lines for 3x3 grid
            thickness = 5 if i % 3 == 0 else 2
            # Horizontal lines
            pygame.draw.line(surface, THICK_LINE_COLOR, (x, y + i * (size // 3)), 
                            (x + size, y + i * (size // 3)), thickness)
            # Vertical lines
            pygame.draw.line(surface, THICK_LINE_COLOR, (x + i * (size // 3), y), 
                            (x + i * (size // 3), y + size), thickness)

    def draw_main_board(self):
        """Draw the main 9x9 game board."""
        board_x = MARGIN
        board_y = MARGIN
        cell_size = BOARD_SIZE // 9
        sub_board_size = cell_size * 3
        
        # Draw white background
        pygame.draw.rect(self.window, WHITE, (board_x, board_y, BOARD_SIZE, BOARD_SIZE))
        
        # Highlight active sub-board if set
        if self.active_sub_row is not None and self.active_sub_col is not None and not self.game_over:
            sub_x = board_x + self.active_sub_col * sub_board_size
            sub_y = board_y + self.active_sub_row * sub_board_size
            pygame.draw.rect(self.window, ACTIVE_SUBBOARD_COLOR, 
                           (sub_x, sub_y, sub_board_size, sub_board_size))
        
        # Highlight last move
        if self.last_move:
            last_row, last_col = self.last_move
            cell_x = board_x + last_col * cell_size
            cell_y = board_y + last_row * cell_size
            pygame.draw.rect(self.window, HIGHLIGHT_COLOR, 
                           (cell_x, cell_y, cell_size, cell_size))
        
        # Draw the main grid (thick lines separating 3x3 sub-boards)
        self.draw_big_grid(self.window, board_x, board_y, BOARD_SIZE)
        
        # Draw sub-board grids and pieces
        for sr in range(3):
            for sc in range(3):
                sub_x = board_x + sc * sub_board_size
                sub_y = board_y + sr * sub_board_size
                
                # Draw grid for this sub-board
                for i in range(1, 3):  # Inner grid lines (thin)
                    # Horizontal lines
                    pygame.draw.line(self.window, GRID_COLOR, 
                                  (sub_x, sub_y + i * cell_size), 
                                  (sub_x + sub_board_size, sub_y + i * cell_size), 1)
                    # Vertical lines
                    pygame.draw.line(self.window, GRID_COLOR, 
                                  (sub_x + i * cell_size, sub_y), 
                                  (sub_x + i * cell_size, sub_y + sub_board_size), 1)
                
                # Draw X's and O's in the cells
                rows, cols = self.get_sub_board_indices(sr, sc)
                for r_idx, r in enumerate(rows):
                    for c_idx, c in enumerate(cols):
                        cell_x = sub_x + c_idx * cell_size
                        cell_y = sub_y + r_idx * cell_size
                        
                        if self.board[r][c] == PLAYER_X:
                            self.draw_x(self.window, cell_x, cell_y, cell_size, 3)
                        elif self.board[r][c] == PLAYER_O:
                            self.draw_o(self.window, cell_x, cell_y, cell_size, 3)

    def draw_meta_board(self):
        """Draw the smaller meta-board showing sub-board winners."""
        meta_x = WINDOW_WIDTH - META_BOARD_SIZE - MARGIN
        meta_y = MARGIN
        cell_size = META_BOARD_SIZE // 3
        
        # Draw background
        pygame.draw.rect(self.window, LIGHT_GRAY, 
                       (meta_x, meta_y, META_BOARD_SIZE, META_BOARD_SIZE))
        
        # Draw grid
        self.draw_grid(self.window, meta_x, meta_y, META_BOARD_SIZE, cell_size)
        
        # Draw X's and O's for sub-board winners
        for r in range(3):
            for c in range(3):
                cell_x = meta_x + c * cell_size
                cell_y = meta_y + r * cell_size
                
                if self.meta_board[r][c] == PLAYER_X:
                    self.draw_x(self.window, cell_x, cell_y, cell_size, 2)
                elif self.meta_board[r][c] == PLAYER_O:
                    self.draw_o(self.window, cell_x, cell_y, cell_size, 2)

    def draw_status_bar(self):
        """Draw the status bar with game info."""
        status_x = MARGIN
        status_y = MARGIN + BOARD_SIZE + 10
        status_width = WINDOW_WIDTH - (2 * MARGIN)
        status_height = WINDOW_HEIGHT - status_y - MARGIN
        
        # Draw background
        pygame.draw.rect(self.window, LIGHT_GRAY, 
                       (status_x, status_y, status_width, status_height))
        
        # Draw text
        if self.game_over:
            if self.winner:
                status_text = f"Player {self.winner} wins the game!"
                text_color = BLUE if self.winner == PLAYER_X else RED
            else:
                status_text = "Game ended in a draw!"
                text_color = PURPLE
        else:
            status_text = f"Player {self.current_player}'s turn"
            text_color = BLUE if self.current_player == PLAYER_X else RED
            
            if self.active_sub_row is not None:
                sub_board_text = f"Active sub-board: ({self.active_sub_row}, {self.active_sub_col})"
                sub_board_render = self.small_font.render(sub_board_text, True, DARK_GRAY)
                self.window.blit(sub_board_render, (status_x + 10, status_y + 40))
        
        # Render the status text
        status_render = self.font.render(status_text, True, text_color)
        self.window.blit(status_render, (status_x + 10, status_y + 10))

    def draw_instructions(self):
        """Draw game instructions."""
        instr_x = WINDOW_WIDTH - META_BOARD_SIZE - MARGIN
        instr_y = META_BOARD_SIZE + MARGIN + 10
        
        instructions = [
            "How to play:",
            "- Click to make a move",
            "- You must play in the sub-board",
            "  corresponding to the last move",
            "- Win 3 sub-boards in a row to win",
            "",
            "Press 'R' to restart",
            "Press 'A' to toggle AI"
        ]
        
        for i, line in enumerate(instructions):
            instr_render = self.small_font.render(line, True, DARK_GRAY)
            self.window.blit(instr_render, (instr_x, instr_y + i * 20))

    def check_for_draw(self):
        """Check if the game is a draw (board full with no winner)."""
        for r in range(9):
            for c in range(9):
                if self.board[r][c] is EMPTY:
                    return False
        return True

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset game
                    self.__init__()
                elif event.key == pygame.K_a:  # Toggle AI
                    self.ai_enabled = not self.ai_enabled
            
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if self.current_player == PLAYER_X:  # Only handle clicks for human player
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    board_x = MARGIN
                    board_y = MARGIN
                    
                    # Check if click is within the main board
                    if (board_x <= mouse_x <= board_x + BOARD_SIZE and 
                        board_y <= mouse_y <= board_y + BOARD_SIZE):
                        # Convert click to board coordinates
                        cell_size = BOARD_SIZE // 9
                        col = (mouse_x - board_x) // cell_size
                        row = (mouse_y - board_y) // cell_size
                        
                        # Try to make a move
                        self.make_move(row, col)

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        
        while True:
            # Handle events
            self.handle_events()
            
            # Clear the screen
            self.window.fill(GRAY)
            
            # Draw game elements
            self.draw_main_board()
            self.draw_meta_board()
            self.draw_status_bar()
            self.draw_instructions()
            
            # Update display
            pygame.display.flip()
            
            # AI move if it's the AI's turn
            if self.current_player == PLAYER_O and self.ai_enabled and not self.game_over:
                self.ai_timer += clock.get_time()
                if self.ai_timer >= self.ai_delay:
                    self.ai_move()
                    self.ai_timer = 0
            
            # Check for draw
            if not self.game_over and self.check_for_draw():
                self.game_over = True
            
            # Cap at 60 FPS
            clock.tick(60)

if __name__ == "__main__":
    game = UltimateTicTacToe()
    game.run()