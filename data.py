units = [
    dict(name='ns',     label='Nanosecond', format='%(unit)s ns'),
    dict(name='nm',     label='Nanometer', format='%(unit)s nm'),
    dict(name='mm',     label='Millimeter', format='%(unit)s mm'),
    dict(name='mm^2',   label='Square millimeter', format='%(unit)s mm<sup>2</sup>'),
    dict(name='MHz',    label='Megahertz', format='%(unit)s MHz', note='We dont use the minimal unit Hertz because processors are in the MHz area'),
    dict(name='date',   label='Date'),
    dict(name='year',   label='Year'),
    dict(name='count',  label='Count'),
    dict(name='order',  label='Order', note='Information about the order/sequence of a Part'),
    dict(name='B',      label='Byte', format='%(unit)s Byte'),
    dict(name='KB',     label='Kilobyte', format='%(unit)s Kilobyte'),
    dict(name='MB',     label='Megabyte', format='%(unit)s Megabyte'),
    dict(name='MiB',    label='Mebibyte', format='%(unit)s Mebibyte'),
    dict(name='GB',     label='Gigabyte', format='%(unit)s Gigabyte'),
    dict(name='MT/s',   label='Megatransfer/Second', format='%(unit)s MT/s'),
    dict(name='MB/s',   label='Megabyte/Second', format='%(unit)s MB/s'),
    dict(name='factor', label='Factor', format='%(unit)sx', note='ie cpu clock multiplier'),
    dict(name='V',      label='Volt', format='%(unit)s V'),
    dict(name='W',      label='Watt', format='%(unit)s W'),
    dict(name='$',      label='Dollar', format='$%(unit)s'),
    dict(name='url',    label='Url', format='<a href="%(unit)s">%(unit)s</a>'),
    dict(name='text',   label='Text'),
    dict(name='bool',   label='Boolean'),
    dict(name='hex',    label='Hex'),
    dict(name='clock_cycles', label='Number of clock cycles', note='Should this be merged with "Count"? Used for RAM timings'),
    dict(name='json', label='JSON encoded string'),
]

attr_types = [
    {'name': 'Area (mm<sup>2</sup>)', 'unit': 'mm^2'},
    {'name': 'Average half-pitch of a memory cell', 'unit': 'nm'},
    {'name': 'Bus speed', 'unit': 'MHz'},
    {'name': 'CPUID', 'unit': 'text'},
    {'name': 'Casing Size', 'unit': 'text', 'note': 'Minitower, miditower, bigtower'},
    {'name': 'Clock multiplier', 'unit': 'factor'},
    {'name': 'Color', 'unit': 'text'},
    {'name': 'Column Address Strobe latency [CL]', 'unit': 'clock_cycles'},
    {'name': 'Cycle time', 'unit': 'ns'},
    {'name': 'Data rate', 'unit': 'MT/s'},
    {'name': 'Die size', 'unit': 'mm^2'},
    {'name': 'Frequency', 'unit': 'MHz'},
    {'name': 'Front side bus', 'unit': 'MT/s'},
    {'name': 'Harddrive size', 'unit': 'GB'},
    {'name': 'Height', 'unit': 'mm'},
    {'name': 'Hyperthreading', 'unit': 'bool'},
    {'name': 'I/O bus clock', 'unit': 'MHz'},
    {'name': 'L1 cache', 'unit': 'B'},
    {'name': 'L2 cache', 'unit': 'KB'},
    {'name': 'L3 cache', 'unit': 'KB'},
    {'name': 'Length', 'unit': 'mm'},
    {'name': 'Maximal Clock', 'unit': 'MHz'},
    {'name': 'Maximal RAM capacity', 'unit': 'MB'},
    {'name': 'Maximal power consumption', 'unit': 'W'},
    {'name': 'Memory channels', 'unit': 'count'},
    {'name': 'Memory clock', 'unit': 'MHz'},
    {'name': 'Modified', 'unit': 'bool', 'note': 'Was this computer modified after initial delivery?'},
    {'name': 'Module name', 'unit': 'text'},
    {'name': 'Number of cores', 'unit': 'count'},
    {'name': 'Part number', 'unit': 'json'},
    {'name': 'Peak transfer rate', 'unit': 'MB/s'},
    {'name': 'Pin count', 'unit': 'count'},
    {'name': 'Pin pitch', 'unit': 'mm'},
    {'name': 'Position', 'unit': 'order', 'note': 'The position of the associated Part in relation to other Parts'},
    {'name': 'Power', 'note': 'electric power (output? input?)', 'unit': 'W'},
    {'name': 'RAM Size', 'unit': 'B'},
    {'name': 'Release date', 'unit': 'date'},
    {'name': 'Release price', 'unit': '$'},
    {'name': 'Row Active Time [T<sub>RAS</sub>]', 'unit': 'clock_cycles'},
    {'name': 'Row Address to Column Address Delay [T<sub>RCD</sub>]', 'unit': 'clock_cycles'},
    {'name': 'Row Precharge Time [T<sub>RP</sub>]', 'unit': 'clock_cycles'},
    {'name': 'S-Spec', 'unit': 'json'},
    {'name': 'Serial number', 'unit': 'text'},
    {'name': 'Source', 'unit': 'url', 'note': 'Where does the information for this part come from?'},
    {'name': 'Thermal design power', 'unit': 'W'},
    {'name': 'Transistors', 'unit': 'count'},
    {'name': 'Vendor', 'unit': 'text'},
    {'name': 'Vendor hex', 'unit': 'hex'},
    {'name': 'Version', 'unit': 'text'},
    {'name': 'Voltage range', 'unit': 'V'},
    {'name': 'Width', 'unit': 'mm'},
    {'name': 'Year of introduction', 'unit': 'year'}
]


