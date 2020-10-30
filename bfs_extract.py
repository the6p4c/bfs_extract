import os
import struct
import sys
import zlib

def snap_dword(pos):
    if pos % 4 != 0:
        return 4 - (pos & 3)
    else:
        return 0

with open(sys.argv[1], 'rb') as f:
    paths = []

    pos = 0x20
    f.seek(pos, os.SEEK_SET)
    
    while True:
        path_len = struct.unpack('<H', f.read(2))[0]
        pos += 2

        if path_len == 0:
            break

        path = bytes([b ^ 0xea for b in f.read(path_len)]).decode('ascii')
        print(f'Found file {path}')

        pos += path_len

        pos_delta = snap_dword(pos)
        pos += pos_delta
        f.seek(pos_delta, os.SEEK_CUR)

        offset = struct.unpack('<I', f.read(4))[0]
        pos += 4

        print(f'    Offset: {offset:x}')

        paths.append((path, offset))
    
    for path_offset in paths:
        path, offset = path_offset

        f.seek(offset, os.SEEK_SET)

        header = f.read(4 * 3)
        len_decompressed, len_data, unk = struct.unpack('<III', header)

        print(f'Extracting {path}')
        print(f'    Offset: {pos:x}')
        print(f'    Length (decompressed): {len_decompressed:x}')
        print(f'    Length (data): {len_data:x}')
        print(f'    Unknown: {unk:x}')

        path_components = path.split('/')
        dir_path = os.path.join(sys.argv[2], *path_components[:-1])
        file_path = os.path.join(sys.argv[2], *path_components)
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        data = f.read(len_data)
        with open(file_path, 'wb') as f2:
            if unk & 1 == 0:
                print('    obfuscated data')
                f2.write(bytes([b ^ 0xea for b in data]))
            else:
                print('    compressed data')
                f2.write(bytes([b ^ 0xea for b in zlib.decompress(data)]))
