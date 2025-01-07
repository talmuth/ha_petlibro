"""Module contains device definitions for the Petlibro custom components."""

from .device import Device
from .feeders.granary_camera_feeder import GranaryCameraFeeder
from .feeders.granary_feeder import GranaryFeeder
from .fountains.dockstream_smart_fountain import DockstreamSmartFountain

product_name_map: dict[str, type[Device]] = {
    "Granary Feeder": GranaryFeeder,
    "Granary Camera Feeder": GranaryCameraFeeder,
    "Dockstream Smart Fountain": DockstreamSmartFountain,
}
