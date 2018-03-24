from . import exc, pipelookup, soil
from .main import gen_line

__all__ = 'A2 C1 C2 C3 C4 C5'.split()


def L3(cid):
    for group_num, _ in enumerate(range(cid.ngroups), 1):
        try:
            yield from A2(cid, group_num)
        except StopIteration:
            raise
        except Exception as e:
            raise exc.CIDProcessingError('cid failed at pipe group #'
                               '{:d}'.format(group_num)) from e
    # cid.listener.throw(exc.SequenceComplete, ('Groups completed', len(cid.groups)))
    yield from C1(cid)
    yield from C2(cid)
    yield from soil.D1(cid)


def A2(cid, group_num):
    yield from gen_line('A2')
    group = cid.groups[group_num-1]
    try:
        type_ = group.type_
        gen = pipelookup[type_]
        yield from gen(cid, group)
    except StopIteration:
        raise
    except Exception as e:
        raise exc.CIDProcessingError('cid section B failed for '
                       '{}'.format(group)) from e
    # cid.listener.throw(exc.ObjectComplete)


def C1(cid):
    yield from gen_line('C1')


def C2(cid):
    yield from gen_line('C2')
    for n_objs, gen, name, nplural in ((cid.nnodes, C3, 'node', 'nnodes'),
                              (cid.nelements, C4, 'element', 'nelements'),
                              (cid.nboundaries, C5, 'boundary', 'nboundaries')):
        for cid_obj_num in range(1, n_objs + 1):
            try:
                yield from gen(cid, cid_obj_num)
            except StopIteration:
                raise
            except Exception as e:
                raise exc.CIDProcessingError('cid L3.{} failed at {} #'
                               '{:d}'.format(gen.__name__, name,
                                             cid_obj_num)) from e
        # cid.listener.throw(exc.SequenceComplete, ('{}s completed'.format(name), getattr(cid, nplural)))


def C3(cid, node_num):
    yield from gen_line('C3')


def C4(cid, element_num):
    yield from gen_line('C4')


def C5(cid, bound_num):
    yield from gen_line('C5')
