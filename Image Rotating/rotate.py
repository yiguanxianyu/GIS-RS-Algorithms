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

This script is used to rotate a GeoTiff image. The rotation angle is set
by the variable theta, theta > 0 means counter-clockwise. The resampling
method is set as nearest neighbor, other methods will cause the image to
be blurred. The rotation center is the center of the image. In this version
most metadata will be discarded.
"""

import numpy as np
from PIL import Image
from math import sin, cos, radians
from osgeo import gdal
from pathlib import Path

theta = 15  # 旋转角度，逆时针为正
resampling = Image.NEAREST  # 重采样方法
input_path = 'Image Rotating/test_input.tif'  # 文件路径
output_path = 'Image Rotating/test_output.tif'  # 输出路径
Path(output_path).resolve().parent.mkdir(parents=True, exist_ok=True)  # 创建文件夹，如果不存在的话

dataset = gdal.Open(input_path)  # 打开文件
trans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
x_start, y_start = trans[0], trans[3]  # 起点坐标(左上)
x_step, y_step = trans[1], trans[5]  # 步长
x_shear, y_shear = trans[2], trans[4]  # 斜切系数

im_width = dataset.RasterXSize  # 栅格矩阵的列数
im_height = dataset.RasterYSize  # 栅格矩阵的行数
band_count = dataset.RasterCount  # 栅格矩阵的波段数
data_type = dataset.GetRasterBand(1).DataType  # 获取数据类型

# 旋转前图像的XY坐标跨度
x_range = abs(dataset.RasterXSize * x_step)
y_range = abs(dataset.RasterYSize * y_step)
# 旋转过后图像的XY坐标跨度
new_x_range = x_range * cos(radians(theta)) + y_range * sin(radians(theta))
new_y_range = y_range * cos(radians(theta)) + x_range * sin(radians(theta))
# 旋转过后图像的XY像素数量
new_width = int(round(abs(new_x_range / x_step)))
new_height = int(round(abs(new_y_range / y_step)))
# 中心位置不变，计算中心坐标
xpixel, yline = im_width / 2, im_height / 2
x_center = x_start + xpixel * x_step  # + yline * x_shear
y_center = y_start + yline * y_step  # + xpixel * y_shear
# 计算新的左上角坐标
x_start_r = x_center - new_width / 2 * x_step
y_start_r = y_center - new_height / 2 * y_step

target = dataset.GetDriver().Create(output_path, xsize=new_width, ysize=new_height, bands=band_count, eType=data_type)
target.SetProjection(dataset.GetProjection())  # 设置投影坐标
target.SetGeoTransform((x_start_r, x_step, x_shear, y_start_r, y_shear, y_step))  # 设置地理变换参数


def get_rotated_image(band, nodata):
    rawimg = Image.fromarray(band.ReadAsArray())
    rotated_img = rawimg.rotate(theta, expand=True, resample=resampling, fillcolor=nodata)
    resized_img = rotated_img.resize((new_width, new_height), resample=resampling)
    return np.array(resized_img)


for index in range(1, band_count + 1):
    print(f"Writing band {index}/{band_count}")
    input_band = dataset.GetRasterBand(index)
    output_band = target.GetRasterBand(index)

    nodata = input_band.GetNoDataValue()
    if nodata:
        out_data = get_rotated_image(input_band, nodata)
        output_band.SetNoDataValue(nodata)  # 设定nodata值
    else:
        out_data = get_rotated_image(input_band, 0)

    output_band.WriteArray(out_data)  # 写入数据到新影像中
    output_band.FlushCache()
    output_band.ComputeBandStats(False)  # 计算统计信息

target = None
dataset = None
print("All bands written")
