# Ultimate Tic-Tac-Toe with Q-Learning AI

A web-based implementation of Ultimate Tic-Tac-Toe with an AI opponent that uses Q-Learning to improve its gameplay over time.

## Features

- Beautiful, responsive UI with dark/light theme support
- Q-Learning AI opponent that learns from gameplay
- Mobile-friendly design
- Smooth animations and visual feedback
- Difficulty levels (Easy, Medium, Hard)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd UltimateTicTakToe
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

## How to Play

1. The game is played on a 3x3 grid of 3x3 sub-boards
2. Players take turns placing their marks (X or O) in empty cells
3. The location of your move determines which sub-board your opponent must play in next
4. Win a sub-board by getting three in a row
5. Win the game by winning three sub-boards in a row

## AI Implementation

The AI opponent uses Q-Learning to improve its gameplay:

- The Q-table is saved after each game
- The AI learns from both wins and losses
- The model improves over time as more games are played

## Development

The project structure is organized as follows:

- `app.py`: Flask server and API endpoints
- `medium.py`: Q-Learning implementation
- `index.html`: Main game interface
- `css/styles.css`: Styling
- `js/game.js`: Game logic and UI interactions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
