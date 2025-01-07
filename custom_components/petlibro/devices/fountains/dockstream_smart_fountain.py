"""Module containing the DockstreamSmartFountain class, which represents the Dockstream Smart Fountain device."""

from .fountain import Fountain


class DockstreamSmartFountain(Fountain):
    """A class representing the Dockstream Smart Fountain device."""

    @property
    def days_before_cleaning(self) -> int | None:
        """Number of days before fontain needs cleaning."""
        return self._data.get("remainingCleaningDays")

    @property
    def days_before_filter_replacement(self) -> int | None:
        """Number of days before filter needs to be replaced."""
        return self._data.get("remainingReplacementDays")

    @property
    def today_water_consumption(self) -> int | None:
        """Total water consumed today in mL."""
        return self._data.get("todayTotalMl")

    @property
    def remaining_water(self) -> int | None:
        """Remaining water in the fountain in mL."""

        # Assuming 1g of water is 1mL
        return self._data.get("weight")

    @property
    def water_level(self) -> int | None:
        """Water level percentage in the fountain."""
        return self._data.get("weightPercent")

    @property
    def filter_replacement_required(self) -> bool:
        """Whether the filter needs to be replaced."""
        return self.days_before_filter_replacement <= 0

    @property
    def cleaning_required(self) -> bool:
        """Whether the fountain needs cleaning."""
        return self.days_before_cleaning <= 0
