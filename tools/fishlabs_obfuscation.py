# implements Fishlabs asset (de)obfuscation

import sys

def fishlabs_deobfuscate(data):
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

if __name__ == "__main__":
    with open(sys.argv[1], 'rb+') as f:
        data = f.read()
        f.seek(0)
        f.write(fishlabs_deobfuscate(data))
