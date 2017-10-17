#!/usr/bin/env python2

# Python port of the geo_pos_conv.hh from the Autoware project
# https://github.com/CPFL/Autoware
# Also adds the common planes for the Japanese coordinate system

from math import sin, cos, tan, pow, sqrt, floor
import math


class GeoPosConv:
    # http://www.gsi.go.jp/sokuchikijun/jpc.html
    coordinates = {
        1: {
            'lat': 2.26020138,
            'lon': 0.575958653,
            'desc': 'Southern Kyushu',
        },
        2: {
            'lat': 2.28638132,
            'lon': 0.575958653,
            'desc': 'Northern Kyushu',
        },
        3: {
            'lat': 2.30674349,
            'lon': 0.628318531,
            'desc': 'Chugoku',
        },
        4: {
            'lat': 2.33001455,
            'lon': 0.575958653,
            'desc': 'Shikoku',
        },
        5: {
            'lat': 2.34455896,
            'lon': 0.628318531,
            'desc': 'Kansai',
        },
        6: {
            'lat': 2.373647782712,
            'lon': 0.628318530717,
            'desc': 'Kansai, Kinki',
        },
        7: {
            'lat': 2.39400995732,
            'lon': 0.628318530717,
            'desc': 'Tokai',
        },
        9: {
            'lat': 2.4405520707,
            'lon': 0.628318530717,
            'desc': 'Tokyo',
        },
        10: {
            'lat': 2.45800536322535,
            'lon': 0.69813170079773,
            'desc': 'Tohoku',
        },
        11: {
            'lat': 2.44782328,
            'lon': 0.768138796,
            'desc': 'Southern Hokkaido',
        },
        12: {
            'lat': 2.48273086,
            'lon': 0.768138796,
            'desc': 'Western Hokkaido',
        },
        13: {
            'lat': 2.51763745,
            'lon': 0.768138796,
            'desc': 'Eastern Hokkaido',
        }
    }

    def __init__(self):
        self.m_x = None
        self.m_y = None
        self.m_z = None
        self.m_lat = None
        self.m_lon = None
        self.m_h = None
        self.m_PLato = None
        self.m_PLo = None

    def x(self):
        return self.m_x

    def y(self):
        return self.m_y

    def z(self):
        return self.m_z

    def set_plane(self, num):
        if num not in self.coordinates.keys():
            raise Exception("No such plane: {0}".format(num))
        self.m_PLato = self.coordinates[num]['lat']
        self.m_PLo = self.coordinates[num]['lon']

    def set_plane_latlon(self, lat, lon):
        self.m_PLato = lat
        self.m_PLo = lon

    def set_xyz(self, cx, cy, cz):
        self.m_x = cx
        self.m_y = cy
        self.m_z = cz
        self.conv_xyz2llh()

    def set_llh_nmea_degrees(self, latd, lond, h):
        # 1234.56 -> 12'34.56 -> 12 + 34.56/60
        lad = floor(latd / 100.0)
        lat = latd - lad * 100.0
        lod = floor(lond / 100.0)
        lon = lond - lod * 100.0

        # Changing Longitude and Latitude to Radians
        self.m_lat = (lad + lat / 60.0) * math.pi / 180
        self.m_lon = (lod + lon / 60.0) * math.pi / 180
        self.m_h = h

        self.conv_llh2xyz()

    def llh_to_xyz(self, lat, lon, ele):
        self.m_lat = lat * math.pi / 180
        self.m_lon = lon * math.pi / 180
        self.m_h = ele

        self.conv_llh2xyz()

    def conv_llh2xyz(self):
        Pmo = 0.9999

        # WGS84 Parameters
        AW = 6378137.0  # Semi-major Axis
        FW = 1.0 / 298.257222101  # //298.257223563 //Geometrical flattening

        Pe = 1.0 * sqrt(2.0 * FW - pow(FW, 2))
        Pet = 1.0 * sqrt(pow(Pe, 2) / (1.0 - pow(Pe, 2)))

        PA = 1.0 * 1.0 + 3.0 / 4.0 * pow(Pe, 2) + 45.0 / 64.0 * pow(Pe, 4) + 175.0 / 256.0 * pow(Pe, 6) + 11025.0 \
                / 16384.0 * pow(Pe, 8) + 43659.0 / 65536.0 * pow(Pe, 10) + 693693.0 / 1048576.0 * pow(Pe, 12) \
                + 19324305.0 / 29360128.0 * pow(Pe, 14) + 4927697775.0 / 7516192768.0 * pow(Pe, 16)

        PB = 1.0 * 3.0 / 4.0 * pow(Pe, 2) + 15.0 / 16.0 * pow(Pe, 4) + 525.0 / 512.0 * pow(Pe, 6) + 2205.0 / 2048.0 \
            * pow(Pe, 8) + 72765.0 / 65536.0 * pow(Pe, 10) + 297297.0 / 262144.0 * pow(Pe, 12) + 135270135.0 \
            / 117440512.0 * pow(Pe, 14) + 547521975.0 / 469762048.0 * pow(Pe, 16)

        PC = 1.0 * 15.0 / 64.0 * pow(Pe, 4) + 105.0 / 256.0 * pow(Pe, 6) + 2205.0 / 4096.0 * pow(Pe, 8) + 10395.0 \
            / 16384.0 * pow(Pe, 10) + 1486485.0 / 2097152.0 * pow(Pe, 12) + 45090045.0 / 58720256.0 * pow(Pe, 14) \
            + 766530765.0 / 939524096.0 * pow(Pe, 16)

        PD = 1.0 * 35.0 / 512.0 * pow(Pe, 6) + 315.0 / 2048.0 * pow(Pe, 8) + 31185.0 / 131072.0 * pow(Pe, 10) \
            + 165165.0 / 524288.0 * pow(Pe, 12) + 45090045.0 / 117440512.0 * pow(Pe, 14) + 209053845.0 / 469762048.0 \
            * pow(Pe, 16)

        PE = 1.0 * 315.0 / 16384.0 * pow(Pe, 8) + 3465.0 / 65536.0 * pow(Pe, 10) + 99099.0 / 1048576.0 * pow(Pe, 12) \
            + 4099095.0 / 29360128.0 * pow(Pe, 14) + 348423075.0 / 1879048192.0 * pow(Pe, 16)

        PF = 1.0 * 693.0 / 131072.0 * pow(Pe, 10) + 9009.0 / 524288.0 * pow(Pe, 12) + 4099095.0 / 117440512.0 * \
            pow(Pe, 14) + 26801775.0 / 469762048.0 * pow(Pe, 16)

        PG = 1.0 * 3003.0 / 2097152.0 * pow(Pe, 12) + 315315.0 / 58720256.0 * pow(Pe, 14) + 11486475.0 / 939524096.0 \
            * pow(Pe, 16)

        PH = 1.0 * 45045.0 / 117440512.0 * pow(Pe, 14) + 765765.0 / 469762048.0 * pow(Pe, 16)

        PI = 1.0 * 765765.0 / 7516192768.0 * pow(Pe, 16)

        PB1 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PA
        PB2 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PB / -2.0
        PB3 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PC / 4.0
        PB4 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PD / -6.0
        PB5 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PE / 8.0
        PB6 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PF / -10.0
        PB7 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PG / 12.0
        PB8 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PH / -14.0
        PB9 = 1.0 * AW * (1.0 - pow(Pe, 2)) * PI / 16.0

        PS = 1.0 * PB1 * self.m_lat + PB2 * sin(2.0 * self.m_lat) + PB3 * sin(4.0 * self.m_lat) + PB4 \
            * sin(6.0 * self.m_lat) + PB5 * sin(8.0 * self.m_lat) + PB6 * sin(10.0 * self.m_lat) + PB7 \
            * sin(12.0 * self.m_lat) + PB8 * sin(14.0 * self.m_lat) + PB9 * sin(16.0 * self.m_lat)

        PSo = 1.0 * PB1 * self.m_PLato + PB2 * sin(2.0 * self.m_PLato) + PB3 * sin(4.0 * self.m_PLato) + PB4 \
            * sin(6.0 * self.m_PLato) + PB5 * sin(8.0 * self.m_PLato) + PB6 * sin(10.0 * self.m_PLato) + PB7 \
            * sin(12.0 * self.m_PLato) + PB8 * sin(14.0 * self.m_PLato) + PB9 * sin(16.0 * self.m_PLato)

        PDL = 1.0 * self.m_lon - self.m_PLo
        Pt = 1.0 * tan(self.m_lat)
        PW = 1.0 * sqrt(1.0 - pow(Pe, 2) * pow(sin(self.m_lat), 2))
        PN = 1.0 * AW / PW
        Pnn = 1.0 * sqrt(pow(Pet, 2) * pow(cos(self.m_lat), 2))

        self.m_x = 1.0 * ((PS - PSo) + (1.0 / 2.0) * PN * pow(cos(self.m_lat), 2.0) * Pt * pow(PDL, 2.0) \
            + (1.0 / 24.0) * PN * pow(cos(self.m_lat), 4) * Pt * (5.0 - pow(Pt, 2) + 9.0 * pow(Pnn, 2) + 4.0 \
            * pow(Pnn, 4)) * pow(PDL, 4) - (1.0 / 720.0) * PN * pow(cos(self.m_lat), 6) * Pt * (-61.0 + 58.0 \
            * pow(Pt, 2) - pow(Pt, 4) - 270.0 * pow(Pnn, 2) + 330.0 * pow(Pt, 2) * pow(Pnn, 2)) * pow(PDL, 6) \
            - (1.0 / 40320.0) * PN * pow(cos(self.m_lat), 8) * Pt * (-1385.0 + 3111 * pow(Pt, 2) - 543 \
            * pow(Pt, 4) + pow(Pt, 6)) * pow(PDL, 8)) * Pmo

        self.m_y = 1.0 * (PN * cos(self.m_lat) * PDL - 1.0 / 6.0 * PN * pow(cos(self.m_lat), 3) * (-1 + pow(Pt, 2) \
            - pow(Pnn, 2)) * pow(PDL, 3) - 1.0 / 120.0 * PN * pow(cos(self.m_lat), 5) * (-5.0 + 18.0 * pow(Pt, 2) \
            - pow(Pt, 4) - 14.0 * pow(Pnn, 2) + 58.0 * pow(Pt, 2) * pow(Pnn, 2)) * pow(PDL, 5) - 1.0 / 5040.0 * PN \
            * pow(cos(self.m_lat), 7) * (-61.0 + 479.0 * pow(Pt, 2) - 179.0 * pow(Pt, 4) + pow(Pt, 6)) * pow(PDL, 7)) \
            * Pmo

        self.m_z = self.m_h

    def conv_xyz2llh(self):
        pass
