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

# for now, this only works with two peptides
PEPTIDE_WELLS = ["A1", "A2"]
FRZ_WELL = "A12"
PEPTIDE_AMOUNT = 8
FRZ_AMOUNT = 2
LYSATE_AMOUNT = 8


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
        protocol.pause("Confirm plates of lysate are present in the correct locations.")
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
                    ),  # Grab from 6mm above the bottom of the plate to avoid lysate goo. TODO change this when switch to eCPX.
                    row.top(
                        z=-2
                    ),  # Dispense at the top of the well so that pipette tip is not contaminated.
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
            #    protocol.load_labware('nest_96_wellplate_2ml_deep', 1),
            #    protocol.load_labware('nest_96_wellplate_2ml_deep', 2),
            protocol.load_labware_from_definition(deepwell_def, 1),
            protocol.load_labware_from_definition(deepwell_def, 2),
        ]
        well384 = protocol.load_labware_from_definition(grenier384_def, 3)
    else:
        deepwell_plates = [
            protocol.load_labware("labcon_96_wellplate_2200ul", 1),
            protocol.load_labware("labcon_96_wellplate_2200ul", 2),
        ]
        well384 = protocol.load_labware("grenierbioone_384_wellplate_138ul", 3)

    well12 = protocol.load_labware("nest_12_reservoir_15ml", 4)

    tip_racks = [
        protocol.load_labware("opentrons_96_tiprack_20ul", 11),
        protocol.load_labware("opentrons_96_tiprack_20ul", 10),
        protocol.load_labware("opentrons_96_tiprack_20ul", 9),
        protocol.load_labware("opentrons_96_tiprack_20ul", 8),
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
        # right_pipette.distribute(
        #     PEPTIDE_AMOUNT,
        #     well12.wells_by_name()[well],
        #     well384.rows()[n],
        #     blowout_location="source well",
        # )  # This will draw extra into the pipette to be able to dispense at multiple places with the same movement. Saves time.
        right_pipette.transfer(
            PEPTIDE_AMOUNT, well12.wells_by_name()[well], well384.rows()[n]
        )
        # print("transferred: ", n, well)
        amounts["peptides"][n + 1] += PEPTIDE_AMOUNT * 8 * len(well384.rows()[n])

    # Now distribute the two, 96 well plates of mutants into the 384 well plate.
    consolidate_plate(protocol, right_pipette, deepwell_plates, well384, PEPTIDE_AMOUNT)

    # Pause and confirm ready to add FRZ
    protocol.pause("Confirm that FRZ is in the appropriate well and ready.")

    # Now add FRZ
    right_pipette.transfer(
        FRZ_AMOUNT,
        well12.wells_by_name()[FRZ_WELL],
        well384.wells(),
        new_tip="always",
        # mix_after=(3, 20), # If this is skipped, mix on the plate reader.
    )
    amounts["frz"] += 384 * FRZ_AMOUNT

    print("Amounts of reagents used: ", amounts)
