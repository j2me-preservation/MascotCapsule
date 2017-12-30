MBAC file format
================

## Abstract

The MBAC format contains geometry data, referred to in M3D as Figures. No official documentation for the format is available. It is a binary serialization of the documented BAC format which is used in the content pipeline. A MBAC file is often accompanied by a MTRA file which contains animation data.

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

## Format versions

Known versions of the format, along with allowed data encodings, are listed below.

| Version        | vertexformats | normalformats | polygonformats | segmentformats(?) | Seen in |
|----------------|---------------|---------------|----------------|-------------------|---------|
| 3 | 1 | 0 | 1 | 1 |
| 4 | 1, 2 | 0, 1, 2 | 1, 2 | 1 |
| 5 | 1, 2 | 0, 1, 2 | 1, 2, 3 | 1 | Burning Tires, GoF, Deep, Blades & Magic, GoF 2 |

Some data: https://docs.google.com/spreadsheets/d/1KYqJr-XSWoTbdRDF-JLuCdAbYaKsaRQLp_yNlxpCmp8/edit?usp=sharing

## Format description

All fields are in little-endian.

The file starts with this header:

    struct {
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
    }

Note: Segments = bones.

For polygonformat >= 3, more header data follows.

    struct {
        uint16_t num_polyF3;
        uint16_t num_polyF4;
        uint16_t matcnt0C;      // something like number of materials
        uint16_t max0E;         // unknown, but related to some polygon attributes
        uint16_t num_color;

        // meaning of the following is completely unknown
        repeat(max0E) {
            uint16_t unk1;
            uint16_t unk2;

            repeat(matcnt0E) {
                uint16_t unk3;
                uint16_t unk4;
            }
        }
    }

### Vertices (vertexformat=2)

Vertices are packed in blocks of up to 64 each. These blocks form a bitstream and are not necessarily byte-aligned. The entire bitstream does start on byte boundary and, if necessary, is padded to also end on one.

    align uint8_t;

    bitstream {
        while (have_vertices < num_vertices) {
            uint6_t count_minus_one;
            uint2_t range;

            num_vertices_in_block := count_minus_one + 1;

            switch (range) {
                case 0:
                    repeat(num_vertices_in_block) {
                        int8_t x;
                        int8_t y;
                        int8_t z;
                    }
                    break;
                case 1:
                    repeat(num_vertices_in_block) {
                        int10_t x;
                        int10_t y;
                        int10_t z;
                    }
                    break;
                case 2:
                    repeat(num_vertices_in_block) {
                        int13_t x;
                        int13_t y;
                        int13_t z;
                    }
                    break;
                case 3:
                    repeat(num_vertices_in_block) {
                        int16_t x;
                        int16_t y;
                        int16_t z;
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
            int7_t x;

            if (x == -64) {
                uint3_t direction;
            }
            else {
                int7_t y;
                int1_t z_sign;
            }
        }
    }

TODO: describe `direction`

If XYZ format is used, Z can be calculated as `+/- sqrt(1 - x^2 - y^2)`. `z_sign` is 1 if Z is negative.

Some files I've examined have x^2 + y^2 > 1, not sure what that means.

### Polygons (polygonformat=3)

F-polygons: not documented for now.

T-polygons:

    uint8_t unknown_bits;
    uint8_t vertex_index_bits;
    uint8_t uv_bits;
    uint8_t somedata;                       // meaning unknown

    repeat (num_polyt3) {
        uint{unknown_bits}_t unknown;       // could be polygon flags
                                            // definitely NOT material index

        repeat(3) {
            uint{vertex_index_bits}_t vertex_index;
        }

        repeat(3) {
            uint{uv_bits}_t u;
            uint{uv_bits}_t v;
        }
    }

    repeat (num_polyt4) {
        uint{unknown_bits}_t unknown;

        repeat(4) {
            uint{vertex_index_bits}_t vertex_index;
        }

        repeat(4) {
            uint{uv_bits}_t u;
            uint{uv_bits}_t v;
        }
    }

Note that polygon->material mapping is not stored here.

### Rest of the file

There is a lot more, which is yet to be understood/documented.
