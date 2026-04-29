import json
import os
import random

class BestPlayer1:
    def __init__ (self, player_idx):
        self.player_idx = player_idx
        self.W_1, self.W_2, self.W_3, self.W_4, self.W_5, self.W_6 = (5, 10, 10, 10, 20, 250)
    def _card_to_bull_heads(self, card):
        if card % 55 == 0:
            return 7
        elif card % 11 == 0:
            return 5
        elif card % 10 == 0:
            return 3
        elif card % 5 == 0:
            return 2
        else:
            return 1
    def _get_row_penalty(self, row):
        return sum(self._card_to_bull_heads(c) for c in row)
    def _one_step_lookahead(self, card, history, hand, unseen_cards):
        available_cards = [i for i in range(1, 105) if unseen_cards[i]]
        penalty_sum = 0
        # simulate others actions and evaluate the outcome for 100 times, then average the results to get an estimate of the risk of playing this card
        for _ in range(100):
            cards = random.sample(available_cards, 3)
            cards.append(card)
            simulated_history = {
                "board": [row[:] for row in history["board"]]
            }
            sorted_cards = cards[:]
            sorted_cards.sort()
            for i in range(4):
                best_row = -1
                min_diff = 104
                for j in range(4):
                    if sorted_cards[i] > simulated_history["board"][j][-1]:
                        diff = sorted_cards[i] - simulated_history["board"][j][-1]
                        if diff < min_diff:
                            min_diff = diff
                            best_row = j
                if sorted_cards[i] != card:
                    if best_row == -1:
                        simulated_history["board"][min(range(4), key=lambda r: self._get_row_penalty(simulated_history["board"][r]))].clear()
                        simulated_history["board"][min(range(4), key=lambda r: self._get_row_penalty(simulated_history["board"][r]))].append(sorted_cards[i])
                    elif len(simulated_history["board"][best_row]) == 5:
                        simulated_history["board"][best_row].clear()
                        simulated_history["board"][best_row].append(sorted_cards[i])
                    else:
                        simulated_history["board"][best_row].append(sorted_cards[i])
                else:
                    if best_row == -1:
                        penalty_sum += self._get_row_penalty(simulated_history["board"][min(range(4), key=lambda r: self._get_row_penalty(simulated_history["board"][r]))])
                        simulated_history["board"][min(range(4), key=lambda r: self._get_row_penalty(simulated_history["board"][r]))].clear()
                        simulated_history["board"][min(range(4), key=lambda r: self._get_row_penalty(simulated_history["board"][r]))].append(sorted_cards[i])
                    elif len(simulated_history["board"][best_row]) == 5:
                        penalty_sum += self._get_row_penalty(simulated_history["board"][best_row])
                        simulated_history["board"][best_row].clear()
                        simulated_history["board"][best_row].append(sorted_cards[i])
                    else:
                        simulated_history["board"][best_row].append(sorted_cards[i])
        penalty_sum /= 100
        return penalty_sum
    def _evaluate_card(self, card, history, hand, unseen_cards):
        row_penalties = [self._get_row_penalty(r) for r in history["board"]]
        min_diff = 104
        best_row = -1
        for j in range(4):
            if card > history["board"][j][-1]:
                diff = card - history["board"][j][-1]
                if diff < min_diff:
                    min_diff = diff
                    best_row = j
        penalty_sum = 0
        # feature 1
        if best_row == -1:
            f1_min_diff = 0
        else:
            f1_min_diff = min_diff
        #feature 2
        if best_row == -1:
            f2_row_length = 0
        else:
            f2_row_length = len(history["board"][best_row])
        #feature 3
        if best_row == -1:
            f3_row_penalty = min(row_penalties)
        else:
            f3_row_penalty = row_penalties[best_row]
        #feature 4
        if best_row == -1:
            f4_card_value = card
        else:
            f4_card_value = 0
        #feature 5
        if best_row != -1 and 5 - len(history["board"][best_row]) >= min_diff:
            f5_overflow_risk = 1
        else:
            f5_overflow_risk = 0
        
        penalty_sum += self.W_1 * f1_min_diff + self.W_2 * f2_row_length + self.W_3 * f3_row_penalty + self.W_4 * f4_card_value + self.W_5 * f5_overflow_risk + self.W_6 * self._one_step_lookahead(card, history, hand, unseen_cards)
        return penalty_sum
    
    def action(self, hand, history):
        unseen_cards = [True] * 105
        unseen_cards[0] = False
        for row in history["board"]:
            for c in row:
                unseen_cards[c] = False
        for c in hand:
            unseen_cards[c] = False
        if history.get("board_history"):
            for past_board in history["board_history"]:
                for row in past_board:
                    for c in row:
                        unseen_cards[c] = False
        evaluated_cards = [self._evaluate_card(c, history, hand, unseen_cards) for c in hand]
        # print("hand:", hand)
        return hand[evaluated_cards.index(min(evaluated_cards))]