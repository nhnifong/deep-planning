#Simple Go playing program
#Goals are:
#1) Easy to understand:
#   If fully understanding GnuGo could be considered advanced,
#   then this should be beginner level Go playing program
#   Main focus is in understanding code, not in fancy stuff.
#   It should illustrate Go concepts using simple code.
#2) Plays enough well to get solid rating at KGS
#3) Small
#4) Dual license: GPL and license used at Senseis

#Why at Senseis?
#Goal is to illustrate Go programming and not to code another "GnuGo".
#Senseis looks like good place to co-operatively write text and 
#create diagrams to illustrate algorithms.
#So main focus is in explaining code.
#Also possibility is to crosslink between concepts and documented code.
#http://senseis.xmp.net/?SimpleGo

#v0.0:
#Select move randomly from all legal moves including pass move.

#v0.1:
#Its quite simple actually:
#Unconditionally alive groups and dead groups in those eyes and eyes are counted as 1/each intersection
#For other white/black blocks: (1 - (1 - (liberties/max_liberties)**2 ) ) * 0.7 * block size:
#    if group has maximum amount of liberties, it gets 0.7*amount of stones
#Try each move and score them: also atari replies to block and neighbour block are checked
#Thats about it.

#v0.1.1:
#Adding stone is now much faster.
#Groups completely surrounded by live blocks:
#ignore empty points adjacent to live block when counting potential eyes.

#v0.1.2:
#Can detect more unconditional life cases: hopefully now equivalent to Benson algorithm
#This mean less futile moves at end in some cases.

#v0.1.3:
#Can detect more unconditionally dead grops:
#It analyses false eyes. Then potential eye areas in previous unconditional life analysis consisting of empty points and
#opponent stones that don't have enough potential true eyes are also marked as unconditionally dead.

#v0.1.4:
#Handles big handicaps on small boards better: usually same as playing them.

#v0.1.5:
#Implemented Zobrist hashing: now 2-3x faster

#v0.1.6:
#Detects many groups that are unconditionally dead even if there are capturable opponent stones inside.

#TODO: v0.2 and later:
#chain and dragon building
#read ladders
#influence: bouzy? maybe something else instead
#liberty counting: potential
#  eye counting part of above?
#  diagonal connction cut?

import string, random, sys

EMPTY = "."
BLACK = "X"
WHITE = "O"

BOTH = BLACK + WHITE

colors = [BLACK, WHITE]

other_side = {BLACK: WHITE, WHITE: BLACK}

PASS_MOVE = (-1, -1)

WORST_SCORE = -1000000000

normal_stone_value_ratio = 0.7 #how much value is given to stones that are not unconditionally alive and have max liberties

x_coords_string = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
max_size = len(x_coords_string)

debug_flag = False

def move_as_string(move, board_size):
    """convert move tuple to string
       example: (2, 3) -> B3
    """
    if move==PASS_MOVE: return "PASS"
    x, y = move
    return x_coords_string[x-1] + str(y)

def string_as_move(m, size):
    """convert string to move tuple
       example: B3 -> (2, 3)
    """
    if m=="PASS": return PASS_MOVE
    x = string.find(x_coords_string, m[0]) + 1
    y = int(m[1:])
    return x,y

class Block:
    """Solidly connected group of stones or empy points as defined in Go rules

       Attributes:
       stones: position of stones or empty points
               empty points are like trasparent stones
       liberties: position of liberties
       color: color of stones
    """
    def __init__(self, color):
        self.stones = {}
        self.neighbour = {}
        self.color = color

    def add_stone(self, pos):
        """add stone or empty point at given position
        """
        self.stones[pos] = True

    def remove_stone(self, pos):
        """remove stone or empty point at given position
        """
        del self.stones[pos]

    def add_block(self, other_block):
        """add all stones and neighbours to this block
        """
        self.stones.update(other_block.stones)
        self.neighbour.update(other_block.neighbour)

    def mark_stones(self, mark):
        """mark all stones with given value
        """
        for stone in self.stones:
            self.stones[stone] = mark

    def size(self):
        """returns block size
        """
        return len(self.stones)

    def max_liberties(self):
        """returns maximum amount liberties possible for this block size
        """
        return self.size() * 2 + 2

    def get_origin(self):
        """return origin pos of block
        """
        lst = self.stones.keys()
        lst.sort()
        return lst[0]

class Eye:
    """Eye: collection of empty blocks and either black or white blocks

       Attributes:
       parts: list of blocks forming this eye
    """
    def __init__(self):
        self.parts = []

    def iterate_stones(self):
        """Go through all stones in all blocks in eye
        """
        for block in self.parts:
            for stone in block.stones:
                yield stone

    def mark_status(self, live_color):
        """Go through all stones in all blocks in eye
           All opposite colored blocks are marked dead.
           Empty blocks are marked as territory for live_color.
        """
        for block in self.parts:
            if block.color == live_color:
                block.status = "alive"
            elif block.color == other_side[live_color]:
                block.status = "dead"
            else:
                block.status = live_color + " territory"

