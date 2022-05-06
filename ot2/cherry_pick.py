from typing import List
from opentrons import protocol_api
import time
import json
import csv

# metadata
metadata = {
    "protocolName": "Cherry pick hits",
    "author": "Colin Rathbun <rathbunc@dickinson.edu>",
    "description": "Given a CSV, cherry pick hits from 96 well plates into epp tubes",
    "apiLevel": "2.12",
}

# This should be False when not testing
TESTING = True

# Specify how much you want the robot to collect for each hit
CHERRY_PICK_AMOUNT = 10

# Specify where you want each peptide to go for the epp tube rack.
TO_PICK_POSITIONS = (
    {  # to specify the locations of the peptide names in the epp tube rack
        "104": "A1",
        "86": "B1",
    }
)

# Paste CSV file here.
CSV_RAW = """
,to_pick,plate_number,row,column
peptide,,,,
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
"""

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    if TESTING:
        well96_def = json.load(
            open(
                "../labware/celltreat_96_wellplate_350ul/celltreat_96_wellplate_350ul.json"
            )
        )
        well96_plates = [
            protocol.load_labware_from_definition(well96_def, 3),
            protocol.load_labware_from_definition(well96_def, 4),
        ]
    else:
        # These need to be the locally-defined strings.
        well96_def = "fisherbrand_96_wellplate_400ul"

        well96_plates = [
            protocol.load_labware(well96_def, 3),
            protocol.load_labware(well96_def, 4),
        ]

    # use this definition for now. Not sure if I'll need to define my particular epp tubes. TODO test this.
    epp_tubes = protocol.load_labware("opentrons_24_tuberack_nest_1.5ml_snapcap", 1)

    tip_racks = [
        protocol.load_labware("opentrons_96_tiprack_20ul", 11),
        protocol.load_labware("opentrons_96_tiprack_20ul", 10),
    ]

    left_pipette = protocol.load_instrument(
        "p20_single_gen2", "left", tip_racks=tip_racks
    )

    csv_data = CSV_RAW.splitlines()[1:]  # Discard the blank first line.
    cherries = csv.DictReader(csv_data)
    for i, cherry in enumerate(cherries):
        # the first line will be a heading that we don't want that's added by pandas.
        if i == 0:
            continue
        origin_plate = (
            int(cherry["plate_number"]) - 1
        )  # Plates in CSV will be 1 indexed
        origin_well = cherry["row"] + str(cherry["column"])
        destination = TO_PICK_POSITIONS[cherry["to_pick"]]

        left_pipette.transfer(
            CHERRY_PICK_AMOUNT,
            well96_plates[origin_plate][origin_well],
            epp_tubes[destination],
        )
