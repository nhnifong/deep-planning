from __future__ import division
from copy import copy, deepcopy
from pprint import pprint
from random import randint
import sys
import go

sys.setrecursionlimit(19*19+10)

class Player:
	def __init__(self):
		pass
	
	def decideMove(gs):
		"""Given a gamestate, return a move
		A move is a tuple, (col,row)
		The gamestate will be presented from black's perspective, you are black
		pass is None
		if you return an illegal move you forfeit.
		"""
		return None
		
class RandomPlayer(Player):
	def decideMove(self, gs):
		# try 5 times to choose a legal move randomly, then pass.
		for i in range(5):
			mymove = (randint(0,18), randint(0,18))
			try:
				nextgs = go.nextGameState(gs,mymove)
				return mymove
			except go.IllegalMove:
				pass
		return None