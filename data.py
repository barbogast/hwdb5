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
    dict(name='KB',     label='Kilobyte', format='%(unit)s KB'),
    dict(name='MB',     label='Megabyte', format='%(unit)s MMB'),
    dict(name='MiB',    label='Mebibyte', format='%(unit)s MiB'),
    dict(name='GB',     label='Gigabyte', format='%(unit)s GB'),
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
    {'name': 'Version number', 'unit': 'text'},
    {'name': 'Voltage range', 'unit': 'V'},
    {'name': 'Width', 'unit': 'mm'},
    {'name': 'Year of introduction', 'unit': 'year'}
]


part_schema = [{
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
        ],
        #'<children>': ['Desktop CPU'],
    },
    'Computer': {
        '<note>': 'Part to safe fix compilations of parts, i.e. PCs, Laptops, Servers, ...)',
        '<attr_types>': [ "Modified", "Vendor", "Serial number" ],
        '<children>': ['Desktop', 'Laptop', 'Server'],
    },
    'Casing': { '<note>': 'Computer casing',
                '<attr_types>': [ "Vendor", "Casing Size", "Color", "Width", "Length", "Height" ]
    },
    'Motherboard': { '<attr_types>': [ "Vendor", "Serial number", "Maximal RAM capacity" ] },
    #'DIMM': { '<attr_types>': [ "Pin count", "Source" ] },
    'Power supply': { '<attr_types>': [ 'Power' ] },
    'Chipset': { '<attr_types>': ["Vendor"] },
    'Harddrive': {
        '<attr_types>': ["Harddrive size"],
        '<children>': ['IDE', 'SATA', 'SAS', 'SCSI'],
    },
    'RAM':  {
        '<attr_types>': ["RAM Size"],
        '<children>': [{
            'DDR3 SDRAM': ['DDR3-1333']
        }],
    },
    'Drive': ['Floppy', 'CD', 'DVD', 'Blue-ray'],
    'Graphics card': ['PCI', 'AGP', 'PCIe'],
    },
    'Memory card controller',
    'Audio controller',
    'GPU',
]

