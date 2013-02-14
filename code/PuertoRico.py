from random import randint, choice, shuffle
from copy import copy,deepcopy

resourceOrder = ['empty','indigo','corn','sugar','coffee','tobacco','quarry']
roleCardOrder = ['settler','mayor','builder','craftsman','trader','captain','prospector']
buildingTypes = {
   0:{'name':'small indigo plant',
      'circles':1, # circles occupiable by colonists
      'vpoints':1, # victory points
      'cost':1, # doubloons cost
      'size':1, # big or small building (1|2)
      'qnum':1, # number of quarries the cost can be reduced by (1 - 4)
      'init':4, # number available at the beginning of the game
      'vio':0   # violet building
     },
   1 :{'name':'small sugar mill', 'circles':1, 'vpoints':1, 'cost':2, 'size':1, 'qnum':1, 'init':4, 'vio':0 },
   2 :{'name':'small market', 'circles':1, 'vpoints':1, 'cost':1, 'size':1, 'qnum':1, 'init':2, 'vio':1 },
   3 :{'name':'hacienda', 'circles':1, 'vpoints':1, 'cost':2, 'size':1, 'qnum':1, 'init':2, 'vio':1 },
   4 :{'name':'construction hut', 'circles':1, 'vpoints':1, 'cost':2, 'size':1, 'qnum':1, 'init':2, 'vio':1 },
   5 :{'name':'small warehouse', 'circles':1, 'vpoints':1, 'cost':3, 'size':1, 'qnum':1, 'init':2, 'vio':1 },
   6 :{'name':'indigo plant', 'circles':3, 'vpoints':2, 'cost':3, 'size':1, 'qnum':2, 'init':3, 'vio':0 },
   7 :{'name':'sugar mill', 'circles':3, 'vpoints':2, 'cost':4, 'size':1, 'qnum':2, 'init':3, 'vio':0 },
   8 :{'name':'hospice', 'circles':1, 'vpoints':2, 'cost':4, 'size':1, 'qnum':2, 'init':2, 'vio':1 },
   9 :{'name':'office', 'circles':1, 'vpoints':2, 'cost':5, 'size':1, 'qnum':2, 'init':2, 'vio':1 },
   10:{'name':'large market', 'circles':1, 'vpoints':2, 'cost':5, 'size':1, 'qnum':2, 'init':2, 'vio':1 },
   11:{'name':'large warehouse', 'circles':1, 'vpoints':2, 'cost':6, 'size':1, 'qnum':2, 'init':2, 'vio':1 },
   12:{'name':'tobacco storage', 'circles':3, 'vpoints':3, 'cost':5, 'size':1, 'qnum':3, 'init':3, 'vio':0 },
   13:{'name':'coffee roaster', 'circles':2, 'vpoints':3, 'cost':6, 'size':1, 'qnum':3, 'init':3, 'vio':0 },
   14:{'name':'factory', 'circles':1, 'vpoints':3, 'cost':8, 'size':1, 'qnum':3, 'init':2, 'vio':1 }, # part one of "balanced" variant. costs of factory and university swapped
   15:{'name':'university', 'circles':1, 'vpoints':3, 'cost':7, 'size':1, 'qnum':3, 'init':2, 'vio':1 },
   16:{'name':'harbor', 'circles':1, 'vpoints':3, 'cost':8, 'size':1, 'qnum':3, 'init':2, 'vio':1 },
   17:{'name':'wharf', 'circles':1, 'vpoints':3, 'cost':9, 'size':1, 'qnum':3, 'init':2, 'vio':1 },
   18:{'name':'guild hall', 'circles':1, 'vpoints':4, 'cost':10, 'size':2, 'qnum':4, 'init':1, 'vio':1 },
   19:{'name':'residence', 'circles':1, 'vpoints':4, 'cost':10, 'size':2, 'qnum':4, 'init':1, 'vio':1 },
   20:{'name':'fortress', 'circles':1, 'vpoints':4, 'cost':10, 'size':2, 'qnum':4, 'init':1, 'vio':1 },
   21:{'name':'customs house', 'circles':1, 'vpoints':4, 'cost':10, 'size':2, 'qnum':4, 'init':1, 'vio':1 },
   22:{'name':'city hall', 'circles':1, 'vpoints':4, 'cost':10, 'size':2, 'qnum':4, 'init':1, 'vio':1 }
}
numSlots = sum([buildingTypes[b]['circles'] for b in range(23)])