parts = [{
    'Memory controller': { '<note>': 'Seems to be integrated into a cpu (pc alt)',
                           '<attr_types>': ['Memory channels']},
    'CPU Core': { '<attr_types>': [
        "L2 cache", "L3 cache", "Front side bus", "Transistors", "Die size", "Average half-pitch of a memory cell" ]
     },
    'CPU': {
        '<attr_types>': [
            "Frequency", "Clock multiplier", "Voltage range", "Thermal design power",
            "Release date", "Release price", "Part number", "Source", "Number of cores",
            "S-Spec", "Vendor", "Hyperthreading", "Version", "Maximal power consumption",
            "L1 cache", "L2 cache", "L3 cache", "Front side bus"
    ]},
    'Computer': { '<note>': 'Part to safe fix compilations of parts, i.e. PCs, Laptops, Servers, ...)',
                    '<attr_types>': [ "Modified", "Vendor", "Serial number" ]},
    'Casing': { '<note>': 'Computer casing',
                '<attr_types>': [ "Vendor", "Casing Size", "Color", "Width", "Length", "Height" ]
    },
    'Motherboard': { '<attr_types>': [ "Vendor", "Serial number", "Maximal RAM capacity" ] },
    #'DIMM': { '<attr_types>': [ "Pin count", "Source" ] },
    'Power supply': { '<attr_types>': [ 'Power' ] },
    'Chipset': { '<attr_types>': ["Vendor"] },
    'Harddrive': { '<attr_types>': ["Harddrive size"] },
    'RAM':  { '<attr_types>': ["RAM Size"] },
    },
    'Flash memory',
    'Memory card reader',
    'Memory card controller',
    'Audio controller',
]

standards = [{
    'CPU Instruction set': [ 'MMX', 'SSE', 'SSE2', 'SSE 4.x', '32bit', '64bit', 'XD bit', 'Smart Cache' ],
    'CPU Stepping': {
        '<attr_types>': ('Area (mm<sup>2</sup>)', 'CPUID', 'Maximal Clock', 'Release date', 'Source', 'L2 cache'),
        '<children>':[
            'D0 (CPU Stepping)',
            { 'CPU Stepping 65nm': [
                'A1 (CPU Stepping 65nm)', 'B2 (CPU Stepping 65nm)', 'B3 (CPU Stepping 65nm)', 'E1 (CPU Stepping 65nm)',
                'G0 (CPU Stepping 65nm)', 'G2 (CPU Stepping 65nm)', 'L2 (CPU Stepping 65nm)', 'M0 (CPU Stepping 65nm)'],
             'CPU Stepping 45nm': [
                'A1 (CPU Stepping 45nm)', 'C0 (CPU Stepping 45nm)', 'C1 (CPU Stepping 45nm)', 'E0 (CPU Stepping 45nm)',
                'M0 (CPU Stepping 45nm)', 'M1 (CPU Stepping 45nm)', 'R0 (CPU Stepping 45nm)']
            },
        ]
    },
    'RAM': {
        '<attr_types>': ('Memory clock', 'I/O bus clock', 'Data rate', 'Source', 'Cycle time', 'Module name', 'Peak transfer rate',
                         'Column Address Strobe latency [CL]', 'Row Address to Column Address Delay [T<sub>RCD</sub>]',
                         'Row Precharge Time [T<sub>RP</sub>]', 'Row Active Time [T<sub>RAS</sub>]'),
        '<children>': [{
            'SDRAM': [ 'PC-66', 'PC-100', 'PC-133' ], # http://de.wikipedia.org/wiki/Synchronous_Dynamic_Random_Access_Memory#Verschiedene_Typen
            'DDR SDRAM': [ 'DDR-200', 'DDR-266', 'DDR-333', 'DDR-400' ],
            'DDR2 SDRAM': ['DDR2-400', 'DDR2-533', 'DDR2-667', 'DDR2-800', 'DDR2-1066'],
            'DDR3 SDRAM': ['DDR3-800', 'DDR3-1066', 'DDR3-1333', 'DDR3-1600', 'DDR3-1866', 'DDR3-2133'],
        }]
    },

    'CPU Socket': [ 'Socket 1155', 'Socket 423', 'Socket 478' ],
    'PCI': [ 'PCI 1.0', 'PCI 2.0', 'PCI 2.1', 'PCI 2.2', 'PCI 2.3', 'PCI 3.0' ], # http://en.wikipedia.org/wiki/Conventional_PCI#History
    'PCI Express': [ 'PCIe 1.0a', 'PCIe 1.1', 'PCIe 2.0', 'PCIe 2.1', 'PCI 3.0' ], # http://en.wikipedia.org/wiki/PCI_Express#History_and_revisions
    'USB': [ 'USB 1', 'USB 2.0', 'USB 3.0' ],
    'SATA': [ 'SATA 1.0', 'SATA 2.0', 'SATA 3.0', 'SATA 3.1', 'SATA 3.2' ],
    'Memory card': [ 'SD card', 'MMC card', 'MMCplus card', 'xD card', 'MS card', 'MS PRO card' ],
    },
    'AGP',
    'Ethernet (10Mbits)',
    'Fast Ethernet (100Mbits)',
    'Gigabit Ethernet (1000Mbits)',
]


