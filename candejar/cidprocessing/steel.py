from .main import gen_line

def B1Steel(cid, group):
    yield from gen_line('B1Steel')
    if cid.mode == 'ANALYS':
        yield from gen_line('B2SteelA')
    elif cid.mode == 'DESIGN':
        if cid.method == 0: #  WSD
            yield from gen_line('B2SteelDWSD')
        if cid.method == 1: #  LRFD
            yield from gen_line('B2SteelDLRFD')
    if group.jointslip: #  Slotted Joints
        yield from gen_line('B2bSteel')
        if cid.level > 1:
            yield from gen_line('B2cSteel')
            if group.varytravel: # Model of "Half Joints"
                yield from gen_line('B2dSteel')
    if cid.method == 1: #  LRFD
        yield from gen_line('B3SteelADLRFD')
