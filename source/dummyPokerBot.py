import pokerBot
from treys import Card
from pokerBot import getCard
from poker import GetStage
from poker import Stage
from poker import Action
from pokerStrategy import CardEvaluator

class DummyPokerBot(pokerBot.PokerBot):
	total_games = 0
	total_chips = 0
	total_round = 0
	win_round = 0
	raise_count = 0
	bet_count = 0
	my_chips = 0
	number_players = 0
	folded_players = 0
	min_bet = 0
	my_call_bet = 0
	my_raise_bet = 0
	my_bet_chips = 0
	big_blind = 0
	small_blind = 0
	player_bb = None
	table_pot = 0 # total bet
	hands_strength = 0.0
	board = []
	hands = []
	opponent_action = []
	stage = None
	round_name = None
	player_name = None

	player_hashed_name = None
	winRateStrategy = CardEvaluator()

	def initRound(self, data):
		print("\ninitialize {} round...\n".format(data['table']['roundCount']))
		# print(data)
		self.raise_count = 0
		self.bet_count = 0
		self.my_chips = 0
		self.player_name = None
		self.number_players = 0
		self.folded_players = 0
		self.my_call_bet = 0
		self.my_raise_bet = 0
		self.my_bet_chips = 0
		self.min_bet = 0
		self.table_pot = 0
		self.hands_strength = 0.0
		self.board = []
		self.hands = []
		self.opponent_action = []
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
		self.big_blind = data['table']['bigBlind']['amount']
		self.small_blind = data['table']['smallBlind']['amount']
		self.player_bb = data['table']['bigBlind']['playerName']
		print("Big blind:{} by {}".format(self.big_blind, self.player_bb))
		print("Small blind:{} by {}\n".format(self.small_blind, data['table']['smallBlind']['playerName']))

	def initAction(self, data):
		round_name = data['game']['roundName']
		self.updateStage(round_name, data)
		
		if self.player_hashed_name == None:
			self.player_hashed_name = data['self']['playerName']
			print("My name:"+self.player_hashed_name)
		
		self.my_chips = data['self']['chips']
		self.min_bet = data['self']['minBet']
		print("My chips:{}".format(self.my_chips))

		survive_players = 0
		folded_players = 0
		for player in data['game']['players']:
			if player['isSurvive']:
				survive_players += 1
			if player['isSurvive'] and player['folded']:
				folded_players += 1

		self.folded_players = folded_players
		self.number_players = survive_players

	def showAction(self, data):
		self.table_pot = data['table']['totalBet']
		player = data['action']['playerName']
		action = data['action']['action']
		amount = 0
		if action == "bet" or action == "allin":
			amount = data['action']['amount'] 
		self.opponent_action.append(action)

	def updateStage(self, stage_name, data):
		stage = GetStage(stage_name)
		if stage != self.stage:
			self.stage = stage			
			if stage == Stage.PreFlop:
				hands = data['self']['cards']
				for card in hands:
					self.hands.append(getCard(card))
			elif stage == Stage.Showdown:
				self.board = []
				for card in (data['table']['board']):
					self.board.append(getCard(card))
			elif stage != Stage.HandOver:
				self.board = []
				boards = data['game']['board']
				for card in (boards):
					self.board.append(getCard(card))

	def showCard(self, cards):
		output = " "
		for card in (cards):
			output += Card.int_to_pretty_str(getCard(card)) + ","

		return output

	def endGame(self, data):
		try:
			self.total_games += 1
			players = data['players']
			for player in (players):
				name = player['playerName']				
				if name == self.player_hashed_name:					
					self.total_chips += player['chips']

			output1 = 'Total games:{:3d}, total chips:{:5d},  avg.chips:{:5.2f}\n'.format(self.total_games, self.total_chips, self.total_chips/self.total_games)
			output2 = "Total rounds:{:3d}, win rounds:{:3d}, win rate:{:2.2%}\n".format(self.total_round, self.win_round, float(self.win_round)/float(self.total_round))

			print(output1)
			print(output2)

			# Save result
			with open('../data/{}.log'.format(self.player_hashed_name), 'a') as f:	
				f.write(output1)
				f.write(output2)
			
			print('File saved ok({})'.format(f.closed))
		except Exception:
			traceback.print_exc()
			print(data)

	def endRound(self, data):
		try:
			self.total_round += 1
			round_name = data['table']['roundName']
			self.updateStage(round_name, data)
			Card.print_pretty_cards(self.board)

			players = data['players']
			for player in (players):
				name = player['playerName']
				isAlive = player['isSurvive']
				if isAlive:
					message = player['hand']['message']
					if player['winMoney'] > 0:
						print('{} has {} to win {} ({})'.format(name, message, player['winMoney'], self.showCard(player['hand']['cards'])))
						if name == self.player_hashed_name:
							self.win_round += 1	
					else:
						if name == self.player_hashed_name:
							print('{} has {} ({})'.format(name, message, self.showCard(player['hand']['cards'])))
						else:
							print('{} has {}'.format(name, message))
				else:
					print("{} out".format(name))
		except Exception:
			traceback.print_exc()
			print(data)

	def declareAction(self, data, isBet=False):
		self.initAction(data)
		(action, amount) = self.evalStregth(isBet)
		self.updateBetChips(action, amount)

		return (action, amount)

	def evalStregth(self, isBet = False):
		action = Action.Check
		amount = 0

		pre_percent = self.hands_strength
		if self.stage != Stage.PreFlop and self.stage != Stage.HandOver:
			print("Hand card:")
			Card.print_pretty_cards(self.hands)
			print("Board card:")
			Card.print_pretty_cards(self.board)
			self.hands_strength = self.winRateStrategy.evaluate(self.hands, self.board)

		isBetter = (self.hands_strength > pre_percent)

		if self.hands_strength >= 0.9:
			if isBetter:
				action = Action.Allin
			else:
				action = Action.Raise
		elif self.hands_strength >= 0.8 and self.hands_strength < 0.9:
			action = Action.Bet
			amount = max(self.min_bet, self.my_chips/2)
		elif self.hands_strength >= 0.6 and self.hands_strength < 0.8:
			if self.min_bet < (self.my_chips / 3) and isBetter:
				action = Action.Raise
			elif "allin" in self.opponent_action:
				action = Action.Fold
			else:
				action = Action.Call
		elif self.hands_strength >= 0.5 and self.hands_strength < 0.6:
			if self.min_bet < (self.my_chips / 5) and self.my_bet_chips < (self.my_chips / 2):
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.4 and self.hands_strength < 0.5:
			if self.min_bet < (self.my_chips / 10):
				action = Action.Call
			else:
				action = Action.Fold
		elif self.hands_strength >= 0.18 and self.hands_strength < 0.4:
			if not isBet:
				action = Action.Check
			elif self.min_bet < (self.my_chips / 20):
				action = Action.Call
			else:
				action = Action.Fold
		else:
			if self.stage == Stage.PreFlop:
				Card.print_pretty_cards(self.hands)
				if "allin" not in self.opponent_action:
					action = Action.Call
				else:
					action = Action.Fold
			else:
				action = Action.Fold

		return (action, amount)


	def updateBetChips(self, action, amount):
		if action == Action.Call:
			self.my_bet_chips += self.min_bet
		elif action == Action.Raise:
			self.my_bet_chips += (self.min_bet * 2)
		elif action == Action.Bet:
			self.my_bet_chips += amount
		elif action == Action.Allin:
			self.my_bet_chips += self.my_chips
		else:
			pass
