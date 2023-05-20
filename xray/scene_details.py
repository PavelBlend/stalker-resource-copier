from . import utils
from . import reader


CHUNK_DETAIL_OBJECTS = 0x800c
DETMGR_CHUNK_OBJECTS = 0x0001
DETOBJ_CHUNK_REFERENCE = 0x0101
DETMGR_CHUNK_TEXTURE = 0x1002


def read_objects(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == DETOBJ_CHUNK_REFERENCE:
            packed_reader = reader.PackedReader(chunk_data)
            reference_object = packed_reader.gets()
            objects_list.add(reference_object)


def read_objects(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for obj_index, obj_data in chunked_reader:
        read_objects(obj_data, objects_list)


def read_detail_objects(data, objects_list, textures):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == DETMGR_CHUNK_OBJECTS:
            read_objects(chunk_data, objects_list)

        elif chunk_id == DETMGR_CHUNK_TEXTURE:
            tex_reader = reader.PackedReader(chunk_data)
            base_tex = tex_reader.gets()
            textures.add(base_tex)


def read_level_details(file_path, objects_list, textures):
    data = utils.read_file(file_path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == CHUNK_DETAIL_OBJECTS:
            read_detail_objects(chunk_data, objects_list, textures)
