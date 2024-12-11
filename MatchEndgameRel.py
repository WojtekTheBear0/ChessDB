import chess.pgn
import chess
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'ChessDB'
}

def extract_and_evaluate_fen(match_pgn):
    # Parse PGN
    game = chess.pgn.read_game(match_pgn)
    endgame_fens = []
    
    # Iterate through the moves and extract FENs
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()
        
        # Apply endgame detection logic
        if is_endgame(fen):
            endgame_fens.append(fen)
    
    return endgame_fens

def is_endgame(fen):
    # Example: Simple endgame detection logic
    board = chess.Board(fen)
    piece_counts = sum(1 for piece in board.piece_map().values())
    if piece_counts <= 5:  
        return True
    return False

def process_matches():
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch matches
    cursor.execute("SELECT `Event`, Round, PGN FROM `match`;")
    matches = cursor.fetchall()

    for match_event, match_round, match_pgn in matches:
        # Extract and evaluate FEN positions
        endgame_fens = extract_and_evaluate_fen(match_pgn)

        # Insert endgame FENs into the database
        for fen in endgame_fens:
            cursor.execute(
                "INSERT INTO match_endgame (Match_Event, Match_Round, Endgame_FEN) VALUES (%s, %s, %s);",
                (match_event, match_round, fen)
            )
    
    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

# Run the process
process_matches()