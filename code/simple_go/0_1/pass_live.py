import sys
import simple_go

start_no = long(sys.argv[1])
end_no = long(sys.argv[2])

fp = open("pass_live.log", "w")
size = 6
limit = 12
bits = size**2

print "Running with size %i with stone limit at %i" % (size, limit)
print "from position %s to position %s" % (start_no, end_no)
print "Result to screen and to pass_live.log"

def create_board(size):
    simple_board = []
    for y in range(size):
        simple_board.append([0]*size)
    return simple_board

def iterate_bit_goban(no, bits=bits):
    x = 1
    y = 1
    for i in xrange(bits):
        if (1L<<i) & no:
            yield x,y
        x += 1
        if x>size:
            x = 1
            y += 1

def ref1(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-x][y]

def ref2(b2, b1, x, y, size=size):
    b2[x][y] = b1[x][size-1-y]

def ref3(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-x][size-1-y]

def ref4(b2, b1, x, y, size=size):
    b2[x][y] = b1[y][x]

def ref5(b2, b1, x, y, size=size):
    b2[x][y] = b1[y][size-1-x]

def ref6(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-y][x]

def ref7(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-y][size-1-x]


simple_board2 = create_board(size)
no = start_no
while no<=end_no and no<2**bits:
    bit_count = 0
    for i in xrange(bits):
        if (1L<<i) & no:
            bit_count += 1
    if no%100==0:
        sys.stderr.write("%i\r" % no)
    if bit_count<=limit:
        simple_board = create_board(size)
        for x,y in iterate_bit_goban(no):
            simple_board[x-1][y-1] = 1
        for reflection_function in ref1, ref2, ref3, ref4, ref5, ref6, ref7:
            for x in range(size):
                for y in range(size):
                    reflection_function(simple_board2, simple_board, x, y)
            if simple_board2 < simple_board:
                break
        else:
            b = simple_go.Board(size)
            for x,y in iterate_bit_goban(no):
                b.add_stone(simple_go.BLACK, (x, y))
            if b.unconditional_score(simple_go.BLACK)==size**2:
                fp.write("%i: %i\n" % (no, bit_count))
                fp.write(str(b))
                fp.write("\n")
                fp.flush()
                print no, bit_count
                print b
    no = no + 1

fp.close()
