from ..defaults import DEFAULT_COLORS
from .singleton import SingletonMeta


class ColorManager(metaclass=SingletonMeta):
    """
    A singleton class for managing named colors and their hexadecimal values.
    """

    def __init__(self) -> None:
        self._colors: dict[str, str] = DEFAULT_COLORS.copy()

    @property
    def colors(self) -> dict[str, str]:
        """
        Returns the dictionary of colors.
        """
        return self._colors

    def add_color(self, name: str, hex_value: str) -> None:
        """
        Adds a new color or updates an existing one.
        """
        self._colors[name] = hex_value

    def add_multiple_colors(self, new_colors: dict[str, str]) -> None:
        """
        Adds multiple colors to the ColorManager.
        """
        invalid_colors = {
            name: hex_val
            for name, hex_val in new_colors.items()
            if not self._is_valid_hex(hex_val)
        }
        if invalid_colors:
            invalid_entries = ", ".join(
                [f"'{name}': '{hex_val}'" for name, hex_val in invalid_colors.items()]
            )
            raise ValueError(f"The following hex values are invalid: {invalid_entries}")

        self._colors.update(new_colors)

    def get_color(self, name: str) -> str:
        """
        Retrieves the hexadecimal value of the specified color.
        """
        name = str(name).strip()
        if self._is_valid_hex(name):
            return name
        elif name in self._colors:
            return self._colors[name]
        else:
            raise ValueError(f"Color '{name}' not found.")

    def __str__(self) -> str:
        return f"COLORS\n-----\n{self._colors}"

    @staticmethod
    def _is_valid_hex(hex_value: str) -> bool:
        """
        Validates whether a string is a valid hexadecimal color code.
        """
        if isinstance(hex_value, str):
            if len(hex_value) == 7 and hex_value.startswith("#"):
                try:
                    int(hex_value[1:], 16)
                    return True
                except ValueError:
                    return False
        return False
