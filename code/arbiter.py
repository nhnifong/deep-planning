from copy import copy, deepcopy
import PuertoRico

class Player:
    def __init__(self):
        self.wins = 0

    def prepare(self):
        """Get ready for new game"""
        pass

    def play(self,gamestate):
        # build a model input vector based on recent past and current gamestate.
        # leave information about own moves missing.
        incompleteVec = gamestate.serialize()
        incompleteVec.extend(self.history[-3:])
        activeVec = self.model.activate(incompleteVec)
        # extract preditions of own actions from expectation of future gamestate
        chosenmove = activeVex[NN:DD]
        return chosenmove

numPlayers = 4
players = [Player for i in range(numPlayers)]
gamesPlayed = 0
totalTurns = 0
draws = 0

while True:
    for pl in players:
        pl.prepare()
    gamestate = PuertoRico.initialState( numPlayers )
    winner = None
    while winner in [None, "draw"]:
        
        winner = PuertoRico.checkwin(gamestate)
    if winner == "draw":
        draws += 1
    else:
        winner.wins += 1
