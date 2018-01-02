# MBAC to OBJ converter (stand-alone / importable)
# todo: do we really want to use this garbage format? PLY is a thing.

import math
import struct
import sys

MAGNITUDE_8BIT   = 0
MAGNITUDE_10BIT  = 1
MAGNITUDE_13BIT  = 2
MAGNITUDE_16BIT  = 3

class VertexSink:
    def __init__(self, f):
        self.f = f

    def sink(self, x, y, z):
        print('v %d %d %d' % (x, y, z), file=self.f)

    def normal(self, x, y, z):
        print('n %d %d %d' % (x, t, z), file=self.f)

    def triangle(self, a, b, c):
        print('f %d %d %d' % (1+a, 1+b, 1+c), file=self.f)

class Unpacker:
    def __init__(self, f):
        self.f = f
        self.havebits = 0
        self.data = 0

    def unpackbits(self, nbits):
        while nbits > self.havebits:
            self.addbits()

        bits = self.data & ((1 << nbits) - 1)
        self.havebits -= nbits
        self.data >>= nbits
        return bits

    def unpackbits_signed(self, nbits):
        value = self.unpackbits(nbits)
        sign = value & (1 << (nbits - 1))

        if sign:
            value -= (1 << nbits)

        return value

    def addbits(self):
        self.data |= ord(self.f.read(1)) << self.havebits
        self.havebits += 8

def unpackvertices_f2(unp, vs):
    have_vertices = 0

    header = unp.unpackbits(8)
    magnitude = header >> 6
    count = (header & 0x3F) + 1

    #print('packed vertices: magnitude=%d, count=%d' % (magnitude, count))

    print_vertices = False

    if magnitude == MAGNITUDE_8BIT:
        for i in range(count):
            x = unp.unpackbits_signed(8)
            y = unp.unpackbits_signed(8)
            z = unp.unpackbits_signed(8)
            if print_vertices: print('  vert', x, y, z)
            vs.sink(x, y, z)
            have_vertices += 1
    elif magnitude == MAGNITUDE_10BIT:
        for i in range(count):
            x = unp.unpackbits_signed(10)
            y = unp.unpackbits_signed(10)
            z = unp.unpackbits_signed(10)
            if print_vertices: print('  vert', x, y, z)
            vs.sink(x, y, z)
            have_vertices += 1
    elif magnitude == MAGNITUDE_13BIT:
        for i in range(count):
            x = unp.unpackbits_signed(13)
            y = unp.unpackbits_signed(13)
            z = unp.unpackbits_signed(13)
            if print_vertices: print('  vert', x, y, z)
            vs.sink(x, y, z)
            have_vertices += 1
    elif magnitude == MAGNITUDE_16BIT:
        for i in range(count):
            x = unp.unpackbits_signed(16)
            y = unp.unpackbits_signed(16)
            z = unp.unpackbits_signed(16)
            if print_vertices: print('  vert', x, y, z)
            vs.sink(x, y, z)
            have_vertices += 1
    else:
        raise Exception('invalid magnitude')

    return have_vertices

def unpacknormals_f2(unp, vs):
    x = unp.unpackbits_signed(7)

    print_normals = False

    if x == -64:
        direction = unp.unpackbits(3)
        if print_normals: print('  direction', direction)
    else:
        x = x / 64
        y = unp.unpackbits_signed(7) / 64
        z_negative = unp.unpackbits(1)
        #print(x, y, z_negative, 1 - x * x - y * y)

        if 1 - x * x - y * y >= 0:
            z = math.sqrt(1 - x * x - y * y) * (-1 if z_negative else 1)
        else:
            # what
            z = 0

        if print_normals: print('  norm', x, y, z)

    return 1

