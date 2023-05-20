from . import reader
from . import utils


CHUNK_SHADERS = 0x2


def read_shaders(data, textures):
    packed_reader = reader.PackedReader(data)
    shaders_count = packed_reader.getf('<I')[0]

    for shader_index in range(shaders_count):
        shader = packed_reader.gets()

        if not shader:
            continue

        texs = shader.split('/')[-1].split(',')

        for tex in texs:
            textures.add(tex)


def read_game_level_textures(path, textures):
    data = utils.read_file(path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_SHADERS:
            read_shaders(chunk_data, textures)
