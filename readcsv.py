#-*- coding: utf-8 -*-

import json
import csv
from StringIO import StringIO

FILE_SPLITTOR = '### <newfile> ###'


def _inflate_meta_data(d):
    for k in d.keys():
        if isinstance(k, (list, tuple)):
            v = d.pop(k)
            for sub_key in k:
                d[sub_key] = v


def parse_csv(file_string, meta_data):
    _inflate_meta_data(meta_data)

    data = []
    for row in csv.DictReader(StringIO(file_string)):
        single_row_cols = {}
        multi_row_cols = {}
        for name, value in row.iteritems():
            if value:
                value = value.decode('utf-8').encode('ascii', 'replace') # TODO: evil codec bug
            if not name:
                # seems to be an empty column
                continue

            name = name.replace('\n', ' ').replace('\xc2\xa0', ' ').strip(' \n\r\t\xa0\xc2') # xa0 and xc2 are nbsp
            try:
                col_info = meta_data[name]
            except KeyError:
                raise Exception('Unknown column: %r. Allowed columns: %s'%(name, meta_data.keys()))

            if col_info.get('ignore'):
                continue

            name = col_info.get('col', name)

            if '\n' in value:
                # check for illegal multirows
                if col_info.get('multi'):
                    multi_row_cols[name] = value.split('\n')
                elif col_info.get('not_multi'):
                    single_row_cols[name] = value.split('\n')
                else:
                    raise Exception()

            else:
                single_row_cols[name] = value

        if multi_row_cols:

            # Check if all multi_row_columns have the same number of rows
            row_length_set = set((len(m) for m in multi_row_cols.values()))
            if len(row_length_set) != 1:
                # We cannot know how to handle a different number of rows
                raise Exception()

            for i in xrange(row_length_set.pop()):
                new_row = single_row_cols.copy()
                for name, value_list in multi_row_cols.iteritems():
                    new_row[name] = value_list[i]

                data.append(new_row)

        else:
            data.append(single_row_cols)

    return data


def handle_DDR_SDRAM(file_string, url):
    timings = ('Timings (CL-tRCD-tRP)', 'Timings[2][3] (CL-tRCD-tRP)')
    cycle_time = ('Cycle time (ns)', 'Cycle time[4] (ns)')
    columns = {
        'Standard name':                dict(col='Name', multi=True),
        'Memory clock (MHz)':           dict(col='Memory clock'),
        cycle_time:                     dict(col='Cycle time'),
        'I/O bus clock (MHz)':          dict(col='I/O bus clock'),
        'Data rate (MT/s)':             dict(col='Data rate'),
        'Module name':                  dict(),
        'Peak transfer rate (MB/s)':    dict(col='Peak transfer rate'),
        timings:                        dict(col='Timings', multi=True),
        'VDDQ (V)':                     dict(ignore=True),
        'CAS latency (ns)':             dict(ignore=True),
    }

    data = parse_csv(file_string, columns)
    standards = []
    for row in data:
        row['Source'] = url
        name = row.pop('Name')
        timings = row.pop('Timings', None)
        if timings:
            timings = timings.split('-')
            row['Column Address Strobe latency [CL]'] = timings[0]
            row['Row Address to Column Address Delay [T<sub>RCD</sub>]'] = timings[1]
            row['Row Precharge Time [T<sub>RP</sub>]'] = timings[2]
        standards.append({'<name>': name, '<attrs>': row})

    return dict(standards=standards)


def handle_pentium4_willamette(file_string, url):
    columns = {
        'sSpec Number':             dict(col='S-Spec', not_multi=True),
        'Frequency':                dict(),
        'L2 Cache':                 dict(col='L2 cache'),
        'Front Side Bus':           dict(col='Front side bus'),
        'Clock Multiplier':         dict(col='Clock multiplier'),
        'Voltage Range':            dict(col='Voltage range'),
        'TDP':                      dict(col='Thermal design power'),
        'Socket':                   dict(),
        'Release Date':             dict(col='Release date', multi=True),
        'Part Number(s)':           dict(col='Part number', not_multi=True),
        'Release Price (USD)':      dict(col='Release price'),
        'Model Number Clock Speed': dict(col='Name')
    }

    data = parse_csv(file_string, columns)
    parts = []
    connections = []
    for row in data:
        row['Source'] = url
        name = row.pop('Name')
        socket = row.pop('Socket')

        row['L2 cache'] = row['L2 cache'].strip(' Kilobyte')
        row['Front side bus'] = row['Front side bus'].strip(' MT/s')
        row['Voltage range'] = row['Voltage range'].strip(' V')
        #row['Clock multiplier'] = row['Clock multiplier'].strip('×'.decode('utf-8'))
        row['Clock multiplier'] = row['Clock multiplier'].strip('?x')
        row['Frequency'] = row['Frequency'].strip(' MHz')
        row['Thermal design power'] = row['Thermal design power'].strip(' W')
        row['Release price'] = row['Release price'].strip('$')
        row['Part number'] = str(row['Part number'])
        row['S-Spec'] = str(row['S-Spec'])

        parts.append({ '<name>': name, '<attrs>': row, '<standards>': (socket,)})
        connections.append({ '<name>': name, '<no_connector>': [{'<name>': 'Willamette'}]})

    return dict(parts=parts, connections=connections)


handlers = {
    'DDR_SDRAM': handle_DDR_SDRAM,
    'DDR2_SDRAM': handle_DDR_SDRAM,
    'DDR3_SDRAM': handle_DDR_SDRAM,
    'Pentium4_Willamette': handle_pentium4_willamette,
}

def read_all_files(filepath):
    f = open(filepath)
    file_strings = f.read().split(FILE_SPLITTOR)
    file_strings.pop(0) #remove the first empty item
    all_files = {}

    for file_string in file_strings:
        file_string = file_string.strip(',\n')

        lines = file_string.strip().splitlines()
        name = lines[0].strip(' #,')
        url = lines[1].strip(' #,')
        handler = handlers.get(name)
        if handler:
            print 'Parse', name
            all_files[name] = handler('\n'.join(lines[2:]), url)
        else:
            print 'no handler for', name

    return all_files


