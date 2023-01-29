"""
Copyright 2023 Zhang Chi chizhangrs@gmail.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

STILL UNDER DEVELOPMENT

This script is used to rotate a GeoTiff image. Different from rotate.py,
this script will change the 6-element tuple of the geotransform metadata
of the image but will not change the value of the array. The rotation angle
is set by the variable theta, theta > 0 means counter-clockwise. In this
version most metadata will be retained.
"""

from osgeo import gdal
import numpy as np
from math import sin, cos, radians

theta = 90

file_path = './UAV_yunnan_first_2.tif'
dataset = gdal.Open(file_path, 1)  # 打开文件
dataset.GetGeoTransform()

trans = list(dataset.GetGeoTransform())

im_width = dataset.RasterXSize  # 栅格矩阵的列数
im_height = dataset.RasterYSize  # 栅格矩阵的行数
bands = dataset.RasterCount  # 栅格矩阵的波段数

im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
im_proj = dataset.GetProjection()  # 地图投影信息
im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵
dataset.GetGeoTransform()

angle = radians(theta)
a = np.array([[trans[1], 0], [0, trans[5]]])
b = np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
s = a @ b
print(a)
print(b)
print(a @ b)
trans = (trans[0], s[0][0], s[0][1], trans[3], s[1][0], s[1][1])
print(trans)

dataset.SetGeoTransform(tuple(trans))