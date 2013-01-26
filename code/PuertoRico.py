
class PlayerMat:
    def __init__(self):
        self.doubloons = 0

    def serialize(self):
        flat = []
        flat.append(float(self.doubloons))
        return flat

class Gamestate:
    def __init__(self,np):
        self.numPlayers = np
        self.playerTurn = 0
        self.playerMats = []
        for i in range(self.numPlayers):
            self.playerMats.append( PlayerMat() )

    def serialize(self):
        flat = []
        flat.append(float(self.numPlayers))
        flat.append(float(self.playerTurn))
        for mat in self.playerMats:
            flat.extend(mat.serialize())
        return flat

def initialState(numPlayers):
    gamestate = Gamestate(numPlayers)
    return gamestate

def islegal(gamestate,move):
    return True

def nextGamestate(gamestate,move):
    return gamestate

def checkwin(gamestate):
    pass
