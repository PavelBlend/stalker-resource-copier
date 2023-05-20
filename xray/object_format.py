from . import utils
from . import reader


def read_object_main(data, textures):
    chunked_reader = reader.ChunkedReader(data)
    object_type = None

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id in (0x0905, 0x0906, 0x0907):    # surfaces
            packed_reader = reader.PackedReader(chunk_data)
            surfaces_count = packed_reader.getf('<I')[0]

            for surface_index in range(surfaces_count):
                if chunk_id in (0x0906, 0x0907):
                    name = packed_reader.gets()
                    eshader = packed_reader.gets()
                    cshader = packed_reader.gets()
                    if chunk_id == 0x0907:
                        gamemtl = packed_reader.gets()
                    texture = packed_reader.gets()
                    vmap = packed_reader.gets()
                    surface_flags = packed_reader.getf('<I')[0]
                    packed_reader.skip(4 + 4)    # fvf and ?
                else:
                    name = packed_reader.gets()
                    eshader = packed_reader.gets()
                    packed_reader.skip(1)    # flags
                    packed_reader.skip(4 + 4)    # fvf and TCs count
                    texture = packed_reader.gets()
                    vmap = packed_reader.gets()
                textures.add(texture)

        elif chunk_id == 0x0903:    # flags (object type)
            packed_reader = reader.PackedReader(chunk_data)
            flags = packed_reader.getf('I')[0]

            if flags == 0x1:    # multiple usage
                object_type = 'MULIPLE_USAGE'

    return object_type


def get_object_textures(path, textures):
    data = utils.read_file(path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == 0x7777:    # main
            object_type = read_object_main(chunk_data, textures)
            return object_type
