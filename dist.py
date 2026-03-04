from math import radians, sin, cos, sqrt, atan2

def distancia_geografica(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en metros
    R = 6371000  

    # Convertir grados a radianes
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distancia = R * c
    return distancia

# Ejemplo de uso
lat1, lon1 = -34.59, -58.39  # Jujuy
lat2, lon2 = -34.591, -58.391  # Buenos Aires

print(f"Distancia: {distancia_geografica(lat1, lon1, lat2, lon2):.2f} metros")
