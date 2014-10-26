__author__ = 'Gregory'

import argparse
from queue import PriorityQueue

class HuffmanTree:
    def __init__(self, left = None, right = None, symbol = None, probability = None, frequency_table = None):
        self.left = left
        self.right = right
        self.symbol = symbol
        self.probability = probability

        if frequency_table != None:
            self.from_frequencies(frequency_table)

    def __lt__(self, other):
        return self.probability < other.probability

    def from_frequencies(self, frequencies):
        forest = PriorityQueue()

        for key in frequencies:
            frequency = frequencies[key]
            tree = HuffmanTree(symbol=key, probability=frequency)
            forest.put(tree)

        while forest.qsize() > 1:
            tree1 = forest.get()
            tree2 = forest.get()

            combined = HuffmanTree(left=tree1, right=tree2, probability=tree1.probability + tree2.probability)

            forest.put(combined)

        tree = forest.get()
        self.left = tree.left
        self.right = tree.right
        self.probability = tree.probability

    def make_code_table(self):
        self.code_table = {}

        self.traverse(self, '')

        return self.code_table

    def traverse(self, tree, path):
        if tree.symbol is not None:
            self.code_table[tree.symbol] = path
        else:
            if tree.left is not None:
                self.traverse(tree.left, path + '0')
            if tree.right is not None:
                self.traverse(tree.right, path + '1')

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

def analyze_counts(string):
    counts = {}

    for character in string:
        if character in counts:
            counts[character] += 1
        else:
            counts[character] = 1

    return counts

def analyze_frequencies(string):
    frequencies = {}

    counts = analyze_counts(string)

    for key in counts:
        frequencies[key] = counts[key] / len(string)

    return frequencies

def encode(filename, output_name):
    if output_name == None:
        output_name = filename + '.huff'

    print('encoding file \'' + filename + '\' to \'' + output_name + '\'')

    with open(filename, 'r') as f:
        string = f.read()

    frequencies = analyze_frequencies(string)

    tree = HuffmanTree(frequency_table = frequencies)

    code_table = tree.make_code_table()

    order = sorted(frequencies, key = frequencies.__getitem__, reverse = True)

    for key in order:
        print(key + ': ' + code_table[key])

def decode(filename, output_name):
    if output_name == None:
        if filename.endswith('.huff'):
            output_name = filename[:-5]
        else:
            output_name = filename

    print('decoding file \'' + filename + '\' to \'' + output_name + '\'')

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