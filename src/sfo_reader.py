"""
Created on Jan 16, 2013

@author: mystique
"""
import getopt
import os
import struct
import sys
from os.path import join, getsize

length_map = {'APP_VER': 8, 'ATTRIBUTE': 4, 'BOOTABLE': 4,
              'CATEGORY': 4, 'LICENSE': 512, 'NP_COMMUNICATION_ID': 16,
              'PARENTAL_LEVEL': 4, 'PS3_SYSTEM_VER': 8, 'RESOLUTION': 4,
              'SOUND_FORMAT': 4, 'TITLE': 128, 'TITLE_ID': 16, 'VERSION': 8}


def get_title_text(_title_ids, _value_offset, _file, _find_title_id):
    read_value_offset = _value_offset

    for _title_id in _title_ids.split(' '):

        if _title_id == _find_title_id:
            _file.seek(read_value_offset)
            ver_title_length = length_map[_title_id]
            ps3_system_ver = struct.unpack(str(ver_title_length) + 's', _file.read(ver_title_length))[0]

            return ps3_system_ver.decode().replace('\x00', ' ').strip()

        if _title_id in length_map.keys():
            read_value_offset += length_map[_title_id]
        else:
            print('TITLE_ID: ' + _title_id + '\'s length not found.')


def get_title_offset(_file):
    _file.seek(8, 0)
    return struct.unpack('I', _file.read(4))[0]


def get_value_offset(_file):
    _file.seek(12, 0)
    return struct.unpack('I', _file.read(4))[0]


def get_title_ids(_title_offset, _value_offset, file):
    file.seek(_title_offset)
    title_length = _value_offset - _title_offset

    _title_ids = struct.unpack(str(title_length) + 's', file.read(title_length))[0]
    _title_ids = _title_ids.decode().replace('\x00', ' ').strip()

    return _title_ids


def get_folder_size(_folder):
    _folder_size = 0

    for root, dirs, files in os.walk(_folder):
        _folder_size += sum([getsize(join(root, name)) for name in files])

    if _folder_size > 1024 * 1024 * 1024:
        return '%.2f' % (_folder_size / 1024 / 1024 / 1024) + 'G'
    if _folder_size > 1024 * 1024:
        return '%.2f' % (_folder_size / 1024 / 1024) + 'M'
    if _folder_size > 1024:
        return '%.2f' % (_folder_size / 1024) + 'K'


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:')

    input_file_name = ''
    output_file_name = ''

    for op, value in opts:
        if op == '-i':
            input_file_name = value
        if op == '-o':
            output_file_name = value

    if input_file_name == '' or output_file_name == '':
        print('usage: python sfo_reader.py -i input_dir -o output_file')
        sys.exit(0)

    input_file = open(input_file_name, 'rb')
    output_file = open(output_file_name, 'w')

    title_offset = get_title_offset(input_file)
    value_offset = get_value_offset(input_file)

    title_ids = get_title_ids(title_offset, value_offset, input_file)

    title_id = get_title_text(title_ids, value_offset, input_file, 'TITLE_ID')
    ver_text = get_title_text(title_ids, value_offset, input_file, 'PS3_SYSTEM_VER')
    folder_size = get_folder_size(input_file_name)

    output_file.writelines(title_id + '\t\t\t' + ver_text + '\t\t\t' + folder_size)

    input_file.close()
    output_file.close()
