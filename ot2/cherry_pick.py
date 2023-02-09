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
1443,86,16,A,4
1445,104,16,A,6
1451,86,16,A,12
1457,104,16,B,6
1480,104,16,D,5
1499,86,16,E,12
1502,104,16,F,3
1504,86,16,F,5
1512,104,16,G,1
1516,104,16,G,5
1527,86,16,H,4
1528,86,16,H,5
1531,104,16,H,8
1533,104,16,H,10
1540,104,17,A,5
1573,104,17,D,2
1610,104,17,G,3
1618,104,17,G,11
1620,104,17,H,1
1622,104,17,H,3
1626,104,17,H,7
1641,86,18,A,10
1643,86,18,A,12
1646,104,18,B,3
1652,104,18,B,9
1658,86,18,C,3
1671,104,18,D,4
1690,104,18,E,11
1691,104,18,E,12
1696,104,18,F,5
1701,86,18,F,10
1707,104,18,G,4
1715,104,18,G,12
1718,104,18,H,3
1726,104,18,H,11
1736,86,19,A,9
1738,86,19,A,11
1743,86,19,B,4
1748,86,19,B,9
1749,86,19,B,10
1750,86,19,B,11
1756,104,19,C,5
1760,86,19,C,9
1761,86,19,C,10
1762,86,19,C,11
1766,104,19,D,3
1771,104,19,D,8
1790,104,19,F,3
1795,104,19,F,8
1805,104,19,G,6
1806,104,19,G,7
1809,86,19,G,10
1810,86,19,G,11
1814,104,19,H,3
1815,104,19,H,4
1817,86,19,H,6
1818,104,19,H,7
1821,104,19,H,10
1823,104,19,H,12
1827,104,20,A,4
1831,104,20,A,8
1833,86,20,A,10
1838,104,20,B,3
1840,104,20,B,5
1845,86,20,B,10
1853,104,20,C,6
1854,86,20,C,7
1856,104,20,C,9
1866,104,20,D,7
1867,104,20,D,8
1874,104,20,E,3
1876,104,20,E,5
1878,104,20,E,7
1887,104,20,F,4
1889,104,20,F,6
1893,104,20,F,10
1898,104,20,G,3
1899,104,20,G,4
1904,104,20,G,9
1906,86,20,G,11
1908,104,20,H,1
1909,104,20,H,2
1910,104,20,H,3
1917,104,20,H,10
1924,86,21,A,5
1926,104,21,A,7
1927,86,21,A,8
1933,86,21,B,2
1937,86,21,B,6
1938,86,21,B,7
1941,104,21,B,10
1942,86,21,B,11
1943,86,21,B,12
1945,104,21,C,2
1948,86,21,C,5
1950,86,21,C,7
1953,86,21,C,10
1954,86,21,C,11
1955,86,21,C,12
1957,104,21,D,2
1958,86,21,D,3
1959,104,21,D,4
1962,86,21,D,7
1966,86,21,D,11
1967,86,21,D,12
1972,86,21,E,5
1973,86,21,E,6
1974,86,21,E,7
1975,86,21,E,8
1978,86,21,E,11
1985,104,21,F,6
1988,86,21,F,9
1992,86,21,G,1
1993,86,21,G,2
1995,86,21,G,4
1997,86,21,G,6
2003,86,21,G,12
2004,104,21,H,1
2006,86,21,H,3
2011,86,21,H,8
2012,104,21,H,9
2013,104,21,H,10
2014,86,21,H,11
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