_dimm_url = 'http://en.wikipedia.org/wiki/DIMM'
connectors = [{
    'Socket': {
        '<note>': 'Generic parent for all kinds of sockets',
        '<children>': [
            'CPU-Socket',
            {
            'DIMM': {
                '<attr_types>': [ "Pin count", "Source" ],
                '<children>':
                    [{
                    '168-pin DIMM': {
                        '<attrs>': {'Pin count': 168, 'Source': _dimm_url},
                        '<standards>': ('SDRAM',)
                    },
                    '184-pin DIMM': {
                        '<attrs>': {'Pin count': 184, 'Source': _dimm_url},
                        '<standards>': ('DDR SDRAM',)
                    },
                    '240-pin DIMM (DDR2 SDRAM)': {
                        '<attrs>': {'Pin count': 240, 'Source': _dimm_url},
                        '<standards>': ('DDR2 SDRAM',)
                    },
                    '240-pin DIMM (DDR3 SDRAM)': {
                        '<attrs>': {'Pin count': 240, 'Source': _dimm_url},
                        '<standards>': ('DDR3 SDRAM',)
                    },
                }],
            },
            'PCIe Socket': ['PCIe x16 Socket'], # number of lanes as attribute
            }
        ]
    },
    'Port': {
        '<note>': 'Generic parent for all kinds of ports',
        '<children>': [
            {
            'USB 2.0 Port': [{
                'Anonymous USB 2.0 Port': { '<standards>': ('USB 2.0',) },
            }],
            'USB 3.0 Port': [{
                'Anonymous USB 3.0 Port': { '<standards>': ('USB 2.0', 'USB 3.0') },
            }],
            'RJ-45': [{
                'Anonymous RJ-45':  { '<standards>': ( 'Ethernet (10Mbits)', 'Fast Ethernet (100Mbits)', 'Gigabit Ethernet (1000Mbits)') },
            }],
            },
            'SATA', 'Audio port', 'SD card port', 'MMC card port', 'MMCplus card port',
            'xD card port', 'MS card port', 'MS PRO card port'
        ]
    },
}]


