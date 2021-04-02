import math as m

class ProjMapper:
    '''
    From Class for georeferencing Lab34 projs
       Alexey Zagumenov FEB RAS
    '''
    def __init__(self, 
                 pt, # porjection type -1
                 lon, # left bottom longitude
                 lat, # left bottom latitude
                 lon_size, # longitude region size
                 lat_size, # latitude region size
                 lon_res, # longitude resolution per pixel in degrees
                 lat_res): # latitude resolution per pixel in degrees
        self.pt = pt
        lon = m.radians(lon)
        lat = m.radians(lat)
        lon_size = m.radians(lon_size)
        lat_size = m.radians(lat_size)
        lon_res = m.radians(lon_res)
        lat_res = m.radians(lat_res)

        if self.pt == 0:
            m1 = m.log(m.tan(0.5 * lat + 0.25 * m.pi))
            m2 = m.log(m.tan(0.5 * (lat + lat_size) + 0.25 * m.pi))
            self.size_y = int((m2 - m1) / lat_res + 0.5) + 1
            self.lat_a = (self.size_y - 1) / (m2 - m1)
            self.lat_b = -self.lat_a * m1
            self.size_x = int(lon_size / lon_res + 0.5) + 1
            self.lon_a = (self.size_x - 1) / lon_size
            self.lon_b = -self.lon_a * lon
        if self.pt == 1:
            self.size_y = int(lat_size / lat_res + 0.5) + 1
            self.lat_a = (self.size_y - 1) / lat_size
            self.lat_b = -self.lat_a * lat
            self.size_x = int(lon_size / lon_res + 0.5) + 1
            self.lon_a = int(self.size_x - 1) / lon_size
            self.lon_b = -self.lon_a * lon

    def lat(self, scan): # get latitude for certain y coordinate
        scan = self.size_y - scan - 1
        if self.pt == 0:
            return m.degrees(2.0 * m.atan(m.exp((scan - self.lat_b) / self.lat_a)) - m.pi / 2.0)
        if self.pt == 1:
            return m.degrees((scan - self.lat_b) / self.lat_a)

    def lon(self, column): # get longitude for certain x coordinate
        return m.degrees((column - self.lon_b) / self.lon_a)

    def y(self, lat): # get y for certain latitude
        lat = m.radians(lat)
        if self.pt == 0:
            return self.size_y - int(m.log(m.tan(0.5 * lat + 0.25 * m.pi)) * self.lat_a + self.lat_b + 1e-12) - 1
        if self.pt == 1:
            return self.size_y - int(lat * self.lat_a + self.lat_b + 1e-12) - 1

    def x(self, lon): # get x for certain 
        lon = m.radians(lon)
        return int(lon * self.lon_a + self.lon_b + 1e-12)