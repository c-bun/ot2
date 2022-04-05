
from opentrons import protocol_api
import time

# metadata
metadata = {
    'protocolName': 'Distribute Peptides 384',
    'author': 'Colin Rathbun <rathbunc@dickinson.edu>',
    'description': 'Distribute a 96 well plate plus 4 substrates into a 384 well plate.',
    'apiLevel': '2.12'
}

# for now, this only works with two peptides
PEPTIDE_WELLS = ['A1','A2']
FRZ_WELL = 'A12'

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    amounts = {
        'peptides':{
            1:0,
            2:0,
        },
        'frz':0
    }

    # labware
    deepwell_plates = [
        protocol.load_labware('nest_96_wellplate_2ml_deep', 1),
        protocol.load_labware('nest_96_wellplate_2ml_deep', 2)
    ]
    well384 = protocol.load_labware('corning_384_wellplate_112ul_flat', 3)
    well12 = protocol.load_labware('nest_12_reservoir_15ml', 4)

    tip_racks = [
        protocol.load_labware('opentrons_96_tiprack_20ul', 11),
        protocol.load_labware('opentrons_96_tiprack_20ul', 10),
        protocol.load_labware('opentrons_96_tiprack_20ul', 9),
        protocol.load_labware('opentrons_96_tiprack_20ul', 8),
        protocol.load_labware('opentrons_96_tiprack_20ul', 7),
        protocol.load_labware('opentrons_96_tiprack_20ul', 6),
        protocol.load_labware('opentrons_96_tiprack_20ul', 5),
    ]

    # pipettes
    #left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=tip_racks)
    right_pipette = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=tip_racks)

    # Add peptides to wells first.
    for n, well in enumerate(PEPTIDE_WELLS):
        right_pipette.transfer(10, well12.wells_by_name()[well], well384.rows()[n])
        amounts['peptides'][n+1] += 10*8*len(well384.rows()[n])
    
    # Now distribute the two, 96 well plates of mutants into the 384 well plate.
    for n, plate in enumerate(deepwell_plates):
        for i, col in enumerate(plate.columns_by_name()):
            right_pipette.transfer(
                10, 
                plate.columns_by_name()[col], 
                well384.columns()[i + (12*n)], # so that the second plate is on the right side of the 384
                mix_before=(3,20), 
                mix_after=(3,20),
                new_tip='always'
                )
    
    # Wait 5 minutes for things to fully mix
    # Maybe this is when we can add tips to the deck??
    incubate_start = time.perf_counter()
    protocol.pause("Please add tips to any empty positions.")
    incubate_end = time.perf_counter()

    # This assumes that we added tips!!
    right_pipette.reset_tipracks()

    # Add additional delay if tips were replaced too quickly
    if incubate_end - incubate_start < 300:
        protocol.delay(seconds=300-(incubate_end-incubate_start))

    # Now add FRZ
    right_pipette.transfer(5, well12.wells_by_name()[FRZ_WELL], well384.wells(),
        new_tip='always',
        mix_after=(3,20)
    )
    amounts['frz']+=384*5
    
    print("Amounts of reagents used: ",amounts)
