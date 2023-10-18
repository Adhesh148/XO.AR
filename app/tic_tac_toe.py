def areMovesLeft(board):
    """
    checks if there any moves left in the board
    :param board: matrix that gives the current state of the board
    :return bool: True if any move is left and False if none are left
    """
    for i in range(3):
        for j in range(3):
            if board[i][j] == '_':
                return True
    return False


def evaluate(board, player, opponent):
    """
    evaluation function that gives the score
    """
    
    # Check for horizontal victory possibility
    for i in range(3):
        if((board[i][0] == board[i][1]) and (board[i][1] == board[i][2])):
            if board[i][0] == player:
                return 10
            elif board[i][0] == opponent:
                return -10
    
    # Check for vertical victory possibility
    for j in range(3):
        if((board[0][j] == board[1][j]) and (board[1][j] == board[2][j])):
            if board[0][j] == player:
                return 10
            elif board[0][j] == opponent:
                return -10
            
    # Finally, check for diagonal victory possibility
    if(((board[0][0] == board[1][1]) and (board[1][1] == board[2][2])) or \
       ((board[0][2] == board[1][1]) and (board[1][1] == board[2][0]))):
        if board[1][1] == player:
                return 10
        elif board[1][1] == opponent:
                return -10
    
    return 0

def minimax(board, depth, isMax, player, opponent):
    """
    considers all possible future moves and returns the value of the board
    """
    
    score = evaluate(board, player, opponent)
    
    # if maximizer or minimizer has won the game already, just return the score
    if score == 10 or score == -10:
        return score
    
    # if it is a tie state, return 0
    if areMovesLeft(board) == False:
        return 0
    
    # if it is maximizer's move
    if(isMax == True):
        best = -1000
        
        # From all possible moves, calculate the best possible moves score 
        for i in range(3):
            for j in range(3):
                if(board[i][j] == '_'):
                    board[i][j] = player                                    # make the move
                    best = max(best,minimax(board,depth+1,not isMax, player,opponent))      # call minmax recursively
                    board[i][j] = '_'                                       # undo the move     
        return best
                    
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if(board[i][j] == '_'):
                    board[i][j] = opponent
                    best = min(best, minimax(board,depth+1,not isMax, player, opponent))
                    board[i][j] = '_'
        return best

def findBestMove(board, player, opponent):
    best = -1000
    best_move = (-1,-1)
    
    # Traverse all empty cells and return the cell with optimal value
    for i in range(3):
        for j in range(3):
            if board[i][j] == '_':
                board[i][j] = player
                val = minimax(board, 0, False, player, opponent)
                board[i][j] = '_'
                
                if val > best:
                    best_move = (i,j)
                    best = val
                    
    return best_move