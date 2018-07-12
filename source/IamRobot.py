from pokereval.card import Card
import websockets
import json


def getCard(Card):
	card_type = card[1]
	cardnume_code = card[0]
	card_num = 0
	card_num_type = 0
	
	if card_type == 'H':
		card_num_type = 1
	elif card_type == 'S':
		card_num_type = 2
	elif card_type == 'D':
		card_num_type = 3
	else:
		card_num_type = 4

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
		return Card(card_num,card_num_type)

class PokerBot(object):
	def declareAction(self,hole, board, round, my_Raise_Bet, my_Call_Bet,Table_Bet,number_players,raise_count,bet_count,my_Chips,total_bet):
		err_msg = self.__build_err_msg("declare_action")
		raise NotImplementedError(err_msg)
	def game_over(self,isWin,winChips,data):
		err_msg = self.__build_err_msg("game_over")
		raise NotImplementedError(err_msg)

class PokerSocket(object):
	ws = ""
	raise_count=0
	bet_count=0
	my_chips=0
	player_name=None
	number_players = 0
	my_call_bet = 0
	my_raise_bet = 0

	def __init__(self,playerName,connect_url, pokerbot):
		self.pokerbot = pokerbot
		self.playerName = playerName
		self.connect_url = connect_url

	def getAction(self,data):
		round = data['game']['roundName']
		players = data['game']['players']
		chips = data['self']['chips']
		hands = data['self']['cards']

		self.raise_count = data['game']['raiseCount']
		self.bet_count = data['game']['betCount']
		self.my_chips=chips
		self.playerGameName=data['self']['playerName']
		self.number_players = len(players)
		self.my_call_bet = data['self']['minBet']
		self.my_raise_bet = int(chips / 4)
		
		self.hole = []
		for card in (hands):
			self.hole.append(getCard(card))

		#print 'my_call_bet:{}'.format(self.my_call_bet)
		#print 'my_raise_bet:{}'.format(self.my_raise_bet)
		#print 'board:{}'.format(self.board)
		#print 'total_bet:{}'.format(self.Table_Bet)
		#print 'hands:{}'.format(self.hole)

		if self.board == []:
			round = 'preflop'

		print("round:{}".format(round))

		action, amount= self.pokerbot.declareAction(self.hole, self.board, round, self.my_Raise_Bet,self.my_Call_Bet, self.Table_Bet, self.number_players,self.raise_count,self.bet_count,self.my_Chips,self.total_bet)
		self.total_bet += amount
		return action, amount

	def takeAction(self,action, data):
		# Get number of players and table info
		if action == "__show_action" or action=='__deal' :
			print("show action or deal")
		elif action == "__bet":
			action,amount=self.getAction(data)
			print("action: {}".format(action))
			print("action amount: {}".format(amount))
			self.ws.send(json.dumps({
				"eventName": "__action",
				"data": {
					"action": action,
					"playerName": self.playerName,
					"amount": amount
				}}))
		elif action == "__action":
			action,amount=self.getAction(data)
			print("action: {}".format(action))
			print("action amount: {}".format(amount))
		elif action == "__round_end":
			print("Game Over")
			self.total_bet=0
			players=data['players']
			isWin=False
			winChips=0
			for player in players:
				winMoney=player['winMoney']
				playerid=player['playerName']
				if (self.playerGameName == playerid):
					if (winMoney==0):
						isWin = False
					else:
						isWin = True
					winChips=winMoney
					print("winPlayer:{}".format(isWin))
					print("winChips:{}".format(winChips))
					self.pokerbot.game_over(isWin,winChips,data)

	def doListen(self):
		try:
			self.ws = websockets.connect(self.connect_url)
			self.ws.send(json.dumps({
				"eventName": "__join",
				"data": {
					"playerName": self.playerName
				}
			}))
			while 1:
				result = self.ws.recv()
				msg = json.loads(result)
				event_name = msg["eventName"]
				data = msg["data"]
				print(event_name)
				print(data)
				self.takeAction(event_name, data)
		except Exception as e:
			print(e.message)
			self.doListen()

class FreshPokerBot(PokerBot):
	def game_over(self, isWin,winChips,data):
		pass

	def declareAction(self,holes, boards, round, my_Raise_Bet, my_Call_Bet, Table_Bet,number_players,raise_count,bet_count,my_Chips,total_bet):
		action = 'fold'
		amount = 0
		return action,amount

if __name__ == '__main__':
	playerName="iamrobot"
	connect_url="ws://poker-training.vtr.trendnet.org:3001"
	myPokerBot=FreshPokerBot()
	myPokerSocket=PokerSocket(playerName,connect_url,myPokerBot)
	myPokerSocket.doListen()