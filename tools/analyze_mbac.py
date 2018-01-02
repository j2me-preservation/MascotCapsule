# analyze all MBAC files in a directory, print out stats

import io, os, struct, sys

import mbac2obj
import render_obj

from fishlabs_obfuscation import fishlabs_deobfuscate

DIR = sys.argv[1]

def render_MBAC(path, filedata):
    with open('tmp.mbac', 'wb+') as f:
    #f = io.BytesIO(filedata)
        f.write(filedata)
        f.seek(0)

        print(path, file=sys.stderr)

        TMPOBJ = path + '.obj'
        with open(TMPOBJ, 'wt') as obj:
            mbac2obj.MBAC_to_obj(f, obj)

        SCALE = 0.001
        render_obj.render_obj(render_obj.BLENDER_EXE, TMPOBJ,
                os.path.join('outputs', path.replace('/', '_').replace('\\', '_')), SCALE)
        os.remove(TMPOBJ)

def analyze_filedata(path, filedata, render):
    size = len(filedata)

    (magic, version) = struct.unpack('HH', filedata[0:4])

    if magic != 0x424D:
        raise Exception('Not a MBAC file')
    if version != 5:
        raise Exception('Unsupported MBAC version')

    (vertexformat, normalformat, polygonformat, segmentformat) = struct.unpack('BBBB', filedata[4:8])
    (num_vertices, num_polyt3, num_polyt4, num_segments) = struct.unpack('HHHH', filedata[8:16])

    (num_polyf3, num_polyf4, matcnt, unk21, num_color) = struct.unpack('HHHHH', filedata[16:26])

    print('%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' % (
            path, size, version, vertexformat, normalformat, polygonformat, segmentformat,
            num_vertices, num_polyt3, num_polyt4, num_segments,
            num_polyf3, num_polyf4, matcnt, unk21, num_color))

    if render:
        render_MBAC(path, filedata)

def analyze_file(path, render):
    with open(path, 'rb') as f:
        filedata = f.read()

        if filedata[0:2] == b'MB':
            analyze_filedata(path, filedata, render)
        elif filedata[len(filedata)-2:] == b'BM':
            # File is obfuscated (GoF 1, Deep)
            analyze_filedata(path, fishlabs_deobfuscate(filedata), render)
        else:
            raise Exception('Invalid format of ' + path)

print('Path,Size,formatversion,vertexformat,normalformat,polygonformat,segmentformat,num_vertices,num_polyt3,num_polyt4,num_segments,num_polyf3,num_polyf4,matcnt,unk21,num_color')

render = True

for file in os.listdir(DIR):
    if file.endswith('.mbac'):
        analyze_file(os.path.join(DIR, file), render)
