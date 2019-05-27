#!/usr/bin/env python3

import struct

def MTRA(f, verbose=False):
    (magic, version) = struct.unpack('2sH', f.read(4))

    if magic != b'MT':
        raise Exception('Not a MTRA file. Perhaps it needs to be deobfuscated first?')
    if version != 5:
        raise Exception('Unsupported MTRA version')

    num_actions, num_segments, tra_unk3, tra_unk4 = struct.unpack('<HH16sI', f.read(24))
    print('header', (num_actions, num_segments, tra_unk3, tra_unk4))

    for action in range(num_actions):
        print('action #', action)
        num_keyframes, = struct.unpack('<H', f.read(2))
        print(num_keyframes, 'keyframes')

        for segment in range(num_segments):
            type = ord(f.read(1))
            print(f'bone type {type}')
            if type == 0:
                print('    full matrix')
                for i in range(3):
                    print('        ', struct.unpack('<HHHH', f.read(8)))
            elif type == 1:
                print('    identity')
            elif type == 2:
                print('    animation')
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        translation', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        scale', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        rotation', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        roll', struct.unpack('<HH', f.read(4)))
            elif type == 4:
                print('    unknown4')
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown4_type1', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown4_type2', struct.unpack('<HH', f.read(4)))
            elif type == 5:
                print('    unknown5')
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown5', struct.unpack('<HHHH', f.read(8)))
            elif type == 6:
                print('    unknown6')
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown6_type1', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown6_type2', struct.unpack('<HHHH', f.read(8)))
                count, = struct.unpack('<H', f.read(2))
                for i in range(count):
                    print('        unknown6_type3', struct.unpack('<HH', f.read(4)))
            else:
                # TODO: handle types 3, 4, 5, 6 if they exist in the wild
                raise Exception()

        count, = struct.unpack('<H', f.read(2))
        for i in range(count):
            print('aux', struct.unpack('<HHH', f.read(6)))

    # MT trailer
    for i in range(2):
        key = struct.unpack('BB', f.read(2))

        print('key: %02X%02X' % key)

        for word_index in range(4):
            word = [None, None]

            for byte_index in range(2):
                encrypted_byte = ord(f.read(1))
                word[byte_index] = ((encrypted_byte ^ key[byte_index]) + 127) & 0xff

            print('%02X%02X "%c%c"' % tuple(word + word))

    end_at = f.tell()
    f.seek(0, 2)
    file_end = f.tell()

    if file_end > end_at:
        print('WARNING: %d uninterpreted bytes in file' % (file_end - end_at))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='dump MTRA file')
    parser.add_argument('mtrafile')
    args = parser.parse_args()

    with open(args.mtrafile, 'rb') as f:
        MTRA(f, True)
