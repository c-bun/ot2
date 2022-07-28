from opentrons import protocol_api
import json
from typing import List

# metadata
metadata = {
    "protocolName": "Test mutants",
    "author": "Colin Rathbun <rathbunc@dickinson.edu>",
    "description": "Test up to 16 mutants with up to 8 conditions in triplicate in a single 384 well plate.",
    "apiLevel": "2.12",
}

NUMBER_OF_MUTANTS = 8  # up to 16
NUMBER_OF_CONDITIONS = 7  # up to 8 conditions

AMOUNT_OF_PEPTIDE = 10
AMOUNT_OF_FRZ = (
    2  # FRZ should be in the 12th column of the second (conditions) deepwell plate.
)
AMOUNT_OF_LYSATE = 10

# Error to raise if there are setup issues.
class SetupError(Exception):
    pass


# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    next_position = 11
    # Load the correct number of tip racks. Turns out this will only ever be one rack max!
    tip_racks = [protocol.load_labware("opentrons_96_tiprack_20ul", next_position)]
    next_position -= len(tip_racks)

    # Try loading the plates. If not found, try loading from file.
    try:
        # These need to be the locally-defined strings.
        deepwell96_def = "labcon_96_wellplate_2200ul"
        deepwell_mutants = protocol.load_labware(deepwell96_def, next_position)
        next_position -= 1
        deepwell_peptides = protocol.load_labware(deepwell96_def, next_position)
        next_position -= 1
        well384_def = "grenierbioone_384_wellplate_138ul"
        well384plate = protocol.load_labware(well384_def, next_position)
        next_position -= 1

    except:
        # Try loading from file in the case that we are testing.
        deepwell96_def = json.load(
            open(
                "../labware/labcon_96_wellplate_2200ul/labcon_96_wellplate_2200ul.json"
            )
        )
        deepwell_mutants = protocol.load_labware_from_definition(
            deepwell96_def, next_position
        )
        next_position -= 1
        deepwell_peptides = protocol.load_labware_from_definition(
            deepwell96_def, next_position
        )
        next_position -= 1
        well384_def = json.load(
            open(
                "../labware/grenierbioone_384_wellplate_138ul/grenierbioone_384_wellplate_138ul.json"
            )
        )
        well384plate = protocol.load_labware_from_definition(well384_def, next_position)
        next_position -= 1

    right_pipette = protocol.load_instrument(
        "p20_multi_gen2", "right", tip_racks=tip_racks
    )

    # First, transfer the mutants to the 384 well plate.
    right_pipette.pick_up_tip()
    right_pipette.distribute(
        AMOUNT_OF_LYSATE,
        deepwell_mutants.wells_by_name()["A1"],
        [
            well384plate.wells_by_name()["A{}".format(i + 1)]
            for i in range(NUMBER_OF_CONDITIONS * 3)
        ],
        new_tip="never",
        disposal_volume=0,
    )
    right_pipette.drop_tip()
    if NUMBER_OF_MUTANTS > 8:
        # The same thing needs to happen with the second column if there are mutants there.
        right_pipette.pick_up_tip()
        right_pipette.distribute(
            AMOUNT_OF_LYSATE,
            deepwell_mutants.wells_by_name()["A2"],
            [
                well384plate.wells_by_name()["B{}".format(i + 1)]
                for i in range(NUMBER_OF_CONDITIONS * 3)
            ],
            new_tip="never",
            disposal_volume=0,
        )
        right_pipette.drop_tip()

    # Now, transfer the peptides to the 384 well plate.
    for i in range(NUMBER_OF_CONDITIONS):
        right_pipette.pick_up_tip()  # each new condition gets a new tip
        right_pipette.distribute(
            AMOUNT_OF_PEPTIDE,
            deepwell_peptides.wells_by_name()["A{}".format(i + 1)],
            [
                well384plate.wells_by_name()["A{}".format(x + 1)].top(z=-5)
                for x in range(i * 3, i * 3 + 3)
            ],
            new_tip="never",
            disposal_volume=0,
        )
        if NUMBER_OF_MUTANTS > 8:
            right_pipette.distribute(
                AMOUNT_OF_PEPTIDE,
                deepwell_peptides.wells_by_name()["A{}".format(i + 1)],
                [
                    well384plate.wells_by_name()["B{}".format(x + 1)].top(z=-5)
                    for x in range(i * 3, i * 3 + 3)
                ],
                new_tip="never",
                disposal_volume=0,
            )
        right_pipette.drop_tip()

    # Pause protocol before FRZ addition.
    protocol.pause(
        "Please add FRZ to the 12th column of the second (conditions) deepwell plate."
    )

    # Now, transfer the FRZ to the 384 well plate.
    right_pipette.distribute(
        AMOUNT_OF_FRZ,
        deepwell_peptides.wells_by_name()[
            "A12"
        ],  # by definition, this is the 12th column of the second (conditions) deepwell plate.
        [
            well384plate.wells_by_name()["A{}".format(x + 1)].top(z=-1)
            for x in range(NUMBER_OF_CONDITIONS * 3)
        ],
        touch_tip=True,
        disposal_volume=0,
    )
    if NUMBER_OF_MUTANTS > 8:
        right_pipette.distribute(
            AMOUNT_OF_FRZ,
            deepwell_peptides.wells_by_name()["A12"],
            [
                well384plate.wells_by_name()["A{}".format(x + 1)].top(z=-1)
                for x in range(NUMBER_OF_CONDITIONS * 3)
            ],
            touch_tip=True,
            disposal_volume=0,
        )
