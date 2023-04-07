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
,to_pick,plate_number,row,column
peptide,,,,
95,86,1,H,9
42,86,1,D,4
39,104,1,D,12
38,86,1,D,11
35,86,1,C,9
34,86,1,C,8
33,86,1,C,7
29,86,1,C,3
27,86,1,C,12
25,86,1,C,10
23,86,1,B,9
43,86,1,D,5
22,86,1,B,8
20,86,1,B,6
19,86,1,B,5
18,86,1,B,4
16,86,1,B,2
15,86,1,B,12
14,86,1,B,11
13,86,1,B,10
9,86,1,A,7
7,86,1,A,5
1,86,1,A,10
21,86,1,B,7
44,86,1,D,6
45,86,1,D,7
69,86,1,F,7
88,86,1,H,2
86,86,1,H,11
85,86,1,H,10
84,86,1,H,1
83,86,1,G,9
82,86,1,G,8
80,86,1,G,6
79,86,1,G,5
75,86,1,G,12
73,86,1,G,10
71,86,1,F,9
46,86,1,D,8
89,86,1,H,3
67,86,1,F,5
66,86,1,F,4
65,86,1,F,3
64,86,1,F,2
62,86,1,F,11
61,86,1,F,10
59,86,1,E,9
57,86,1,E,7
54,86,1,E,4
51,86,1,E,12
50,86,1,E,11
68,86,1,F,6
187,104,2,H,5
191,104,2,H,9
113,104,2,B,3
136,104,2,D,2
135,104,2,D,12
129,104,2,C,7
122,86,2,C,11
121,104,2,C,10
119,104,2,B,9
118,104,2,B,8
137,104,2,D,3
117,104,2,B,7
109,86,2,B,10
107,86,2,A,9
105,104,2,A,7
104,86,2,A,6
103,104,2,A,5
102,104,2,A,4
98,104,2,A,11
115,104,2,B,5
139,104,2,D,5
128,104,2,C,6
141,104,2,D,7
186,104,2,H,4
185,104,2,H,3
184,104,2,H,2
182,104,2,H,11
140,104,2,D,6
174,104,2,G,4
172,104,2,G,2
170,104,2,G,11
167,86,2,F,9
178,104,2,G,8
161,104,2,F,3
159,104,2,F,12
158,104,2,F,11
157,86,2,F,10
153,104,2,E,7
152,104,2,E,6
147,104,2,E,12
166,104,2,F,8
255,86,3,F,12
254,86,3,F,11
249,86,3,E,7
247,104,3,E,5
244,86,3,E,2
238,86,3,D,8
242,86,3,E,11
239,86,3,D,9
259,104,3,F,5
237,86,3,D,7
243,86,3,E,12
261,86,3,F,7
235,86,3,D,5
263,86,3,F,9
265,86,3,G,10
266,86,3,G,11
267,86,3,G,12
270,104,3,G,4
271,86,3,G,5
272,86,3,G,6
274,86,3,G,8
275,86,3,G,9
278,86,3,H,11
236,86,3,D,6
262,86,3,F,8
234,86,3,D,4
211,86,3,B,5
230,86,3,D,11
193,86,3,A,10
195,86,3,A,12
197,86,3,A,3
199,86,3,A,5
200,86,3,A,6
203,86,3,A,9
205,86,3,B,10
207,86,3,B,12
231,86,3,D,12
210,86,3,B,4
212,86,3,B,6
213,86,3,B,7
208,104,3,B,2
217,86,3,C,10
214,86,3,B,8
227,86,3,C,9
226,104,3,C,8
225,86,3,C,7
223,86,3,C,5
229,86,3,D,10
221,104,3,C,3
219,86,3,C,12
218,86,3,C,11
222,86,3,C,4
311,86,4,B,9
289,104,4,A,10
291,86,4,A,12
296,86,4,A,6
297,86,4,A,7
299,86,4,A,9
302,86,4,B,11
308,86,4,B,6
310,104,4,B,8
313,86,4,C,10
317,86,4,C,3
350,86,4,F,11
356,86,4,F,6
357,86,4,F,7
358,86,4,F,8
359,86,4,F,9
362,86,4,G,11
363,86,4,G,12
364,86,4,G,2
366,104,4,G,4
368,86,4,G,6
369,86,4,G,7
370,86,4,G,8
371,86,4,G,9
372,104,4,H,1
377,86,4,H,3
379,104,4,H,5
383,104,4,H,9
315,86,4,C,12
355,104,4,F,5
353,86,4,F,3
314,86,4,C,11
328,86,4,D,2
321,86,4,C,7
322,86,4,C,8
323,86,4,C,9
325,86,4,D,10
326,86,4,D,11
327,86,4,D,12
349,86,4,F,10
330,86,4,D,4
331,86,4,D,5
333,86,4,D,7
334,86,4,D,8
335,86,4,D,9
337,86,4,E,10
338,86,4,E,11
339,86,4,E,12
345,86,4,E,7
347,86,4,E,9
320,86,4,C,6
318,86,4,C,4
"""

# Read the CSV file and return a list of dictionaries.
csv_data = CSV_RAW.splitlines()[1:]
# if the first entry of the second line is 'peptide', remove it.
if csv_data[1].split(",")[0] == "peptide":
    csv_data.pop(1)  # Remove the second entry from the list of cherries.
print("Read CSV: ", csv_data)
cherries = list(csv.DictReader(csv_data))

# Find the set of the plate number column, this will map on to the plate positions.
plate_positions = set([int(row["plate_number"]) for row in cherries])  # type: Set[int]
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
            int(cherry["plate_number"])
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
