from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development. Be more specific in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state
game_state = {
    "board": [["", "", ""], ["", "", ""], ["", "", ""]],
    "current_player": "X",
    "status": "playing",  # "playing", "X_wins", "O_wins", "draw"
}

class Move(BaseModel):
    row: int
    col: int

def check_winner(board):
    # Check rows
    for row in board:
        if row[0] != "" and row[0] == row[1] == row[2]:
            return row[0]
    
    # Check columns
    for col_idx in range(3):
        if board[0][col_idx] != "" and board[0][col_idx] == board[1][col_idx] == board[2][col_idx]:
            return board[0][col_idx]
    
    # Check diagonals
    if board[0][0] != "" and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != "" and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    return None

def check_draw(board):
    for row in board:
        for cell in row:
            if cell == "":
                return False  # Game is not a draw yet
    return True # All cells filled, no winner

def reset_game():
    global game_state
    game_state = {
        "board": [["", "", ""], ["", "", ""], ["", "", ""]],
        "current_player": "X",
        "status": "playing",
    }
    return game_state

@app.get("/game")
async def get_game_state():
    return game_state

@app.post("/game/reset")
async def reset_game_endpoint():
    return reset_game()

@app.post("/game/move")
async def make_move(move: Move):
    global game_state

    row, col = move.row, move.col

    if not (0 <= row < 3 and 0 <= col < 3):
        raise HTTPException(status_code=400, detail="Invalid move coordinates.")
    
    if game_state["status"] != "playing":
        raise HTTPException(status_code=400, detail=f"Game is already over. Status: {game_state['status']}")

    if game_state["board"][row][col] != "":
        raise HTTPException(status_code=400, detail="Cell is already occupied.")

    # Apply move
    game_state["board"][row][col] = game_state["current_player"]

    # Check for winner
    winner = check_winner(game_state["board"])
    if winner:
        game_state["status"] = f"{winner}_wins"
    elif check_draw(game_state["board"]):
        game_state["status"] = "draw"
    else:
        # Switch player
        game_state["current_player"] = "O" if game_state["current_player"] == "X" else "X"
    
    return game_state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()
