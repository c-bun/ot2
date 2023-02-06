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
675,104,8,A,4
679,86,8,A,8
686,86,8,B,3
689,86,8,B,6
690,86,8,B,7
692,86,8,B,9
694,86,8,B,11
701,86,8,C,6
702,86,8,C,7
704,104,8,C,9
709,86,8,D,2
711,86,8,D,4
714,86,8,D,7
716,86,8,D,9
723,86,8,E,4
727,86,8,E,8
728,86,8,E,9
739,86,8,F,8
748,86,8,G,5
750,86,8,G,7
751,86,8,G,8
752,86,8,G,9
753,86,8,G,10
758,104,8,H,3
760,104,8,H,5
769,86,9,A,2
772,86,9,A,5
773,86,9,A,6
778,86,9,A,11
779,86,9,A,12
788,86,9,B,9
818,104,9,E,3
835,86,9,F,8
837,86,9,F,10
843,86,9,G,4
850,86,9,G,11
862,86,9,H,11
867,104,10,A,4
868,86,10,A,5
869,86,10,A,6
872,86,10,A,9
874,86,10,A,11
884,86,10,B,9
887,86,10,B,12
889,86,10,C,2
890,104,10,C,3
894,86,10,C,7
895,104,10,C,8
897,86,10,C,10
906,86,10,D,7
910,86,10,D,11
914,104,10,E,3
915,86,10,E,4
916,86,10,E,5
922,86,10,E,11
925,86,10,F,2
927,86,10,F,4
928,86,10,F,5
930,86,10,F,7
931,86,10,F,8
932,86,10,F,9
933,104,10,F,10
934,86,10,F,11
938,104,10,G,3
946,86,10,G,11
948,86,10,H,1
952,86,10,H,5
954,86,10,H,7
958,86,10,H,11
966,104,11,A,7
975,104,11,B,4
977,86,11,B,6
981,86,11,B,10
984,104,11,C,1
986,104,11,C,3
987,104,11,C,4
988,86,11,C,5
998,104,11,D,3
999,104,11,D,4
1000,104,11,D,5
1001,104,11,D,6
1005,86,11,D,10
1016,104,11,E,9
1018,86,11,E,11
1022,104,11,F,3
1029,104,11,F,10
1032,86,11,G,1
1034,104,11,G,3
1036,104,11,G,5
1039,104,11,G,8
1041,104,11,G,10
1042,104,11,G,11
1043,104,11,G,12
1046,104,11,H,3
1048,104,11,H,5
1050,104,11,H,7
1053,104,11,H,10
1083,86,12,C,4
1105,86,12,E,2
1106,86,12,E,3
1107,86,12,E,4
1117,86,12,F,2
1119,86,12,F,4
1120,86,12,F,5
1128,86,12,G,1
1132,86,12,G,5
1144,86,12,H,5
1150,104,12,H,11
1153,104,13,A,2
1158,86,13,A,7
1162,86,13,A,11
1163,86,13,A,12
1167,86,13,B,4
1172,86,13,B,9
1174,86,13,B,11
1187,86,13,C,12
1195,86,13,D,8
1196,104,13,D,9
1197,86,13,D,10
1221,104,13,F,10
1224,104,13,G,1
1226,104,13,G,3
1235,104,13,G,12
1249,86,14,A,2
1251,104,14,A,4
1254,104,14,A,7
1255,104,14,A,8
1257,104,14,A,10
1266,104,14,B,7
1268,104,14,B,9
1269,86,14,B,10
1271,104,14,B,12
1274,104,14,C,3
1281,104,14,C,10
1287,104,14,D,4
1290,104,14,D,7
1292,104,14,D,9
1295,86,14,D,12
1297,104,14,E,2
1298,104,14,E,3
1300,86,14,E,5
1302,104,14,E,7
1305,104,14,E,10
1307,104,14,E,12
1312,104,14,F,5
1313,104,14,F,6
1314,104,14,F,7
1322,104,14,G,3
1323,104,14,G,4
1328,104,14,G,9
1329,104,14,G,10
1330,104,14,G,11
1332,104,14,H,1
1334,104,14,H,3
1337,104,14,H,6
1343,104,14,H,12
1352,104,15,A,9
1369,104,15,C,2
1375,104,15,C,8
1393,104,15,E,2
1399,104,15,E,8
1421,104,15,G,6
1422,104,15,G,7
1425,104,15,G,10
1426,104,15,G,11
1428,104,15,H,1
1438,104,15,H,11
1439,104,15,H,12
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