class Board:
    """Go board: one position in board and relevant methods

       Attributes:
       size: board size
       side: side to move
       captures: number of stones captured
       self.goban: actual board
       blocks: solidly connected group of stones or empty points as defined in Go rules
               there is reference to same block from every position block has stone
       chains: connected group of stones
               This is for v0.2 or later. Not used currently.
    """
    def __init__(self, size):
        """Initialize board:
           argument: size
        """
        self.size = size
        self.side = BLACK
        self.captures = {}
        self.captures[WHITE] = 0
        self.captures[BLACK] = 0
        self.goban = {} #actual board
        self.init_hash()
        #Create and initialize board as empty size*size
        for pos in self.iterate_goban():
            #can't use set_goban method here, because goban doesn't yet really exists
            self.goban[pos] = EMPTY
            self.current_hash = self.current_hash ^ self.board_hash_values[EMPTY, pos]
        self.blocks = {} #blocks dictionary
        #Create and initialize one whole board empty block
        new_block = Block(EMPTY)
        for pos in self.iterate_goban():
            new_block.add_stone(pos)
            self.blocks[pos] = new_block
        self.block_list = [new_block]
        self.chains = {}

    def iterate_goban(self):
        """This goes through all positions in goban
           Example usage: see above __init__ method
        """
        for x in range(1, self.size+1):
            for y in range(1, self.size+1):
                yield x, y

    def iterate_neighbour(self, pos):
        """This goes through all neighbour positions in clockwise:
           up, right, down, left
           Example usage: see legal_move method
        """
        x, y = pos
        for x2,y2 in ((x,y+1), (x+1,y), (x,y-1), (x-1,y)):
            if 1<=x2<=self.size and 1<=y2<=self.size:
                yield (x2, y2)

    def iterate_diagonal_neighbour(self, pos):
        """This goes through all neighbour positions in clockwise:
           NE, SE, SW, NW
           Example usage: see analyse_eye_point method
        """
        x, y = pos
        for x2,y2 in ((x+1,y+1), (x+1,y-1), (x-1,y-1), (x-1,y+1)):
            if 1<=x2<=self.size and 1<=y2<=self.size:
                yield (x2, y2)

    def iterate_blocks(self, colors):
        """This goes through all distinct blocks on board with given colors.
           Example usage: see analyze_unconditionally_alive
        """
        for block in self.block_list:
            if block.color in colors:
                yield block

    def iterate_neighbour_blocks(self, block):
        """Go through all neighbour positions and add new blocks.
           Return once for each new block
        """
        blocks_seen = []
        for stone in block.neighbour:
            block2 = self.blocks[stone]
            if block2 not in blocks_seen:
                yield block2
                blocks_seen.append(block2)

    def iterate_neighbour_eye_blocks(self, eye):
        """First copy eye blocks to list of blocks seen
           Then go through all neighbour positions and add new blocks.
           Return once for each new block
        """
        blocks_seen = eye.parts[:]
        for block in eye.parts:
            for pos in block.neighbour:
                block2 = self.blocks[pos]
                if block2 not in blocks_seen:
                    yield block2
                    blocks_seen.append(block2)

    def init_hash(self):
        """Individual number for every possible color and position combination"""
        self.board_hash_values = {}
        for color in EMPTY+WHITE+BLACK:
            for pos in self.iterate_goban():
                self.board_hash_values[color, pos] = random.randint(-sys.maxint-1, sys.maxint)
        self.current_hash = 0

    def set_goban(self, color, pos):
        """Set stone at position to color and update hash value"""
        old_color = self.goban[pos]
        self.current_hash = self.current_hash ^ self.board_hash_values[old_color, pos]
        self.goban[pos] = color
        self.current_hash = self.current_hash ^ self.board_hash_values[color, pos]

    def key(self):
        """This returns unique key for board.
           Returns hash value for current position (Zobrist hashing)
           Key can be used for example in super-ko detection
        """
        return self.current_hash
##        stones = []
##        for pos in self.iterate_goban():
##            stones.append(self.goban[pos])
##        return string.join(stones, "")

    def change_side(self):
        self.side = other_side[self.side]

    def are_adjacent_points(self, pos1, pos2):
        """Tests whether pos1 and pos2 are adjacent.
           Returns True or False.
        """
        for pos in self.iterate_neighbour(pos1):
            if pos==pos2:
                return True
        return False

    def list_empty_3x3_neighbour(self, pos):
        #check normal neighbour positions first
        neighbour_list = []
        for pos2 in self.iterate_neighbour(pos):
            if self.goban[pos2]==EMPTY:
                neighbour_list.append(pos2)

        #check diagonal neighbour positions first
        #this is done to ensure that empty block is/will not splitted
        diagonal_neighbour_list = []
        for pos2 in self.iterate_diagonal_neighbour(pos):
            if self.goban[pos2]==EMPTY:
                diagonal_neighbour_list.append(pos2)
                
        return neighbour_list, diagonal_neighbour_list

    def is_3x3_empty(self, pos):
        if self.goban[pos]!=EMPTY: return False
        neighbour_list, diagonal_neighbour_list = self.list_empty_3x3_neighbour(pos)
        if len(neighbour_list)==4 and len(diagonal_neighbour_list)==4:
            return True
        return False

    def simple_same_block(self, pos_list):
        """Check if all positions in pos_list are in same block.
           This searches only at immediate neighbour.
           Return True if they are or False if not or can't decide with this simple search.
        """
        if len(pos_list) <= 1:
            return True
        color = self.goban[pos_list[0]]
        temp_block = Block(color)
        #Add all stones in pos_list and their neighbour to block if they have same color.
        for pos in pos_list:
            temp_block.add_stone(pos)
            for pos2 in self.iterate_neighbour(pos):
                if self.goban[pos2]==color:
                    temp_block.add_stone(pos2)
        
        new_mark = 2 #When stones are added they get by default value True (==1)
        self.flood_mark(temp_block, pos_list[0], new_mark)
        for pos in pos_list:
            if temp_block.stones[pos]!=new_mark:
                return False
        return True

    def add_stone(self, color, pos):
        """add stone or empty at given position
           color: color of stone or empty
           pos: position of stone
           This will create new block for stone
           and add stones from same colored neighbour blocks if any.
           Also makes every position in combined block to point to block.
           Remove pos from existing block and potentially split it.
           Finally calculate new neighbours for all changed blocks:
           This is needed only when block is split into 2 or more blocks.
           Other cases are handed in need to do basis.
        """
        old_block = self.blocks[pos]
        old_color = old_block.color
        old_block.remove_stone(pos)
        if old_block.size()==0:
            self.block_list.remove(old_block)
        self.set_goban(color, pos)
        new_block = Block(color)
        new_block.add_stone(pos)
        self.add_block(new_block)
        changed_blocks = [] #only those blocks that need complete neighbour calculation

        #old_block: Is anything left?
        #           Is it split into pieces?
        #new_block: Is there existing same colored neighbour blocks?
        #both and all existing neighbours: calculate neighbor list (from scratch?)
        #........OO.........
        #......OO.O.........
        #......O.!.O...OOOO.
        #.......O.OO...O..O.
        #.XXX...XX....XX.O..
        #.X.!XX.X.!XX.X.!...
        #.XXX...XX.....X.O..
        #..........X!X......
        #...........O.......

        #combine and split blocks as needed
        split_list = []
        for pos2 in self.iterate_neighbour(pos):
            other_block = self.blocks[pos2]
            if self.goban[pos2]==color:
                new_block = self.combine_blocks(new_block, other_block)
            else:
                new_block.neighbour[pos2] = True
                if self.goban[pos2]==old_color:
                    split_list.append(pos2)
        
        #If these splits are actually trivially same: do update fast
        if self.simple_same_block(split_list):
            old_block.neighbour[pos] = True
            #are pos neighbour positions also neighbour to reduced old_block?
            for pos2 in self.iterate_neighbour(pos):
                if pos2 not in old_block.stones: #this if is slight optimization: can't be neighbour if belongs to block
                    for pos3 in self.iterate_neighbour(pos2):
                        if pos3 in old_block.stones:
                            break #yes, pos2 is neighbour
                    else: #no, it's not neighbour
                        #was it neighbour to old_block? remove it if it is
                        if pos2 in  old_block.neighbour:
                            del old_block.neighbour[pos2]
        else:
            changed_blocks.append(old_block) #now we need this
            old_block.mark_stones(0)
            last_old_mark = 0
            for pos2 in split_list:
                other_block = self.blocks[pos2]
                if other_block.stones[pos2]==0:
                    last_old_mark = last_old_mark + 1
                    self.flood_mark(other_block, pos2, last_old_mark)
                    if last_old_mark>1:
                        splitted_block = self.split_marked_group(other_block, last_old_mark)
                        self.add_block(splitted_block)
                        changed_blocks.append(splitted_block)

        if pos in new_block.neighbour:
            del new_block.neighbour[pos]

        for block in changed_blocks:
            self.calculate_neighbour(block)

