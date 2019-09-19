import math
import struct

MAGNITUDE_8BIT   = 0
MAGNITUDE_10BIT  = 1
MAGNITUDE_13BIT  = 2
MAGNITUDE_16BIT  = 3

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

def unpackvertices_f2(unp):
    header = unp.unpackbits(8)
    magnitude = header >> 6
    count = (header & 0x3F) + 1

    #print('packed vertices: magnitude=%d, count=%d' % (magnitude, count))

    print_vertices = False
    vertices = []

    if magnitude == MAGNITUDE_8BIT:
        for i in range(count):
            x = unp.unpackbits_signed(8)
            y = unp.unpackbits_signed(8)
            z = unp.unpackbits_signed(8)
            if print_vertices: print('  vert', x, y, z)

            vertices += [(x, y, z)]
    elif magnitude == MAGNITUDE_10BIT:
        for i in range(count):
            x = unp.unpackbits_signed(10)
            y = unp.unpackbits_signed(10)
            z = unp.unpackbits_signed(10)
            if print_vertices: print('  vert', x, y, z)

            vertices += [(x, y, z)]
    elif magnitude == MAGNITUDE_13BIT:
        for i in range(count):
            x = unp.unpackbits_signed(13)
            y = unp.unpackbits_signed(13)
            z = unp.unpackbits_signed(13)
            if print_vertices: print('  vert', x, y, z)

            vertices += [(x, y, z)]
    elif magnitude == MAGNITUDE_16BIT:
        for i in range(count):
            x = unp.unpackbits_signed(16)
            y = unp.unpackbits_signed(16)
            z = unp.unpackbits_signed(16)
            if print_vertices: print('  vert', x, y, z)

            vertices += [(x, y, z)]
    else:
        raise Exception('invalid magnitude')

    return vertices

def unpacknormals_f2(unp):
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