class ResourceCollection:
    """A container that can have any number of any of the resources in it.
    Optionally can be exlusively one resource, the first one that it encounters. must become empty to disassociate from it.
    Optionally can have a finite capacity, in which case it will init full of 'empty'
    """
    def __init__(self, capacity=None, exclusive=False):
        self.d = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        self.capacity = capacity
        if capacity is not None:
            self.d[0] = capacity
        self.exclusive = exclusive

    def can_add(self, res, amount):
        if type(res) == str:
            res = resourceOrder.index(res)
        if self.capacity is not None:
            if self.d[0] < amount:
                return False # wont fit
        if self.exclusive:
            # determine if we associate with a type, and which it is.
            for i in range(1,7):
                if self.d[i] > 0:
                    if res != i:
                        return False
        return True

    def add(self, res, amount):
        if type(res) == str:
            res = resourceOrder.index(res)
        if self.can_add(res, amount):
            self.d[res] += amount
            if self.capacity is not None:
                self.d[0] -= amount

    def can_remove(self, res, amount):
        if type(res) == str:
            res = resourceOrder.index(res)
        if self.d[res] >= amount:
            return true

    def remove(self, res, amount):
        if type(res) == str:
            res = resourceOrder.index(res)
        if self.can_remove(res, amount):
            self.d[res] -= amount
            if self.capacity is not None:
                self.d[0] += amount

    def remove_random(self):
        available = []
        for i in range(1,7):
            available.extend([i]*(self.d[i]))
        what = choice(available)
        self.remove(what)
        return what

class PlayerMat:
    def __init__(self):
        self.victoryPoints = 0
        self.doubloons = 0
        self.isGoverner = False
        # zero is empty. is this is the number of plantation tiles of each type you have
        self.plantationTiles = # Like a resource collection but the tiles can be occupied or not
        self.buildingTiles = # Like the above, but can have partially occupied spaces, cannot have more than one of each building, and some building take two spaces.
        self.colonistsInSanJuan = 0


class RoleCard:
    def __init_-(self, kind)
        if type(kind) == str:
            kind = roleCardOrder.index(kind)
        self.kind = kind
        self.faceup = True
        self.doubloons = 0

class Gamestate:
    def __init__(self,np):
        self.numPlayers = np
        self.cp = randint(0, np-1) # short for current player

        # pile of hidden plantation tiles
        self.hiddenTiles = ResourceCollection()
        self.hiddenTiles.add( 'coffee', 8 )
        self.hiddenTiles.add( 'tobacco', 9  )
        self.hiddenTiles.add( 'corn', 10 )
        self.hiddenTiles.add( 'sugar', 11 )
        self.hiddenTiles.add( 'indigo', 12 )

        # give tiles to players before turning over 5 random tiles
        self.playerMats = [PlayerMat() for pm in range(np)]
        self.playerMats[self.cp].isGoverner = True
        for i,mat in enumerate(self.playerMats):
            mat.doubloons = np-1
            # just a function for prodcing a 1 (indigo) or a 2 (corn) depending on whether we are halfway around the board from the starting player 
            res_get = (i-cp+np)%np*2//np+1
            self.hiddenTiles.remove(res_get)
            mat.plantationTiles.add(res_get)

        # turn over 5 random tiles
        self.knownTiles = ResourceCollection()
        for i in range(np+1):
            self.knownTiles.add( self.hiddenTiles.remove_random() )

        self.freeVictoryPoints = np*25
        self.freeQuarryTiles = 8
        self.ships = [ResourceCollection(capacity=np+1+i, exclusive=True) for i in range(3)]
        self.freeGoods = ResourceCollection()
        self.freegoods.add( 'coffee', 9 )
        self.freegoods.add( 'tobacco', 9 )
        self.freegoods.add( 'corn', 10 )
        self.freegoods.add( 'sugar', 11 )
        self.freegoods.add( 'indigo', 11 )
        self.tradingHouse = ResourceCollection( capacity=4, exclusive=False)
        # the trading house only accepts one of each type unless you have an office, this is managed by the nextstate function
        self.freeColonists = np*20-5
        self.colonistShip = np

        numProspectors = max(np-3,0)
        self.rolecards = [ # (state, num_doubloons_on_card
            RoleCard('settler'),
            RoleCard('mayor'),
            RoleCard('builder'),
            RoleCard('craftsman'),
            RoleCard('trader'),
            RoleCard('captian')
        ]
        for i in range(numProspectors):
            self.roleCards.append(RoleCard('prospector'))

        self.round = 0
        self.turnInRound = 0
        self.turnInRole = 0
        self.roleInProgress = None # or the index of one of the rolecards

