import sys

# 添加cst库的路径
sys.path.append(r"D:\Program Files\CST Studio Suite 2020\AMD64\python_cst_libraries")
import cst
import cst.results
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
#mpl.rcParams['font.sans-serif'] = ['SimHei']
from pylab import *  # 支持中文
def result_save(file_path):
    project = cst.results.ProjectFile(file_path, allow_interactive=True)

    smaxmax11 = project.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(1),Zmax(1)")
    smaxmax21 = project.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(2),Zmax(1)")

    data1 = smaxmax11.get_data()
    data2 = smaxmax21.get_data()

    #sminmax11 = project.get_3d().get_result_item(r"1D Results\S-Parameters\SZmin(1),Zmax(1)")
    #print(sminmax11)
    #data2 = sminmax11.get.data()
    freq = []
    xibolv = []
    mag11 = []
    arg11 = []
    for i in range(len(data1)):
        # 频率
        freq.append(data1[i][0])
        # mag1, arg1 = cmath.polar(data1[i][1] + data2[i][1])
        mag1, arg1 = cmath.polar(data1[i][1])
        mag2, arg2 = cmath.polar(data2[i][1])
        mag11.append(mag1)
        arg11.append(arg1)
        #mag21.append(mag2)
        xibo = 1 - abs(mag1) * abs(mag1)
        xibolv.append(xibo)
    return mag1, arg1, mag2, arg2




