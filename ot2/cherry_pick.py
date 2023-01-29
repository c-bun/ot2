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
        "104": "A1",
        "86": "B1",
    }
)

# Paste CSV file here.
CSV_RAW = """
,to_pick,plate_number,row,column
10,86,1,A,11
28,86,1,C,5
50,104,1,E,3
56,86,1,E,9
58,86,1,E,11
60,86,1,F,1
73,104,1,G,2
75,86,1,G,4
82,86,1,G,11
84,104,1,H,1
87,104,1,H,4
101,86,2,A,6
103,86,2,A,8
105,86,2,A,10
106,86,2,A,11
107,86,2,A,12
111,86,2,B,4
114,104,2,B,7
117,86,2,B,10
119,86,2,B,12
122,104,2,C,3
128,86,2,C,9
130,86,2,C,11
135,86,2,D,4
137,104,2,D,6
142,86,2,D,11
143,86,2,D,12
145,86,2,E,2
146,104,2,E,3
147,86,2,E,4
148,86,2,E,5
149,86,2,E,6
152,86,2,E,9
159,104,2,F,4
162,104,2,F,7
163,104,2,F,8
166,104,2,F,11
171,104,2,G,4
172,104,2,G,5
173,104,2,G,6
181,86,2,H,2
186,104,2,H,7
190,86,2,H,11
191,86,2,H,12
193,86,3,A,2
195,86,3,A,4
199,86,3,A,8
200,86,3,A,9
203,86,3,A,12
211,86,3,B,8
212,86,3,B,9
213,86,3,B,10
219,86,3,C,4
221,86,3,C,6
225,104,3,C,10
237,86,3,D,10
242,86,3,E,3
250,86,3,E,11
251,86,3,E,12
260,86,3,F,9
262,86,3,F,11
263,86,3,F,12
264,104,3,G,1
265,86,3,G,2
266,104,3,G,3
268,86,3,G,5
273,86,3,G,10
279,104,3,H,4
280,86,3,H,5
286,86,3,H,11
290,86,4,A,3
291,86,4,A,4
293,86,4,A,6
295,86,4,A,8
296,104,4,A,9
297,104,4,A,10
298,104,4,A,11
303,86,4,B,4
305,86,4,B,6
307,86,4,B,8
310,104,4,B,11
313,86,4,C,2
314,86,4,C,3
318,86,4,C,7
335,104,4,D,12
337,86,4,E,2
338,104,4,E,3
339,86,4,E,4
340,104,4,E,5
341,86,4,E,6
345,104,4,E,10
347,104,4,E,12
349,86,4,F,2
355,104,4,F,8
356,86,4,F,9
359,86,4,F,12
360,86,4,G,1
361,104,4,G,2
364,86,4,G,5
366,86,4,G,7
373,104,4,H,2
375,86,4,H,4
381,86,4,H,10
382,104,4,H,11
383,104,4,H,12
389,104,5,A,6
392,104,5,A,9
393,104,5,A,10
404,104,5,B,9
405,104,5,B,10
406,104,5,B,11
407,104,5,B,12
419,104,5,C,12
427,104,5,D,8
430,104,5,D,11
431,104,5,D,12
439,104,5,E,8
440,86,5,E,9
441,86,5,E,10
442,86,5,E,11
443,86,5,E,12
446,86,5,F,3
451,86,5,F,8
455,86,5,F,12
465,86,5,G,10
467,86,5,G,12
482,86,6,A,3
485,86,6,A,6
486,86,6,A,7
487,86,6,A,8
489,86,6,A,10
490,86,6,A,11
495,86,6,B,4
499,104,6,B,8
501,86,6,B,10
502,86,6,B,11
503,86,6,B,12
505,104,6,C,2
508,86,6,C,5
509,86,6,C,6
510,86,6,C,7
511,104,6,C,8
512,104,6,C,9
513,86,6,C,10
517,104,6,D,2
519,86,6,D,4
520,86,6,D,5
521,86,6,D,6
522,86,6,D,7
525,104,6,D,10
526,104,6,D,11
532,86,6,E,5
533,104,6,E,6
537,86,6,E,10
538,86,6,E,11
539,86,6,E,12
543,104,6,F,4
547,86,6,F,8
548,86,6,F,9
550,86,6,F,11
558,86,6,G,7
560,86,6,G,9
561,86,6,G,10
562,104,6,G,11
563,86,6,G,12
566,86,6,H,3
567,86,6,H,4
568,86,6,H,5
570,104,6,H,7
572,86,6,H,9
573,86,6,H,10
574,86,6,H,11
581,86,7,A,6
594,86,7,B,7
597,86,7,B,10
598,86,7,B,11
599,86,7,B,12
608,86,7,C,9
609,86,7,C,10
616,86,7,D,5
619,104,7,D,8
623,86,7,D,12
"""

# Read the CSV file and return a list of dictionaries.
csv_data = CSV_RAW.splitlines()[1:]
# if the first entry of the second line is 'peptide', remove it.
if csv_data[1].split(",")[0] == "peptide":
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
            touch_tip=True,
            mix_before=(3,10),
        )
