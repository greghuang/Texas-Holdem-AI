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

	def declareAction(self, data, isBet=False):
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

		return (action, amount)
		# return super(CardCountingBot, self).declareAction(data, isBet)

	def withPreFlop(self, data):
		self.initAction(data)
		amount = 0
		action = Action.Check

		Card.print_pretty_cards(self.hands)
		if "allin" not in self.opponent_action:
			action = Action.Call
		else:
			action = Action.Fold

		return (action, amount)

	def withFlop(self, data):
		self.initAction(data)
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)

		drawCard = self.cardCounting.evaluate(self.hands, self.board, 0.7)
		print('Draw Card:')
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)
		percentage = float(len(drawCard)) / float(deal)
		ev = self.evalEV(percentage)
		
		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.85:
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.8 and ev > 0:
			action = Action.Raise
		elif self.hands_strength >= 0.5 and ev > 0:
			action = Action.Call
		elif ev > 0 and (self.number_players - self.folded_players) <= 3:
			action = Action.Call
		else:
			action = Action.Fold

		return (action, amount)


	def withTurn(self, data):
		self.initAction(data)
		amount = 0
		action = Action.Check

		self.updateHandsStrength(self.hands, self.board)
		
		drawCard = self.cardCounting.evaluate(self.hands, self.board, 0.7)
		print('Draw Card:')
		Card.print_pretty_cards(drawCard)

		deal = 52 - len(self.hands) * self.number_players - len(self.board)		
		percentage = float(len(drawCard)) / float(deal)
		ev = self.evalEV(percentage)

		if "allin" in self.opponent_action:
			if self.hands_strength >= 0.9 and ev > 0:
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.8 and ev > 0:
			action = Action.Raise
		elif self.hands_strength >= 0.5 and ev > 0:
			action = Action.Call
		elif ev > 0:
			action = Action.Check
		else:
			action = Action.Fold

		return (action, amount)

	def withRiver(self, data):
		return super(CardCountingBot, self).declareAction(data)

	def evalEV(self, percentage):
		num_playing = self.number_players - self.folded_players
		percentage = pow(percentage, int(num_playing/2))
		
		print("Playing #:{}".format(num_playing))
		print("Percentage:{:2.2%}".format(percentage))
		print("Pot:{}, min bet:{}".format(self.table_pot, self.min_bet))

		ev = percentage * (self.table_pot + self.min_bet) - (1 - percentage) * self.min_bet
		print('EV:{}'.format(ev))

	def updateHandsStrength(self, hole, boards):
		print("Hand card:")
		Card.print_pretty_cards(self.hands)
		print("Board card:")
		Card.print_pretty_cards(self.board)
		self.hands_strength = handEvaluator.evaluate(self.hands, self.board)