connection_schema = [{
    'Computer': [{
        'Casing': [{
            'Motherboard': [{
                'CPU': ['CPU Core', 'Memory controller'],
                'Graphics card': ['GPU'],
                },
                'Chipset',
                'RAM',
                'Memory card controller',
                'Audio controller'
            ],
            },
            'Power supply',
            'Harddrive',
            'Drive'
        ],
    }]
}]

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
            #'DDR SDRAM': [ 'DDR-200', 'DDR-266', 'DDR-333', 'DDR-400' ],
            'DDR SDRAM': {'<import>': 'DDR_SDRAM'},
            'DDR2 SDRAM': {'<import>': 'DDR2_SDRAM'},
            'DDR3 SDRAM': {'<import>': 'DDR3_SDRAM'},
        }]
    },

    'CPU Socket': [ 'Socket 1155', 'Socket 423', 'Socket 478' ],
    'PCI': [ 'PCI 1.0', 'PCI 2.0', 'PCI 2.1', 'PCI 2.2', 'PCI 2.3', 'PCI 3.0' ], # http://en.wikipedia.org/wiki/Conventional_PCI#History
    'PCI Express': [ 'PCIe 1.0a', 'PCIe 1.1', 'PCIe 2.0', 'PCIe 2.1', 'PCIe 3.0' ], # http://en.wikipedia.org/wiki/PCI_Express#History_and_revisions
    'USB': [ 'USB 1', 'USB 2.0', 'USB 3.0' ],
    'SATA Standard': [ 'SATA 1.0', 'SATA 2.0', 'SATA 3.0', 'SATA 3.1', 'SATA 3.2' ],
    'Memory card': [ 'SD card', 'MMC card', 'MMCplus card', 'xD card', 'MS card', 'MS PRO card' ],
    'DirectX': {
        '<attr_types>': ('Release date', 'Version number'),
        '<children>':['DirectX 1.0', 'DirectX 2.0', 'DirectX 2.0a', 'DirectX 3.0', 'DirectX 3.0a', 'DirectX 3.0b', 'DirectX 4.0', 'DirectX 5.0', 'DirectX 5.2',
                      'DirectX 6.0', 'DirectX 6.1', 'DirectX 6.1a', 'DirectX 7.0', 'DirectX 7.0a', 'DirectX 7.1', 'DirectX 8.0', 'DirectX 8.0a', 'DirectX 8.1',
                      'DirectX 8.1a', 'DirectX 8.1b', 'DirectX 8.2', 'DirectX 9.0', 'DirectX 9.0a', 'DirectX 9.0b', 'DirectX 9.0c', 'DirectX 10', 'DirectX 10.1',
                      'DirectX 11', 'DirectX 11.1'],
    },
    'OpenGL': {
        '<attr_types>': ('Release date',),
        '<children>':['OpenGL 1.0', 'OpenGL 1.1', 'OpenGL 1.2', 'OpenGL 1.2.1', 'OpenGL 1.3', 'OpenGL 1.4', 'OpenGL 1.5', 'OpenGL 2.0', 'OpenGL 2.1', 'OpenGL 3.0',
                      'OpenGL 3.1', 'OpenGL 3.2', 'OpenGL 3.3', 'OpenGL 4.0', 'OpenGL 4.1', 'OpenGL 4.2', 'OpenGL 4.3'],
    },
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
            {
            'CPU-Socket': [{
                'Intel Sockets': ['DIP', 'PLICC', 'Socket 1', 'Socket 2', 'Socket 3', 'Socket 4', 'Socket 6', 'Socket 8', 'Slot 1', 'Slot 2', 'Socket 423', 'Socket 478/Socket N',
                                  'Socket 495', 'PAC418', 'Socket 603', 'Socket 604', 'Socket 479', 'LGA 775/Socket T', 'Socket M', 'LGA 771/Socket J', 'Socket P', 'Socket 441',
                                  'LGA 1366/Socket B', 'rPGA 988A/Socket G1', 'LGA 1156/Socket H', 'LGA 1248', 'LGA 1567', 'LGA 1155/Socket H2', 'LGA 2011/Socket R', 'rPGA 988B/Socket G2'
                                  'LGA 1150/Socket H3', 'Socket G3/Socket G3'],
                'AMD Sockets': ['Slot A', 'Socket 462/Socket A', 'Socket 754', 'Socket 940', 'Socket 939', 'Socket 563', 'Socket S1', 'Socket AM2', 'Socket F', 'Socket AM2+',
                                'Socket AM3', 'Socket G34', 'Socket C32', 'Socket FM1', 'Socket AM3+', 'Socket FM2', ],
                'Various': ['Socket 5', 'Socket 7', 'Super Socket 7', 'Socket 463/Socket NexGen', 'Socket 587', 'Slot B', 'Socket 370', 'PAC611'],
            }],
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
            'SATA port', 'Audio port', 'SD card port', 'MMC card port', 'MMCplus card port',
            'xD card port', 'MS card port', 'MS PRO card port'
        ]
    },
}]


