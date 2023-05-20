from . import utils
from . import reader


def read_wallmark_object(data, textures):
    packed_reader = reader.PackedReader(data)
    item_count = packed_reader.getf('<I')[0]
    shader_name = packed_reader.gets()
    tex_name = packed_reader.gets()
    textures.add(tex_name)


def read_wallmarks_objects(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for wallmark_id, wallmark_data in chunked_reader:
        read_wallmark_object(wallmark_data, textures)


def read_wallmarks(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x0005:
            read_wallmarks_objects(chunk_data, textures)


def read_level_wallmarks(path, textures):
    data = utils.read_file(path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x800e:
            read_wallmarks(chunk_data, textures)
