# Pirate's Cove

A treasure-hunting board game created using Flask and Python for CIST 1600.

## Description

Pirate's Cove is a turn-based board game where players select spaces on a 10x10 grid to reveal events that can affect their coin totals. The first player to collect 100 coins wins the game.

## Game Features

- 6x6 grid board where players select spaces
- Various event types:
  - Gain coins (e.g., Blackbeard's treasure, X marks the spot)
  - Lose coins (e.g., Walk the plank, Swashbuckled)
  - No change (e.g., Shiver me timbers!, Yo ho ho!)
  - Special actions (e.g., Pirate Raid, Drunken Dealings)
- Player turn system with visual indicators
- Win condition: first player to reach 100 coins

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pirates-cove.git
   cd pirates-cove
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install requirements:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
pirates_cove/
│
├── app.py               # Main Flask application
│
├── templates/           # HTML templates folder
│   ├── base.html        # Base template with common styling
│   ├── setup.html       # Player setup page
│   └── game.html        # Main game page
│
├── static/              # Static assets (optional)
│   └── images/          # If you want to add images
│
├── requirements.txt     # Project dependencies
│
└── README.md            # Project documentation
```

## Design Document

The original game design document can be found here:
[Pirate's Cove Design Document](https://docs.google.com/document/d/1EsTncXmXBVEbCfjERBhDIZjBE4dqVLPP7yi4AZ1QORo/edit?usp=sharing)

## How to Play

1. Enter names for both players on the setup screen
2. Take turns selecting spaces on the grid
3. Each space reveals an event that can affect your coin total
4. The first player to reach 100 coins wins!

## Authors

- Jacob Lamoureux
- Noah Morland

## License

This project is created for educational purposes for CIST 1600.