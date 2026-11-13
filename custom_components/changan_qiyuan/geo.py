"""GCJ-02 inverse via iterative residual correction; identity outside China."""
import math

def _offset(lon, lat):
    x, y = lon - 105, lat - 35
    a = -100 + 2*x + 3*y + .2*y*y + .1*x*y + .2*math.sqrt(abs(x))
    b = 300 + x + 2*y + .1*x*x + .1*x*y + .1*math.sqrt(abs(x))
    wave = (20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    a += wave + (20*math.sin(y*math.pi)+40*math.sin(y*math.pi/3))*2/3
    a += (160*math.sin(y*math.pi/12)+320*math.sin(y*math.pi/30))*2/3
    b += wave + (20*math.sin(x*math.pi)+40*math.sin(x*math.pi/3))*2/3
    b += (150*math.sin(x*math.pi/12)+300*math.sin(x*math.pi/30))*2/3
    rad = lat*math.pi/180
    magic = 1-.006693421622965943*math.sin(rad)**2
    return b*180/(6378245/math.sqrt(magic)*math.cos(rad)*math.pi), a*180/((6378245*(1-.006693421622965943))/(magic**1.5)*math.pi)

def to_wgs84(lat, lon):
    if not (72.004 <= lon <= 137.8347 and .8293 <= lat <= 55.8271):
        return lat, lon
    a, b = lat, lon
    for _ in range(8):
        dx, dy = _offset(b, a)
        a -= a+dy-lat
        b -= b+dx-lon
    return a, b
