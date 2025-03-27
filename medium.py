import numpy as np
import pickle
import os
from typing import Tuple, List, Dict
import random

class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1, epsilon_decay=0.995, epsilon_min=0.01):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = {}
        self.state_history = []
        self.action_history = []
        self.reward_history = []
        self.learning_metrics = {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0,
            'average_reward': 0,
            'total_states': 0,
            'exploration_rate': self.epsilon
        }
        
    def get_state_key(self, main_board: List[List[str]], meta_board: List[List[str]], 
                      last_move: Tuple[int, int], current_player: str) -> str:
        """Convert game state to a string key for Q-table"""
        state = []
        # Add main board state
        for row in main_board:
            for cell in row:
                state.append(cell if cell else ' ')
        # Add meta board state
        for row in meta_board:
            for cell in row:
                state.append(cell if cell else ' ')
        # Add last move and current player
        state.extend([str(last_move[0]), str(last_move[1]), current_player])
        return ''.join(state)
    
    def get_valid_actions(self, main_board: List[List[str]], meta_board: List[List[str]], 
                         last_move: Tuple[int, int]) -> List[Tuple[int, int, int, int]]:
        """Get all valid actions for the current state"""
        valid_actions = []
        if last_move is None:
            # First move can be anywhere
            for i in range(3):
                for j in range(3):
                    for sub_i in range(3):
                        for sub_j in range(3):
                            valid_actions.append((i, j, sub_i, sub_j))
        else:
            # Must play in the sub-board corresponding to last move
            sub_board_i, sub_board_j = last_move
            if meta_board[sub_board_i][sub_board_j] == ' ':
                for sub_i in range(3):
                    for sub_j in range(3):
                        if main_board[sub_board_i * 3 + sub_i][sub_board_j * 3 + sub_j] == ' ':
                            valid_actions.append((sub_board_i, sub_board_j, sub_i, sub_j))
        return valid_actions
    
    def choose_action(self, main_board: List[List[str]], meta_board: List[List[str]], 
                     last_move: Tuple[int, int], current_player: str) -> Tuple[int, int, int, int]:
        """Choose an action using epsilon-greedy policy"""
        state = self.get_state_key(main_board, meta_board, last_move, current_player)
        valid_actions = self.get_valid_actions(main_board, meta_board, last_move)
        
        if random.random() < self.epsilon:
            # Explore: choose random action
            return random.choice(valid_actions)
        
        # Exploit: choose best action
        best_value = float('-inf')
        best_actions = []
        
        for action in valid_actions:
            action_key = f"{state}:{action}"
            value = self.q_table.get(action_key, 0)
            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)
        
        return random.choice(best_actions)
    
    def update_metrics(self, reward, is_game_over):
        """Update learning metrics after each game"""
        self.learning_metrics['total_games'] += 1
        if is_game_over:
            if reward == 1.0:
                self.learning_metrics['wins'] += 1
            elif reward == -1.0:
                self.learning_metrics['losses'] += 1
            else:
                self.learning_metrics['draws'] += 1
            
            # Update win rate
            self.learning_metrics['win_rate'] = self.learning_metrics['wins'] / self.learning_metrics['total_games']
            
            # Update average reward
            self.learning_metrics['average_reward'] = sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0
            
            # Update total states
            self.learning_metrics['total_states'] = len(self.q_table)
            
            # Decay epsilon and update exploration rate
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            self.learning_metrics['exploration_rate'] = self.epsilon
            
            # Clear history for next game
            self.state_history = []
            self.action_history = []
            self.reward_history = []
    
    def get_metrics(self):
        """Get current learning metrics"""
        return self.learning_metrics
    
    def update(self, state: str, action: Tuple[int, int, int, int], 
               reward: float, next_state: str, next_valid_actions: List[Tuple[int, int, int, int]]):
        """Update Q-values using Q-learning update rule"""
        action_key = f"{state}:{action}"
        current_value = self.q_table.get(action_key, 0)
        
        # Get max Q-value for next state
        next_max_value = float('-inf')
        for next_action in next_valid_actions:
            next_action_key = f"{next_state}:{next_action}"
            next_value = self.q_table.get(next_action_key, 0)
            next_max_value = max(next_max_value, next_value)
        
        # Q-learning update
        new_value = current_value + self.learning_rate * (
            reward + self.discount_factor * next_max_value - current_value
        )
        self.q_table[action_key] = new_value
        
        # Track history
        self.state_history.append(state)
        self.action_history.append(action)
        self.reward_history.append(reward)
        
        # Update metrics
        self.update_metrics(reward, not next_valid_actions)
    
    def save_model(self, filename: str = 'q_learning_model.pkl'):
        """Save the Q-table and metrics to a file"""
        save_data = {
            'q_table': self.q_table,
            'metrics': self.learning_metrics,
            'epsilon': self.epsilon
        }
        with open(filename, 'wb') as f:
            pickle.dump(save_data, f)
    
    def load_model(self, filename: str = 'q_learning_model.pkl'):
        """Load the Q-table and metrics from a file"""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
                self.q_table = save_data.get('q_table', {})
                self.learning_metrics = save_data.get('metrics', self.learning_metrics)
                self.epsilon = save_data.get('epsilon', self.epsilon)
                self.learning_metrics['exploration_rate'] = self.epsilon

def check_winner(board: List[List[str]]) -> str:
    """Check if there's a winner in a 3x3 board"""
    # Check rows
    for row in board:
        if row.count(row[0]) == 3 and row[0] != ' ':
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    
    return ' '

def get_sub_board(main_board: List[List[str]], sub_board_i: int, sub_board_j: int) -> List[List[str]]:
    """Extract a sub-board from the main board"""
    sub_board = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(main_board[sub_board_i * 3 + i][sub_board_j * 3 + j])
        sub_board.append(row)
    return sub_board

def make_move(main_board: List[List[str]], meta_board: List[List[str]], 
              action: Tuple[int, int, int, int], player: str) -> Tuple[List[List[str]], List[List[str]]]:
    """Make a move on the board and return updated boards"""
    sub_board_i, sub_board_j, sub_i, sub_j = action
    main_board[sub_board_i * 3 + sub_i][sub_board_j * 3 + sub_j] = player
    
    # Update meta board if sub-board is won
    sub_board = get_sub_board(main_board, sub_board_i, sub_board_j)
    winner = check_winner(sub_board)
    if winner != ' ':
        meta_board[sub_board_i][sub_board_j] = winner
    
    return main_board, meta_board

def get_reward(meta_board: List[List[str]], player: str) -> float:
    """Calculate reward based on game state"""
    winner = check_winner(meta_board)
    if winner == player:
        return 1.0
    elif winner != ' ':
        return -1.0
    return 0.0 