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

TESTING = False

NUMBER_OF_DEEPWELL_PLATES = 2  # this can only be 2 right now
PEPTIDE_WELLS = ["A1", "A2"]  # for now, this only works with two peptides
FRZ_WELL = "A12"
PEPTIDE_AMOUNT = 8
FRZ_AMOUNT = 5 # this is in uL and should not be less than 5
LYSATE_AMOUNT = 8
USE_PAUSES = True


def consolidate_plate(
    protocol: protocol_api.ProtocolContext,
    pipette: protocol_api.InstrumentContext,
    origin_plates: List[protocol_api.labware.Labware],
    destination_plate: protocol_api.labware.Labware,
    amount: int,
):
    """
    Consolidate a list of two 96 well plates into a single 384 well plate. The first 96 wells end up in the left side of the 384 well plate. The second 96 wells end up in the right side of the 384 well plate.

    :param pipette: pipette to use for consolidation
    :param origin_plates: list of origin plates
    :param destination_plate: destination plate
    :param amount: amount of material to consolidate
    """
    for n, origin_plate in enumerate(origin_plates):
        #protocol.pause("Confirm plates of lysate are present in the correct locations.")
        for i, col in enumerate(origin_plate.columns_by_name()):
            pipette.pick_up_tip()
            # Correctly iterate through A1 and B1 on the 384 well plate.
            # so that the second plate is on the right side of the 384 well plate.
            for row in destination_plate.columns()[i + (n * 12)][:2]:
                # print(row)
                pipette.transfer(
                    amount,
                    origin_plate.columns_by_name()[col][0].bottom(
                        z=4
                    ),  # Grab from 4mm above the bottom of the plate to avoid lysate goo. TODO change this when switch to eCPX.
                    row.bottom(
                        z=5
                    ),  # Dispense into the middle of the well so that pipette tip is not contaminated.
                    touch_tip=True,
                    new_tip="never",
                )
            pipette.drop_tip()


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

    # Add peptides to wells first.
    for n, well in enumerate(PEPTIDE_WELLS):
        # TODO: this should be able to work regardless of the number of deepwell plates.
        if NUMBER_OF_DEEPWELL_PLATES == 2:
            right_pipette.transfer(
                PEPTIDE_AMOUNT, well12.wells_by_name()[well], well384.rows()[n]
            )
            amounts["peptides"][n + 1] += PEPTIDE_AMOUNT * 8 * len(well384.rows()[n])
        else:
            right_pipette.transfer(
                PEPTIDE_AMOUNT, well12.wells_by_name()[well], well384.rows()[n][:12]
            )
            amounts["peptides"][n + 1] += (
                PEPTIDE_AMOUNT * 8 * len(well384.rows()[n]) / 2
            )

    # Now distribute the two, 96 well plates of mutants into the 384 well plate.
    if USE_PAUSES:
        protocol.pause("Confirm plates of lysate are present in the correct locations.") # pause in case the plates are not currently on the deck
    consolidate_plate(protocol, right_pipette, deepwell_plates, well384, PEPTIDE_AMOUNT)

    # Pause and confirm ready to add FRZ
    if USE_PAUSES:
        protocol.pause("Confirm that FRZ is in the appropriate well and ready.")

    # Now add FRZ
    right_pipette.transfer( # TODO this should be distribute in the future, and should pick up 20 uL and add 2 to each well.
        FRZ_AMOUNT,
        well12.wells_by_name()[FRZ_WELL],
        [x.top(z=-2) for x in well384.wells()],
        new_tip="once",
        touch_tip=True,
        home_after=False,
    )
    amounts["frz"] += 384 * FRZ_AMOUNT

    print("Amounts of reagents used: ", amounts)
