import struct


class PackedReader:
    def __init__(self, reader_data):
        self.offs = 0
        self.data = reader_data
        self.size = len(self.data)

    def getf(self, fmt):
        format_size = struct.calcsize(fmt)
        self.offs += format_size
        return struct.unpack_from(fmt, self.data, self.offs - format_size)

    def gets(self):
        zero_pos = self.offs
        while (zero_pos < self.size) and (self.data[zero_pos] != 0):
            zero_pos += 1

        str_bytes = self.data[self.offs : zero_pos]
        self.offs = zero_pos + 1

        return str(str_bytes, 'cp1251')

    def skip(self, count):
        self.offs += count


class ChunkedReader:
    __MASK_COMPRESSED = 0x80000000

    def __init__(self, data):
        self.offs = 0
        self.data = data

    def __iter__(self):
        return self

    def __next__(self):
        header_offset = self.offs
        header_format = '<2I'
        header_size = struct.calcsize(header_format)

        if header_offset + header_size >= len(self.data):
            raise StopIteration

        chunk_id, chunk_size = struct.unpack(
            header_format,
            self.data[header_offset : header_offset+header_size]
        )
        header_offset += header_size
        self.offs = header_offset + chunk_size

        if chunk_id & ChunkedReader.__MASK_COMPRESSED:
            chunk_id &= ~ChunkedReader.__MASK_COMPRESSED
            raise Exception(
                'unsupported: compressed chunk: {}'.format(chunk_id)
            )

        return chunk_id, self.data[header_offset : header_offset+chunk_size]
