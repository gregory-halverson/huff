__author__ = 'Gregory'

import argparse
from queue import PriorityQueue
from bitarray import bitarray
from array import array
import struct

# output number of bytes as kb, mb, ...
def data_length_string(length):
    for magnitude in ['bytes', 'kb', 'mb', 'gb', 'tb']:
        if length < 1024:
            return "%3.1f %s" % (length, magnitude)
        else:
            length /= 1024

# Huffman tree to convert frequency table to code table
class HuffmanTree:
    # root initialized with frequency table
    # branches initialized with left, right, and probability
    # leaves initialized with symbol and probability
    def __init__(self, left=None, right=None, symbol=None, probability=None, frequency_table=None):
        self.left = left
        self.right = right
        self.symbol = symbol
        self.probability = probability

        if frequency_table is not None:
            self.from_frequencies(frequency_table)

    # make class comparable
    def __lt__(self, other):
        return self.probability < other.probability

    # build tree from frequency table
    def from_frequencies(self, frequencies):
        forest = PriorityQueue()

        # create a new tree for each symbol and add it to the forest
        for key in range(256):
            frequency = frequencies[key]
            tree = HuffmanTree(symbol=key, probability=frequency)
            forest.put(tree)

        # join the two lowest probability trees together until the forest is combined
        while forest.qsize() > 1:
            tree1 = forest.get()
            tree2 = forest.get()

            combined = HuffmanTree(left=tree1, right=tree2, probability=tree1.probability + tree2.probability)

            forest.put(combined)

        # copy combined tree
        tree = forest.get()
        self.left = tree.left
        self.right = tree.right
        self.probability = tree.probability

    # generate code table from tree
    def make_code_table(self):
        self.code_table = {}

        self.traverse(self, '')

        return self.code_table

    # recursively traverse tree to build code table
    def traverse(self, tree, path):
        if tree.symbol is not None:
            self.code_table[tree.symbol] = path
        else:
            if tree.left is not None:
                self.traverse(tree.left, path + '0')
            if tree.right is not None:
                self.traverse(tree.right, path + '1')

# parse argument list
def getargs():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest = 'command', help = 'command')
    subparsers.required = True

    encode_parser = subparsers.add_parser('encode', help = 'encode file to huff format')
    encode_parser.add_argument('filename', help = 'file to encode')
    encode_parser.add_argument('--output', help = 'name of output file')

    decode_parser = subparsers.add_parser('decode', help = 'decode file from huff format')
    decode_parser.add_argument('filename', help = 'file to decode')
    decode_parser.add_argument('--output', help = 'name of output file')

    arguments = parser.parse_args()

    return arguments

# count occurrence of each symbol
def analyze_counts(sequence):
    counts = [0 for i in range(256)]

    for byte in sequence:
        counts[byte] += 1

    return counts

# encode file into huffman file
def encode(filename, output_name):
    if output_name == None:
        output_name = filename + '.huff'

    print('encoding file \'' + filename + '\' to \'' + output_name + '\'')

    with open(filename, 'rb') as f:
        bytes = f.read()
        print('\'' + filename + '\' read, ' + data_length_string(len(bytes)))

    print('analyzing frequency distribution')
    counts = analyze_counts(bytes)

    print('building Huffman tree')
    tree = HuffmanTree(frequency_table = counts)

    print('building code table')
    code_table = tree.make_code_table()

    code = bitarray('')

    i = 0
    file_length = len(bytes)

    for byte in bytes:
        code_string = code_table[byte]
        code += bitarray(code_string)

        if (i % 1024 == 0):
            print('packing %2.1f%%' % (i / file_length * 100.0), end='\r')

        i += 1

    print('packing 100%')

    count_array = array('I')
    count_array.fromlist(counts)

    total = 0

    with open(output_name, 'wb') as f:
        key_bytes = count_array.tobytes()
        f.write(key_bytes)
        key_length = len(key_bytes)
        print('key written, ' + data_length_string(key_length))

        total += key_length
        data_bytes = code.tobytes()
        f.write(data_bytes)
        data_length = len(data_bytes)
        total += data_length
        print('data written, ' + data_length_string(data_length))

    print('\'' + output_name + '\' written, ' + data_length_string(total))
    print('file packed to %2.1f%% of original size' % (total / file_length * 100.0))

# decode huffman file to file
def decode(filename, output_name):
    if output_name == None:
        if filename.endswith('.huff'):
            output_name = filename[:-5]
        else:
            output_name = filename

    print('decoding file \'' + filename + '\' to \'' + output_name + '\'')

    with open(filename, 'rb') as f:
        key_bytes = f.read(4 * 256)
        print('key read, ' + data_length_string(len(key_bytes)))
        data_bytes = f.read()
        print('data read, ' + data_length_string(len(data_bytes)))

    count_array = array('I')
    count_array.frombytes(key_bytes)
    counts = count_array.tolist()

    tree = HuffmanTree()
    tree.from_frequencies(counts)

    code = bitarray()
    code.frombytes(data_bytes)

    node = tree
    output = bytes()

    i = 0
    code_length = len(code)

    for bit in code:
        if bit is True and node.right is not None:
            node = node.right
        elif bit is False and node.left is not None:
            node = node.left

        if node.symbol is not None:
            output += struct.pack('B', node.symbol)
            node = tree

        if (i % 1024 == 0):
            print('unpacking %2.1f%%' % (i / code_length * 100.0), end='\r')

        i += 1

    print('unpacking 100%')

    with open(output_name, 'wb') as f:
        f.write(output)
        print('\'' + output_name + '\' written, ' + data_length_string(len(output)))

# main function if called from command line
def main():
    arguments = getargs()

    command = arguments.command
    filename = arguments.filename
    output_name = arguments.output

    if command == 'encode':
        encode(filename, output_name)
    elif command == 'decode':
        decode(filename, output_name)

if __name__ == '__main__':
    main()