
from opentrons import protocol_api
import time
import json

# metadata
metadata = {
    'protocolName': 'Distribute Peptides 384',
    'author': 'Colin Rathbun <rathbunc@dickinson.edu>',
    'description': 'Distribute a 96 well plate plus 2 substrates into two, 96 well plates.',
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
    # load custom plates?
    deepwell_def = json.load(open('../labware/labcon_96_wellplate_2200ul/labcon_96_wellplate_2200ul.json'))
    #use this one for now
    celltreat96_def = json.load(open('../labware/celltreat_96_wellplate_350ul/celltreat_96_wellplate_350ul.json'))

    deepwell_plates = [
    protocol.load_labware_from_definition(deepwell_def, 1),
    protocol.load_labware_from_definition(deepwell_def, 2),
    ]
    well96_plates = [
        protocol.load_labware_from_definition(celltreat96_def, 3),
        protocol.load_labware_from_definition(celltreat96_def, 4),
        protocol.load_labware_from_definition(celltreat96_def, 5),
        protocol.load_labware_from_definition(celltreat96_def, 6),
    ]
    
    well12 = protocol.load_labware('nest_12_reservoir_15ml', 7)

    tip_racks = [
        protocol.load_labware('opentrons_96_tiprack_20ul', 11),
        protocol.load_labware('opentrons_96_tiprack_20ul', 10),
        protocol.load_labware('opentrons_96_tiprack_20ul', 9),
        protocol.load_labware('opentrons_96_tiprack_20ul', 8),
    ]

    # pipettes
    right_pipette = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=tip_racks)

    # Add peptides to wells first.
    for n, dest_plate in enumerate(well96_plates):
        transfer_amount = 20
        peptide_well_target = PEPTIDE_WELLS[n%len(PEPTIDE_WELLS)]
        right_pipette.transfer(
            transfer_amount, 
            well12.wells_by_name()[peptide_well_target], 
            dest_plate.rows(),
            )
        amounts['peptides'][n%len(PEPTIDE_WELLS)+1] += transfer_amount*8*len(well96_plates[n].rows())
    
    # Now distribute the two, 96 well plates of mutants into the 96 blackwell plates.
    for n, dest_plate in enumerate(well96_plates):
        transfer_amount = 20
        deepwell_plate_target = n//len(deepwell_plates) # TODO is this going to alternate properly??
        right_pipette.transfer(
            transfer_amount,
            deepwell_plates[deepwell_plate_target].wells(),
            dest_plate.wells(),
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
    for plate in well96_plates:
        right_pipette.transfer(5, well12.wells_by_name()[FRZ_WELL], plate.wells(),
            new_tip='always',
            mix_after=(3,20)
        )
    amounts['frz']+=96*len(well96_plates)*5
    
    print("Amounts of reagents used: ",amounts)
