from opentrons import protocol_api
import time
import json
from typing import List

# metadata
metadata = {
    "protocolName": "Distribute Peptides 384",
    "author": "Colin Rathbun <rathbunc@dickinson.edu>",
    "description": "Distribute two 96 deepwell well plates plus 2 substrates into a 384 well plate.",
    "apiLevel": "2.12",
}

TESTING = True # TODO handle this with a try/except block

NUMBER_OF_DEEPWELL_PLATES = 2  # this can only be 2 right now
PEPTIDE_WELLS = ["A1", "A2"]  # for now, this only works with two peptides
FRZ_WELL = "A12"
PEPTIDE_AMOUNT = 8
FRZ_AMOUNT = 5 # this is in uL and should not be less than 5
LYSATE_AMOUNT = 8
USE_PAUSES = True

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    amounts = {
        "peptides": {
            1: 0,
            2: 0,
        },
        "frz": 0,
    }

    if TESTING:

        # custom labware
        deepwell_def = json.load(
            open(
                "../labware/labcon_96_wellplate_2200ul/labcon_96_wellplate_2200ul.json"
            )
        )
        grenier384_def = json.load(
            open(
                "../labware/grenierbioone_384_wellplate_138ul/grenierbioone_384_wellplate_138ul.json"
            )
        )

        deepwell_plates = [
            protocol.load_labware_from_definition(deepwell_def, c + 1)
            for c in range(NUMBER_OF_DEEPWELL_PLATES)
        ]
        well384 = protocol.load_labware_from_definition(grenier384_def, 3)
    else:
        deepwell_plates = [
            protocol.load_labware("labcon_96_wellplate_2200ul", c + 1)
            for c in range(NUMBER_OF_DEEPWELL_PLATES)
        ]
        well384 = protocol.load_labware("grenierbioone_384_wellplate_138ul", 3)

    well12 = protocol.load_labware("nest_12_reservoir_15ml", 4)

    tip_racks = [
        # protocol.load_labware("opentrons_96_tiprack_20ul", 11),
        # protocol.load_labware("opentrons_96_tiprack_20ul", 10),
        # protocol.load_labware("opentrons_96_tiprack_20ul", 9),
        # protocol.load_labware("opentrons_96_tiprack_20ul", 8),
        protocol.load_labware("opentrons_96_tiprack_20ul", 7),
        protocol.load_labware("opentrons_96_tiprack_20ul", 6),
        protocol.load_labware("opentrons_96_tiprack_20ul", 5),
    ]

    # pipettes
    right_pipette = protocol.load_instrument(
        "p20_multi_gen2", "right", tip_racks=tip_racks
    )

    # get a tip
    right_pipette.pick_up_tip()

    for amount, well in zip([3,5,10,15,20], ["A1", "A2", "A3", "A4", "A5"]):
        # Test FRZ addition volumes
        right_pipette.transfer(
            amount,
            well12.wells_by_name()[FRZ_WELL],
            well384.wells_by_name()[well],
            new_tip="never",
            #touch_tip=True,
            home_after=False,
            rate=0.5,
        )
    
    # drop the tip
    right_pipette.drop_tip()

    print("Amounts of reagents used: ", amounts)
