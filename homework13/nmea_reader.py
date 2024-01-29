#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 13

Execution: python3 nmea_reader.py
'''

from geopy.geocoders import Nominatim
from functools import partial


def convert_coordinates(lat, n_s, lon, e_w):
    lat = float(lat[:2]) + float(lat[2:]) / 60.0
    lon = float(lon[:3]) + float(lon[3:]) / 60.0
    if n_s == "S":
        lat *= -1
    if e_w == "W":
        lon *= -1
    return lat, lon


def parse_nmea_message(msg):
    parts = msg.split(",")

    if parts[0].endswith("GPRMC") and parts[2] == "A":
        lat = parts[3]
        n_s = parts[4]
        lon = parts[5]
        e_w = parts[6]
        date = parts[9]
        return lat, n_s, lon, e_w, date
    return None


def format_date(date):
    return f"{date[:2]}/{date[2:4]}/20{date[4:]}"


def main():
    print("My World Travels\n================")
    geolocator = Nominatim(user_agent="address finder")
    printed_addresses = []

    try:
        with open("my_travels.txt", "r") as f:
            for msg in f:
                data = parse_nmea_message(msg)
                if data:
                    lat, n_s, lon, e_w, date = data
                    coordinates = convert_coordinates(lat, n_s, lon, e_w)
                    date = format_date(date)
                    reverse = partial(geolocator.reverse, language="en")
                    location = reverse(coordinates)

                    if location:
                        address = location.address.split(',')
                        short_address = f"{address[0]},{address[-1]}"
                        if short_address not in printed_addresses:
                            printed_addresses.append(short_address)
                            print(f"Date: {date}\nVisited: {short_address}\n")

    except FileNotFoundError:
        print("nmea file not found")


main()
