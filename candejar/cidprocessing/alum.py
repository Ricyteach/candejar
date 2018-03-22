from .main import gen_line


def B1Alum(cid, group):
    yield from gen_line('B1Alum')
    if cid.mode == 'ANALYS':
        yield from gen_line('B2AlumA')
    elif cid.mode == 'DESIGN':
        if cid.method == 0: #  WSD
            yield from gen_line('B2AlumDWSD')
        if cid.method == 1: #  LRFD
            yield from gen_line('B2AlumDLRFD')
    if cid.method == 1: #  LRFD
        yield from gen_line('B3AlumADLRFD')
