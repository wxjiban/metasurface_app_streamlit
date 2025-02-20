# %% Do PSO
import numpy as np
import sys
import os
from post_result import result_post, save_result
from mybuildmodel_son1 import MyModelSon1
import time
# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# 添加CST库的路径
sys.path.append(r"C:\Program Files (x86)\CST Studio Suite 2020\AMD64\python_cst_libraries")
# 检验CST是否可以通过Python启动
import cst
print(cst.__file__)

# 定义一些变量
file_name = "model3"
file_path = "D:\\niurong\\donglin\\CST_file\\"
Freq = [0, 40]
dielectric_materials = {
    'PDMS': [2.35, 0]
}
def screen(rec,df):
    d = False
    k = 0
    j = int(len(rec))
    for i in range(len(df)):
        if ((rec == df[i,0:11]).all()):
           k = i
           d = 1
        else:
            continue
    return (d, k)
def dispose(rec):
    try:
        df = np.loadtxt('./result-para.csv', dtype=float, delimiter=',', skiprows=0)
        result = np.loadtxt('./result-bandwidth-xibolv.csv', dtype=float, delimiter=',', skiprows=0)
        print(f"保存数据数量为{len(df)}")
        d , k= screen(rec, df)
        if(d):
            return(d, result[k, 1])
        else:
            return(0, 0)
    except:
        return (0, 0)
def RCS_topology_demo_func(para_box):
    flag, reward = dispose(para_box)
    if not flag == 0:
        print('已经存在')
        return reward
    else:
        asd = {
            'H1': 2.07,
            'H2': 2.07,
            'r1': para_box[2],
            'r2': para_box[3],
            'd': para_box[4],
            'l': para_box[5],
            'd1': para_box[6],
            'r3': para_box[7],
            'r4': para_box[8],
            'p1': para_box[9],
            'p2': para_box[10],
            'p3': para_box[11],
            'p': 5,
            'D': 0.05,
            'tm': 0.035,
            'T1': 0.000185,
        }
        print(para_box)
        para_data = np.array(list(asd.values()))
        my_model = MyModelSon1(file_name, file_path, Freq, asd, dielectric_materials)
        my_model.build_model()
        my_model.run()
        my_model.cst_environment.close()
        s11_mag, s11_phase, s12_mag, s12_phase = result_post(file_path + file_name + ".cst", para_data, 0, 40, 400)
    return s11_mag, s11_phase, s12_mag, s12_phase

