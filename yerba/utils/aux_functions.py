from __future__ import annotations
import os
import shutil
from manim.utils.family import extract_mobject_family_members
from manim import VMobject

from ..logger_setup import logger, console
from ..defaults import parser_params


def better_error_messages(custom_msg=None, verbose=None):
    """
    IMPORTANT: If custom_msg=None, the first argument, after self,
    of the decorated function must be "text". TODO: Explain this.
    """

    if verbose is None:
        verbose = parser_params["errors.verbose"]

    def inner_decorator(func):
        def wrapped(*f_args, **f_kwargs):
            try:
                return func(*f_args, **f_kwargs)
            except BaseException as e:
                if verbose:
                    console.print_exception(suppress=(__file__,))

                elif custom_msg is None:
                    msg = f_kwargs.pop("text", None)
                    if msg is None:
                        msg = f_args[1]
                        if not isinstance(msg, str):
                            logger.error(
                                f"[red]Better error messages ERROR ??[/red]"
                                f"\n{func.__name__} did not receive a string as the first argument",
                                extra={"markup": True, "highlighter": None},
                            )
                            quit()

                    t = (
                        msg.replace(r"%20", r" ")
                        .replace(r"%22", r'"')
                        .replace(r"%5B", r"[")
                        .replace(r"%5D", r"]")
                    )
                    logger.error(
                        f"There seems to be an error with the following line:\n[blue]{t}[/blue]"
                        f"\n[red]Error message[/red]: {e}",
                        extra={"markup": True, "highlighter": None},
                    )

                elif isinstance(custom_msg, str):
                    logger.error(
                        custom_msg + f"\n[red]Error message[/red]: {e}",
                        extra={"markup": True, "highlighter": None},
                    )

                else:
                    raise ValueError("'custom_msg' must be None or an str")

                quit()

        return wrapped

    return inner_decorator


def define_default_kwargs(new, **defaults):
    return {**defaults, **new}


def look_for_parent_box_recursively(box):
    if box.parent_box is None:
        return box
    else:
        box = look_for_parent_box_recursively(box)


def restructure_list_to_exclude_certain_family_members(mobject_list, to_remove):
    """
    Modified version of the function
    `manim.utils.family_opts.restructure_list_to_exclude_certain_family_members`.
    This version raise a value error if any member of to_remove is not a child of
    the mobject_list.

    ---
    Removes anything in to_remove from mobject_list, but in the event that one of
    the items to be removed is a member of the family of an item in mobject_list,
    the other family members are added back into the list.

    This is useful in cases where a scene contains a group, e.g. Group(m1, m2, m3),
    but one of its submobjects is removed, e.g. scene.remove(m1), it's useful
    for the list of mobject_list to be edited to contain other submobjects, but not m1.
    """
    new_list = []
    to_remove = extract_mobject_family_members(to_remove)

    def add_safe_mobjects_from_list(list_to_examine, set_to_remove):
        removed = False
        for mob in list_to_examine:
            if mob in set_to_remove:
                removed = True
                continue
            intersect = set_to_remove.intersection(mob.get_family())
            if intersect:
                removed = True
                add_safe_mobjects_from_list(mob.submobjects, intersect)
            else:
                new_list.append(mob)
        if not removed:
            raise ValueError("Couldn't find the mobject in the list")

    add_safe_mobjects_from_list(mobject_list, set(to_remove))

    return new_list


def replace_in_list(
    mobj_list: list[VMobject], old_m: VMobject, new_m: VMobject
) -> None:
    """
    Modified version of the function `manim.Scene.replace`
    """
    # We use breadth-first search because some Mobjects get very deep and
    # we expect top-level elements to be the most common targets for replace.
    for i in range(0, len(mobj_list)):
        # Is this the old mobject?
        if mobj_list[i] == old_m:
            # If so, write the new object to the same spot and stop looking.
            mobj_list[i] = new_m
            return
    # Now check all the children of all these mobs.
    for mob in mobj_list:  # noqa: SIM110
        if replace_in_list(mob.submobjects, old_m, new_m):
            # If we found it in a submobject, stop looking.
            return
    # If we did not find the mobject in the mobject list or any submobjects,
    # (or the list was empty), indicate we did not make the replacement.
    raise ValueError("Couldn't find the mobject in the list")


def create_folder_structure():
    if not os.path.exists("./media"):
        os.mkdir("./media")

    if not os.path.exists("./media/slides"):
        os.mkdir("./media/slides")

    if not os.path.exists("./media/old_slides"):
        os.mkdir("./media/old_slides")


def check_dependencies():
    if not shutil.which("rsvg-convert"):
        logger.error("rsvg-convert is not installed or it is not in the system's PATH.")
        quit()
    if not shutil.which("xetex"):
        logger.error("xetex is not installed or it is not in the system's PATH.")
        quit()
