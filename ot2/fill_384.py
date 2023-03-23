from opentrons import protocol_api
import json

# metadata
metadata = {
    "protocolName": "Fill 384 well plate",
    "author": "Colin Rathbun <rathbunc@dickinson.edu>",
    "description": "Fill a 384 well plate with a single reagent.",
    "apiLevel": "2.12",
}

TESTING = False
AMOUNT_TO_ADD = 5 # this is in uL and should not be less than 5
LOCATION_OF_REAGENT = "A1"
ADD_TO_TOP_OF_WELL = True

def populate_deck(
    protocol: protocol_api.ProtocolContext,
    next_open_position=1,
):

    if TESTING:
        well_plate = protocol.load_labware_from_definition(
                json.load(
                    open(
                        "../labware/grenierbioone_384_wellplate_138ul/grenierbioone_384_wellplate_138ul.json"
                    )
                ),
                next_open_position,
            )
        next_open_position += 1

    else:
        well_plate = protocol.load_labware(
                "grenierbioone_384_wellplate_138ul", next_open_position
            )
        
        
        next_open_position += 1

    # Load in a 12-well reservoir.
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", next_open_position)
    next_open_position += 1

        # Load in 4 tipracks.
    tip_racks = [
        protocol.load_labware("opentrons_96_tiprack_20ul", next_open_position + i)
        for i in range(4)
    ]

    print("""
    Loaded labware:
    - 384 well plate
    - 12 well reservoir
    - 4 tipracks
    """)

    return tip_racks, reservoir, well_plate

def run(protocol: protocol_api.ProtocolContext):
    
        # Load in labware.
        tip_racks, reservoir, well_plate = populate_deck(protocol)
    
        # Load in pipettes.
        pipette = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=tip_racks)
    
        # Add reagent to wells.
        pipette.transfer( # TODO this should be distribute in the future, and should pick up 20 uL and add 2 to each well.
            AMOUNT_TO_ADD,
            reservoir.wells_by_name()[LOCATION_OF_REAGENT],
            [x.top(z=-3) for x in well_plate.wells()],
            new_tip="once",
            touch_tip=True,
            home_after=False,
        )