##        for block in self.block_list:
##            old_neighbour = block.neighbour
##            self.calculate_neighbour(block)
##            if old_neighbour!=block.neighbour:
##                print old_neighbour
##                print block.neighbour
##                import pdb; pdb.set_trace()

    def add_block(self, block):
        self.block_list.append(block)
        for stone in block.stones:
            self.blocks[stone] = block

    def combine_blocks(self, new_block, other_block):
        """add all stones from other block to new block
           make board positions to point at new block
        """
        if new_block==other_block: return new_block
        if new_block.size() < other_block.size():
            #Optimization: for example if new_block size is one as is usually case
            #and other_block is most of board as is often case when combining empty point to mostly empty board.
            new_block, other_block = other_block, new_block
        new_block.add_block(other_block)
        for stone in other_block.stones:
            self.blocks[stone] = new_block
        self.block_list.remove(other_block)
        return new_block

    def split_marked_group(self, block, mark):
        """move all stones with given mark to new block
           Return splitted group.
        """
        new_block = Block(block.color)
        for stone, value in block.stones.items():
            if value==mark:
                block.remove_stone(stone)
                new_block.add_stone(stone)
        return new_block

    def flood_mark(self, block, start_pos, mark):
        """mark all stones reachable from given
           starting position with given mark
        """
        to_mark = [start_pos]
        while to_mark:
            pos = to_mark.pop()
            if block.stones[pos]==mark: continue
            block.stones[pos] = mark
            for pos2 in self.iterate_neighbour(pos):
                if pos2 in block.stones:
                    to_mark.append(pos2)

    def calculate_neighbour(self, block):
        """find all neighbour positions for block
        """
        block.neighbour = {}
        for stone in block.stones:
            for pos in self.iterate_neighbour(stone):
                if pos not in block.stones:
                    block.neighbour[pos] = True

    def change_block_color(self, color, pos):
        """change block color and
           set same color to all block positions in goban
        """
        block = self.blocks[pos]
        block.color = color
        for pos2 in self.blocks[pos].stones:
            self.set_goban(color, pos2)

    def remove_block(self, pos):
        self.change_block_color(EMPTY, pos)

    def list_block_liberties(self, block):
        """Returns list of liberties for block of stones.
        """
        liberties = []
        for pos2 in block.neighbour:
            if self.goban[pos2]==EMPTY:
                liberties.append(pos2)
        return liberties

    def block_liberties(self, block):
        """Returns number of liberties for block of stones.
        """
        liberties = self.list_block_liberties(block)
        return len(liberties)

    def liberties(self, pos):
        """Returns number of liberties for block of stones in given position.
        """
        return self.block_liberties(self.blocks[pos])

    def initialize_undo_log(self):
        """Start new undo log
        """
        self.undo_log = []

    def add_undo_info(self, method, color, pos):
        """Add info needed to undo move
           at start of log.
           Its added to start because changes are undone in reverse direction.
        """
        self.undo_log.insert(0, (method, color, pos))

    def apply_undo_info(self, method, color, pos):
        """Apply given change to undo part of move.
        """
        if method=="add_stone":
            self.add_stone(color, pos)
        elif method=="change_block_color":
            self.change_block_color(color, pos)

    def legal_move(self, move):
        """Test whether given move is legal.
           Returns truth value.
        """
        if move==PASS_MOVE:
            return True
        if move not in self.goban: return False
        if self.goban[move]!=EMPTY: return False
        for pos in self.iterate_neighbour(move):
            if self.goban[pos]==EMPTY: return True
            if self.goban[pos]==self.side and self.liberties(pos)>1: return True
            if self.goban[pos]==other_side[self.side] and self.liberties(pos)==1: return True
        return False

    def make_move(self, move):
        """Make move given in argument.
           Returns move or None if illegl.
           First we check given move for legality.
           Then we make move and remove captured opponent groups if there are any.
           While making move record what is needed to undo the move.
        """
        self.initialize_undo_log()
        if move==PASS_MOVE:
            self.change_side()
            return move
        if self.legal_move(move):
            self.add_stone(self.side, move)
            self.add_undo_info("add_stone", EMPTY, move)
            remove_color = other_side[self.side] 
            for pos in self.iterate_neighbour(move):
                if self.goban[pos]==remove_color and self.liberties(pos)==0:
                    self.remove_block(pos)
                    self.add_undo_info("change_block_color", remove_color, pos)
            self.change_side()
            return move
        return None

    def undo_move(self, undo_log):
        """Undo move using undo_log.
        """
        self.change_side()
        for method, color, pos in undo_log:
            self.apply_undo_info(method, color, pos)

    def analyse_eye_point(self, pos, other_color):
        """Analyse one point for eye type.
           If not empty or adjacent to other color: return None.
           Otherwise analyse True/False status of eye.
           
           

           True(!) and false(?) eyes.
           XXX XXO XXO XXO OXO OXO
           X!X X!X X?X X?X X?X X?X
           XXX XXX OXX XXO XXO OXO
           
           --- --- --- +-- +--
           X!X X?X X?X |!X |?X
           XXX XXO OXO |XX |XO
           
           2 empty points: True(!) and false(?) eyes.
           This works just fine with normal (false) eye code.
           XXXX XXXO XXXO XXXO OXXO OXXO
           X!!X X!!X X!!X X!?X X!?X X??X
           XXXX XXXX OXXX XXXO XXXO OXXO
           
           ---- ---- ---- +--- +---
           X!!X X!?X X??X |!!X |!?X
           XXXX XXXO OXXO |XXX |XXO
           
           3 empty points in triangle formation: True(!) and false(?) eyes.
           This works just fine with normal (false) eye code.
           XXXX XXXO XXXO XXXO OXXO OXXO
           X!!X X!!X X!!X X!!X X!!X X?!X
           XX!X XX!X OX!X XX!X XX!X OX!X
            XXX  XXX  XXX  XXO  XXO  XXO
           
           XXXX XXXO XXXO XXXO OXXO OXXO
           X!!X X!!X X!!X X!!X X!!X X?!X
           XX!X XX!X OX!X XX?X XX?X OX?X
            OXX  OXX  OXX  OXO  OXO  OXO
        """
        if self.goban[pos]!=EMPTY:
            return None
        for pos2 in self.iterate_neighbour(pos):
            if self.goban[pos2]==other_color:
                return None
        total_count = 0
        other_count = 0
        for pos2 in self.iterate_diagonal_neighbour(pos):
            total_count = total_count + 1
            if self.goban[pos2]==other_color:
                other_count = other_count + 1
        if total_count==4:
            if other_count > 1:
                return False
            else:
                return True
        else:
            if other_count > 0:
                return False
            else:
                return True

    def analyse_opponent_stone_as_eye_point(self, pos):
        """Analyse one point for eye type.
           Otherwise analyse True/False status of eye.
           Only take into account live other color stones.
           

           True(O) and false(o) eyes.
           @ == unconditionally live O stone.
           XXX XX@ XX@ XX@ @X@ @X@
           .OX .OX .oX .oX .oX .oX
           XXX XXX @XX XX@ XX@ @X@
           
           --- --- --- +-- +--
           .OX .oX .oX |O. |o.
           XXX XX@ @X@ |XX |X@
           
        """
        total_count = 0
        other_count = 0
        color = self.goban[pos]
        for pos2 in self.iterate_diagonal_neighbour(pos):
            total_count = total_count + 1
            if self.goban[pos2]==color and self.blocks[pos2].status=="alive":
                other_count = other_count + 1
        if total_count==4:
            if other_count > 1:
                return False
            else:
                return True
        else:
            if other_count > 0:
                return False
            else:
                return True

    def analyze_color_unconditional_status(self, color):
        """1) List potential eyes (eyes: empty+opponent areas flood filled):
              all empty points must be adjacent to those neighbour blocks with given color it gives eye.
           2) List all blocks with given color
              that have at least 2 of above mentioned areas adjacent
              and has empty point from it as liberty.
           3) Go through all potential eyes. If there exists neighbour
              block with less than 2 eyes: remove this this eye from list.
           4) If any changes in step 3, go back to step 2.
           5) Remaining blocks of given color are unconditionally alive and
              and all opponent blocks inside eyes are unconditionally dead.
           6) Finally update status of those blocks we know.
           7) Analyse dead group status.

             ABCDEFGHI
            +---------+
           9|.........| 9
           8|.XX......| 8
           7|.X.XXX...| 7
           6|.XXX.XOO.| 6
           5|..XOOOX..| 5
           4|.OOXXXX..| 4
           3|..X.X.X..| 3
           2|..XXXXX..| 2
           1|.........| 1
            +---------+
             ABCDEFGHI

             ABCDE
            +-----+
           5|.....|
           4|.XXX.|
           3|.X.X.|
           2|X.X..|
           1|XXX..|
            +-----+
             ABCDE

             ABCDEFGH
            +--------+
           8|........| 8
           7|..XXXXXX| 7
           6|..X..X.X| 6
           5|.XOOOXXX| 5
           4|.X..X...| 4
           3|.XXXX...| 3
           2|..X.X...| 2
           1|..XXX...| 1
            +--------+
           
             ABC
            +---+
           3|OO.| 3
           2|OXX| 2
           1|.OX| 1
            +---+
             ABC
            
             ABC
            +---+
           3|.OO| 3
           2|O.O| 2
           1|.O.| 1
            +---+
             ABC

             ABCDE
            +-----+
           5|X.XO.| 5
           4|.XXOO| 4
           3|X.XO.| 3
           2|OXXO.| 2
           1|.OXO.| 1
            +-----+
             ABCDE

             ABCDE
            +-----+
           5|X.X.O| 5
           4|.XX.O| 4
           3|X.X.O| 3
           2|OXXO.| 2
           1|.OX..| 1
            +-----+
             ABCDE
           
             ABCDEFGHJK
            +----------+
          10|XX.XOO.XX.|10
           9|.OXXXOXX.X| 9
           8|OXX.OXOOXX| 8
           7|OOOXXX.XX.| 7
           6|OXXOOXX.OX| 6
           5|X.X.X..XX.| 5
           4|XXOXXXXOOX| 4
           3|.XOXXXXOOX| 3
           2|XOOOXOOO.X| 2
           1|.OOXXOOOOX| 1
            +----------+
             ABCDEFGHJK
           
             ABCDEFGHJ
            +---------+
           9|O.O.O..X.| 9
           8|.O.O..XX.| 8
           7|O.OO.XX.O| 7
           6|OX.O.X.O.| 6
           5|.O.O.X.O.| 5
           4|O.O..XO.O| 4
           3|.OO..OXO.| 3
           2|OO.O.OXXX| 2
           1|..O.XX.X.| 1
            +---------+
             ABCDEFGHJ

             ABCDE
            +-----+
           5|.OOO.| 5
           4|OXXXO| 4
           3|OX.XO| 3
           2|OXXXO| 2
           1|.OOO.| 1
            +-----+
             ABCDE

             ABCDE
            +-----+
           5|!!?.?| 5
           4|XXXOX| 4
           3|XXXOO| 3
           2|.OOO.| 2
           1|?XO.O| 1
            +-----+
             ABCDE

             ABCDE
            +-----+
           5|XXXO.| 5
           4|X.XO.| 4
           3|XXOOO| 3
           2|X.XOO| 2
           1|XXXO.| 1
            +-----+
             ABCDE
           
             ABCDEFG
            +-------+
           7|.OOOOX.| 7
           6|OXXXOX.| 6
           5|OX.XOX.| 5
           4|OOXOOXX| 4
           3|OX.XOX.| 3
           2|OXXXOX.| 2
           1|.OOOOX.| 1
            +-------+
             ABCDEFG
           
             ABCDEFG
            +-------+
           7|OOOOOOO| 7
           6|OOXXXXO| 6
           5|OXXX.XO| 5
           4|OOOXXXO| 4
           3|O.XX.XO| 3
           2|OOOXXXO| 2
           1|O..OOOO| 1
            +-------+
             ABCDEFG
           
             ABCDEFG
            +-------+
           7|.O.OOX.| 7
           6|OXXXOX.| 6
           5|OX.XOX.| 5
           4|OXXOOXX| 4
           3|OX.XOX.| 3
           2|OXXXOX.| 2
           1|.OOOOX.| 1
            +-------+
             ABCDEFG
           
             ABCDEFG
            +-------+
           7|OO.OOO.| 7
           6|OXXXOOO| 6
           5|OX.XOXX| 5
           4|OXXOOX.| 4
           3|OX.XOXX| 3
           2|OXXXOX.| 2
           1|.OOOOX.| 1
            +-------+
             ABCDEFG
           
             ABCDEFG
            +-------+
           7|.OOOOX.| 7
           6|OXXXOX.| 6
           5|OX.XOX.| 5
           4|O.X.OXX| 4
           3|OX.XOX.| 3
           2|OXXXOX.| 2
           1|.OOOOX.| 1
            +-------+
             ABCDEFG
                      
             ABCDEFG
            +-------+
           7|OOOOOOO| 7
           6|OXXXXXO| 6
           5|OX.X.XO| 5
           4|OXX.XXO| 4
           3|OXXXXXO| 3
           2|OXOOOXO| 2
           1|OO?!?OO| 1
            +-------+
             ABCDEFG
                      
             ABCDEFGHJ
            +---------+
           9|.XXXXXXO.| 9
           8|OXOOO.XOO| 8
           7|OXO.O.XO.| 7
           6|OXXO.OXOO| 6
           5|O.XOOOXXO| 5
           4|O.XXXX?!X| 4
           3|OOOOOOX?X| 3
           2|.O.O.OOXO| 2
           1|.O.O..OOO| 1
            +---------+
             ABCDEFGHJ

             ABCDEFGHJ
            +---------+
           9|XXXXXXO..| 9
           8|XOOOXXOOO| 8
           7|XO.OX.O..| 7
           6|XOOXXOOO.| 6
           5|X.OXOXXOO| 5
           4|XOOXX?!XO| 4
           3|XO.OOX?XO| 3
           2|XOOOOOXOO| 2
           1|XXXXXXXO.| 1
            +---------+
             ABCDEFGHJ

             ABCDEF
            +------+
           6|?....?| 6
           5|.XXXX.| 5
           4|.X.X.?| 4
           3|?.X.X.| 3
           2|!.XXX.| 2
           1|!?...?| 1
            +------+
             ABCDEF

             ABCDEF
            +------+
           6|O!O!!!| 6
           5|!OOOOO| 5
           4|OO.OXX| 4
           3|X.O?X.| 3
           2|OOXXOO| 2
           1|!OOOO!| 1
            +------+
             ABCDEF

             ABCDEFG
            +-------+
           7|O.O....| 7
           6|.OOOOOO| 6
           5|OO.OXXX| 5
           4|X.O.X..| 4
           3|OOXOXXX| 3
           2|.OOOOOO| 2
           1|O.O....| 1
            +-------+
             ABCDEFG

             ABCDEFGHJ
            +---------+
           9|.........| 9
           8|.OOOOOOO.| 8
           7|.OXXXXXO.| 7
           6|.OX.O.XO.| 6
           5|.OOXXXOO.| 5
           4|.OO.X.OO.| 4
           3|.OXXXXXO.| 3
           2|OOX.O.XOO| 2
           1|.OXXXXXO.| 1
            +---------+
             ABCDEFGHJ

             ABCDEFG
            +-------+
           7|OOOOOOO| 7
           6|OXXXXXO| 6
           5|OX.X.XO| 5
           4|OXX.XXO| 4
           3|OXXXXXO| 3
           2|OXOOOXO| 2
           1|OO?X?OO| 1
            +-------+
             ABCDEFG
        """
        #find potential eyes
        eye_list = []
        not_ok_eye_list = [] #these might still contain dead groups if totally inside live group
        eye_colors = EMPTY + other_side[color]
        for block in self.iterate_blocks(EMPTY+WHITE+BLACK):
            block.eye = None
        for block in self.iterate_blocks(eye_colors):
            if block.eye: continue
            current_eye = Eye()
            eye_list.append(current_eye)
            blocks_to_process = [block]
            while blocks_to_process:
                block2 = blocks_to_process.pop()
                if block2.eye: continue
                block2.eye = current_eye
                current_eye.parts.append(block2)
                for pos in block2.neighbour:
                    block3 = self.blocks[pos]
                    if block3.color in eye_colors and not block3.eye:
                        blocks_to_process.append(block3)
        #check that all empty points are adjacent to our color
        ok_eye_list = []
        for eye in eye_list:
            prev_our_blocks = None
            eye_is_ok = False
            for stone in eye.iterate_stones():
                if self.goban[stone]!=EMPTY:
                    continue
                eye_is_ok = True
                our_blocks = []
                for pos in self.iterate_neighbour(stone):
                    block = self.blocks[pos]
                    if block.color==color and block not in our_blocks:
                        our_blocks.append(block)
                #list of blocks different than earlier
                if prev_our_blocks!=None and prev_our_blocks != our_blocks:
                    ok_our_blocks = []
                    for block in our_blocks:
                        if block in prev_our_blocks:
                            ok_our_blocks.append(block)
                    our_blocks = ok_our_blocks
                #this empty point was not adjacent to our block or there is no block that has all empty points adjacent to it
                if not our_blocks:
                    eye_is_ok = False
                    break
                    
                prev_our_blocks = our_blocks
            if eye_is_ok:
                ok_eye_list.append(eye)
                eye.our_blocks = our_blocks
            else:
                not_ok_eye_list.append(eye)
                #remove reference to eye that is not ok
                for block in eye.parts:
                    block.eye = None
        eye_list = ok_eye_list

        #first we assume all blocks to be ok
        for block in self.iterate_blocks(color):
            block.eye_count = 2

        #main loop: at end of loop check if changes
        while True:
            changed_count = 0
            for block in self.iterate_blocks(color):
                #not really needed but short and probably useful optimization
                if block.eye_count < 2:
                    continue
                #count eyes
                block_eye_list = []
                for stone in block.neighbour:
                    eye = self.blocks[stone].eye
                    if eye and eye not in block_eye_list:
                        block_eye_list.append(eye)
                #count only those eyespaces which have empty point(s) adjacent to this block
                block.eye_count = 0
                for eye in block_eye_list:
                    if block in eye.our_blocks:
                        block.eye_count = block.eye_count + 1
                if block.eye_count < 2:
                    changed_count = changed_count + 1
            #check eyes for required all groups 2 eyes
            ok_eye_list = []
            for eye in eye_list:
                eye_is_ok = True
                for block in self.iterate_neighbour_eye_blocks(eye):
                    if block.eye_count < 2:
                        eye_is_ok = False
                        break
                if eye_is_ok:
                    ok_eye_list.append(eye)
                else:
                    changed_count = changed_count + 1
                    not_ok_eye_list.append(eye)
                    #remove reference to eye that is not ok
                    for block in eye.parts:
                        block.eye = None
                eye_list = ok_eye_list
            if not changed_count:
                break

        #mark alive and dead blocks
        for block in self.iterate_blocks(color):
            if block.eye_count >= 2:
                block.status = "alive"
        for eye in eye_list:
            eye.mark_status(color)

        #Unconditional dead part:
        #Mark all groups with only 1 potential empty point and completely surrounded by live groups as dead.
        #All empty points adjacent to live group are not counted.
        for eye_group in not_ok_eye_list:
            eye_group.dead_analysis_done = False
        for eye_group in not_ok_eye_list:
            if eye_group.dead_analysis_done: continue
            eye_group.dead_analysis_done = True
            true_eye_list = []
            false_eye_list = []
            eye_block = Block(eye_colors)
            #If this is true then creating 2 eyes is impossible or we need to analyse false eye status.
            #If this is false, then we are unsure and won't mark it as dead.
            two_eyes_impossible = True
            has_unconditional_neighbour_block = False
            maybe_dead_group = Eye()
            blocks_analysed = []
            blocks_to_analyse = eye_group.parts[:]
            while blocks_to_analyse and two_eyes_impossible:
                block = blocks_to_analyse.pop()
                if block.eye:
                    block.eye.dead_analysis_done = True
                blocks_analysed.append(block)
                if block.status=="alive":
                    if block.color==color:
                        has_unconditional_neighbour_block = True
                    else:
                        two_eyes_impossible = False
                    continue
                maybe_dead_group.parts.append(block)
                for pos in block.stones:
                    eye_block.add_stone(pos)
                    if block.color==EMPTY:
                        eye_type = self.analyse_eye_point(pos, color)
                    elif block.color==color:
                        eye_type = self.analyse_opponent_stone_as_eye_point(pos)
                    else:
                        continue
                    if eye_type==None:
                        continue
                    if eye_type==True:
                        if len(true_eye_list) == 2:
                            two_eyes_impossible = False
                            break
                        elif len(true_eye_list) == 1:
                            if self.are_adjacent_points(pos, true_eye_list[0]):
                                #Second eye point is adjacent to first one.
                                true_eye_list.append(pos)
                            else: #Second eye point is not adjacent to first one.
                                two_eyes_impossible = False
                                break
                        else: #len(empty_list) == 0
                            true_eye_list.append(pos)
                    else: #eye_type==False
                        false_eye_list.append(pos)
                if two_eyes_impossible:
                    #bleed to neighbour blocks that are at other side of blocking color block:
                    #consider whole area surrounded by unconditional blocks as one group
                    for pos in block.neighbour:
                        block = self.blocks[pos]
                        if block not in blocks_analysed and block not in blocks_to_analyse:
                            blocks_to_analyse.append(block)
                
            #must be have some neighbour groups:
            #for example board that is filled with stones except for one empty point is not counted as unconditionally dead
            if two_eyes_impossible and has_unconditional_neighbour_block:
                if (true_eye_list and false_eye_list) or \
                   len(false_eye_list) >= 2:
                    #Need to do false eye analysis to see if enough of them turn to true eyes.
                    both_eye_list = true_eye_list + false_eye_list
                    stone_block_list = []
                    #Add holes to eye points
                    for eye in both_eye_list:
                        eye_block.remove_stone(eye)

                    #Split group by eyes.
                    new_mark = 2 #When stones are added they get by default value True (==1)
                    for eye in both_eye_list:
                        for pos in self.iterate_neighbour(eye):
                            if pos in eye_block.stones:
                                self.flood_mark(eye_block, pos, new_mark)
                                splitted_block = self.split_marked_group(eye_block, new_mark)
                                stone_block_list.append(splitted_block)

                    #Add eyes to block neighbour.
                    for eye in both_eye_list:
                        for pos in self.iterate_neighbour(eye):
                            for block in stone_block_list:
                                if pos in block.stones:
                                    block.neighbour[eye] = True

                    #main false eye loop: at end of loop check if changes
                    while True:
                        changed_count = 0
                        #Remove actual false eyes from list.
                        for block in stone_block_list:
                            if len(block.neighbour)==1:
                                 neighbour_list = block.neighbour.keys()
                                 eye = neighbour_list[0]
                                 both_eye_list.remove(eye)
                                 #combine this block and eye into other blocks by 'filling' false eye
                                 block.add_stone(eye)
                                 for block2 in stone_block_list[:]:
                                     if block!=block2 and eye in block2.neighbour:
                                         block.add_block(block2)
                                         stone_block_list.remove(block2)
                                 del block.neighbour[eye]
                                 changed_count =  changed_count + 1
                                 break #we have changed stone_block_list, restart

                        if not changed_count:
                            break

                    #Check if we have enough eyes.
                    if len(both_eye_list) > 2:
                        two_eyes_impossible = False
                    elif len(both_eye_list) == 2:
                        if not self.are_adjacent_points(both_eye_list[0], both_eye_list[1]):
                            two_eyes_impossible = False
                #False eye analysis done: still surely dead
                if two_eyes_impossible:
                    maybe_dead_group.mark_status(color)

    def analyze_unconditional_status(self):
        """Analyze unconditional status for each color separately
        """
        #Initialize status to unknown for all blocks
        for block in self.iterate_blocks(BLACK+WHITE+EMPTY):
            block.status = "unknown"
        #import pdb; pdb.set_trace()
        self.analyze_color_unconditional_status(BLACK)
        self.analyze_color_unconditional_status(WHITE)
        #cleanup
        for block in self.iterate_blocks(BLACK+WHITE+EMPTY):
            del block.eye

    def has_block_status(self, colors, status):
        for block in self.iterate_blocks(colors):
            if block.status==status:
                return True
        return False

    def territory_as_dict(self):
        territory = {}
        for block in self.iterate_blocks(EMPTY):
            if block.status==WHITE + " territory" or block.status==BLACK + " territory":
                territory.update(block.stones)
        return territory

    def score_stone_block(self, block):
        """Score white/black block.
           All blocks whose status we know will get full score.
           Other blocks with unknown status will get score depending on their liberties and number of stones.

           ....8....8-4=4....
           ...XXX...XXX.O....
           ..................
           .7-4=3..6-2=4.....
           ....XX...XX..7-3=4
           .....X...OX...XXX.
           ...............O..
           .....O............
           ..................
           ..................

           ..................
           .....@OOO.........
           .AXXXBxxxO........
           .....@OOO.........
           ..................
           ..................
           @:filled(@) or empty(.)
           s = block.size()
           l = block.liberties()
           L = block.max_liberties()
           s * l / L
           X:3
           x:3/8(.375)
           AX:4 
           XBx@:7*7/16(3.0625)
           XBx.:7*9/16(3.9375)
           X+x:3.375
           AX+x:4.375
           
           r = l / L
           s * (1 - (1-r)^2)
           X:3
           x:0.703125
           AX:4
           XBx@:4.78515625
           XBx.:5.66015625
           X+x:3.703125
           AX+x:4.703125

           ..................
           .....@OO..........
           ..AXXBxxO.........
           .....@OO..........
           ..................
           ..................
           r = l / L
           s * (1 - (1-r)^2)
           X:2
           x:0.611111111112
           X+x:2.611111111112
           AX:3
           AX+x:3.611111111112
           XBx@:3.29861111112
           XBx.:4.13194444444
           
           0.525 A3
           0.2296875 B3
           0.0875 C1
           -0.13125 C3

             ABC    A3
            +---+
           3|x..|3  X:1.5
           2|OXX|2  x:0.4375
           1|.o.|1  O:-0.4375
            +---+    :1.5
             ABC

             ABC    B3
            +---+
           3|.X.|3  X:1.828125
           2|OXX|2  O:-0.75
           1|.o.|1   :1.078125
            +---+   ->.328125
             ABC
        """

        if block.status=="alive":
            score = block.size()
        elif block.status=="dead":
            score = - block.size()
        else:
            liberties = float(self.block_liberties(block))
            #grant half liberty for each neightbour stone in atari
            for block2 in self.iterate_neighbour_blocks(block):
                if block2.color==other_side[block.color] and self.block_liberties(block2)==1:
                    for stone in block.neighbour:
                        if stone in block2.stones:
                            liberties = liberties + 0.5
            liberty_ratio = liberties / block.max_liberties()
            score = block.size() * normal_stone_value_ratio * (1 - (1-liberty_ratio)**2)
        return score

    def score_block(self, block):
        """Score block.
           All blocks whose status we know will get full score.
           White/black blocks will be scored by separate method and
           then we change sign if block was for other side.
        """
        if block.color==EMPTY:
            if block.status==self.side + " territory":
                score = block.size()
            elif block.status==other_side[self.side] + " territory":
                score = -block.size()
            else: #empty block with unknown status
                score = 0
        else:
            if block.color==self.side:
                score = self.score_stone_block(block)
            else: #block.color==other_side[self.side]
                score = -self.score_stone_block(block)
        return score

    def score_position(self):
        """Score position.
           Analyze position and then sum score for all blocks.
           All blocks whose status we know will get full score.
           Returned score is from side to move viewpoint.
        """
        score = 0
        self.analyze_unconditional_status()
        for block in self.iterate_blocks(BLACK+WHITE+EMPTY):
            score = score + self.score_block(block)
        return score

    def unconditional_score(self, color):
        score = 0
        self.analyze_unconditional_status()
        for block in self.iterate_blocks(WHITE+BLACK+EMPTY):
            if block.status == color + " territory" or \
                   (block.color == color and block.status == "alive") or \
                   (block.color == other_side[color] and block.status == "dead"):
                score = score + block.size()
        return score

    def __str__(self):
        """Convert position to string suitable for printing to screen.
           Returns board as string.
        """
        s = self.side + " to move:\n"
        s = s + "Captured stones: "
        s = s + "White: " + str(self.captures[WHITE])
        s = s + " Black: " + str(self.captures[BLACK]) + "\n"
        board_x_coords = "   " + x_coords_string[:self.size]
        s = s + board_x_coords + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        for y in range(self.size, 0, -1):
            if y < 10:
                board_y_coord = " " + str(y)
            else:
                board_y_coord = str(y)
            line = board_y_coord + "|"
            for x in range(1, self.size+1):
                line = line + self.goban[x,y]
            s = s + line + "|" + board_y_coord + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        s = s + board_x_coords + "\n"
        return s

    def as_string_with_unconditional_status(self):
        """Convert position to string suitable for printing to screen.
           
           Each position gets corresponding character as defined here:
           Empty          : .
           Black          : X
           White          : O
           Alive black    : &
           Alive white    : @
           Dead black     : x
           Dead white     : o
           White territory: =
           Black territory: :
           
           Returns board as string.
        """
        color_and_status_to_character = {
           EMPTY + "unknown"            : EMPTY,
           BLACK + "unknown"            : BLACK,
           WHITE + "unknown"            : WHITE,
           BLACK + "alive"              : "&",
           WHITE + "alive"              : "@",
           BLACK + "dead"               : "x",
           WHITE + "dead"               : "o",
           EMPTY + WHITE + " territory" : "=",
           EMPTY + BLACK + " territory" : ":"
        }
        self.analyze_unconditional_status()
        s = self.side + " to move:\n"
        s = s + "Captured stones: "
        s = s + "White: " + str(self.captures[WHITE])
        s = s + " Black: " + str(self.captures[BLACK]) + "\n"
        board_x_coords = "   " + x_coords_string[:self.size]
        s = s + board_x_coords + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        for y in range(self.size, 0, -1):
            if y < 10:
                board_y_coord = " " + str(y)
            else:
                board_y_coord = str(y)
            line = board_y_coord + "|"
            for x in range(1, self.size+1):
                pos_as_character = color_and_status_to_character[self.goban[x,y] + self.blocks[x,y].status]
                line = line + pos_as_character
            s = s + line + "|" + board_y_coord + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        s = s + board_x_coords + "\n"
        return s

