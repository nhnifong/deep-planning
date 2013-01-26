from random import randint, choice, shuffle

resource = {
    'empty:'0,
    'indigo':1,
    'corn':2,
    'sugar':3,
    'coffee':4,
    'tobacco':5
    'quarry':6
}

class PlayerMat:
    def __init__(self):
        self.doubloons = 0
        self.isGoverner = False
        # zero is empty. is this is the number of plantation tiles of each type you have
        self.plantationTiles = {0:12, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

    def firstEmptyPlantation(self):
        for i,tile in enumerate(self.plantationTiles):
            if tile == 0:
                return i
        return None

    def serialize(self):
        flat = []
        flat.append(float(self.doubloons))
        return flat

class Gamestate:
    def __init__(self,np):
        self.numPlayers = np
        self.cp = randint(0, np-1) # short for current player
        self.playerMats = [PlayerMat() for pm in range(np)]
        self.playerMats[self.cp].isGoverner = True
        for i,mat in enumerate(self.playerMats):
            mat.doubloons = np-1
            # first half of players get indigo, second half get corn
            mat.plantationTiles[ firstEmptyPlantation() ] = (i-cp+np)%np*2//np+1
        self.freeVictoryPoints = np*25
        self.freeQuarryTiles = 8
        # upside down shuffled plantation tiles
        self.hiddenTiles = []
        self.hiddenTiles.extend([resource['coffee']] * 8 )
        self.hiddenTiles.extend([resource['tobacco']]* 9 )
        self.hiddenTiles.extend([resource['corn']]   * 10)
        self.hiddenTiles.extend([resource['sugar']]  * 11 )
        self.hiddenTiles.extend([resource['indigo']] * 12 )
        self.hiddenTiles.shuffle()
        self.knownTiles = {1:0, 2:0, 3:0, 4:0, 5:0}
        numProspectors = max(np-3,0)
        self.ships = [[0]*np+1+i for i in range(3)]
        # number of each type available
        self.freegoods = {
            resource['coffee']: 9,
            resource['tobacco']: 9,
            resource['corn']: 10,
            resource['sugar']: 11
            resource['indigo']: 11,
        }

    def serialize(self, perspective):
        # perspective is a given player number, i.e, yourself.
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