subparts = [{
    'CPU Core': [
        'Intel 80486', 'P5', 'P6', 'Intel Core', 'Enhanced Pentium M',
        'Nehalem', 'Penryn', 'Sandy Bridge', 'Westmere', 'Ivy Bridge', 'Haswell Bridge',
        {
        'Netburst': [{
            'Willamette': {
                '<attrs>': {
                    'Average half-pitch of a memory cell': 180,
                    'L2 cache': 256,
                    'Front side bus': 400,
                    'Transistors': 42000000,
                    'Die size': 217,
                },
                '<standards>': ( 'B2 (CPU Stepping 65nm)', 'C1 (CPU Stepping 45nm)',
                                    'D0 (CPU Stepping)','E0 (CPU Stepping 45nm)',
                                    'MMX', 'SSE', 'SSE2')
            },
            'Northwood': { '<attrs>': { 'L2 cache': 512 }},
            'Prescott': { '<attrs>': {'L2 cache': 1024, 'Front side bus': 533} },
            'Prescott (HT)': { '<attrs>': {'L2 cache': 1024, 'Front side bus': 800} },
            'Prescott 2M': { '<attrs>': {'L2 cache': 2048} },
            'Cedar Mill': { '<attrs>': {'L2 cache': 2048, 'Front side bus': 800} },
            'Gallatin': { '<attrs>': {'L2 cache': 512, 'L3 cache': 2048} },
            }]
        }
    ],
    'CPU': [{
        'Desktop CPU': [{
            'Pentium': [
                { 'Pentium 4': [{
                    'Intel Pentium 4 2.80GHz 15.2.9': {
                        '<attrs>': { 'Vendor': 'Intel','Version': '15.2.9', 'Frequency': '2800' },
                        '<standards>': ('32bit',)
                    }
                }]
                },
                'Pentium 4 Extreme Edition',
                'Pentium 4-M',
                'Mobile Pentium 4'
            ],
            'Intel Pentium Processor G645 (2,9 GHz)': {
                '<attrs>': { 'Number of cores': '2', 'Frequency': '2900', 'Front side bus': '5000', 'Maximal power consumption': '65', 'Vendor': 'Intel' },
                '<standards>': ('SSE 4.x', '64bit', 'XD bit', 'Smart Cache' ),
            },
        }],
    }],
    'Computer': {
        '<children>': [
            { 'Desktop': [{
                'HP d530 CMT(DF368A)': { '<attrs>': { 'Vendor': 'Hewlett-Packard', 'Serial number': 'CZC4301WB9', }},
                'Acer Aspire M1935': { '<attrs>': { 'Vendor': 'Acer' } },
            }]},
            'Laptop',
            'Server'
    ]},
    'Casing': [{
        'Anonymous Mini Tower': { '<attrs>': { 'Vendor': 'Hewlett-Packard', 'Casing Size': 'Minitower' } },
        'Anonymous Tower': { '<attrs>': { 'Width': '180', 'Length': '379', 'Height': '402', 'Color': 'black'} },
    }],
    'RAM': [{
        'DDR3 SDRAM': [{
            'DDR3-1333': [{
                'Anonymous RAM':  { '<attrs>': { 'RAM Size': 2048 } },
            }]
        }]
    }],
    'Motherboard': [{
        '085Ch': { '<attrs>': { 'Vendor': 'Hewlett-Packard', 'Serial number': 'CZC4301WB9', } },
        'Anonymous Motherboard': { '<attrs>': { 'Maximal RAM capacity': 16384 } },
    }],
    'Power supply': [{
        'Anonymous Power Source': { '<attrs>': { 'Power': '250'} },
    }],
    'Memory controller': [{
        'Anonymous Memory Controller': { '<attrs>': { 'Memory channels': '2' } },
    }],
    'Chipset': [{
        'Intel B75 Express': { '<attrs>': { 'Vendor': 'Intel' } },
    }],
    'Harddrive': [{
        'Anonymous harddrive': { '<attrs>': { 'Harddrive size': 500 } },
    }],
    'Memory card controller': [{
        'Anonymous card reader controller': {
            '<standards>': (
                'SD card', 'MMC card', 'MMCplus card',
                'xD card', 'MS card', 'MS PRO card')
        }
    }]
}]



systems = [{
    'HP d530 CMT(DF368A)': {
        '<no_connector>': ['Anonymous Mini Tower', '085Ch', 'Intel Pentium 4 2.80GHz 15.2.9'],
    },
    'Acer Aspire M1935': {
        '<no_connector>': [{
            'Anonymous Tower': {
                '<connectors>': [
                    'SD card port',
                    'MMC card port',
                    'MMCplus card port',
                    'xD card port',
                    'MS card port',
                    'MS PRO card port',
                ],
                '<no_connector>': [
                    'Anonymous Power Source',
                    {
                    'Anonymous Motherboard': {
                        '<no_connector>': [ 'Intel B75 Express', 'Audio controller', 'Anonymous card reader controller'],
                        '<connectors>': [
                            'PCIe x16 Socket',
                            'Anonymous RJ-45',
                            {
                            'SATA': { '<children>': ['Anonymous harddrive'] },
                            'CPU-Socket': {
                                '<children>': [{
                                    'Intel Pentium Processor G645 (2,9 GHz)': {
                                        '<no_connector>': ['Anonymous Memory Controller']
                                    }
                                }]
                            },
                            '240-pin DIMM (DDR3 SDRAM)': {
                                '<quantity>': 4,
                                '<children>': [{'Anonymous RAM': { '<quantity>': 2} }],
                            },
                            'Anonymous USB 2.0 Port': { '<quantity>': 6 },
                            'Anonymous USB 3.0 Port': { '<quantity>': 2 },
                            'Audio port': { '<quantity>': 2 },
                            },
                        ]
                    }
                }],
            }
        }]
    }
}]


