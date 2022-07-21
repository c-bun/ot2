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
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
13,104,1,B,10
28,104,1,C,2
29,104,1,C,3
32,104,1,C,6
35,104,1,C,9
40,104,1,D,2
41,104,2,D,3
42,104,3,D,6
43,104,4,D,9
"""

# Read the CSV file and return a list of dictionaries.
csv_data = CSV_RAW.splitlines()[1:]
csv_data.pop(1)  # Remove the second entry from the list of cherries.
print("Read CSV: ", csv_data)
cherries = list(csv.DictReader(csv_data))

# Find the max value in the plate number column, this is the number of plates.
number_of_plates = max([int(row["plate_number"]) for row in cherries])  # type: int

# Error to raise if there are setup issues.
class SetupError(Exception):
    pass


# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    # This should be the right tube rack.
    epp_tubes = protocol.load_labware("opentrons_24_tuberack_nest_1.5ml_snapcap", 11)

    # Try loading the 96 well plate. If not found, try loading from file.
    try:
        # These need to be the locally-defined strings.
        well96_def = "celltreat_96_wellplate_350ul"

        well96_plates = [
            protocol.load_labware(well96_def, i + 1) for i in range(number_of_plates)
        ]
    except:
        # Try loading from file in the case that we are testing.
        well96_def = json.load(
            open(
                "../labware/celltreat_96_wellplate_350ul/celltreat_96_wellplate_350ul.json"
            )
        )
        well96_plates = [
            protocol.load_labware_from_definition(well96_def, i + 1)
            for i in range(number_of_plates)
        ]

    # Fill the remaining positions with tip racks according to the number of cherries in the CSV.
    number_of_racks_needed = len(cherries) // 96 + 1
    # Try loading tipracks, catch DeckConflictError.
    try:
        tip_racks = [
            protocol.load_labware("opentrons_96_tiprack_20ul", 10 - i)
            for i in range(number_of_racks_needed)
        ]
    except:
        raise SetupError(
            "You have too many different 96 well plates in the CSV relative to the number of tips you'll need."
        )

    left_pipette = protocol.load_instrument(
        "p20_single_gen2", "left", tip_racks=tip_racks
    )

    for i, cherry in enumerate(cherries):
        origin_plate = (
            int(cherry["plate_number"]) - 1
        )  # Plates in CSV will be 1 indexed
        origin_well = cherry["row"] + str(cherry["column"])
        destination = TO_PICK_POSITIONS[cherry["to_pick"]]

        # Every 8 cherries, home the pipette.
        if i % 8 == 0:
            home_after = True
        else:
            home_after = False

        left_pipette.transfer(
            CHERRY_PICK_AMOUNT,
            well96_plates[origin_plate][origin_well],
            epp_tubes[destination],
            home_after=home_after,
        )