def MBAC_to_obj(f, obj):
    (magic, version) = struct.unpack('HH', f.read(4))

    if magic != 0x424D:
        raise Exception('Not a MBAC file')
    if version != 5:
        raise Exception('Unsupported MBAC version')

    (vertexformat, normalformat, polygonformat, segmentformat) = struct.unpack('BBBB', f.read(4))
    print('magic=%04Xh version=%d vertexformat=%d normalformat=%d polygonformat=%d segmentformat=%d' % (
            magic, version, vertexformat, normalformat, polygonformat, segmentformat))

    (num_vertices, num_polyt3, num_polyt4, num_segments) = struct.unpack('HHHH', f.read(8))
    print('num_vertices=%d num_polyt3=%d num_polyt4=%d num_segments=%d' % (
            num_vertices, num_polyt3, num_polyt4, num_segments))


    # unsure about matcnt
    if polygonformat != 3:
        raise Exception('Unsupported polygonformat. Please report this bug.')

    (num_polyf3, num_polyf4, matcnt, unk21, num_color) = struct.unpack('HHHHH', f.read(10))
    print('num_polyf3=%d num_polyf4=%d matcnt=%d unk21=%d num_color=%d' % (
            num_polyf3, num_polyf4, matcnt, unk21, num_color))

    for i in range(unk21):
        (unk1, unk2) = struct.unpack('HH', f.read(4))
        print('#%d unk1=%d unk2=%d' % (i, unk1, unk2))

        for j in range(matcnt):
            (unk3, unk4) = struct.unpack('HH', f.read(4))
            print('\tunk3=%d unk4=%d' % (unk3, unk4))

    vs = VertexSink(obj)

    # decode vertices
    if vertexformat != 2:
        raise Exception('Unsupported vertexformat. Please report this bug.')

    unp = Unpacker(f)

    have_vertices = 0
    while have_vertices < num_vertices:
        have_vertices += unpackvertices_f2(unp, vs)

    if have_vertices != num_vertices:
        print('WARNING: unpacked', have_vertices, 'vertices')

    #print('tell:', f.tell())

    # decode normals
    if normalformat:
        if normalformat != 2:
            raise Exception('Unsupported normalformat. Please report this bug.')

        unp = Unpacker(f)

        have_normals = 0
        while have_normals < num_vertices:
            have_normals += unpacknormals_f2(unp, vs)

    # decode polygons
    if polygonformat != 3:
        raise Exception('Unsupported polygonformat. Please report this bug.')

    if num_polyf3 + num_polyf4 > 0:
        raise Exception('F-type polygons not supported. Please report this bug.')

    #print('tell:', f.tell())

    unp = Unpacker(f)

    # expect 0x07 now
    #if f.read(1) != b'\x07':
    #   raise Exception('Unexpected encoding mode. Please report this bug.')

    unknown_bits = unp.unpackbits(8)
    vertex_index_bits = unp.unpackbits(8)
    uv_bits = unp.unpackbits(8)
    somedata = unp.unpackbits(8)

    print('POLYGONFORMAT 3: unknown_bits=%d vertex_index_bits=%d uv_bits=%d somedata=%d' % (
            unknown_bits, vertex_index_bits, uv_bits, somedata))

    if unknown_bits > 8:
        raise Exception('Format error. Please report this bug.')

    print_faces = False

    #max_index = 0
    for i in range(num_polyt3):
        unknown = unp.unpackbits(unknown_bits)
        a = unp.unpackbits(vertex_index_bits)
        b = unp.unpackbits(vertex_index_bits)
        c = unp.unpackbits(vertex_index_bits)

        u1 = unp.unpackbits(uv_bits)
        v1 = unp.unpackbits(uv_bits)
        u2 = unp.unpackbits(uv_bits)
        v2 = unp.unpackbits(uv_bits)
        u3 = unp.unpackbits(uv_bits)
        v3 = unp.unpackbits(uv_bits)

        if print_faces:
            print('unknown=%d a=%d b=%d c=%d (%d %d) (%d %d) (%d %d)' % (
                    unknown, a, b, c, u1, v1, u2, v2, u3, v3))
        #max_index = max(max_index, a, b, c)

        vs.triangle(a, b, c)

    #max_index = 0
    for i in range(num_polyt4):
        unknown = unp.unpackbits(unknown_bits)
        a = unp.unpackbits(vertex_index_bits)
        b = unp.unpackbits(vertex_index_bits)
        c = unp.unpackbits(vertex_index_bits)
        d = unp.unpackbits(vertex_index_bits)

        u1 = unp.unpackbits(uv_bits)
        v1 = unp.unpackbits(uv_bits)
        u2 = unp.unpackbits(uv_bits)
        v2 = unp.unpackbits(uv_bits)
        u3 = unp.unpackbits(uv_bits)
        v3 = unp.unpackbits(uv_bits)
        u4 = unp.unpackbits(uv_bits)
        v4 = unp.unpackbits(uv_bits)

        if print_faces:
            print('unknown=%d a=%d b=%d c=%d d=%d (%d %d) (%d %d) (%d %d) (%d %d)' % (
                    unknown, a, b, c, d, u1, v1, u2, v2, u3, v3, u4, v4))
        #max_index = max(max_index, a, b, c, d)

    # decode segments
    seg_vertices_sum = 0
    have_root = False

    for i in range(num_segments):
        print('segment #', i)
        (seg_vertices, parent) = struct.unpack('Hh', f.read(4))
        print('\tseg_vertices=%d parent=%d' % (seg_vertices, parent))

        (m00, m01, m02, m03) = struct.unpack('hhhh', f.read(8))
        (m10, m11, m12, m13) = struct.unpack('hhhh', f.read(8))
        (m20, m21, m22, m23) = struct.unpack('hhhh', f.read(8))

        print('\tmtx = [%d\t%d\t%d\t%d]' % (m00, m01, m02, m03))
        print('\t      [%d\t%d\t%d\t%d]' % (m10, m11, m12, m13))
        print('\t      [%d\t%d\t%d\t%d]' % (m20, m21, m22, m23))

        if parent == -1:
            if have_root:
                raise Exception('Format error (multiple roots). Please report this bug.')
        elif parent < 0:
            raise Exception('Format error (negative parent). Please report this bug.')

        seg_vertices_sum += seg_vertices

    if seg_vertices_sum != num_vertices:
        raise Exception('Format error (seg_vertices_sum). Please report this bug.')

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
    f.seek(0,2)
    file_end = f.tell()

    if file_end > end_at:
        print('WARNING: %d uninterpreted bytes in file' % (file_end - end_at))

if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as f:
        with open('vertexdump.obj', 'wt') as obj:
            MBAC_to_obj(f, obj)
