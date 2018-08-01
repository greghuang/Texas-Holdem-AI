from dummyPokerBot import DummyPokerBot
from pokerStrategy import CardCounting
from pokerStrategy import CardEvaluator
from pokerStrategy import HoleEvaluator
from switch import switch
from poker import Stage
from poker import Action
from treys import Card

class CardCountingBot(DummyPokerBot):
	cardCounting = CardCounting()
	handEvaluator = CardEvaluator()
	holeEvaluator = HoleEvaluator()
	weightDict = {'1':1, '2':1, '3':2, '4':2, '5':3, '6':3, '7':3, '8':4, '9':4, '10':5 }
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
		hole_winrate = self.holeEvaluator.evaluate(self.hands, 3, 100)
		# print('Hole win rate:{}'.format(hole_winrate))
		
		if hole_winrate > 0.5:
			action = Action.Bet
			amount = self.my_chips / 5
		elif "allin" in self.opponent_action:
			if not self.isBetTooMuch(4) and hole_winrate > 0.2:
				action = Action.Call
			else:
				action = Action.Fold
		elif hole_winrate > 0.31:
			action = Action.Raise
		elif self.player_bb == self.player_hashed_name:
			action = Action.Check
		elif not self.isBetTooMuch(5):
			action = Action.Call
		else:
			action = Action.Fold

		return (action, amount)

	def withFlop(self, data):
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)

		(drawCard, expect_rate) = self.cardCounting.evaluate(self.hands, self.board, 0.65)		
		print('Expect rate:{:2.2%}, Draw Card:'.format(expect_rate))
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)
		percentage = min(float(len(drawCard)) / float(deal), 1.0)
		ev = self.evalEV(percentage, expect_rate)
		
		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.9:
				action = Action.Call
			elif self.hands_strength >= 0.8 and self.min_bet <= (self.my_chips / 2):
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.8:
			action = Action.Bet
			amount = self.my_chips / 5
		elif self.hands_strength >= 0.55:
			action = Action.Raise
		elif self.hands_strength >= 0.4 and ev > self.min_bet / 2:
			action = Action.Call
		elif (ev*3) > (self.min_bet*2):
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
		
		isBoardStrong = self.isBoardCardTooStrong(self.hands_strength, 2, 0.4, 0.1, 3000)
		if isBoardStrong:			
			return (Action.Fold, 0)

		(drawCard, expect_rate) = self.cardCounting.evaluate(self.hands, self.board, 0.6)
		print('Expect rate:{:2.2%}, Draw Card:'.format(expect_rate))
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)		
		percentage = min(float(len(drawCard)) / float(deal), 1.0)
		ev = self.evalEV(percentage, expect_rate)

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
		elif self.hands_strength >= 0.8 and not self.isBetTooMuch(2):
			action = Action.Bet
			amount = self.my_chips / 5
		elif self.hands_strength >= 0.7 and not self.isBetTooMuch(2):
			action = Action.Raise
		elif self.hands_strength >= 0.5 and not self.isBetTooMuch(3):
			action = Action.Call
		elif self.hands_strength - self.boardStrength > 0.2:
			action = Action.Call
		elif ev > self.min_bet:
			action = Action.Call
		elif expect_rate > 0.8 and  ev >= 0:
			action = Action.Check
		else:
			action = Action.Fold

		return (action, amount)

	def withRiver(self, data):
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)
		
		isBoardStrong = self.isBoardCardTooStrong(self.hands_strength, 2, 0.5, 0.1, 2000)
		if isBoardStrong:			
			return (Action.Fold, 0)

		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.85:
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength - self.boardStrength > 0.30:
			return (Action.Call, 0)

		return super(CardCountingBot, self).evalStregth()
		

	def evalEV(self, probability, win_rate):
		adjust_prob = probability * win_rate
		num_playing = self.number_players - self.folded_players
		# adjust_prob = pow(probability, self.weightDict[str(num_playing)])
		ev = adjust_prob * (self.table_pot) - (1 - adjust_prob) * (self.min_bet)

		print("Player: {}, Probability:{:2.2%}, adjusted:{:2.2%}".format(num_playing, probability, adjust_prob))
		print("Pot: {}, min bet:{}, my bet:{}, ev:{}".format(self.table_pot, self.min_bet, self.my_bet_chips, ev))
		return ev

	def updateHandsStrength(self, hole, boards):
		print("Hand card:")
		Card.print_pretty_cards(self.hands)
		print("Board card:")
		Card.print_pretty_cards(self.board)
		self.hands_strength = self.handEvaluator.evaluate(self.hands, self.board)

	def isBoardCardTooStrong(self, hands_str, num_card, alpha, beta, num_sim):
		self.boardStrength = self.holeEvaluator.evaluate(self.board, num_card, num_sim)
		diff = abs(self.boardStrength - hands_str)
		print('The difference: {:2.2%}'.format(diff))
		# print('hand str:{}, borad str:{}'.format(self.hands_strength, self.boardStrength))
		if hands_str > alpha and diff < beta:			
			return True
		else:
			return False

	def isBetTooMuch(self, min_ratio):
		ratio_bet = (self.my_bet_chips + self.min_bet) / float(self.my_chips)
		if self.hands_strength > 0:
			max_ratio = 1.8 * self.hands_strength - 0.8
			print('bet ratio:{:2.2%}, max ratio:{:2.2%}'.format(ratio_bet, max_ratio))
			return (ratio_bet > max_ratio)
		else:
			return self.min_bet > self.my_chips / float(min_ratio)