parts = [{
    'CPU Core': [
        'Intel 80486', 'P5', 'P6', 'Intel Core [Core]', 'Enhanced Pentium M',
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
        'Intel CPUs': [
            { 'Pentium 4': {
                '<children>': [
                    {
                    'Intel Pentium 4 2.80GHz 15.2.9': {
                        '<attrs>': { 'Vendor': 'Intel','Version': '15.2.9', 'Frequency': '2800' },
                        '<standards>': ('32bit',)
                    },
                }],

                '<import>': 'Pentium4_Willamette'
                },
            },
            'Intel Pentium', 'Intel Pentium MMX', 'Intel Atom', 'Intel Celeron', 'Intel Pentium Pro', 'Intel Pentium II', 'Intel Pentium III', 'Intel Xeon',
            'Pentium 4 Extreme Edition',
            'Pentium M', 'Pentium D/EE', 'Intel Pentium New', 'Intel Core', 'Intel Core 2', 'Intel Core i3', 'Intel Core i5', 'Intel Core i7',
            'Mobile Pentium 4',
            {
            'Intel Pentium Dual-Core': [{
                'Intel Pentium Processor G645 (2,9 GHz)': {
                    '<attrs>': { 'Number of cores': '2', 'Frequency': '2900', 'Front side bus': '5000', 'Maximal power consumption': '65', 'Vendor': 'Intel' },
                    '<standards>': ('SSE 4.x', '64bit', 'XD bit', 'Smart Cache' ),
                },
            }],
            }
        ],
        'AMD CPUs': [
            {
            'AMD K6 [AMD K6]': ['Model6', 'Littlefoot'],
            'AMD K6-2': ['Chomper', 'Chomper Extended', 'Mobile [AMD K6-2]'],
            },
            'Am386', 'Am486', 'Am5x86', 'AMD K5', 'AMD K6-3', 'Athlon', 'Athlon XP/MP',  'Duron', 'Athlon 4', 'Athlon XP-M', 'Mobile Duron', 'Sempron'
            'Opteron', 'Athlon 64 FX', 'Athlon 64',  'Athlon 64 X2', 'Sempron', 'Mobile Athlon 64', 'Mobile Sempron', 'Turion 64', 'Turion 64 X2',
            'Phenom', 'Athlon X2', 'Phenom II', 'Athlon II', 'Turion II', 'FX',
        ]
    }],
    'Computer': [{
        'Desktop': [{
            'HP d530 CMT(DF368A)': { '<attrs>': { 'Vendor': 'Hewlett-Packard', 'Serial number': 'CZC4301WB9', }},
            'Acer Aspire M1935': { '<attrs>': { 'Vendor': 'Acer' } },
        }],
    }],
    'Casing': [{
        'Anonymous Mini Tower': { '<attrs>': { 'Vendor': 'Hewlett-Packard', 'Casing Size': 'Minitower' } },
        'Anonymous Tower': {
            '<attrs>': { 'Width': '180', 'Length': '379', 'Height': '402', 'Color': 'black'},
             '<connectors>': ['SD card port', 'MMC card port', 'MMCplus card port', 'xD card port', 'MS card port', 'MS PRO card port' ],
         },
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
        'Anonymous Motherboard': {
            '<attrs>': { 'Maximal RAM capacity': 16384 },
            '<connectors>': [
                'PCIe x16 Socket',
                'Anonymous RJ-45',
                'SATA port',
                'CPU-Socket',
                {
                '240-pin DIMM (DDR3 SDRAM)': {'<quantity>': 4,},
                'Anonymous USB 2.0 Port': { '<quantity>': 6 },
                'Anonymous USB 3.0 Port': { '<quantity>': 2 },
                'Audio port': { '<quantity>': 2 },
                },
            ]
        },
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
        'SATA': [{'Anonymous harddrive': { '<attrs>': { 'Harddrive size': 500 } },}],
    }],
    'Memory card controller': [{
        'Anonymous card reader controller': {
            '<standards>': (
                'SD card', 'MMC card', 'MMCplus card',
                'xD card', 'MS card', 'MS PRO card')
        }
    }],
    'GPU': [
        {
        'Intel': [
            'Intel740', '752', 'Extreme Graphics', 'Extreme Graphics 2',
            'GMA 900', 'GMA 950', 'GMA 3100', 'GMA 3150', 'GMA 3000', 'GMA X3000', 'GMA X3500', 'GMA X3100',
            'GMA 4500', 'GMA X4500', 'GMA X4500HD', 'GMA 4500MHD', 'GMA 500', 'GMA 600', 'GMA', 'GMA 3600', 'GMA 3650'
            'HD Graphics', 'HD Graphics 2000' 'HD Graphics 3000', 'HD Graphics P3000', 'HD Graphics 4000', 'HD Graphics P4000'],
        'ATI': [{
            'ATI Wonder': ['Wonder MDA/CGA', 'Wonder EGA', 'Wonder VGA'],
            'ATI Mach': ['Mach 8', 'Mach 32', 'Mach 64'],
            'ATI Rage': ['3D Rage', '3D Rage II', 'Rage XL', 'Rage Pro', 'Rage 128 VR', 'Rage 128 GL', 'Rage 128 Pro', 'Rage Fury MAXX'],
        }],
        'ATI/AMD': [{
            'ATI/AMD Desktop': [{
                'Radeon R100': [
                    {'Radeon R100 AGP/PCI': ['Radeon 7000', 'Radeon 7100', 'Radeon 7200', 'Radeon 7500', 'Radeon 7500 LE', 'Radeon 7500 VIVO']},
                    {'Radeon R100 IGP': ['Radeon 320', 'Radeon 330', 'Radeon 340']},
                ],
                'Radeon R200': [
                    {'Radeon R200 AGP/PCI': ['Radeon 8500', 'Radeon 8500 LE', 'Radeon 9000', 'Radeon 9000 Pro', 'Radeon 9100', 'Radeon 9200', 'Radeon 9200 SE', 'Radeon 9250']},
                    {'Radeon R200 IGP': ['Radeon 9000 [IGP]', 'Radeon 9100 [IGP]', 'Radeon 9100 Pro']},
                ],
                'Radeon R300': [
                    {'Radeon R300 AGP/PCI': ['Radeon 9500', 'Radeon 9500 Pro', 'Radeon 9550', 'Radeon 9550 SE', 'Radeon 9600', 'Radeon 9600 Pro', 'Radeon 9600 SE', 'Radeon XT [AGP/PCI]', 'Radeon 9700', 'Radeon 9700 Pro', 'Radeon 9800', 'Radeon 9800 XL', 'Radeon 9800 Pro', 'Radeon 9800 SE']},
                    {'Radeon R300 PCI-E': ['Radeon X300', 'Radeon X300 LE', 'Radeon SE', 'Radeon SE Hyper Memory', 'Radeon X550', 'Radeon X600 Pro', 'Radeon XT [PCI-E]', 'Radeon X1050']},
                    {'Radeon R300 IGP': ['Radeon Xpress X200', 'Radeon Xpress 1100', 'Radeon Xpress 1150']},
                ],
                'Radeon R400': [
                    {'Radeon R400 AGP': ['Radeon X700 [AGP]', 'Radeon X700 Pro', 'Radeon X800 SE', 'Radeon X800 GT', 'Radeon X800 [AGP]', 'Radeon X800 GTO', 'Radeon X800 Pro [AGP]', 'Radeon X800 XL', 'Radeon X800 XT', 'Radeon X800 XT PE', 'Radeon X850 Pro [AGP]', 'Radeon X850 XT', 'Radeon X850 XT PE']},
                    {'Radeon R400 PCI-E': ['Radeon X700 SE', 'Radeon X700 LE', 'Radeon X700 [PCI-E]', 'Radeon X700 Pro [PCI-E]', 'Radeon X700 XT', 'Radeon X800 GT 128 MB', 'Radeon X800 GT 256MB', 'Radeon X800 [PCI-E]', 'Radeon X800 GTO 128MB', 'Radeon X800 GTO 256 MB', 'Radeon X800 Pro [PCI-E]', 'Radeon X800 Xl [PCI-E]', 'Radeon X800 XT [PCI-E]', 'Radeon X800 XT Platinum Edition', 'Radeon X850 Pro [PCI-E]', 'Radeon X850 XT [PCI-E]', 'Radeon X850 XT CrossFire Master', 'Radeon X850 XT Platinum Edition']},
                    {'Radeon R400 IGP': ['Radeon Xpress X1200', 'Radeon Xpress X1250', 'Radeon Xpress 2100']}
                ],
                'Radeon R500': [],
                'Radeon R600': [],
                'All-In-Wonder': [],
                'Radeon R700': [],
                'Evergreen': [],
                'Northern Islands': [],
                'Southern Islands': [],
                'Sea Islands': [],
            }],
            'ATI/AMD Mobile': [],
            'ATI/AMD Workstation': [],
        }],
        'Nvidia': [{
            'Nvidia Desktop': ['Riva', 'GeForce256', 'GeForce2', 'GeForce3', 'GeForce4', 'GeForceFX', 'GeForce6', 'GeForce7', 'GeForce8', 'GeForce9', 'GeForce100', 'GeForce200', 'GeForce300', 'GeForce400', 'GeForce500', 'GeForce600', 'GeForce700'],
            'Nvidia Mobile': ['GeForce2 Go', 'GeForce4 Go', 'GeForce FX Go 5', 'GeForce Go 6', 'GeForce Go 7', 'GeForce 8M', 'GeForce 9M', 'GeForce 100M', 'GeForce 200M', 'GeForce 300M', 'GeForce 400M', 'GeForce 500M', 'GeForce 600M', 'GeForce 700M', 'Mobility Quadro', 'GeForce Quadro NVS'],
            'Nvidia Workstation': ['Quadro', 'Quadro NVS', 'Tesla'],
        }],
        },
        'test graphics processor',
    ],
    'Graphics card': [{
        'PCIe': ['test graphics card a', 'test graphics card b'],
    }],
}]



