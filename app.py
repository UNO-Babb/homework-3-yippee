from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import json
import os
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Game constants
GRID_SIZE = 6
WINNING_SCORE = 100

# Category probabilities
CATEGORY_PROBS = {
    "gain": 0.3,
    "loss": 0.3,
    "no_change": 0.3,
    "special": 0.1
}

# Event probabilities within categories
GAIN_EVENTS = [
    {"name": "Blackbeard's treasure", "value": 32, "prob": 0.05},
    {"name": "X marks the spot", "value": 16, "prob": 0.2375},
    {"name": "Pieces of eight", "value": 8, "prob": 0.2375},
    {"name": "Handful o' doubloons", "value": 4, "prob": 0.2375},
    {"name": "Just a little booty", "value": 1, "prob": 0.2375}
]

LOSS_EVENTS = [
    {"name": "Down to Davy Jones' locker", "value": 1.0, "prob": 0.05},  # 100% loss
    {"name": "Walk the plank", "value": 0.5, "prob": 0.2375},  # 50% loss
    {"name": "Swashbuckled", "value": 0.4, "prob": 0.2375},  # 40% loss
    {"name": "Plundered", "value": 0.3, "prob": 0.2375},  # 30% loss
    {"name": "Mutiny", "value": 0.2, "prob": 0.2375},  # 20% loss
    {"name": "Scurvy - suck on a lemon", "value": 0.1, "prob": 0.2375}  # 10% loss
]

NO_CHANGE_EVENTS = [
    {"name": "Getting your sea legs", "prob": 0.1},
    {"name": "Hoist the mainsail!", "prob": 0.1},
    {"name": "Heave ho!", "prob": 0.1},
    {"name": "Shiver me timbers!", "prob": 0.1},
    {"name": "Ahoy!", "prob": 0.1},
    {"name": "Yo ho ho!", "prob": 0.1},
    {"name": "Avast!", "prob": 0.1},
    {"name": "I've got a jar of Dirt!", "prob": 0.1},
    {"name": "Get on with it ye scallywags!", "prob": 0.1},
    {"name": "I'm disinclined to acquiesce to your request", "prob": 0.1}
]

SPECIAL_EVENTS = [
    {"name": "Pirate Raid - steal 20% of the other player's coins", "action": "pirate_raid", "prob": 0.4},
    {"name": "That's gotta be the best pirate i've ever seen - take a second turn", "action": "second_turn", "prob": 0.4},
    {"name": "Drunken Dealings - swap coin amounts with other player", "action": "swap_coins", "prob": 0.2}
]

def initialize_game():
    """Initialize a new game state"""
    # Create the board with categories assigned
    board = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            # Assign category based on probabilities
            category = random.choices(
                list(CATEGORY_PROBS.keys()), 
                weights=list(CATEGORY_PROBS.values()), 
                k=1
            )[0]
            row.append({
                "category": category,
                "revealed": False,
                "event": None
            })
        board.append(row)
    
    # Set up game state
    game_state = {
        "board": board,
        "players": [],
        "current_player_index": 0,
        "winner": None,
        "last_action": None,
        "extra_turn": False
    }
    
    return game_state

def select_event(category):
    """Select a specific event from a category based on probabilities"""
    if category == "gain":
        events = GAIN_EVENTS
    elif category == "loss":
        events = LOSS_EVENTS
    elif category == "no_change":
        events = NO_CHANGE_EVENTS
    elif category == "special":
        events = SPECIAL_EVENTS
    else:
        return None
    
    # Select based on probabilities
    event = random.choices(
        events,
        weights=[event["prob"] for event in events],
        k=1
    )[0]
    
    return event

