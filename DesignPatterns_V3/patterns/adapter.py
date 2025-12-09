"""Adapter for normalizing GPS metadata from PIL EXIF dumps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class GPSData:
    latitude: Optional[float]
    longitude: Optional[float]

    def is_valid(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def to_display(self) -> str:
        if self.is_valid():
            return f"GPS: {self.latitude:.5f}, {self.longitude:.5f}"
        return "GPS: не обнаружены"

    def to_dict(self) -> Dict[str, Optional[float]]:
        return {"latitude": self.latitude, "longitude": self.longitude}


class GpsMetadataAdapter:
    """Adapter: converts nested EXIF tuples into decimal GPS data."""

    @staticmethod
    def convert(gps_info: Dict[int, Any]) -> GPSData:
        def to_degrees(value):
            d = value[0][0] / value[0][1]
            m = value[1][0] / value[1][1]
            s = value[2][0] / value[2][1]
            return d + (m / 60.0) + (s / 3600.0)

        lat = to_degrees(gps_info[2]) if 2 in gps_info else None
        lon = to_degrees(gps_info[4]) if 4 in gps_info else None

        lat_ref = gps_info.get(1, "N")
        lon_ref = gps_info.get(3, "E")

        if lat is not None and lat_ref.upper() != "N":
            lat = -lat
        if lon is not None and lon_ref.upper() != "E":
            lon = -lon
        return GPSData(latitude=lat, longitude=lon)