systems = [{
    'test graphics card a': {'<no_connector>': ['test graphics processor']},
    'test graphics card b': {'<no_connector>': ['test graphics processor']},

    'HP d530 CMT(DF368A)': {
        '<no_connector>': ['Anonymous Mini Tower', '085Ch', 'Intel Pentium 4 2.80GHz 15.2.9'],
    },
    'Acer Aspire M1935': {
        '<no_connector>': [{
            'Anonymous Tower': {
                '<no_connector>': [
                    'Anonymous Power Source',
                    {
                    'Anonymous Motherboard': {
                        '<no_connector>': [ 'Intel B75 Express', 'Audio controller', 'Anonymous card reader controller'],
                        '<connectors>': [
                            {
                            'SATA port': ['Anonymous harddrive'],
                            'CPU-Socket': [{
                                'Intel Pentium Processor G645 (2,9 GHz)': {
                                    '<no_connector>': ['Anonymous Memory Controller']
                                }
                            }],
                            '240-pin DIMM (DDR3 SDRAM)': [
                                {'Anonymous RAM': { '<quantity>': 2} },
                            ],
                            },
                        ]
                    }
                }],
            }
        }]
    },
    'Harddrive': { #connection test
        '<no_connector>': [{
            'Anonymous Mini Tower': {
                 '<no_connector>': [{
                    'Anonymous Motherboard': {
                        '<no_connector>': ['Intel Pentium Processor G645 (2,9 GHz)', 'test graphics card a']
                    }
                }]
            }
        }]
    },
}]

