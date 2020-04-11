#!/usr/bin/env python3

# MBAC to OBJ converter (stand-alone / importable)
# todo: do we really want to use this garbage format? PLY is a thing.

from mascotcapsule import Figure

def fixup_index(index):
    if index >= 0:
        return 1 + index
    else:
        return index

class VertexSink:
    def __init__(self, f):
        self.f = f

    def sink(self, x, y, z):
        print('v %d %d %d' % (x, y, z), file=self.f)

    def normal(self, x, y, z):
        print('n %d %d %d' % (x, t, z), file=self.f)

    def texcoord(self, u, v):
        print(f'vt {u/255} {1 - v/255}', file=self.f)

    def quad_vt(self, v1, v2, v3, v4, vt1, vt2, vt3, vt4):
        v1, v2, v3, v4, vt1, vt2, vt3, vt4 = [fixup_index(i) for i in (v1, v2, v3, v4, vt1, vt2, vt3, vt4)]
        print(f'f {v1}/{vt1} {v2}/{vt2} {v3}/{vt3} {v4}/{vt4}', file=self.f)

    def triangle_vt(self, v1, v2, v3, vt1, vt2, vt3):
        v1, v2, v3, vt1, vt2, vt3 = [fixup_index(i) for i in (v1, v2, v3, vt1, vt2, vt3)]
        print(f'f {v1}/{vt1} {v2}/{vt2} {v3}/{vt3}', file=self.f)

def MBAC_to_obj(f, obj, verbose=False):
    figure = Figure.fromfile(f, verbose)

    vs = VertexSink(obj)

    for x, y, z in figure.vertices:
        vs.sink(x, y, z)

    for face in figure.faces:
        if len(face) == 3:
            a, b, c = face

            vs.triangle_vt(a, b, c, -3, -2, -1)
        elif len(face) == 4:
            a, b, c, d = face

            vs.quad_vt(a, b, d, c, -4, -3, -1, -2)
        elif len(face) == 9:
            a, b, c, u1, v1, u2, v2, u3, v3 = face

            vs.texcoord(u1, v1)
            vs.texcoord(u2, v2)
            vs.texcoord(u3, v3)

            vs.triangle_vt(a, b, c, -3, -2, -1)
        else:
            a, b, c, d, u1, v1, u2, v2, u3, v3, u4, v4 = face

            vs.texcoord(u1, v1)
            vs.texcoord(u2, v2)
            vs.texcoord(u3, v3)
            vs.texcoord(u4, v4)

            # last 2 vertices need to be swapped to render correctly
            vs.quad_vt(a, b, d, c, -4, -3, -1, -2)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='convert MBAC models to OBJ')
    parser.add_argument('mbacfile')
    parser.add_argument('objfile')
    parser.add_argument("-v", dest="verbose")
    args = parser.parse_args()

    with open(args.mbacfile, 'rb') as f:
        with open(args.objfile, 'wt') as obj:
            MBAC_to_obj(f, obj, args.verbose)
