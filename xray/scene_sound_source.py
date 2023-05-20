from . import utils
from . import ltx
from . import reader


SOUND_CHUNK_SOURCE_NAME = 0x1003


def read_sound_source_object_data(data, sounds):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == SOUND_CHUNK_SOURCE_NAME:
            packed_reader = reader.PackedReader(chunk_data)
            source_name = packed_reader.gets()
            if source_name:
                sounds.add(source_name)


def read_sound_source_object(data, sounds):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:
            read_sound_source_object_data(chunk_data, sounds)


def read_sound_source_objects(data, sounds):
    chunked_reader = reader.ChunkedReader(data)

    for source_id, source_data in chunked_reader:
        read_sound_source_object(source_data, sounds)


def read_scene_sound_sources(data, sounds):
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x3:
            read_sound_source_objects(chunk_data, sounds)


def read_soc_sound_sources(file_path, sounds):
    data = utils.read_file(file_path)
    chunked_reader = reader.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x8005:
            read_scene_sound_sources(chunk_data, sounds)


def read_cop_sound_sources(path, sounds):
    sound_sources = ltx.LtxParser()
    sound_sources.from_file(path)

    for section in sound_sources.sections.values():
        if not section.name.startswith('object_'):
            continue

        for param_name, param_value in section.params.items():
            if param_name == 'snd_name':
                sounds.add(param_value)


def read_sound_sources(file_path, sounds):
    try:
        # cop
        read_cop_sound_sources(file_path, sounds)

    except:
        # soc
        read_soc_sound_sources(file_path, sounds)
