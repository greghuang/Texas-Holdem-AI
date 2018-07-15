from pokereval.card import Card
from card import getCard
from action import Action
import sys, traceback


class PokerBot(object):
	def initRound(self, data):
		err_msg = self.__build_err_msg("init round")
		raise NotImplementedError(err_msg)

	def initAction(self, data):
		err_msg = self.__build_err_msg("init action")
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
	total_round = 0
	raise_count = 0
	bet_count = 0
	my_chips = 0
	number_players = 0
	min_bet = 0
	my_call_bet = 0
	my_raise_bet = 0
	table_bet = 0
	total_bet = 0
	board = []
	hands = []
	round_name = None
	player_name = None
	player_hashed_name = None

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
		self.board = []
		self.hands = []
		self.player_hashed_name = None
		self.total_round = data['table']['roundCount']
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
		self.round_name = data['game']['roundName']
		
		if self.player_hashed_name == None:
			self.player_hashed_name = data['self']['playerName']
			print("my name:"+self.player_hashed_name)
		
		self.my_chips = data['self']['chips']
		
		print("Round: {}".format(self.round_name))
		print("Chips:{}".format(self.my_chips))

		if self.round_name == "Deal":
			hands = data['self']['cards']
			for card in hands:
				self.hands.append(getCard(card))
			print("Hands:{}".format(self.hands))

		if self.round_name == "Flop":
			boards = data['game']['board']
			for card in (boards):
				self.board.append(getCard(card))
			print("Board:{}".format(self.board))

		self.min_bet = data['self']['minBet']

	def endGame(self, data):
		pass

	def endRound(self, data):
		try:
			players = data['players']
			for player in (players):
				name = player['playerName']
				isAlive = player['isSurvive']
				if isAlive:
					message = player['hand']['message']
					if player['winMoney'] > 0:
						print('{}'.format(name) + ' has {}'.format(message) + ' to win {}'.format(player['winMoney']))
					else:
						print('{}'.format(name) + ' has {}'.format(message))
				else:
					print("{}".format(name) + " out")
		except Exception:
			traceback.print_exc()
			print(data)

	def declareAction(self, data, isBet=False):
		self.initAction(data)
		action = Action.Allin
		amount = self.min_bet
		return action, amount