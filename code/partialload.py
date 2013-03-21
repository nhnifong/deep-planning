"""
Example of how to read a partial NumPy array stored in NPY
format off of disk.
"""
__author__ = "David Warde-Farley"
__copyright__ = "Copyright (c) 2012 by " + __author__
__license__ = "3-clause BSD"
__email__ = "dwf@dwf.name"

import struct
import numpy

def read_npy_chunk(filename, start_row, num_rows):
    """
    Reads a partial array (contiguous chunk along the first
    axis) from an NPY file.

    Parameters
    ----------
    filename : str
        Name/path of the file from which to read.
    start_row : int
        The first row of the chunk you wish to read. Must be
        less than the number of rows (elements along the first
        axis) in the file.
    num_rows : int
        The number of rows you wish to read. The total of
        `start_row + num_rows` must be less than the number of
        rows (elements along the first axis) in the file.

    Returns
    -------
    out : ndarray
        Array with `out.shape[0] == num_rows`, equivalent to
        `arr[start_row:start_row + num_rows]` if `arr` were
        the entire array (note that the entire array is never
        loaded into memory by this function).
    """
    assert start_row >= 0 and num_rows > 0
    with open(filename, 'rb') as fhandle:
        major, minor = numpy.lib.format.read_magic(fhandle)
        shape, fortran, dtype = numpy.lib.format.read_array_header_1_0(fhandle)
        assert not fortran, "Fortran order arrays not supported"
        # Make sure the offsets aren't invalid.
        assert start_row < shape[0], (
            'start_row is beyond end of file'
        )
        assert start_row + num_rows <= shape[0], (
            'start_row + num_rows > shape[0]'
        )
        # Get the number of elements in one 'row' by taking
        # a product over all other dimensions.
        row_size = numpy.prod(shape[1:])
        start_byte = start_row * row_size * dtype.itemsize
        fhandle.seek(start_byte, 1)
        n_items = row_size * num_rows
        flat = numpy.fromfile(fhandle, count=n_items, dtype=dtype)
        return flat.reshape((-1,) + shape[1:])


def read_npy_chunk_demo_unsafe(filename, start_row, num_rows):
    """
    Reads a partial array (contiguous chunk along the first
    axis) from an NPY file (not using `numpy.lib.format` functions,
    for demonstration purposes).

    Parameters
    ----------
    filename : str
        Name/path of the file from which to read.
    start_row : int
        The first row of the chunk you wish to read. Must be
        less than the number of rows (elements along the first
        axis) in the file.
    num_rows : int
        The number of rows you wish to read. The total of
        `start_row + num_rows` must be less than the number of
        rows (elements along the first axis) in the file.

    Returns
    -------
    out : ndarray
        Array with `out.shape[0] == num_rows`, equivalent to
        `arr[start_row:start_row + num_rows]` if `arr` were
        the entire array (note that the entire array is never
        loaded into memory by this function).

    Notes
    -----
    WARNING: This function calls eval() on a data loaded from
    disk and thus should NOT be considered secure. Only load
    NPY files you trust, or replace the call to eval() with a
    suitable safe parsing function (the three properties, 'descr',
    'fortran_order' and 'shape' always come in alphabetical order
    which should make it easier).
    """
    assert start_row >= 0 and num_rows > 0
    with open(filename, 'rb') as fhandle:
        # Format specifier garbage.
        magic = fhandle.read(6)
        assert magic == '\x93NUMPY', 'invalid file'
        version = fhandle.read(1)
        assert version == '\x01', 'only version 1 NPY files supported'
        # Get the header length as a 2-byte short int.
        header_len = struct.unpack('>H', fhandle.read(2))[0]
        # Read +1 for the null byte.
        header_text = fhandle.read(header_len + 1)
        # WARNING: Obviously, NEVER use eval() if security is a concern.
        # This is a vector for *literally* arbitrary code execution. 
        header = eval(header_text.replace('\x00', ' '))
        assert not header['fortran_order'], "Fortran order arrays not supported"
        # Coerce the dtype specifier string to a dtype object.
        dtype = numpy.dtype(header['descr'])
        # Make sure the offsets aren't invalid.
        assert start_row < header['shape'][0], (
            'start_row is beyond end of file'
        )
        assert start_row + num_rows <= header['shape'][0], (
            'start_row + num_rows > shape[0]'
        )
        # Get the number of elements in one 'row' by taking
        # a product over all other dimensions.
        row_size = numpy.prod(header['shape'][1:])
        start_byte = start_row * row_size * dtype.itemsize
        fhandle.seek(start_byte, 1)
        n_items = row_size * num_rows
        flat = numpy.fromfile(fhandle, count=n_items, dtype=dtype)
        return flat.reshape((-1,) + header['shape'][1:])