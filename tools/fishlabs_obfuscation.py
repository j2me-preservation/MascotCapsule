#!/usr/bin/env python3

# implements Fishlabs asset (de)obfuscation

import sys

def deobfuscate(data):
    length = len(data)

    data = bytearray(data)

    if length < 100:
        var5 = 10 + length % 10
    elif length < 200:
        var5 = 50 + length % 20
    elif length < 300:
        var5 = 80 + length % 20
    else:
        var5 = 100 + length % 50

    for i in range(var5):
        var7 = data[i]
        data[i] = data[length - i - 1]
        data[length - i - 1] = var7

    return bytes(data)

# deobfuscate if needed
def normalize(data, ext):
    if is_obfuscated(data, ext):
        return deobfuscate(data)
    else:
        return data

def is_obfuscated(data, ext):
    if ext.upper() == '.BMP':
        if data[-2:] == b'MB':
            return True
        elif data[0:2] == b'BM':
            return False
    elif ext.upper() == '.MBAC':
        if data[-2:] == b'BM':
            return True
        elif data[0:2] == b'MB':
            return False
    elif ext.upper() == '.PNG':
        if data[-4:] == b'GNP\x89':
            return True
        elif data[0:4] == b'\x89PNG':
            return False

    return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='(de)obfuscate Fishlabs game assets')
    parser.add_argument('file', nargs='+')
    args = parser.parse_args()

    for filename in args.file:
        with open(filename, 'rb+') as f:
            data = f.read()
            f.seek(0)
            f.write(deobfuscate(data))
