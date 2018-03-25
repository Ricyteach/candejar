from . import exc
from ..cid.cidlineclasses import cidlineclasses

__all__ = 'A1 E1'.split()


def process(cid):
    for _ in A1(cid):
        pass

def gen_line(tag):
    '''Validate the CID tag'''
    yield getattr(cidlineclasses, tag) # execution pauses here

#@GeneratorObj
def A1(cid):
    yield from gen_line('A1')
    if cid.level == 3:
        from .L3 import L3
        yield from L3(cid)
    else:
        raise exc.CIDProcessingError('L1 and L2 not yet implemented')
    if cid.method == 1: #  LRFD
        for step_num, _ in enumerate(range(cid.nsteps), 1):
            yield from E1(cid)
        # cid.listener.throw(exc.SequenceComplete, ('Factors completed', len(cid.factors)))

#@GeneratorObj
def E1(cid):
    yield from gen_line('E1')