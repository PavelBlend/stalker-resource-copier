import os

from . import ltx
from . import utils
from . import reader


def read_group_object_data(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x902:
            packed_reader = reader.PackedReader(chunk_data)
            ref = packed_reader.gets()
            objects_list.add(ref)


def read_group_object(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:
            read_group_object_data(chunk_data, objects_list)


def read_group_objects(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for object_id, object_data in chunked_reader:
        read_group_object(object_data, objects_list)


def read_group(ref, groups_path, objects_list):
    file_path = os.path.join(groups_path, ref) + os.extsep + 'group'

    if not os.path.exists(file_path):
        return

    data = utils.read_file(file_path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x1:
            read_group_objects(chunk_data, objects_list)


def read_soc_groups_object_ref_data(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x902:
            packed_reader = reader.PackedReader(chunk_data)
            packed_reader.skip(8)
            ref = packed_reader.gets()
            objects_list.add(ref)


def read_soc_groups_object_ref(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:
            read_soc_groups_object_ref_data(chunk_data, objects_list)


def read_soc_groups_objects_refs(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for ref_id, ref_data in chunked_reader:
        read_soc_groups_object_ref(ref_data, objects_list)


def read_soc_groups_object_data(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x1:
            read_soc_groups_objects_refs(chunk_data, objects_list)


def read_soc_groups_object(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:
            read_soc_groups_object_data(chunk_data, objects_list)


def read_soc_groups_objects(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for object_id, object_data in chunked_reader:
        read_soc_groups_object(object_data, objects_list)


def read_soc_groups_data(data, objects_list):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x3:
            read_soc_groups_objects(chunk_data, objects_list)


def read_soc_groups(path, objects_list, groups_path):
    data = utils.read_file(path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x8000:
            read_soc_groups_data(chunk_data, objects_list)


def read_cop_groups(path, objects_list, groups_path):
    groups = ltx.LtxParser()
    groups.from_file(path)

    for section in groups.sections.values():
        if not section.name.startswith('object_'):
            continue

        for param_name, param_value in section.params.items():
            if param_name == 'ref_name':
                read_group(param_value, groups_path, objects_list)


def read_level_groups(file_path, objects_list, groups_path):
    try:
        # cop
        read_cop_groups(file_path, objects_list, groups_path)

    except:
        # soc
        read_soc_groups(file_path, objects_list, groups_path)
