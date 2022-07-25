import json
from opentrons import protocol_api, types


TEST_TIPRACK_SLOT = '5'

RATE = 0.25  # % of default speeds
SLOWER_RATE = 0.1

PIPETTE_MOUNT = 'right'
PIPETTE_NAME = 'p20_single_gen2'


TIPRACK_DEF_JSON = """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"Fisher Inner","brandId":["02-717-134"]},"metadata":{"displayName":"Fisher Inner 96 Tip Rack 10 µL","displayCategory":"tipRack","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.6,"yDimension":85.4,"zDimension":33.4},"wells":{"A1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":76.26,"z":2.09},"B1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":67.27,"z":2.09},"C1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":58.28,"z":2.09},"D1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":49.29,"z":2.09},"E1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":40.3,"z":2.09},"F1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":31.31,"z":2.09},"G1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":22.32,"z":2.09},"H1":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":9.01,"y":13.33,"z":2.09},"A2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":76.26,"z":2.09},"B2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":67.27,"z":2.09},"C2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":58.28,"z":2.09},"D2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":49.29,"z":2.09},"E2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":40.3,"z":2.09},"F2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":31.31,"z":2.09},"G2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":22.32,"z":2.09},"H2":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":18,"y":13.33,"z":2.09},"A3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":76.26,"z":2.09},"B3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":67.27,"z":2.09},"C3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":58.28,"z":2.09},"D3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":49.29,"z":2.09},"E3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":40.3,"z":2.09},"F3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":31.31,"z":2.09},"G3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":22.32,"z":2.09},"H3":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":26.99,"y":13.33,"z":2.09},"A4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":76.26,"z":2.09},"B4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":67.27,"z":2.09},"C4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":58.28,"z":2.09},"D4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":49.29,"z":2.09},"E4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":40.3,"z":2.09},"F4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":31.31,"z":2.09},"G4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":22.32,"z":2.09},"H4":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":35.98,"y":13.33,"z":2.09},"A5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":76.26,"z":2.09},"B5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":67.27,"z":2.09},"C5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":58.28,"z":2.09},"D5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":49.29,"z":2.09},"E5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":40.3,"z":2.09},"F5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":31.31,"z":2.09},"G5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":22.32,"z":2.09},"H5":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":44.97,"y":13.33,"z":2.09},"A6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":76.26,"z":2.09},"B6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":67.27,"z":2.09},"C6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":58.28,"z":2.09},"D6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":49.29,"z":2.09},"E6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":40.3,"z":2.09},"F6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":31.31,"z":2.09},"G6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":22.32,"z":2.09},"H6":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":53.96,"y":13.33,"z":2.09},"A7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":76.26,"z":2.09},"B7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":67.27,"z":2.09},"C7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":58.28,"z":2.09},"D7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":49.29,"z":2.09},"E7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":40.3,"z":2.09},"F7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":31.31,"z":2.09},"G7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":22.32,"z":2.09},"H7":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":62.95,"y":13.33,"z":2.09},"A8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":76.26,"z":2.09},"B8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":67.27,"z":2.09},"C8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":58.28,"z":2.09},"D8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":49.29,"z":2.09},"E8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":40.3,"z":2.09},"F8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":31.31,"z":2.09},"G8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":22.32,"z":2.09},"H8":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":71.94,"y":13.33,"z":2.09},"A9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":76.26,"z":2.09},"B9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":67.27,"z":2.09},"C9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":58.28,"z":2.09},"D9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":49.29,"z":2.09},"E9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":40.3,"z":2.09},"F9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":31.31,"z":2.09},"G9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":22.32,"z":2.09},"H9":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":80.93,"y":13.33,"z":2.09},"A10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":76.26,"z":2.09},"B10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":67.27,"z":2.09},"C10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":58.28,"z":2.09},"D10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":49.29,"z":2.09},"E10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":40.3,"z":2.09},"F10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":31.31,"z":2.09},"G10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":22.32,"z":2.09},"H10":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":89.92,"y":13.33,"z":2.09},"A11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":76.26,"z":2.09},"B11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":67.27,"z":2.09},"C11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":58.28,"z":2.09},"D11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":49.29,"z":2.09},"E11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":40.3,"z":2.09},"F11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":31.31,"z":2.09},"G11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":22.32,"z":2.09},"H11":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":98.91,"y":13.33,"z":2.09},"A12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":76.26,"z":2.09},"B12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":67.27,"z":2.09},"C12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":58.28,"z":2.09},"D12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":49.29,"z":2.09},"E12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":40.3,"z":2.09},"F12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":31.31,"z":2.09},"G12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":22.32,"z":2.09},"H12":{"depth":31.31,"totalLiquidVolume":10,"shape":"circular","diameter":3.4,"x":107.9,"y":13.33,"z":2.09}},"groups":[{"metadata":{},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":true,"tipLength":31.31,"isMagneticModuleCompatible":false,"loadName":"fisherinner_96_tiprack_10ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""
TIPRACK_DEF = json.loads(TIPRACK_DEF_JSON)
TIPRACK_LABEL = TIPRACK_DEF.get('metadata', {}).get(
    'displayName', 'test labware')

metadata = {'apiLevel': '2.0'}


def run(protocol: protocol_api.ProtocolContext):
    tiprack = protocol.load_labware_from_definition(TIPRACK_DEF, TEST_TIPRACK_SLOT, TIPRACK_LABEL)
    pipette = protocol.load_instrument(
        PIPETTE_NAME, PIPETTE_MOUNT, tip_racks=[tiprack])

    num_cols = len(TIPRACK_DEF.get('ordering', [[]]))
    num_rows = len(TIPRACK_DEF.get('ordering', [[]])[0])


    def set_speeds(rate):
        protocol.max_speeds.update({
            'X': (600 * rate),
            'Y': (400 * rate),
            'Z': (125 * rate),
            'A': (125 * rate),
        })

        speed_max = max(protocol.max_speeds.values())

        for instr in protocol.loaded_instruments.values():
            instr.default_speed = speed_max

    set_speeds(RATE)
    firstwell = tiprack.well('A1')
    pipette.move_to(firstwell.top())
    protocol.pause("If the pipette is accurate click 'resume'")
    pipette.pick_up_tip()
    protocol.pause("If the pipette went into the center of the tip, click 'resume'")
    pipette.return_tip()
    protocol.pause("If the pipette successfully picked up the tip(s) but does not eject succesfully, pull the tip(s) off by hand and click 'resume'. Do not worry about tip ejection yet")

    last_col = (num_cols * num_rows) - num_rows
    if (PIPETTE_NAME == 'p20_multi_gen2' or PIPETTE_NAME == 'p300_multi_gen2'):
        well = tiprack.well(last_col)
        pipette.move_to(well.top())
        protocol.pause("If the position is accurate click 'resume'")
        pipette.pick_up_tip(well)
    else:
        last_well = (num_cols) * (num_rows)
        well = tiprack.well(last_well-1)
        pipette.move_to(well.top())
        protocol.pause("If the position is accurate click 'resume'")
        pipette.pick_up_tip(well)

    protocol.pause("If the pipette went to the center of the tip, click 'resume'")
    pipette.return_tip()
    protocol.comment("If the pipette successfully picked up the tip(s) but does not eject succesfully, pull the tip(s) off by hand and click 'resume'. Do not worry about tip ejection yet")

