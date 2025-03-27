from flask import Flask, request, jsonify, send_from_directory
from medium import QLearningAgent
import numpy as np
import os

app = Flask(__name__)
agent = QLearningAgent()
agent.load_model()  # Load existing model if available

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json
    main_board = data['mainBoard']
    meta_board = data['metaBoard']
    last_move = data.get('lastMove')
    current_player = data['currentPlayer']
    
    # Convert empty strings to spaces for consistency
    main_board = [[cell if cell else ' ' for cell in row] for row in main_board]
    meta_board = [[cell if cell else ' ' for cell in row] for row in meta_board]
    
    # Get AI move
    action = agent.choose_action(main_board, meta_board, last_move, current_player)
    
    # Make the move
    sub_board_i, sub_board_j, sub_i, sub_j = action
    main_board[sub_board_i * 3 + sub_i][sub_board_j * 3 + sub_j] = current_player
    
    # Update meta board if sub-board is won
    from medium import get_sub_board, check_winner
    sub_board = get_sub_board(main_board, sub_board_i, sub_board_j)
    winner = check_winner(sub_board)
    if winner != ' ':
        meta_board[sub_board_i][sub_board_j] = winner
    
    # Convert spaces back to empty strings for frontend
    main_board = [[cell if cell != ' ' else '' for cell in row] for row in main_board]
    meta_board = [[cell if cell != ' ' else '' for cell in row] for row in meta_board]
    
    return jsonify({
        'mainBoard': main_board,
        'metaBoard': meta_board,
        'move': {
            'subBoardI': sub_board_i,
            'subBoardJ': sub_board_j,
            'subI': sub_i,
            'subJ': sub_j
        }
    })

@app.route('/api/train', methods=['POST'])
def train_model():
    data = request.json
    state = data['state']
    action = tuple(data['action'])  # Convert list to tuple for dictionary key
    reward = data['reward']
    next_state = data['nextState']
    next_valid_actions = [tuple(action) for action in data['nextValidActions']]  # Convert lists to tuples
    
    # Update the Q-learning model
    agent.update(state, action, reward, next_state, next_valid_actions)
    
    # Save the updated model and metrics
    agent.save_model()
    
    return jsonify({'status': 'success'})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get the current learning metrics"""
    metrics = agent.get_metrics()
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True) 