from . import exc
from .main import gen_line


def B1Plastic(cid, group):
    yield from gen_line('B1Plastic')
    yield from B2Plastic(cid, group)


def B2Plastic(cid, group):
    yield from gen_line('B2Plastic')
    yield from B3_dict[group.walltype](cid)
    if cid.method == 1:  # LRFD
        yield from B4Plastic(cid)


def B3PlasticGeneral(cid):
    if cid.mode != 'ANALYS':
        raise exc.CIDProcessingError('General plastic pipe type for ANALYS mode only')
    yield from gen_line('B3PlasticAGeneral')


def B3PlasticSmooth(cid):
    if cid.mode == 'ANALYS':
        yield from gen_line('B3PlasticASmooth')
    elif cid.mode == 'DESIGN':
        if cid.method == 0:  # WSD
            yield from gen_line('B3PlasticDWSD')
        elif cid.method == 1:  # LRFD
            yield from gen_line('B3PlasticDLRFD')


def B3PlasticProfile(cid):
    if cid.mode != 'ANALYS':
        raise exc.CIDProcessingError('Profile plastic pipe type for ANALYS mode only')
    yield from gen_line('B3PlasticAProfile')
    yield from gen_line('B3bPlasticAProfile')


def B4Plastic(cid):
        yield from gen_line('B4Plastic')


B3_dict = dict(
                GENERAL=B3PlasticGeneral,
                SMOOTH=B3PlasticSmooth,
                PROFILE=B3PlasticProfile
                )
