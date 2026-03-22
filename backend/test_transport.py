from app.data.metro_cities import get_transport_types, get_transport_info, CITY_TRANSPORT
print("Hubli:", get_transport_types('Hubli'))
print("Mumbai:", get_transport_types('Mumbai'))
print("Total cities:", len(CITY_TRANSPORT))
