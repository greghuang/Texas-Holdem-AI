from dummyPokerBot import DummyPokerBot
from pokerStrategy import CardCounting
from pokerStrategy import CardEvaluator
from pokerStrategy import HoleEvaluator
from switch import switch
from poker import Stage
from poker import Action
from pokerBot import getCard
from treys import Card
import math
from random import *


class CardCountingBot(DummyPokerBot):
    cardCounting = CardCounting()
    handEvaluator = CardEvaluator()
    holeEvaluator = HoleEvaluator()
    weightDict = {'2': 1, '3': 1, '4': 2, '5': 2,
                  '6': 3, '7': 3, '8': 3, '9': 4, '10': 4}
    allinTimes = 0
    boardStrength = 0

    def declareAction(self, data, isBet=False):
        self.initAction(data)
        amount = 0
        action = Action.Check

        for case in switch(self.stage):
            if case(Stage.PreFlop):
                (action, amount) = self.withPreFlop(data)
                break
            if case(Stage.Flop):
                (action, amount) = self.withFlop(data)
                break
            if case(Stage.Turn):
                (action, amount) = self.withTurn(data)
                break
            if case(Stage.River):
                (action, amount) = self.withRiver(data)
                break
            if case(Stage.HandOver):
                break

        self.updateBetChips(action, amount)
        return (action, amount)

    def withPreFlop(self, data):
        amount = 0
        action = Action.Check
        self.allinTimes = 0
        self.boardStrength = 0

        Card.print_pretty_cards(self.hands)
        hole_winrate = self.holeEvaluator.evaluate(self.hands, 3, 1000)
        # print('Hole win rate:{}'.format(hole_winrate))
        print('min bet:{}'.format(self.min_bet))

        if hole_winrate > 0.5:  # (J,J)
            action = Action.Allin
        elif hole_winrate > 0.4 and not self.isBetTooMuch(0, 0.5):  # (6,6)
            action = Action.Bet
            amount = self.my_chips / 4
        elif hole_winrate > 0.3:  # (2,2)
        	if not self.isBetTooMuch(0, 0.3):
        		action = Action.Raise
        	else:
        		action = Action.Call
        elif self.player_bb == self.player_hashed_name and not self.isBetTooMuch(0, 0.2):
            action = Action.Check
        elif not self.isBetTooMuch(0, 0.1):
            action = Action.Call
        else:
            action = Action.Fold

        return (action, amount)

    def withFlop(self, data):
        amount = 0
        action = Action.Check

        self.updateHandsStrength(self.hands, self.board)

        (drawCard, expect_rate) = self.cardCounting.evaluate(
            self.hands, self.board, 0.75)
        print('Expect rate:{:2.2%}, Draw Card:'.format(expect_rate))
        Card.print_pretty_cards(drawCard)

        deal = 52 - 2 * self.number_players - len(self.board)
        percentage = min(float(len(drawCard)) / float(deal), 1.0)
        ev = self.evalEV(percentage, expect_rate)

        randEv = self.table_pot * random() / 20
        print('Random EV:{}'.format(randEv))

        if "allin" in self.opponent_action:
            if self.hands_strength >= 0.9:
                action = Action.Call
            elif self.hands_strength >= 0.8 and not self.isBetTooMuch(self.hands_strength):
                action = Action.Call
            else:
                action = Action.Fold
        elif self.hands_strength >= 0.8:
            if not self.isBetTooMuch(self.hands_strength):
                action = Action.Bet
                amount = self.my_chips / 5
            else:
                action = Action.Call
        elif self.hands_strength >= 0.55 and not self.isBetTooMuch(self.hands_strength, 0.35):
            action = Action.Raise
        elif self.hands_strength >= 0.4 and (ev > self.min_bet / 2):
            action = Action.Call
        elif (ev + randEv) > self.min_bet and not self.isBetTooMuch(self.hands_strength, 0.2):
            action = Action.Call
        elif expect_rate > 0.85 and ev > 0:
            action = Action.Call
        else:
            action = Action.Fold

        return (action, amount)

    def withTurn(self, data):
        amount = 0
        action = Action.Check

        self.updateHandsStrength(self.hands, self.board)

        isBoardStrong = self.isBoardCardTooStrong(2, 0.4, 0.1, 3000)
        if isBoardStrong:
            return (Action.Fold, 0)

        (drawCard, expect_rate) = self.cardCounting.evaluate(
            self.hands, self.board, 0.7)
        print('Expect rate:{:2.2%}, Draw Card:'.format(expect_rate))
        Card.print_pretty_cards(drawCard)

        deal = 52 - len(self.hands) * self.number_players - len(self.board)
        percentage = min(float(len(drawCard)) / float(deal), 1.0)
        ev = self.evalEV(percentage, expect_rate)

        randEv = self.table_pot * random() / 10
        print('Random EV:{}'.format(randEv))

        if "allin" in self.opponent_action:
            if self.hands_strength >= 0.85:
                action = Action.Call
            else:
                action = Action.Fold
        elif self.hands_strength >= 0.9:
            if self.allinTimes < 2:
                action = Action.Raise
                self.allinTimes += 1
            else:
                action = Action.Allin
        elif self.hands_strength >= 0.8 and not self.isBetTooMuch(self.hands_strength):
            action = Action.Bet
            amount = self.my_chips / 5
        elif self.hands_strength >= 0.7 and not self.isBetTooMuch(self.hands_strength):
            action = Action.Raise
        elif self.hands_strength >= 0.5 and not self.isBetTooMuch(self.hands_strength, 0.3):
            action = Action.Call
        elif self.hands_strength - self.boardStrength > 0.2:
            if not self.isBetTooMuch(self.hands_strength, 0.4):
                action = Action.Raise
            else:
                action = Action.Call
        elif ev > self.min_bet:
            action = Action.Call
        elif expect_rate > 0.78 and (ev + randEv) >= 0:
            action = Action.Check
        else:
            action = Action.Fold

        return (action, amount)

    def withRiver(self, data):
        amount = 0
        action = Action.Check

        self.updateHandsStrength(self.hands, self.board)

        isBoardStrong = self.isBoardCardTooStrong(2, 0.6, 0.1, 3000)
        if isBoardStrong:
            return (Action.Fold, 0)

        if "allin" in self.opponent_action:
            if self.hands_strength >= 0.85:
                action = Action.Call
            else:
                action = Action.Fold
            return (action, 0)
        elif (self.hands_strength - self.boardStrength) > 0.30:
            return (Action.Call, 0)

        return super(CardCountingBot, self).evalStregth()

    def evalEV(self, probability, win_rate):
        num_playing = self.number_players - self.folded_players
        adjust_prob = win_rate * \
            pow(probability, self.weightDict[str(num_playing)])
        # adjust_prob = pow(probability, self.weightDict[str(num_playing)])
        ev = adjust_prob * (self.table_pot) - \
            (1 - adjust_prob) * (self.min_bet)

        print("Player:{}, Probability:{:2.2%}, adjusted:{:2.2%}".format(
            num_playing, probability, adjust_prob))
        print("Pot:{}, min bet:{}, my bet:{}, ev:{}".format(
            self.table_pot, self.min_bet, self.my_bet_chips, ev))
        return ev

    def updateHandsStrength(self, hole, boards):
        print("Hand card:")
        Card.print_pretty_cards(self.hands)
        print("Board card:")
        Card.print_pretty_cards(self.board)
        self.hands_strength = self.handEvaluator.evaluate(
            self.hands, self.board)

    def isBoardCardTooStrong(self, num_card, alpha, beta, num_sim):
        self.boardStrength = self.holeEvaluator.evaluate(
            self.board, num_card, num_sim)
        diff = self.boardStrength - self.hands_strength
        print('The difference: {:2.2%}'.format(diff))
        # print('hand str:{}, borad str:{}'.format(self.hands_strength, self.boardStrength))
        if diff > 0.3:
            return True
        elif self.boardStrength > alpha and abs(diff) < beta:
            return True
        else:
            return False

    def isBetTooMuch(self, win_rate, default_ratio=1):
        ratio_bet = (self.my_bet_chips + self.min_bet) / float(self.my_chips)

        if win_rate > 0:
            max_ratio = min(round(0.368 * math.exp(win_rate) +
                                  0.368 * (win_rate - 1), 3), default_ratio)
            print('[{:2.2%}] bet ratio:{:2.2%}, max ratio:{:2.2%}'.format(
                win_rate, ratio_bet, max_ratio))
            return (ratio_bet > max_ratio)
        else:
            return (self.my_bet_chips + self.min_bet) > (self.my_chips * default_ratio)


if __name__ == '__main__':
    bot = CardCountingBot()
    bot.hands_strength = 1
    bot.my_chips = 1000
    bot.isBetTooMuch(1)
    bot.isBetTooMuch(0.7)
    bot.isBetTooMuch(0.5)
    bot.isBetTooMuch(0.2)
    bot.isBetTooMuch(0.14)
    bot.isBetTooMuch(0)

    hole = [getCard('9d'), getCard('Ac')]
    boards = [getCard('8d'), getCard('5s'), getCard('4c')]
    (drawCard, expect_rate) = bot.cardCounting.evaluate(hole, boards, 0.75)
    print('Expect rate:{:2.2%}, Draw Card:'.format(expect_rate))
    Card.print_pretty_cards(drawCard)
    deal = 52 - len(hole) * 10 - len(boards)
    percentage = min(float(len(drawCard)) / float(deal), 1.0)
    print('{}, {}, {}'.format(deal, len(drawCard), percentage))