class Figure:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.bones = []

    @staticmethod
    def fromfile(*args, **kwargs):
        figure = Figure()
        figure.load(*args, **kwargs)
        return figure

    def load(self, f, verbose=False):
        (magic, version) = struct.unpack('HH', f.read(4))

        if magic != 0x424D:
            raise Exception('Not a MBAC file')
        if version != 5:
            raise Exception('Unsupported MBAC version')

        (vertexformat, normalformat, polygonformat, boneformat) = struct.unpack('BBBB', f.read(4))
        print('magic=%04Xh version=%d vertexformat=%d normalformat=%d polygonformat=%d boneformat=%d' % (
                magic, version, vertexformat, normalformat, polygonformat, boneformat))

        (num_vertices, num_polyt3, num_polyt4, num_bones) = struct.unpack('HHHH', f.read(8))
        print('num_vertices=%d num_polyt3=%d num_polyt4=%d num_bones=%d' % (
                num_vertices, num_polyt3, num_polyt4, num_bones))


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

        # decode vertices
        if vertexformat != 2:
            raise Exception('Unsupported vertexformat. Please report this bug.')

        unp = Unpacker(f)

        while len(self.vertices) < num_vertices:
            self.vertices += unpackvertices_f2(unp)

        if len(self.vertices) != num_vertices:
            print('WARNING: unpacked', len(self.vertices), 'vertices')

        #print('tell:', f.tell())

        # decode normals
        if normalformat:
            if normalformat != 2:
                raise Exception('Unsupported normalformat. Please report this bug.')

            unp = Unpacker(f)

            have_normals = 0
            while have_normals < num_vertices:
                have_normals += unpacknormals_f2(unp)

        # decode polygons
        if polygonformat != 3:
            raise Exception('Unsupported polygonformat. Please report this bug.')

        #print('tell:', f.tell())

        unp = Unpacker(f)

        # expect 0x07 now
        #if f.read(1) != b'\x07':
        #   raise Exception('Unexpected encoding mode. Please report this bug.')

        if num_polyf3 + num_polyf4 > 0:
            unknown_bits = unp.unpackbits(8)
            vertex_index_bits = unp.unpackbits(8)
            color_bits = unp.unpackbits(8)
            color_id_bits = unp.unpackbits(8)
            unp.unpackbits(8)

            for i in range(num_color):
                r = unp.unpackbits(color_bits)
                g = unp.unpackbits(color_bits)
                b = unp.unpackbits(color_bits)

            for i in range(num_polyf3):
                unknown = unp.unpackbits(unknown_bits)
                a = unp.unpackbits(vertex_index_bits)
                b = unp.unpackbits(vertex_index_bits)
                c = unp.unpackbits(vertex_index_bits)

                color_id = unp.unpackbits(color_id_bits)

                if verbose:
                    print('unknown=%d a=%d b=%d c=%d color_id=%d' % (
                        unknown, a, b, c, color_id))
                self.faces.append((a, b, c))

            for i in range(num_polyf4):
                unknown = unp.unpackbits(unknown_bits)
                a = unp.unpackbits(vertex_index_bits)
                b = unp.unpackbits(vertex_index_bits)
                c = unp.unpackbits(vertex_index_bits)
                d = unp.unpackbits(vertex_index_bits)

                color_id = unp.unpackbits(color_id_bits)

                if verbose:
                    print('unknown=%d a=%d b=%d c=%d d=%d color_id=%d' % (
                        unknown, a, b, c, d, color_id))
                self.faces.append((a, b, c, d))

        if num_polyt3 + num_polyt4 > 0:
            unknown_bits = unp.unpackbits(8)
            vertex_index_bits = unp.unpackbits(8)
            uv_bits = unp.unpackbits(8)
            somedata = unp.unpackbits(8)

            print('POLYGONFORMAT 3: unknown_bits=%d vertex_index_bits=%d uv_bits=%d somedata=%d' % (
                unknown_bits, vertex_index_bits, uv_bits, somedata))

            if unknown_bits > 8:
                raise Exception('Format error. Please report this bug.')

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

                if verbose:
                    print('unknown=%d a=%d b=%d c=%d (%d %d) (%d %d) (%d %d)' % (
                        unknown, a, b, c, u1, v1, u2, v2, u3, v3))
                #max_index = max(max_index, a, b, c)

                self.faces.append((a, b, c, u1, v1, u2, v2, u3, v3))

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

                if verbose:
                    print('unknown=%d a=%d b=%d c=%d d=%d (%d %d) (%d %d) (%d %d) (%d %d)' % (
                        unknown, a, b, c, d, u1, v1, u2, v2, u3, v3, u4, v4))
                #max_index = max(max_index, a, b, c, d)

                self.faces.append((a, b, c, d, u1, v1, u2, v2, u3, v3, u4, v4))

        # decode bones
        bone_vertices_sum = 0
        have_root = False

        for i in range(num_bones):
            print('bone #', i)
            (bone_vertices, parent) = struct.unpack('Hh', f.read(4))
            print('\tbone_vertices=%d parent=%d' % (bone_vertices, parent))

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

            mtx = (m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23)
            mtx_parent = self.get_parent_matrix(parent)
            mtx_res = self.mult_matrix(mtx_parent, mtx)
            self.bones.append((parent, mtx_res, bone_vertices_sum, bone_vertices_sum + bone_vertices))

            bone_vertices_sum += bone_vertices

        if bone_vertices_sum != num_vertices:
            raise Exception('Format error (bone_vertices_sum). Please report this bug.')

        # apply bone transformations
        for i, (parent, mtx, start, end) in enumerate(self.bones):
            # apply transformation to vertices
            for i in range(start, end):
                x, y, z = self.vertices[i]
                m = mtx
                self.vertices[i] = ((m[ 0] * x + m[ 1] * y + m[ 2] * z) // 4096 + m[ 3],
                                    (m[ 4] * x + m[ 5] * y + m[ 6] * z) // 4096 + m[ 7],
                                    (m[ 8] * x + m[ 9] * y + m[10] * z) // 4096 + m[11])

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

    def get_parent_matrix(self, parent):
        if parent < 0:
            parent_mtx = (4096, 0, 0, 0,
                          0, 4096, 0, 0,
                          0, 0, 4096, 0)
        else:
            assert parent < len(self.bones)
            parent_mtx = self.bones[parent][1]

        return parent_mtx

    def mult_matrix(self, a, b):
        m00 = (a[0] * b[0] + a[1] * b[4] + a[2] * b[8]) / 4096
        m01 = (a[0] * b[1] + a[1] * b[5] + a[2] * b[9]) / 4096
        m02 = (a[0] * b[2] + a[1] * b[6] + a[2] * b[10]) / 4096
        m03 = (a[0] * b[3] + a[1] * b[7] + a[2] * b[11]) / 4096 + a[3]

        m10 = (a[4] * b[0] + a[5] * b[4] + a[6] * b[8]) / 4096
        m11 = (a[4] * b[1] + a[5] * b[5] + a[6] * b[9]) / 4096
        m12 = (a[4] * b[2] + a[5] * b[6] + a[6] * b[10]) / 4096
        m13 = (a[4] * b[3] + a[5] * b[7] + a[6] * b[11]) / 4096 + a[7]

        m20 = (a[8] * b[0] + a[9] * b[4] + a[10] * b[8]) / 4096
        m21 = (a[8] * b[1] + a[9] * b[5] + a[10] * b[9]) / 4096
        m22 = (a[8] * b[2] + a[9] * b[6] + a[10] * b[10]) / 4096
        m23 = (a[8] * b[3] + a[9] * b[7] + a[10] * b[11]) / 4096 + a[11]

        return (m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23)
