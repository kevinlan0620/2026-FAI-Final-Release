class best_player1:
    def __init__ (self, player_idx):
        self.player_idx = player_idx
    
    def action(self, hand, history):
        threshold_min = 20
        min_diff = 104
        min_diff_idx = -1
        for i in range(len(hand)-1):
            if hand[i] < threshold_min:
                return hand[i]
            else:
                for j in range(4):
                    if hand[i] > history.board[j][len(history.board[j])-1]:
                        diff = hand[i] - history.board[j][len(history.board[j])-1]
                        if diff < min_diff and len(history.board[j]) < 5:
                            min_diff = diff
                            min_diff_idx = i
        if min_diff == 104:
            return hand[len(hand)-1]
        return hand[min_diff_idx]