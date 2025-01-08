from functools import partial
from collections.abc import Callable

from manim import VMobject
from ..managers.id_manager import IDManager

def _hide_func(mo, val):
    if val is True:
        mo.set_opacity(0)
    else:
        mo.set_opacity(1)


def _id_func(mo, val):
    IDManager().add(val, mo) 
    return None


custom_props: dict = {
    'id': _id_func,
    'opacity': lambda mo, val: mo.set_opacity(val),
    'hide': _hide_func
}


def funcs_from_props(props, only_custom_props=False):

    funcs = []
    for custom_prop in custom_props:
        if custom_prop in props:
            f = custom_props[custom_prop]
            val = props.pop(custom_prop)
            funcs.append(partial(f, val=val))

    if only_custom_props:
        return funcs, props

    for prop in list(props.keys()):
        f = getattr(VMobject, prop, None)
        if isinstance(f, Callable):
            val = props.pop(prop)
            funcs.append(
                partial(lambda mo, f, val: f(mo, val), f=f, val=val)
            )

    if props:
        funcs.append(lambda mo: mo.set(**props))

    return funcs, props
