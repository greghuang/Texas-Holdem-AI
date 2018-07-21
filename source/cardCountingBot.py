from dummyPokerBot import DummyPokerBot
from pokerStrategy import CardCounting
from pokerStrategy import WinRateStrategy
from switch import switch
from poker import Stage
from poker import Action
from treys import Card

class CardCountingBot(DummyPokerBot):
	cardCounting = CardCounting()
	handEvaluator = WinRateStrategy()
	weightDict = {'1':1, '2':1, '3':1, '4':2, '5':3, '6':3, '7':3, '8':4, '9':4, '10':5 }

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

		Card.print_pretty_cards(self.hands)
		if "allin" in self.opponent_action:
			if self.min_bet < (self.my_chips / 10):
				action = Action.Call
			else:
				action = Action.Fold
		else:
			action = Action.Call

		return (action, amount)

	def withFlop(self, data):
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)

		drawCard = self.cardCounting.evaluate(self.hands, self.board, 0.75)
		print('Draw Card:')
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)
		percentage = float(len(drawCard)) / float(deal)
		ev = self.evalEV(percentage)
		
		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.9:
				action = Action.Call
			elif self.hands_strength >= 0.8 and self.min_bet <= (self.my_chips / 2):
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.8:
			action = Action.Raise
		elif self.hands_strength >= 0.5 and ev > 0:
			action = Action.Call
		elif ev > 60:
			action = Action.Call
		else:
			action = Action.Fold

		return (action, amount)


	def withTurn(self, data):
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)

		drawCard = self.cardCounting.evaluate(self.hands, self.board, 0.7)
		print('Draw Card:')
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)		
		percentage = min(float(len(drawCard)) / float(deal), 1.0)
		ev = self.evalEV(percentage)

		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.85:
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.9:
			action = Action.Allin
		elif self.hands_strength >= 0.8:
			action = Action.Raise
		elif self.hands_strength >= 0.7:
			action = Action.Call
		elif self.hands_strength >= 0.5 and ev > 0:
			action = Action.Call
		elif ev > 0:
			action = Action.Check
		else:
			action = Action.Fold

		return (action, amount)

	def withRiver(self, data):
		return super(CardCountingBot, self).evalStregth()

	def evalEV(self, probability):
		adjust_prob = probability
		num_playing = self.number_players - self.folded_players
		adjust_prob = pow(probability, self.weightDict[str(num_playing)])
		
		print("Playing #:{}".format(num_playing))
		print("Probability:{:2.2%}, adjusted:{:2.2%}".format(probability, adjust_prob))
		print("Pot:{}, min bet:{}, my bet:{}".format(self.table_pot, self.min_bet, self.my_bet_chips))

		ev = adjust_prob * (self.table_pot) - (1 - adjust_prob) * (self.min_bet)
		print('EV:{}'.format(ev))
		return ev

	def updateHandsStrength(self, hole, boards):
		print("Hand card:")
		Card.print_pretty_cards(self.hands)
		print("Board card:")
		Card.print_pretty_cards(self.board)
		self.hands_strength = self.handEvaluator.evaluate(self.hands, self.board)


