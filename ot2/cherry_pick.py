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
CHERRY_PICK_AMOUNT = 5

# Specify where you want each peptide to go for the epp tube rack.
TO_PICK_POSITIONS = (
    {  # to specify the locations of the peptide names in the epp tube rack
        "86": "A1",
        "104": "B1",
    }
)

# Paste CSV file here.
CSV_RAW = """
,to_pick,deck_position,row,column,plate_label
peptide,,,,,
67,86,1,F,5,3
93,104,1,H,7,3
63,104,1,F,12,3
39,104,1,D,12,3
83,104,1,G,9,3
85,104,1,H,10,3
71,104,1,F,9,3
64,104,1,F,2,3
57,104,1,E,7,3
52,104,1,E,2,3
92,104,1,H,6,3
27,86,1,C,12,3
8,86,1,A,6,3
91,86,1,H,5,3
29,86,1,C,3,3
95,86,1,H,9,3
41,86,1,D,3,3
26,86,1,C,11,3
74,86,1,G,11,3
53,86,1,E,3,3
175,104,2,G,5,4
189,104,2,H,7,4
185,104,2,H,3,4
161,104,2,F,3,4
191,104,2,H,9,4
178,104,2,G,8,4
182,104,2,H,11,4
186,104,2,H,4,4
187,104,2,H,5,4
181,104,2,H,10,4
167,86,2,F,9,4
105,86,2,A,7,4
135,86,2,D,12,4
183,86,2,H,12,4
166,86,2,F,8,4
180,86,2,H,1,4
149,86,2,E,3,4
121,86,2,C,10,4
176,86,2,G,6,4
159,86,2,F,12,4
233,104,3,D,3,7
275,104,3,G,9,7
196,104,3,A,2,7
234,104,3,D,4,7
211,104,3,B,5,7
232,104,3,D,2,7
235,104,3,D,5,7
246,104,3,E,4,7
264,104,3,G,1,7
243,104,3,E,12,7
280,86,3,H,2,7
201,86,3,A,7,7
220,86,3,C,2,7
214,86,3,B,8,7
209,86,3,B,3,7
271,86,3,G,5,7
236,86,3,D,6,7
259,86,3,F,5,7
267,86,3,G,12,7
282,86,3,H,4,7
374,104,4,H,11,8
302,104,4,B,11,8
322,104,4,C,8,8
375,104,4,H,12,8
381,104,4,H,7,8
350,104,4,F,11,8
326,104,4,D,11,8
307,104,4,B,5,8
370,104,4,G,8,8
372,104,4,H,1,8
335,86,4,D,9,8
337,86,4,E,10,8
320,86,4,C,6,8
340,86,4,E,2,8
292,86,4,A,2,8
310,86,4,B,8,8
361,86,4,G,10,8
378,86,4,H,4,8
321,86,4,C,7,8
294,86,4,A,4,8
468,104,5,H,1,A
395,104,5,A,9,A
394,104,5,A,8,A
425,104,5,D,3,A
439,104,5,E,5,A
476,104,5,H,6,A
391,104,5,A,5,A
457,104,5,G,10,A
414,104,5,C,4,A
410,104,5,C,11,A
452,86,5,F,6,A
398,86,5,B,11,A
465,86,5,G,7,A
417,86,5,C,7,A
409,86,5,C,10,A
399,86,5,B,12,A
434,86,5,E,11,A
449,86,5,F,3,A
422,86,5,D,11,A
453,86,5,F,7,A
521,104,6,D,3,B
533,104,6,E,3,B
555,104,6,G,12,B
525,104,6,D,7,B
538,104,6,E,8,B
503,104,6,B,9,B
515,104,6,C,9,B
544,104,6,F,2,B
523,104,6,D,5,B
575,104,6,H,9,B
486,86,6,A,4,B
534,86,6,E,4,B
553,86,6,G,10,B
532,86,6,E,2,B
554,86,6,G,11,B
512,86,6,C,6,B
574,86,6,H,8,B
573,86,6,H,7,B
558,86,6,G,4,B
537,86,6,E,7,B
604,104,7,C,2,C
663,104,7,H,12,C
648,104,7,G,1,C
641,104,7,F,3,C
584,104,7,A,6,C
668,104,7,H,6,C
650,104,7,G,11,C
664,104,7,H,2,C
634,104,7,E,8,C
658,104,7,G,8,C
590,86,7,B,11,C
577,86,7,A,10,C
611,86,7,C,9,C
632,86,7,E,6,C
599,86,7,B,9,C
618,86,7,D,4,C
592,86,7,B,2,C
657,86,7,G,7,C
621,86,7,D,7,C
580,86,7,A,2,C
679,104,8,A,5,D
734,104,8,F,11,D
694,104,8,B,8,D
721,104,8,E,10,D
729,104,8,E,7,D
744,104,8,G,1,D
706,104,8,C,8,D
736,104,8,F,2,D
728,104,8,E,6,D
754,104,8,G,8,D
724,86,8,E,2,D
710,86,8,D,11,D
689,86,8,B,3,D
713,86,8,D,3,D
738,86,8,F,4,D
693,86,8,B,7,D
683,86,8,A,9,D
704,86,8,C,6,D
678,86,8,A,4,D
681,86,8,A,7,D
"""

# Read the CSV file and return a list of dictionaries.
csv_data = CSV_RAW.splitlines()[1:]
# if the first entry of the second line is 'peptide', remove it.
if csv_data[1].split(",")[0] == "peptide":
    csv_data.pop(1)  # Remove the second entry from the list of cherries.
print("Read CSV: ", csv_data)
cherries = list(csv.DictReader(csv_data))

# Find the set of the plate number column, this will map on to the plate positions.
plate_positions = set([int(row["deck_position"]) for row in cherries])  # type: Set[int]
# Sort the plate positions.
plate_positions = sorted(plate_positions)  # type: List[int]
number_of_plates = len(plate_positions)  # type: int

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
            plate_positions.index(
            int(cherry["deck_position"])
            )
        )
        origin_well = cherry["row"] + str(cherry["column"])
        destination = TO_PICK_POSITIONS[cherry["to_pick"]]

        # Every 8 cherries, home the pipette.
        # TODO I don't think this actually does anything.
        if i % 8 == 0:
            home_after = True
        else:
            home_after = False

        left_pipette.transfer(
            CHERRY_PICK_AMOUNT,
            well96_plates[origin_plate][origin_well],
            epp_tubes[destination],
            home_after=home_after,
            touch_tip=True,
            mix_before=(1,10),
        )
