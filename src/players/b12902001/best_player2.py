class best_player2:
    def __init__ (self, player_idx):
        self.player_idx = player_idx
    
    def action(self, hand, history):
        return hand[len(hand)-1]