class Move:
    """A data structure fully defining a move"""
    def __init__(self, roleCardIndex):
        # the index in this gamestate's list of rolecards that this move pertains to.
        # the move does not explicitly declare to be the first use of that card, this is implied by the gamestate.
        # for ease of use by SDA algorithms, if the move is overspecified, the extra parts are ignored.
        # for example, if this is a captain role, and the move also specifies a building choice, the building is ignored.
        self.roleCardIndex = roleCardIndex
        # a player has the choice to take the special privilige or not when he is the first to take a role card in a round
        # for settler, players must indicate the type of tile they want
        self.takeTileType = 0
        # special privlige of mayor
        # self.takeOneFromColonistSupply = True #assumed
        # during the mayor phase, players must indicate which of the circles on their mat they will leave empty, if they cannot fill them all with colonists.
        # thankfully a player can only have one of each type of building, so this is specified with one bit for each possible circle a player could have.
        # False means empty. It is not legal to specify more circles filled than you can actually fill, or to specify that any colonists remain unused.
        # slots for which you do not have buildings are ignored.
        self.circleSlots = [True]*numSlots
        # special privlige of builder
        self.takeBuildingDiscount = True
        # indicate type of building you will build. any valid key of buildingTypes
        self.building = 0
        # craftsman's special privlige: which type of good he will produce as his extra good [0|1|2|3|4|5]
        # zero indicates the craftsman chooses not to use the privlige
        self.craftsmanGood = 1
        # trader's special privlige: recieve extra doubloon
        self.traderPriv = True
        self.whichTradeGood = 1
        # captian's special privlige: take an extra victory point
        self.captainPriv = True
        # player must indicate which type of good they will attempt to ship. If they can't ship that type, it's not a legal move
        # they will never be asked what to ship if they cannot ship anything, their turn will be skipped.
        self.shipgood = 1 
        # at the end of the captian's phase, each player may store one barrel. if you don't have anything to store, you won't be asked.
        self.storeGood = 1
        # special building privs
        self.smallWarehouseGood = 2
        self.largeWarehouseGoods = [3,4]
        # hacienda owners may choose to take a face down planation tile on his of the settler phase
        #self.haciendaExtraTile = True #assumed
        # Hospice owners may take a colonist --in the settler phase-- from the supply and put it on the tile they choose in this turn. 
        #self.hospiceColonist = True #hospice owners are assumed to take this privige when they can.
        # University - same as hospice, but wiht buildings.
        #self.universityColonist = True #assumed
        # Wharf owners may use their own ship if they want to
        #self.useWharfShip = True #assumed

def nextGamestate(gamestate,move):
    gs = deepcopy(gamestate)
    player = gs.playerMats[gs.cp]
    if gs.roleInProgress is None:
        assert gs.turnInRole == 0
        assert gs.roleCards[move.roleCardIndex].faceup
        # set the new role to the one chosen by the player
        gs.roleInProgress = move.roleCardIndex
        # Give the doubloons on the card to the player
        gs.cp.doubloons += gs.roleCards[gs.roleInProgress].doubloons
        gs.roleCards[gs.roleInProgress].doubloons = 0
        gs.roleCards[gs.roleInProgress].faceup = False
    role = gs.roleCards[gs.roleInProgress]
    
    if role.kind == 'settler':
        if move.takeTileType == resourceOrder['quarry']: # quarries can only be taken on certain conditions
            assert any([ gs.turnInRole == 0, # either the player is the one who chose the settler card
                         player.buildingTiles.typeOccupied('construction hut') >= 1, # or the player has an occupied construction hut
                       ])
            assert # the player has room for another plantation
            assert # there is a plantation of that type available 
            
            # hospice owners are assumed to take their privlige.
            if player.buildingTiles.typeOccupied('hospice') >= 1:
                pass # newly placed plantation will be occupied with a colonist from the supply

            # if there are any plantations left to choose
            # and the next player has not already chosen one this role
            # and the next player has room for one
            # increment the cp to the next player who can choose
            # if there are no more players who can choose,
            # set the turn in role to 0 and increment the turn in round,
            # set the role in progress to none
            # draw new plantation tiles.
        elif move.takeTileType == resourceOrder['mayor']:
            # 

    gs.turnInRole += 1

    return gamestate


def initialState(numPlayers):
    gamestate = Gamestate(numPlayers)
    return gamestate

def islegal(gamestate, move):
    
    # is selected role card valid or relevant?
    if gamestate.roleInProgress is None:
        if not self.playerMats[self.cp].isGoverner:
            return False
        try:
            card = gamestate.roleCards[ move.roleCardIndex ]
        except IndexError, ValueError:
            return False
        if not card.faceup:
            return False
    else:
        role = gamestate.rolecards[gamestate.roleInProgress]
        #role.kind.....
    return True

def checkwin(gamestate):
    pass
