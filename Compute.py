import chess

# Constants for piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables for WHITE and BLACK
PAWN_TABLE_WHITE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    35, 35, 35, 50, 50, 35, 35, 35,
    35, 25, 35, 45, 45, 35, 25, 35,
    0, 20, 30, 40, 40, 30, 20, 0,
    0, 10, 25, 30, 30, -5, 0, 0,
    0, 0, 0, 20, 20, -15, 0, 0,
    0, 0, 0, 0, 0, 10, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
]

KNIGHT_TABLE_WHITE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, 20, 0, 0, 0, 0, 20, -40,
    10, 15, 30, 25, 25, 30, 15, 10,
    15, 5, 25, 20, 20, 25, 5, 15,
    20, 0, 15, 20, 20, 15, 0, 20,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

# Flipping piece-square tables for black (mirror effect)
PAWN_TABLE_BLACK = PAWN_TABLE_WHITE[::-1]
KNIGHT_TABLE_BLACK = KNIGHT_TABLE_WHITE[::-1]

# Function to get piece-square value based on color
def piece_square_value(piece_type, square, color):
    if piece_type == chess.PAWN:
        return PAWN_TABLE_WHITE[square] if color == chess.WHITE else PAWN_TABLE_BLACK[square]
    if piece_type == chess.KNIGHT:
        return KNIGHT_TABLE_WHITE[square] if color == chess.WHITE else KNIGHT_TABLE_BLACK[square]
    # Add other piece-square tables as necessary
    return 0

class Compute:
    def __init__(self):
        pass

    def evaluate_position(self, board, color):
        score = 0
        own_pieces = board.occupied_co[color]
        opp_pieces = board.occupied_co[not color]

        # Iterate over all squares and calculate material and positional value
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = PIECE_VALUES[piece.piece_type]
                positional_value = piece_square_value(piece.piece_type, square, piece.color)
                score += (value + positional_value) if piece.color == color else -(value + positional_value)

        # Evaluate pawn structure, king safety, etc.
        score += self.pawn_structure(board, color)
        score += self.king_safety(board, color)
        score += self.mobility_evaluation(board, color)
        score += self.bishop_pair_bonus(board, color)
        score += self.rook_activity(board, color)
        score += self.connected_rooks(board, color)
        score += self.outpost_bonus(board, color)

        score -= self.pawn_structure(board, not color)
        score -= self.king_safety(board, not color)
        score -= self.mobility_evaluation(board, not color)
        score -= self.bishop_pair_bonus(board, not color)
        score -= self.rook_activity(board, not color)
        score -= self.connected_rooks(board, not color)
        score -= self.outpost_bonus(board, not color)

        # Return the final score
        print(score)
        return score

    def pawn_structure(self, board, color):
        score = 0
        pawns = board.pieces(chess.PAWN, color)
        opponent_pawns = board.pieces(chess.PAWN, not color)

        # Check for doubled, isolated, passed, and backward pawns
        for pawn in pawns:
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)

            # Doubled pawns
            same_file_pawns = [sq for sq in pawns if chess.square_file(sq) == file]
            if len(same_file_pawns) > 1:
                score -= 50

            # Isolated pawns
            adjacent_files = [file - 1, file + 1]
            isolated = not any(chess.square_file(p) in adjacent_files for p in pawns)
            if isolated:
                score -= 50

            # Passed pawns
            passed = not any(
                chess.square_file(p) == file and (
                    (color == chess.WHITE and chess.square_rank(p) > rank) or
                    (color == chess.BLACK and chess.square_rank(p) < rank)
                )
                for p in opponent_pawns
            )
            if passed:
                score += 100

            # Backward pawns
            backward = all(
                file_offset not in range(8) or not board.piece_at(chess.square(file_offset, rank - 1 if color == chess.WHITE else rank + 1))
                for file_offset in [file - 1, file + 1]
            )
            if backward:
                score -= 30

        return score

    def king_safety(self, board, color):
        score = 0
        king_square = board.king(color)
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)

        # Check for pawn shield around the king
        shield_squares = [
            chess.square(king_file + offset, king_rank - 1) if color == chess.WHITE else chess.square(king_file + offset, king_rank + 1)
            for offset in [-1, 0, 1]
        ]

        for sq in shield_squares:
            if 0 <= chess.square_file(sq) < 8 and 0 <= chess.square_rank(sq) < 8:
                piece = board.piece_at(sq)
                if piece is None or piece.piece_type != chess.PAWN:
                    score -= 50  # Penalty for missing pawn shield

        return score

    def mobility_evaluation(self, board, color):
        legal_moves = len(list(board.legal_moves))
        return legal_moves

    def bishop_pair_bonus(self, board, color):
        if len(board.pieces(chess.BISHOP, color)) == 2:
            return 30  # Bishop pair bonus
        return 0

    def rook_activity(self, board, color):
        score = 0
        for rook in board.pieces(chess.ROOK, color):
            file = chess.square_file(rook)

            # Open file bonus (no pawns on this file)
            open_file = all(
                board.piece_at(chess.square(file, rank)) is None or board.piece_at(chess.square(file, rank)).piece_type != chess.PAWN
                for rank in range(8)
            )
            if open_file:
                score += 50

            # 7th/8th rank bonus for rooks
            if chess.square_rank(rook) == (7 if color == chess.WHITE else 0):
                score += 30

        return score

    def connected_rooks(self, board, color):
        rooks = list(board.pieces(chess.ROOK, color))
        if len(rooks) == 2:
            if chess.square_file(rooks[0]) == chess.square_file(rooks[1]) or chess.square_rank(rooks[0]) == chess.square_rank(rooks[1]):
                return 30  # Bonus for connected rooks
        return 0

    def outpost_bonus(self, board, color):
        score = 0
        knights = board.pieces(chess.KNIGHT, color)
        for knight in knights:
            file = chess.square_file(knight)
            rank = chess.square_rank(knight)
            if (color == chess.WHITE and rank >= 4) or (color == chess.BLACK and rank <= 3):
                outpost = not any(
                    board.piece_at(chess.square(file, r)) and board.piece_at(chess.square(file, r)).piece_type == chess.PAWN
                    for r in (range(rank, 8) if color == chess.WHITE else range(0, rank + 1))
                )
                if outpost:
                    score += 40

        return score