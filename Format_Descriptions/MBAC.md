MBAC file format
================

## Abstract

The MBAC format contains geometry data, referred to in M3D as Figures. No official documentation for the format is available. It is a binary serialization of the documented BAC format which is used in the content pipeline. A MBAC file is often accompanied by a MTRA file which contains animation data.

MBAC files don't store any texture names, but they have a notion of texture indices.

## Known implementations

All known implementations are in native code.

- MascotCapsule SDK (M3DConverter, PVMicro)
- Sony Ericsson WTK emulator (in zayitlib.dll)
- official implementation used in cell phones (we don't have this code)

Known NON-implementations (as of 2017/12):

- KEmulator (only implements parts of the API)
- FreeJ2ME (stubbed)
- J2ME-Loader (doesn't implement API)
- phoneME (doesn't implement API)

## Overall structure

- Header(s)
- Vertices
- Normals (if present)
- Polygons (types: T3, T4, F3, F4)
- Segments (bones)
- 20-byte encrypted trailer

## Format versions

Known versions of the format, along with allowed data encodings, are listed below.

| Version        | vertexformats | normalformats | polygonformats | segmentformats(?) | Seen in |
|----------------|---------------|---------------|----------------|-------------------|---------|
| 3 | 1 | 0 (= N/A) | 1 | 1 |
| 4 | 1, 2 | 0, 1, 2 | 1, 2 | 1 |
| 5 | 1, 2 | 0, 1, 2 | 1, 2, 3 | 1 | Burning Tires, GoF, Deep, Blades & Magic, GoF 2 |

Some data: https://docs.google.com/spreadsheets/d/1KYqJr-XSWoTbdRDF-JLuCdAbYaKsaRQLp_yNlxpCmp8/edit?usp=sharing

## Format description

All fields are in little-endian.

The file starts with this common header:

    char magic[2] = {'M', 'B'};
    uint16_t formatversion;

    if (formatversion > 3) {
        uint8_t vertexformat;
        uint8_t normalformat;
        uint8_t polygonformat;
        uint8_t segmentformat?;
    }

    uint16_t num_vertices;
    uint16_t num_polyT3;
    uint16_t num_polyT4;
    uint16_t num_segments;

For polygonformat >= 3, more header data follows.

    uint16_t num_polyF3;
    uint16_t num_polyF4;
    uint16_t matcnt0C;      // something like number of materials
    uint16_t max0E;         // unknown, but related to some polygon attributes
    uint16_t num_color;

    // meaning of the following is unknown; likely to be related to materials and/or textures
    repeat(max0E) {
        uint16_t unk1;
        uint16_t unk2;

        repeat(matcnt0E) {
            uint16_t unk3;
            uint16_t unk4;
        }
    }

### Vertices (vertexformat=2)

Vertices are packed in blocks of up to 64 each. These blocks form a bitstream and are not necessarily byte-aligned. The entire bitstream does start on byte boundary and, if necessary, is padded to also end on one.

    align uint8_t;

    bitstream {
        while (have_vertices < num_vertices) {
            uint(6) count_minus_one;
            uint(2) range;

            num_vertices_in_block := count_minus_one + 1;

            switch (range) {
                case 0:
                    repeat(num_vertices_in_block) {
                        sint(8) x;
                        sint(8) y;
                        sint(8) z;
                    }
                    break;
                case 1:
                    repeat(num_vertices_in_block) {
                        sint(10) x;
                        sint(10) y;
                        sint(10) z;
                    }
                    break;
                case 2:
                    repeat(num_vertices_in_block) {
                        sint(13) x;
                        sint(13) y;
                        sint(13) z;
                    }
                    break;
                case 3:
                    repeat(num_vertices_in_block) {
                        sint(16) x;
                        sint(16) y;
                        sint(16) z;
                    }
                    break;
            }

            have_vertices := have_vertices + num_vertices_in_block;
        }
    }

    align uint8_t;

### Normals (normalformat=2)

If normalformat=0, there is no data for normals.

Normals are packed in blocks of up to 64 each. These blocks form a bitstream and are not necessarily byte-aligned. The entire bitstream does start on byte boundary and, if necessary, is padded to also end on one.

    bitstream {
        repeat (num_vertices) {
            sint(7) x;

            if (x == -64) {
                uint(3) direction;
            }
            else {
                sint(7) y;
                sint(1) z_sign;
            }
        }
    }

TODO: describe `direction`

If XYZ format is used, Z can be calculated as `+/- sqrt(1 - x^2 - y^2)`. `z_sign` is -1 if Z is negative.

Some files I've examined have x^2 + y^2 > 1, not sure what that means.

### Polygons (polygonformat=3)

F-polygons: not documented for now.

T-polygons:

    uint(8) unknown_bits;
    uint(8) vertex_index_bits;
    uint(8) uv_bits;
    uint(8) somedata;                       // meaning unknown

    repeat (num_polyt3) {
        uint(unknown_bits) unknown;         // could be polygon flags
                                            // not material index, but maybe material flags baked into polygons

        repeat(3) {
            uint(vertex_index_bits) vertex_index;
        }

        repeat(3) {
            uint(uv_bits) u;
            uint(uv_bits) v;
        }
    }

    repeat (num_polyt4) {
        uint(unknown_bits) unknown;

        repeat(4) {
            uint(vertex_index_bits) vertex_index;
        }

        repeat(4) {
            uint(uv_bits) u;
            uint(uv_bits) v;
        }
    }

UV coordinates seem to be simply in pixels. Unknown if `uv_bits` can be 0.

Note that polygon->material mapping is not stored here.

### Segments (segmentformat=1)

    repeat (num_segments) {
        uint(16)    seg_vertices;
        int(16)     parent;

        int(16)     matrix[3][4];
    }

`seg_vertices` specifies the number of vertices in this segment (starting at wherever the previous segment left off)

`parent` should be "-1" for exactly one segment (root of the skeleton), otherwise it is the non-negative index of parent segment.

`matrix` is 3 rows (outer loop) by 4 columns; columns 0 through 2 are pre-multiplied by 4096 before conversion to int16; in other words, they use 4.12 signed format. Usually, the matrix will specify rotation + translation, but always unity scale.

### 20-byte encrypted trailer

Format:

    uint(16)    key1;
    uint(8)     data1[8];
    uint(16)    key2;
    uint(8)     data2[8];

Data is encrypted using a simple XOR cipher with the corresponding keys. After decryption, `data1` should == `data2`. For MBAC files generated with stock M3DConverter5.1, decrypted data reads as `HI000000` (HI standing for HI CORP.). Abyss engine games have `SE000000` (SE = Sony Ericsson???).

This might have been used for copyright protection, as hinted in `man_pg_comdot_v3_e_102.pdf`.

During conversion, keys are chosen using an MT PRNG (seeded with `time()`) and some scene metadata. The plaintext comes from the BAC struct, so it might be possible to specify it in the source BAC file.