os = [{
    'Windows': [
        {
        'Windows 1': ['Windows 1.01', 'Windows 1.02', 'Windows 1.03', 'Windows 1.04'],
        'Windows 2': ['Windows 2.03', 'Windows 2.10', 'Windows 2.11'],
        'Windows 3': ['Windows 3.0', 'Windows 3.1', 'Windows 3.2'],
        'Windows for Workgroups': ['Windows for Workgroups 3.1', 'Windows for Workgroups 3.11'],
        'Windows NT 3': ['Windows NT 3.1', 'Windows NT 3.5', 'Windows NT 3.51'],
        },
        'Windows NT 4', 'Windows 95', 'Windows 98', 'Windows ME', 'Windows 2000', 'Windows XP ', 'Windows Mobile 6', 'Windows Server 2003',
        'Windows Vista', 'Windows Server 2008', 'Windows Embedded CE 6.0', 'Windows Home Server', 'Windows Phone 7', 'Windows 7', 'Windows 8'
    ],
    'Linux': [
        '1.0.0', '1.1', '1.2', '1.3', '2.0', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.6.20', '2.6.21', '2.6.22', '2.6.23', '2.6.24',
        '2.6.25', '2.6.26', '2.6.27', '2.6.28', '2.6.29', '2.6.30', '2.6.31', '2.6.32', '2.6.33', '2.6.34', '2.6.35', '2.6.36', '2.6.37',
        '2.6.38', '2.6.39', '3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7'
    ],
    },
    'MS-DOS',
    'FreeBSD',
    'NetBSD'


]
