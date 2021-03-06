from poker import Action
from dummyPokerBot import DummyPokerBot
from cardCountingBot import CardCountingBot
import websockets
import json
import asyncio
import sys, traceback
import signal


class PokerSocket(object):
	isRejoin = True

	def __init__(self, player_name, connect_url, pokerbot):
		self.pokerbot = pokerbot
		self.player_name = player_name
		self.connect_url = connect_url

	def showAction(self, data):
		self.pokerbot.showAction(data)
		
		round = data['table']['roundName']
		player = data['action']['playerName']
		action = data['action']['action']
		amount = 0
		if action == "bet" or action == "allin":
			amount = data['action']['amount'] 
		print("[{}]".format(round))
		print("Player:{}".format(player) + " {}".format(action) + " {}\n".format(amount))

	async def evtHandler(self, ws, event, data):
		if event == "__new_round":
			self.pokerbot.initRound(data)
		elif event == "__action" or event == "__bet":
			action, amount = self.pokerbot.declareAction(data, (event == "__bet"))
			print("action: {}".format(action))
			print("amount: {}".format(amount))
			print("Current my bet:{}\n".format(self.pokerbot.my_bet_chips))
			await ws.send(json.dumps({
				"eventName": "__action",
				"data": {
					"action": action.value,
					"playerName": self.player_name,
					"amount": amount
				}}))	
		# when each betting round end up, server will send this event
		elif event =='__deal':
			self.pokerbot.table_pot = data['table']['totalBet']
			print("Total round bet:{}\n".format(self.pokerbot.table_pot))
		elif event == "__show_action":
			self.showAction(data)
		elif event == "__round_end":
			print("[Round end]")
			self.pokerbot.endRound(data)
		elif event == "__game_over":
			print("[Game over]")
			self.pokerbot.endGame(data)
			if self.isRejoin:
				print("===== Rejoin game =====")
				await self.joinGame(ws)
			else:
				await self.cancelTask()

	async def cancelTask(self):
		for task in asyncio.Task.all_tasks():
			task.cancel()

	async def joinGame(self, ws):
		await ws.send(json.dumps({
			"eventName": "__join",
			"data": {
				"playerName": self.player_name
			}
		}))

	async def doListen(self):
		print("\ntry to connect "+self.connect_url + " with player=" + self.player_name+"\n")

		async with websockets.connect(self.connect_url) as ws:
			try:
				await self.joinGame(ws)

				async for message in ws:
					msg = json.loads(message)
					event_name = msg["eventName"]
					data = msg["data"]
					await self.evtHandler(ws, event_name, data)
			except asyncio.CancelledError:
				print("disconnect websocket")
				# await self.cancelTask()
			except asyncio.TimeoutError:
				print('server timeout')
				try:
					pong_waiter = await ws.ping()
					await asyncio.wait_for(pong_waiter, timeout=5)
				except asyncio.TimeoutError:
					# No response to ping in 5 seconds, disconnect.
					ws.close()

		print("Stop loop")
		asyncio.get_event_loop().stop()


def ask_exit():
	for task in asyncio.Task.all_tasks():
		task.cancel()

if __name__ == '__main__':
	playerName = "54a311a2c59c4bdb8b0d3ee2203eb002"
	connectURL = "ws://poker-battle.vtr.trendnet.org:3001"
	# playerName = "iamrobot"
	# connectURL = "ws://poker-training.vtr.trendnet.org:3001"
	dummyBot = DummyPokerBot()
	countingBot = CardCountingBot()
	myPokerBot = countingBot

	myPokerSocket = PokerSocket(playerName, connectURL, myPokerBot)

	loop = asyncio.get_event_loop()
	try:
		for sig in (signal.SIGINT, signal.SIGTERM):
			loop.add_signal_handler(sig, ask_exit)

		# asyncio.ensure_future(myPokerSocket.doListen())
		loop.run_until_complete(myPokerSocket.doListen())
		loop.run_forever()
	except websockets.exceptions.ConnectionClosed:
		print("Connection close")
		loop.stop()
	except Exception:
		traceback.print_exc()
		loop.stop()
	finally:
		# loop.run_until_complete(loop.shutdown_asyncgens())
		# I had to manually remove the handlers to
		# avoid an exception on BaseEventLoop.__del__
		for sig in (signal.SIGINT, signal.SIGTERM):
			loop.remove_signal_handler(sig)

		loop.close()
		print("The program end up")