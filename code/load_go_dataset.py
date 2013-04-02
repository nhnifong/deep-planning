from __future__ import division
import os
import numpy
import smhasher
# murmur3 has low collisions and high randomness for numbers.
from pprint import pprint
from partialload import *

def mh(x):
    return smhasher.murmur3_x86_128(str(x))

def randomize_chunks(data_dir, output_dir):
    """ uses the a nicely random hash and external merge sort to randomize the dataset while
        staying in memory and divide it into training / test / validation sets and storing
        files no larger than output chunk size which is measured in bytes.
        
        Expects output_dir to contain the subdirs train, test, valid
    """
    shapes = eval(open(os.path.join(data_dir, 'shapes')).read())
    shapes = sorted(shapes.items(),key=lambda k: k[0])

    offset = 0
    counter = 0
    
    outshapes = open(os.path.join(output_dir, 'temp', 'shapes'), 'w')

    for fname,shape in shapes:
        fpath = os.path.join(data_dir, fname)
        print fpath
        nn = numpy.fromfile(fpath)
        nn.shape = shape
        nn = nn.astype(numpy.float16)
        indices = [x-offset for x in sorted(range(offset, offset+len(nn)), key=mh)]
        offset += len(nn)
        nn = nn.take(indices, axis=0)
        outname = 'arr_%i.npy' % counter
        numpy.save(os.path.join(output_dir, 'temp', outname), nn)
        counter +=1
        outshapes.write('%s %i\n' % (outname, len(nn)))
        del nn

    outshapes.close()

def merge_chunks(data_dir, output_file_size=536870912, test_ratio=0.2):

    class Chunk:
        def __init__(self, fname, size, offset):
            self.fname = fname
            self.size = size
            self.offset = offset
            self.fpath = os.path.join(data_dir,'temp', self.fname)
            self.read_index = 0 
            self.nexthash = mh(self.read_index + self.offset)
            self.readup()

        def readup(self):
            self.arr = read_npy_chunk(self.fpath,
                                      self.read_index,
                                      min(1000, (self.size-self.read_index)))
            self.read_began = self.read_index
            self.next_read = self.read_index + 1000

        def next(self):
            result = self.arr[self.read_index - self.read_began]
            self.read_index += 1
            if self.read_index >= self.size:
                self.nexthash = None
            else:
                self.nexthash = mh(self.read_index + self.offset)
                if self.read_index >= self.next_read:
                    self.readup()
            return result


    chunks = []
    offset = 0
    for line in open(os.path.join(data_dir,'temp','shapes')).read().split('\n'):
        if line=='': continue
        spl = line.split()
        ch = Chunk( str(spl[0]), int(spl[1]), offset )
        offset += ch.size
        chunks.append(ch)

    # caculate size of resulting datsets
    total = sum([ch.size for ch in chunks])
    train_size = total - int(total * test_ratio)
    t_v = (total - train_size)
    test_size = t_v - int(t_v * test_ratio)
    validation_size = t_v - test_size
    assert (train_size + test_size + validation_size) == total
    print ''
    print "%i total records" % total
    print "Training set size: %i" % train_size
    print "Testing set size: %i" % test_size
    print "Validation set size: %i" % validation_size
    
    class Output_Manager:
        def __init__(self, datasets):
            max_records = output_file_size // (363*2)
            self.outfiles = []
            for set_name, set_size in datasets:
                togo = set_size
                counter = 0
                while togo > 0:
                    outsize = min(togo, max_records)
                    outpath = os.path.join(data_dir, set_name,"arr_%i.npy"%counter)
                    self.outfiles.append((outpath,outsize))
                    counter += 1
                    togo -= max_records
            self.file_index = 0
            self.record_index = 0
            self.outarray = numpy.zeros(shape=(self.outfiles[self.file_index][1],363), dtype=numpy.float16)

        def write_next(self, vec):
            # if record index has reached size of current output,
            if self.record_index >= self.outfiles[self.file_index][1]:
                # flush output
                print "Saving %s..." % self.outfiles[self.file_index][0]
                numpy.save(self.outfiles[self.file_index][0], self.outarray)
                self.file_index += 1
                self.record_index = 0
                # begin next out array
                self.outarray = numpy.zeros(shape=(self.outfiles[self.file_index][1],363), dtype=numpy.float16)
            # write the record to the current out array
            self.outarray[self.record_index] = vec
            self.record_index += 1

    om = Output_Manager([('train',train_size),('test',test_size),('valid',validation_size)])

    print " begin merging files"
    while len(chunks)>0:
        # take murmur hash of current index of each chunk
        minchunk = min(chunks, key=lambda k: k.nexthash)
        # take the next vector from the chunk with the lowest next hash and write that vector with the output manager
        om.write_next( minchunk.next() )
        # remove dead
        if minchunk.nexthash is None:
            chunks.remove(minchunk)
            print "A chunk was finished and removed. %i remain" % (len(chunks))

def load_data(dataset="/media/foundation/GoMoves/randomized/"):
    def shared_dataset(data_xy, borrow=True):
        data_x, data_y = data_xy
        shared_x = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        shared_y = theano.shared(numpy.asarray(data_y,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        return shared_x, T.cast(shared_y, 'int32')


    test_set_x, test_set_y = shared_dataset(test_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    train_set_x, train_set_y = shared_dataset(train_set)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval




if __name__ == "__main__":
    #randomize_chunks( '/media/foundation/GoMoves/sorted',
    #                  '/media/foundation/GoMoves/randomized')
    
    #merge_chunks('/media/foundation/GoMoves/randomized')
