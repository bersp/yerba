from __future__ import annotations

from typing import Any, Union

from manim import VMobject

from .singleton import SingletonMeta

IDType = Union[int, float, str]


class IDManager(metaclass=SingletonMeta):
    """
    A singleton class for managing IDs and their associated VMobjects.

    - The user chooses IDs, which can be int, float, or str.
    - ID 0 is privileged: it always holds exactly one VMobject,
      replacing any previously stored VMobject.
    """

    def __init__(self) -> None:
        self._data: dict[IDType, list[Any]] = {}

    def add(self, id_: IDType, mobjects: VMobject | list[VMobject]) -> None:
        """
        Adds a VMobject or a list of VMobjects under the specified ID.

        - If id_ is 0, only a single VMobject can be added, replacing any existing one.
        - For other IDs, a single VMobject is appended, or a list of VMobjects is extended.
        """
        if id_ == 0:
            if isinstance(mobjects, list):
                raise ValueError(
                    "ID 0 is privileged and can only hold a single VMobject."
                )
            self._data[0] = [mobjects]
        else:
            if isinstance(mobjects, list):
                if id_ not in self._data:
                    self._data[id_] = []
                self._data[id_].extend(mobjects)
            elif isinstance(mobjects, VMobject):
                if id_ not in self._data:
                    self._data[id_] = []
                self._data[id_].append(mobjects)
            else:
                raise ValueError(
                    f"Expected VMobject or list of VMobjects, but got {type(mobjects)}"
                )

    def get(self, id_: IDType) -> list[Any]:
        """
        Retrieves the list of VMobjects associated with the given ID.
        """
        if id_ in self._data:
            return self._data[id_]
        else:
            raise ValueError(f"ID {id_} not found")

    def replace(self, id_: IDType, old: VMobject, new: VMobject) -> None:
        """
        Replaces an old VMobject with a new VMobject under the specified ID.
        """
        try:
            mo_l = self._data[id_]
        except KeyError:
            raise ValueError(f"ID {id_} not found") from None

        try:
            index = mo_l.index(old)
            mo_l[index] = new
        except ValueError:
            raise ValueError(f"VMobject {old} not found under ID {id_}") from None

    def reset(self) -> None:
        """
        Resets the ID manager by clearing all stored data.
        """
        self._data.clear()

    def __str__(self) -> str:
        return f"IDS\n---\n{self._data}"
