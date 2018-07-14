from pokereval.card import Card
import websockets
import json
import asyncio

"""Create a card. Rank is 2-14, representing 2-A,
   while suit is 1-4 representing spades, hearts, diamonds, clubs"""
def getCard(card):
	cardnume_code = card[0]
	card_type = card[1]
	
	card_num = 0
	card_num_type = 0
	
	if card_type == 'S':
		card_num_type = 1
	elif card_type == 'H':
		card_num_type = 2
	elif card_type == 'D':
		card_num_type = 3
	elif card_type == "C":
		card_num_type = 4
	else:
		raise NameError(card_type + " is not defined")
	
	if cardnume_code == 'T':
		card_num = 10
	elif cardnume_code == 'J':
		card_num = 11
	elif cardnume_code == 'Q':
		card_num = 12
	elif cardnume_code == 'K':
		card_num = 13
	elif cardnume_code == 'A':
		card_num = 14
	else:
		card_num = int(cardnume_code)
	return Card(card_num, card_num_type)

class PokerBot(object):
	def declareAction(self,hole, board, round, my_Raise_Bet, my_Call_Bet,Table_Bet,number_players,raise_count,bet_count,my_Chips,total_bet):
		err_msg = self.__build_err_msg("declare_action")
		raise NotImplementedError(err_msg)
	def game_over(self,isWin,winChips,data):
		err_msg = self.__build_err_msg("game_over")
		raise NotImplementedError(err_msg)

class PokerSocket(object):
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

	def __init__(self, player_name, connect_url, pokerbot):
		self.pokerbot = pokerbot
		self.player_name = player_name
		self.connect_url = connect_url

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
		print("chips:{}".format(self.my_chips))
		
		print("round: {}".format(self.round_name))
		if self.round_name == "Deal":
			hands = data['self']['cards']
			for card in hands:
				self.hands.append(getCard(card))
			print("hands:{}".format(self.hands))

		if self.round_name == "Flop":
			boards = data['game']['board']
			for card in (boards):
				self.board.append(getCard(card))
			print("Board:{}".format(self.board))

		self.min_bet = data['self']['minBet']

	def showAction(self, data):
		round = data['table']['roundName']
		player = data['action']['playerName']
		action = data['action']['action']
		amount = 0
		if action == "bet" or action == "allin":
			amount = data['action']['amount'] 
		print("Round:{}".format(round))
		print("Player:{}".format(player) + " {}".format(action) + " {}".format(amount))
		
	def getAction(self, data):
		# round = data['game']['roundName']
		# players = data['game']['players']
		# chips = data['self']['chips']
		# hands = data['self']['cards']
		# self.raise_count = data['game']['raiseCount']
		# self.bet_count = data['game']['betCount']
		# self.my_chips = chips
		
		#print("minbet:{}".format(data['self']['minBet']))		
		# self.number_players = len(players)
		# self.my_call_bet = data['self']['minBet']
		# self.my_raise_bet = int(chips / 4)
		
		# self.hole = []
		# for card in (hands):
		# 	self.hole.append(getCard(card))
		#print 'my_call_bet:{}'.format(self.my_call_bet)
		#print 'my_raise_bet:{}'.format(self.my_raise_bet)
		#print 'board:{}'.format(self.board)
		#print 'total_bet:{}'.format(self.Table_Bet)
		#print 'hands:{}'.format(self.hole)
		action, amount = self.pokerbot.declareAction(self.hands, self.board, round, self.my_raise_bet, self.my_call_bet, self.table_bet, self.number_players, self.raise_count, self.bet_count, self.my_chips,self.total_bet, self.min_bet)
		self.total_bet += amount
		return action, amount

	async def takeAction(self, ws, event, data):
		# Get number of players and table info
		if event == "__new_round":
			self.initRound(data)
		elif event == "__action":
			self.initAction(data)
			action, amount = self.getAction(data)
			print("action: {}".format(action))
			print("action amount: {}".format(amount))
			await ws.send(json.dumps({
                "eventName": "__action",
                "data": {
                    "action": action,
                    "playerName": self.player_name,
                    "amount": amount
                }}))
		elif event =='__deal':
			# when each betting round end up, server will send this event
			print("Total bet:{}".format(data['table']['totalBet']))
		elif event == "__show_action":
			self.showAction(data)
		elif event == "__bet":
			self.initAction(data)
			action, amount = self.getAction(data)
			print("action: {}".format(action))
			print("action amount: {}".format(amount))
			await ws.send(json.dumps({
                "eventName": "__action",
                "data": {
                    "action": action,
                    "playerName": self.player_name,
                    "amount": amount
                }}))
		elif event == "__round_end":
			print("Round End")
			self.total_bet = 0
			players = data['players']
			isWin = False
			winChips = 0
			for player in players:
				winMoney = player['winMoney']
				playerid = player['playerName']
				if (self.player_hashed_name == playerid):
					if (winMoney == 0):
						isWin = False
					else:
						isWin = True
					winChips = winMoney
					print("winPlayer:{}".format(isWin))
					print("winChips:{}".format(winChips))
					self.pokerbot.game_over(isWin,winChips,data)
		elif event == "__game_over":
			print("rejoin game")
			ws.send(json.dumps({
				"eventName": "__join",
				"data": {
					"playerName": self.player_name
				}
			}))

	async def doListen(self):
		print("\ntry to connect "+self.connect_url + " with player=" + self.player_name+"\n")

		async with websockets.connect(self.connect_url) as ws:
			await ws.send(json.dumps({
				"eventName": "__join",
				"data": {
					"playerName": self.player_name
				}
			}))

			async for message in ws:
				msg = json.loads(message)
				event_name = msg["eventName"]
				data = msg["data"]
				print("\n" + event_name)
				await self.takeAction(ws, event_name, data)

class FreshPokerBot(PokerBot):
	def game_over(self, isWin, winChips, data):
		pass

	def declareAction(self, hands, boards, round, my_raise_bet, my_call_bet, table_bet, number_players,raise_count, bet_count, my_chips, total_bet, min_bet):
		action = 'call'
		amount = min_bet
		return action,amount

if __name__ == '__main__':
	playerName = "iamrobot"
	connectURL = "ws://poker-training.vtr.trendnet.org:3001"
	myPokerBot = FreshPokerBot()
	myPokerSocket = PokerSocket(playerName, connectURL, myPokerBot)
	asyncio.get_event_loop().run_until_complete(myPokerSocket.doListen())