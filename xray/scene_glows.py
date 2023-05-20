from . import utils
from . import reader


CHUNK_GLOWS = 0x8001
CHUNK_GLOW_OBJECTS = 0x3
CHUNK_GLOW_OBJECT_DATA = 0x7777
CHUNK_GLOW_OBJECT_TEXTURE = 0xc415


def read_glow_data(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_GLOW_OBJECT_TEXTURE:
            packed_reader = reader.PackedReader(chunk_data)
            texture = packed_reader.gets()
            textures.add(texture)


def read_glow(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_GLOW_OBJECT_DATA:
            read_glow_data(chunk_data, textures)


def read_glows_objects(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for glow_index, glow_data in chunked_reader:
        read_glow(glow_data, textures)


def read_glows(data, textures):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_GLOW_OBJECTS:
            read_glows_objects(chunk_data, textures)


def read_level_glows(path, textures):
    data = utils.read_file(path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_GLOWS:
            read_glows(chunk_data, textures)
