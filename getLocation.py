import json
from urllib.request import urlopen
from urllib.parse import quote
import numpy
import math

"""
用于获取指定位置的经度纬度坐标
def getLocation(address,  # 指定的地址
                city = None, # 指定的城市，用于提升精确度
                coordtype = None # 获取坐标的坐标系，默认为gcj02ll
                ):
获取结果为gcj02ll坐标
"""
def getLocation(address, city = None, coordtype = 'gcj02ll'):
    encodeAdress = quote(address)  # 把地址转码
    
    # 确认方法参数
    if city:
        encodeCity = quote(city)
        cityPara = '&city=' + encodeCity
    else:
        cityPara = ''
    if coordtype:
        coorPara = '&ret_coordtype=' + coordtype
    else:
        coorPara = ''
    
    # 将方法参数转为url格式
    locUrl = 'https://api.map.baidu.com/geocoding/v3/' \
             + '?address=' + encodeAdress \
             + cityPara \
             + '&output=json' \
             +  coorPara\
             + '&ak=6ujEgLZ56RpEldqFam2461U4fouc8Sn4'
    
    
    try:
        # 传入百度地图接口
        result = urlopen((locUrl))
        
        # 获取结果
        res = result.read().decode()
        # 将json数据转为数组形式
        encodeResult = json.loads(res)
        lng = float(encodeResult['result']['location']['lng'])
        lat = float(encodeResult['result']['location']['lat'])
        location = [lng, lat]
    except KeyError as err:
        print(err)
        location = [numpy.nan, numpy.nan]
    return location
# 坐标转换
def wgs84togcj02(localStr):
    lng = localStr[0]
    lat = localStr[1]
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    dlat = __transformlat(lng - 105.0, lat - 35.0)
    dlng = __transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]

def gcj02towgs84(localStr):
    lng = localStr[0]
    lat = localStr[1]
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    dlat = __transformlat(lng - 105.0, lat - 35.0)
    dlng = __transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def __transformlat(lng, lat):
    PI = 3.1415926535897932384626
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * \
          lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

def __transformlng(lng, lat):
    PI = 3.1415926535897932384626
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret
