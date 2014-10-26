from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='huff',
    version='0.1',
    packages=['bitarray'],
    url='',
    license='GPL',
    author='Gregory H. Halverson',
    author_email='gregory.halverson@gmail.com',
    description='Encode and decode files into Huffman coding format'
)