class Game:
    """Game record and move generation

       Attributes:
       size: board size
       current_board: current board position
       move_history: past moves made
       undo_history: undo info for each past move
       position_seen: keeps track of position seen: this is used for super-ko detection
    """
    def __init__(self, size):
        """Initialize game:
           argument: size
        """
        self.size = size
        self.current_board = Board(size)
        self.move_history = []
        self.undo_history = []
        self.position_seen = {}
        self.position_seen[self.current_board.key()] = True

    def make_unchecked_move(self, move):
        """This is utility method.
           This does not check legality.
           It makes move in current_board and returns undo log and also key of new board
        """
        self.current_board.make_move(move)
        undo_log = self.current_board.undo_log[:]
        board_key = self.current_board.key()
        return undo_log, board_key

    def legal_move(self, move):
        """check whether move is legal
           return truth value
           first check move legality on current board
           then check for repetition (situational super-ko)
        """
        if move==PASS_MOVE:
            return True
        if not self.current_board.legal_move(move):
            return False
        undo_log, board_key = self.make_unchecked_move(move)
        self.current_board.undo_move(undo_log)
        if board_key in self.position_seen:
            return False
        return True

    def make_move(self, move):
        """make given move and return new board
           or return None if move is illegal
           First check move legality.
           This checks for move legality for itself to avoid extra make_move/make_undo.
           This is a bit more complex but maybe 2-3x faster.
           Then make move and update history.
        """
        if not self.current_board.legal_move(move):
            return None

        undo_log, board_key = self.make_unchecked_move(move)
        if move!=PASS_MOVE and board_key in self.position_seen:
            self.current_board.undo_move(undo_log)
            return None

        self.undo_history.append(undo_log)
        self.move_history.append(move)
        if move!=PASS_MOVE:
            self.position_seen[board_key] = True
        return self.current_board

    def undo_move(self):
        """undo latest move and return current board
           or return None if at beginning.
           Update repetition history and make previous position current.
        """
        if not self.move_history: return None
        last_move = self.move_history.pop()
        if last_move!=PASS_MOVE:
            del self.position_seen[self.current_board.key()]
        last_undo_log = self.undo_history.pop()
        self.current_board.undo_move(last_undo_log)
        return self.current_board

    def iterate_moves(self):
        """Go through all legal moves including pass move
        """
        yield PASS_MOVE
        for move in self.current_board.iterate_goban():
            if self.legal_move(move):
                yield move

    def list_moves(self):
        """return all legal moves including pass move
        """
        all_moves = [PASS_MOVE]
        for move in self.current_board.iterate_goban():
            if self.legal_move(move):
                all_moves.append(move)
        return all_moves

    def score_move(self, move):
        """Score position after move
           and go through moves that capture block that is part of move if any.
           Return best score from these.
        """
        self.make_move(move)
        cboard = self.current_board
        best_score = cboard.score_position()
        if move!=PASS_MOVE:
            block = cboard.blocks[move]
            liberties = cboard.list_block_liberties(block)
            #Check if this group is now in atari.
            if len(liberties)==1:
                move2 = liberties[0]
                if self.make_move(move2):
                    #get score from our viewpoint: negative of opponent score
                    score = -cboard.score_position()
                    if score > best_score:
                       best_score = score
                    self.undo_move()
            else:
                #Check if some our neighbour group is in atari instead.
                for stone in cboard.iterate_neighbour(move):
                    block = cboard.blocks[stone]
                    if block.color==cboard.side and cboard.block_liberties(block)==1:
                        #make_move later changes block.neighbour dictionary in some cases so this is needed
                        for block2 in list(cboard.iterate_neighbour_blocks(block)):
                            liberties = cboard.list_block_liberties(block2)
                            if len(liberties)==1:
                                move2 = liberties[0]
                                if self.make_move(move2):
                                    #get score from our viewpoint: negative of opponent score
                                    score = -cboard.score_position()
                                    if score > best_score:
                                       best_score = score
                                    self.undo_move()
        self.undo_move()
        return best_score

    def select_scored_move(self, remove_opponent_dead=False, pass_allowed=True):
        """Go through all legal moves.
           Keep track of best score and all moves that achieve it.
           Select one move from best moves and return it.
        """
        territory_moves_forbidden = pass_allowed
        base_score = self.current_board.score_position()
        if debug_flag:
            print "?", base_score
        #if abs(base_score)==self.size**2:
        #    import pdb; pdb.set_trace()
        has_unknown_status_block = self.current_board.has_block_status(WHITE+BLACK+EMPTY, "unknown")
        has_opponent_dead_block = self.current_board.has_block_status(other_side[self.current_board.side], "dead")
        #has unsettled blocks
        if has_unknown_status_block:
            pass_allowed = False
        #dead removal has been requested and there are dead opponent stones
        if remove_opponent_dead and has_opponent_dead_block:
            territory_moves_forbidden = False
            pass_allowed = False

        if territory_moves_forbidden:
            forbidden_moves = self.current_board.territory_as_dict()
        else:
            forbidden_moves = {}
        best_score = WORST_SCORE
        best_moves = []
        for move in self.iterate_moves():
            if move in forbidden_moves:
                continue
            score = -self.score_move(move) - base_score
            #self.make_move(move)
            #get score from our viewpoint: negative of opponent score
            #score = -self.current_board.score_position() - base_score
            #score = -self.score_position() - base_score
            if debug_flag:
                print score, move_as_string(move, self.size)
            #self.undo_move()
            #Give pass move slight bonus so its preferred among do nothing moves
            if move==PASS_MOVE:
                if not pass_allowed:
                    continue
                score = score + 0.001
            if score >= best_score:
                if score > best_score:
                   best_score = score
                   best_moves = []
                best_moves.append(move)
        if debug_flag:
            print "!", best_score, map(lambda m,s=self.size:move_as_string(m, s), best_moves)
        if len(best_moves)==0:
            return PASS_MOVE
        return random.choice(best_moves)

    def place_free_handicap(self, count):
        result = []
        move_candidates = []
        for move in self.current_board.iterate_goban():
            if self.current_board.is_3x3_empty(move):
                move_candidates.append(move)

        while len(result) < count:
            if self.current_board.side==WHITE:
                self.make_move(PASS_MOVE)
            if move_candidates:
                move = random.choice(move_candidates)
            else:
                move = PASS_MOVE
            #check if heuristics is correct, if not, then we use normal move generation routine
            current_score = self.current_board.score_position()
            score_diff = -self.score_move(move) - current_score
            #0.001: because floating point m,ath is inaccurate
            if score_diff + 0.001 < normal_stone_value_ratio:
                if debug_flag:
                    print self.current_board
                    print move, score_diff
                move = self.select_scored_move(pass_allowed=False)
            if self.make_move(move):
                result.append(move)
            if move in move_candidates:
                move_candidates.remove(move)
        return result

    def final_status_list(self, status):
        """list blocks with given color and status
        """
        result_list = []
        self.current_board.analyze_unconditional_status()
        for block in self.current_board.iterate_blocks(WHITE+BLACK):
            if block.status==status:
                result_list.append(block.get_origin())
        return result_list

    def select_random_move(self):
        """return randomly selected move from all legal moves
        """
        return random.choice(self.list_moves())

    def select_random_no_eye_fill_move(self):
        """return randomly selected move from all legal moves but don't fill our own eyes
           not that this doesn't make difference between true 1 space eye and 1 space false eye
        """
        all_moves = []
        eye_moves = []
        capture_or_defence_moves = []
        make_eye_moves = []
        remove_liberty = []
        board = self.current_board
        for move in board.iterate_goban():
            if self.legal_move(move):
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]!=board.side:
                        all_moves.append(move)
                        break
                else:
                    eye_moves.append(move)
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]!=EMPTY and board.liberties(pos)==1:
                        capture_or_defence_moves.append(move)
                        break
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]==EMPTY:
                        for pos2 in board.iterate_neighbour(pos):
                            if pos2!=move and board.goban[pos2]!=board.side:
                                break
                        else:
                            make_eye_moves.append(move)
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]==other_side[board.side]:
                        for pos2 in board.iterate_neighbour(move):
                            if board.goban[pos2]==board.side:
                                remove_liberty.append(move)
                            break
                        break
        if capture_or_defence_moves:
            return random.choice(capture_or_defence_moves)
        if make_eye_moves:
            return random.choice(make_eye_moves)
        if remove_liberty:
            return random.choice(remove_liberty)
        if all_moves:
            return random.choice(all_moves)
        else:
            #if len(eye_moves)>=6:
            #    return random.choice(eye_moves)
            return PASS_MOVE
        

    def generate_move(self, remove_opponent_dead=False, pass_allowed=True):
        """generate move using scored move generator
        """
        #return self.select_random_move()
        return self.select_scored_move(remove_opponent_dead, pass_allowed)


def main():
    """Play game against itself on 5x5 board.
       Print all positions and moves made while playing.
    """
    #random.seed(1)
    size = 19
    g = Game(size)
    while True:
        move = g.generate_move()
        g.make_move(move)
        print move_as_string(move, g.size)
        print g.current_board
        print g.current_board.as_string_with_unconditional_status()
        print g.current_board.score_position()
        #import pdb; pdb.set_trace()
        #if last 2 moves are pass moves: exit loop
        #if len(g.move_history)==10:
        #    break
        if len(g.move_history)>=2 and \
           g.move_history[-1]==PASS_MOVE and \
           g.move_history[-2]==PASS_MOVE:
            break

if __name__=="__main__":
    #If this file is executed directly it will play game against itself.
    main()
