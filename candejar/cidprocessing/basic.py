from .main import gen_line

def B1Basic(cid, group):
    if cid.mode == 'ANALYS':
        yield from gen_line('B1Basic')
        yield from gen_line('B2Basic')
    elif cid.mode == 'DESIGN':
        raise ValueError("Can't use Basic pipe type with design mode.")
