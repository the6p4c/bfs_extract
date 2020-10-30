import os
import struct
import sys

with open(sys.argv[1], 'rb') as f, open(sys.argv[2], 'wb') as f2:
    header = f.read(4 * 4)
    sig, unk, size, data_offset = struct.unpack('<IIII', header)
    
    size_data = size - data_offset

    f.seek(data_offset, os.SEEK_SET)

    while True:
        b = f.read(4)
        if len(b) != 4:
            break

        v = struct.unpack('<I', b)[0]
        v ^= size
        f2.write(struct.pack('<I', v))