def apply_event(game_state, event, category, row, col):
    """Apply the selected event's effects to the game state"""
    current_player = game_state["current_player_index"]
    other_player = 1 - current_player if len(game_state["players"]) > 1 else None
    
    # Update the board with the event that was triggered
    game_state["board"][row][col]["event"] = event["name"]
    
    # Set last action for display
    game_state["last_action"] = {
        "category": category,
        "event": event["name"],
        "effect": None
    }
    
    # Apply effect based on category
    if category == "gain":
        gain_amount = event["value"]
        game_state["players"][current_player]["coins"] += gain_amount
        game_state["last_action"]["effect"] = f"Gained {gain_amount} coins"
    
    elif category == "loss":
        current_coins = game_state["players"][current_player]["coins"]
        loss_percentage = event["value"]
        loss_amount = math.floor(current_coins * loss_percentage)
        game_state["players"][current_player]["coins"] -= loss_amount
        game_state["last_action"]["effect"] = f"Lost {loss_amount} coins"
    
    elif category == "no_change":
        game_state["last_action"]["effect"] = "No effect on coins"
    
    elif category == "special" and other_player is not None:
        if event["action"] == "pirate_raid":
            raid_amount = math.floor(game_state["players"][other_player]["coins"] * 0.2)
            game_state["players"][other_player]["coins"] -= raid_amount
            game_state["players"][current_player]["coins"] += raid_amount
            game_state["last_action"]["effect"] = f"Stole {raid_amount} coins from opponent"
        
        elif event["action"] == "second_turn":
            game_state["extra_turn"] = True
            game_state["last_action"]["effect"] = "You get another turn!"
        
        elif event["action"] == "swap_coins":
            current_coins = game_state["players"][current_player]["coins"]
            other_coins = game_state["players"][other_player]["coins"]
            game_state["players"][current_player]["coins"] = other_coins
            game_state["players"][other_player]["coins"] = current_coins
            game_state["last_action"]["effect"] = f"Swapped coin amounts! You now have {other_coins} coins"
    
    # Check for winner
    for i, player in enumerate(game_state["players"]):
        if player["coins"] >= WINNING_SCORE:
            game_state["winner"] = i
            break
    
    return game_state

def next_turn(game_state):
    """Advance to the next player's turn"""
    if not game_state["extra_turn"]:
        game_state["current_player_index"] = (game_state["current_player_index"] + 1) % len(game_state["players"])
    else:
        # Reset the extra turn flag but don't change the player
        game_state["extra_turn"] = False
    
    return game_state

def check_board_full(game_state):
    """Check if all spaces on the board have been revealed"""
    for row in game_state["board"]:
        for cell in row:
            if not cell["revealed"]:
                return False
    return True

def reset_board(game_state):
    """Reset the board but keep player scores and turn order"""
    board = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            category = random.choices(
                list(CATEGORY_PROBS.keys()), 
                weights=list(CATEGORY_PROBS.values()), 
                k=1
            )[0]
            row.append({
                "category": category,
                "revealed": False,
                "event": None
            })
        board.append(row)
    
    game_state["board"] = board
    return game_state

@app.route('/')
def index():
    """Main game page"""
    # Check if a game is in progress
    if 'game_state' not in session:
        return redirect(url_for('setup'))
    
    game_state = json.loads(session['game_state'])
    
    return render_template('game.html', 
                          game_state=game_state, 
                          grid_size=GRID_SIZE,
                          current_player=game_state["players"][game_state["current_player_index"]])

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Game setup page for entering player names"""
    if request.method == 'POST':
        player1 = request.form.get('player1')
        player2 = request.form.get('player2')
        
        if not player1 or not player2:
            return render_template('setup.html', error="Both player names are required")
        
        # Initialize a new game
        game_state = initialize_game()
        game_state['players'] = [
            {"name": player1, "coins": 0},
            {"name": player2, "coins": 0}
        ]
        
        # Store game state in session
        session['game_state'] = json.dumps(game_state)
        
        return redirect(url_for('index'))
    
    return render_template('setup.html')

@app.route('/select', methods=['POST'])
def select_space():
    """Handle a player selecting a space on the board"""
    row = int(request.form.get('row'))
    col = int(request.form.get('col'))
    
    game_state = json.loads(session['game_state'])
    
    # Check if the game is already won
    if game_state["winner"] is not None:
        return redirect(url_for('index'))
    
    # Check if the space is already revealed
    if game_state["board"][row][col]["revealed"]:
        return redirect(url_for('index'))
    
    # Mark the space as revealed
    game_state["board"][row][col]["revealed"] = True
    
    # Get the category and select a specific event
    category = game_state["board"][row][col]["category"]
    event = select_event(category)
    
    # Apply the event's effects
    game_state = apply_event(game_state, event, category, row, col)
    
    # Check if the board is full and reset if needed
    if check_board_full(game_state) and game_state["winner"] is None:
        game_state = reset_board(game_state)
    
    # Advance to the next player's turn if no winner
    if game_state["winner"] is None:
        game_state = next_turn(game_state)
    
    # Update session
    session['game_state'] = json.dumps(game_state)
    
    return redirect(url_for('index'))

@app.route('/reset')
def reset_game():
    """Reset the game completely"""
    session.pop('game_state', None)
    return redirect(url_for('setup'))

if __name__ == '__main__':
    app.run(debug=True)