from __future__ import annotations
import math
from typing import Dict, List, Tuple


class Ring:
    """Anillo circular simplificado para comprobar zonas de emergencia.

    - inner_radius: radio interior (metros). Si un punto está a <= inner_radius -> zona 1.
    - outer_radius: radio exterior (metros). Si inner_radius < distancia <= outer_radius -> zona 2.
    - fuera si distancia > outer_radius -> zona 0.

    Métodos sencillos para filtrar listas de puntos y serializar el anillo.
    """

    METROS_POR_CUADRA = 100.0

    def __init__(
        self,
        latitude: float,
        longitude: float,
        inner_radius_m: float = 500.0,
        outer_radius_m: float = 600.0,
    ) -> None:
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.inner_radius = float(inner_radius_m)
        self.outer_radius = float(outer_radius_m)
        if self.outer_radius < self.inner_radius:
            raise ValueError("outer_radius_m must be >= inner_radius_m")

    def calculate_distance(self, to_lat: float, to_lon: float) -> float:
        """Devuelve la distancia en metros entre el centro del anillo y (to_lat, to_lon)."""
        R = 6371000.0
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(to_lat), math.radians(to_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def contains(self, latitude: float, longitude: float) -> int:
        """Comprueba en qué zona (0,1,2) cae el punto dado.

        Returns:
            1: dentro del radio interior (zona crítica)
            2: dentro del anillo exterior (zona de alerta)
            0: fuera de ambos radios
        """
        distance = self.calculate_distance(latitude, longitude)
        if distance <= self.inner_radius:
            return 1
        if distance <= self.outer_radius:
            return 2
        return 0

    def contains_exclusive(self, latitude: float, longitude: float, inner_radius_m: float) -> bool:
        """True si inner_radius_m < distancia <= outer_radius."""
        d = self.calculate_distance(latitude, longitude)
        return inner_radius_m < d <= self.outer_radius

    def filter_points_within(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Devuelve los puntos cuya distancia al centro es <= outer_radius."""
        return [(lat, lon) for lat, lon in points if self.calculate_distance(lat, lon) <= self.outer_radius]

    def filter_points_in_annulus(self, points: List[Tuple[float, float]], inner_radius_m: float) -> List[Tuple[float, float]]:
        """Devuelve puntos con inner_radius_m < distancia <= outer_radius."""
        return [(lat, lon) for lat, lon in points if inner_radius_m < self.calculate_distance(lat, lon) <= self.outer_radius]

    def filter_points_union(self, points: List[Tuple[float, float]], inner_radius_m: float) -> List[Tuple[float, float]]:
        """Union (sin duplicados) de puntos dentro del inner_radius_m y del anillo exterior."""
        seen = set()
        result: List[Tuple[float, float]] = []
        for lat, lon in points:
            key = (float(lat), float(lon))
            if key in seen:
                continue
            d = self.calculate_distance(lat, lon)
            if d <= inner_radius_m or (inner_radius_m < d <= self.outer_radius):
                seen.add(key)
                result.append(key)
        return result

    def to_dict(self) -> Dict:
        return {
            "center": {"latitude": self.latitude, "longitude": self.longitude},
            "inner_radius_m": self.inner_radius,
            "outer_radius_m": self.outer_radius,
            "inner_radius_blocks": self.inner_radius / self.METROS_POR_CUADRA,
            "outer_radius_blocks": self.outer_radius / self.METROS_POR_CUADRA,
        }

    def __repr__(self) -> str:
        return (
            f"Ring(latitude={self.latitude}, longitude={self.longitude}, "
            f"inner_radius={self.inner_radius}, outer_radius={self.outer_radius})"
        )