
import numpy as np
import time
from post_result import result_save
import sys
import cst.interface
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# import openpyxl
# 添加cst库的路径
# sys.path.append(r"D:\Program Files\CST Studio Suite 2020\AMD64\python_cst_libraries")
sys.path.append(r"C:\Program Files (x86)\CST Studio Suite 2020\AMD64\python_cst_libraries")

from mybuildmodel_son1 import MyModelSon1

# 检验CST是否可以通过Python启动
print(cst.__file__)
def RCS_Toroidal_demo_func(x):
    # 定义一些变量
    file_name = "try2"
    # file_path = "D:/python_cst/deep_learning/model/"
    file_path = "D:/niurong/xingwentao/deep_learning//model/"


    Freq = [1, 20]


    para_box1 = {
        "d1": 4,
        'd2': 4,
        'T1': 0.000185,

        'p': 10,
        'a': 1,
        'b': 2,
        'theta_1': 10,
        'theta_2': 20,


    }

    dielectric_materials = {

    }

    my_model = MyModelSon1(file_name, file_path, Freq, para_box1, dielectric_materials)

    x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, x21, x22, x23, x24, x25, x26, x27, x28, x29, x30, x31, x32, x33, x34, x35, x36, x37, x38, x39, x40, x41 = x
    x0 = [x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, x21, x22, x23, x24, x25, x26, x27, x28, x29, x30, x31, x32, x33, x34, x35, x36, x37, x38, x39, x40, x41]
    asd = {
        'p': x1,
        'a': x2,
        'b': x3,
        'theta_1': x4,
        'theta_2': x5,

        "d1": 4,
        'd2': 4,
        'T1': 0.000185,
    }
    print(asd)
    my_model.new_project.close()
    my_model.new_project = my_model.cst_environment.new_mws()  # 新建项目
    my_model.modeler = my_model.new_project.modeler
    my_model.init_model()
    my_model.change_para_box(asd)
    my_model.build_model()
    my_model.set_port(0)
    my_model.define_boundary()
    # my_model.set_mesh()
    time_start_0 = time.time()
    my_model.run()
    freq0, mag0, arg0, mag0xx, arg0xx, mag0yx, arg0yx, xibolv0 = result_save(file_path + file_name + ".cst")
    my_model.rotation_structure('topITO', center=[0, 0, 0], angle=[0, 0, -90], repetition=1, enable_unite=False,
                                enable_copy=False, component='component1')
    my_model.run()
    freq1, mag1, arg1, mag1xx, arg1xx, mag1yx, arg1yx, xibolv1 = result_save(file_path + file_name + ".cst")

    time_end_0 = time.time()
    print('Time cost = %fs' % (time_end_0 - time_start_0))

    new_freq, new_mag0, new_mag1, new_arg0, new_arg1, new_mag0xx, new_arg0xx, new_mag0yx, new_arg0yx, new_xibolv0, new_mag1xx, new_arg1xx, new_mag1yx, new_arg1yx, new_xibolv1 = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

    dict1 = {freq0_value: freq0_index for freq0_index, freq0_value in enumerate(freq0)}

    for j, freq1_value in enumerate(freq1):
        if freq1_value in dict1:
            i = dict1[freq1_value]
            new_freq.append(freq1_value)
            new_mag0.append(mag0[i])
            new_mag1.append(mag1[j])
            new_arg0.append(arg0[i])
            new_arg1.append(arg1[j])

            new_mag0xx.append(mag0xx[i])
            new_arg0xx.append(arg0xx[i])
            new_mag0yx.append(mag0yx[i])
            new_arg0yx.append(arg0yx[i])
            new_xibolv0.append(xibolv0[i])

            new_mag1xx.append(mag1xx[j])
            new_arg1xx.append(arg1xx[j])
            new_mag1yx.append(mag1yx[j])
            new_arg1yx.append(arg1yx[j])
            new_xibolv1.append(xibolv1[j])





    freq_index = (list(map(round, [20 + x * (len(new_freq[1:-1])-20) / 398 for x in range(398)])))
    sampled_freq = [new_freq[0]] + list(np.array(new_freq)[freq_index]) + [new_freq[-1]]
    sampled_mag0 = [new_mag0[0]] + list(np.array(new_mag0)[freq_index]) + [new_mag0[-1]]
    sampled_arg0 = [new_arg0[0]] + list(np.array(new_arg0)[freq_index]) + [new_arg0[-1]]
    sampled_mag1 = [new_mag1[0]] + list(np.array(new_mag1)[freq_index]) + [new_mag1[-1]]
    sampled_arg1 = [new_arg1[0]] + list(np.array(new_arg1)[freq_index]) + [new_arg1[-1]]

    sampled_mag0xx = [new_mag0xx[0]] + list(np.array(new_mag0xx)[freq_index]) + [new_mag0xx[-1]]
    sampled_arg0xx = [new_arg0xx[0]] + list(np.array(new_arg0xx)[freq_index]) + [new_arg0xx[-1]]
    sampled_mag0yx = [new_mag0yx[0]] + list(np.array(new_mag0yx)[freq_index]) + [new_mag0yx[-1]]
    sampled_arg0yx = [new_arg0yx[0]] + list(np.array(new_arg0yx)[freq_index]) + [new_arg0yx[-1]]
    sampled_xibolv0 = [new_xibolv0[0]] + list(np.array(new_xibolv0)[freq_index]) + [new_xibolv0[-1]]

    sampled_mag1xx = [new_mag1xx[0]] + list(np.array(new_mag1xx)[freq_index]) + [new_mag1xx[-1]]
    sampled_arg1xx = [new_arg1xx[0]] + list(np.array(new_arg1xx)[freq_index]) + [new_arg1xx[-1]]
    sampled_mag1yx = [new_mag1yx[0]] + list(np.array(new_mag1yx)[freq_index]) + [new_mag1yx[-1]]
    sampled_arg1yx = [new_arg1yx[0]] + list(np.array(new_arg1yx)[freq_index]) + [new_arg1yx[-1]]
    sampled_xibolv1 = [new_xibolv1[0]] + list(np.array(new_xibolv1)[freq_index]) + [new_xibolv1[-1]]
    return sampled_mag0, sampled_arg0, sampled_mag1, sampled_arg1










