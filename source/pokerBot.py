# from pokereval.card import Card
# from pokereval.hand_evaluator import HandEvaluator
from treys import Card
from treys import Evaluator
from poker import Action
from poker import Stage
from poker import GetStage
import sys, traceback

def getCard(card):
	return Card.new(card[0] + card[1].lower())

def showCard(cards):
	Card.print_pretty_cards(cards)
# 2018.07.17
# Total games:40 total chips:130178 avg.chips:3254.0625
# Total rounds:415, win rounds:100, win rate:0.240964
class PokerBot(object):
	def initRound(self, data):
		err_msg = self.__build_err_msg("init round")
		raise NotImplementedError(err_msg)

	def declareAction(self, data, isBet=False):
		err_msg = self.__build_err_msg("declare action")
		raise NotImplementedError(err_msg)

	def endRound(self, data):
		err_msg = self.__build_err_msg("round over")
		raise NotImplementedError(err_msg)

	def endGame(self, data):
		err_msg = self.__build_err_msg("game over")
		raise NotImplementedError(err_msg)

class DummyPokerBot(PokerBot):
	total_games = 0
	total_chips = 0
	total_round = 0
	win_round = 0
	raise_count = 0
	bet_count = 0
	my_chips = 0
	number_players = 0
	min_bet = 0
	my_call_bet = 0
	my_raise_bet = 0
	table_bet = 0
	total_bet = 0
	percentage = 0.0
	board = []
	hands = []
	stage = None
	round_name = None
	player_name = None
	player_hashed_name = None
	evaluator = Evaluator()

	def initRound(self, data):
		print("\ninitialize round...\n")
		# print(data)
		self.raise_count = 0
		self.bet_count = 0
		self.my_chips = 0
		self.player_name = None
		self.number_players = 0
		self.my_call_bet = 0
		self.my_raise_bet = 0
		self.min_bet = 0
		self.table_bet = 0
		self.total_bet = 0
		self.percentage = 0.0
		self.board = []
		self.hands = []
		self.stage = None
		self.player_hashed_name = None
		self.round_name = data['table']['roundName']
		players = data['players']
		self.number_players = len(players)
		for player in (players):
			print("Player:{}".format(player['playerName']))
			print("Is Human:{}".format(player['isHuman']))
			print("Is Online:{}".format(player['isOnline']))
			print("Chips:{}".format(player['chips']))
			print("\n")
		print("Big blind:{}".format(data['table']['bigBlind']['amount']))
		print("Small blind:{}".format(data['table']['smallBlind']['amount']))

	def initAction(self, data):
		round_name = data['game']['roundName']
		
		if self.player_hashed_name == None:
			self.player_hashed_name = data['self']['playerName']
			print("My name:"+self.player_hashed_name)
		
		self.my_chips = data['self']['chips']
		self.updateStage(round_name, data)

		self.min_bet = data['self']['minBet']

	def updateStage(self, stage_name, data):
		stage = GetStage(stage_name)
		if stage != self.stage:
			self.stage = stage
			# print('[{}]'.format(self.stage))
			if stage == Stage.PreFlop:
				hands = data['self']['cards']
				for card in hands:
					self.hands.append(getCard(card))
			elif stage != Stage.HandOver:
				self.board = []
				boards = data['game']['board']
				for card in (boards):
					self.board.append(getCard(card))

	def endGame(self, data):
		try:
			self.total_games += 1
			players = data['players']
			for player in (players):
				name = player['playerName']				
				if name == self.player_hashed_name:					
					self.total_chips += player['chips']

				print('Total games:{}'.format(self.total_games) + ' total chips:{}'.format(self.total_chips) + ' avg.chips:{}'.format(self.total_chips/self.total_games))
				print("Total rounds:%d, win rounds:%d, win rate:%f" %(self.total_round, self.win_round, float(self.win_round)/float(self.total_round)))
		except Exception:
			traceback.print_exc()
			print(data)

	def endRound(self, data):
		try:
			self.total_round += 1
			players = data['players']
			for player in (players):
				name = player['playerName']
				isAlive = player['isSurvive']
				if isAlive:
					message = player['hand']['message']
					if player['winMoney'] > 0:
						print('{}'.format(name) + ' has {}'.format(message) + ' to win {}'.format(player['winMoney']))
						if name == self.player_hashed_name:
							self.win_round += 1
					else:
						print('{}'.format(name) + ' has {}'.format(message))
				else:
					print("{}".format(name) + " out")
		except Exception:
			traceback.print_exc()
			print(data)

	def declareAction(self, data, isBet=False):
		self.initAction(data)
		# print("Round: {}".format(round_name))
		print("My chips:{}".format(self.my_chips))

		pre_percent = self.percentage
		if self.stage != Stage.PreFlop and self.stage != Stage.HandOver:
			self.percentage = self.evaluate()

		amount = 0
		action = Action.Check
		isBetter = (self.percentage > pre_percent)

		if self.percentage >= 0.8 and isBetter:
			action = Action.Allin
		elif self.percentage >= 0.6 and self.percentage < 0.8:
			action = Action.Bet
			amount = max(self.min_bet, self.my_chips/2)
		elif self.percentage >= 0.5 and self.percentage < 0.6:
			if self.min_bet < self.my_chips / 10:
				action = Action.Raise
			else:
				action = Action.Call
		elif self.percentage >= 0.18 and self.percentage < 0.5:
			if self.min_bet < self.my_chips / 10:
				action = Action.Call
			else:
				action = Action.Fold
		else:
			if self.stage == Stage.PreFlop:
				print('Card 1:{}'.format(self.hands[0])+' Card 2:{}'.format(self.hands[1]))
				action = Action.Call
			else:
				action = Action.Fold

		return action, amount

	def evaluate(self):
		print("Hand card:")
		showCard(self.hands)
		print("Board card:")
		showCard(self.board)
		rank = self.evaluator.evaluate(self.board, self.hands)
		percentage = 1.0 - self.evaluator.get_five_card_rank_percentage(rank)
		p_class = self.evaluator.get_rank_class(rank)
		print("My hand rank = %f (%s)" % (percentage, self.evaluator.class_to_string(p_class)))
		return percentage