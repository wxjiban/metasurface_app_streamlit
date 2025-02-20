import sys

# 添加cst库的路径
sys.path.append(r"C:\Program Files (x86)\CST STUDIO SUITE 2020\AMD64\python_cst_libraries")
computer_name = 'server1'
import cst
import cst.results
import math
import cmath
import pandas as pd
import numpy as np
import time
#连续吸波带宽计算函数
def bandwidth_calculate(f1, f2, sampnum, xibolv, xibolv_threshold):
    xibolv_low = 0
    xibolv_high = 0
    tag = 0
    bandwidth = []
    freq_high = []
    freq_low = []
    bandwidth_max = 0
    bandwidth_all = 0
    for i in range(0, len(xibolv)):
        if i == len(xibolv) - 1 and xibolv[i] > xibolv_threshold and tag == 1:
            xibolv_high = i * (f2 - f1) / sampnum
            bandwidth.append(xibolv_high - xibolv_low)
            tag = 0
            continue
        if xibolv[i] > xibolv_threshold and tag == 0:
            xibolv_low = i * (f2 - f1) / sampnum + f1
            tag = 1
        elif xibolv[i] < xibolv_threshold and tag == 1:
            xibolv_high = i * (f2 - f1) / sampnum + f1
            bandwidth.append(xibolv_high - xibolv_low)
            freq_high.append(xibolv_high)
            freq_low.append(xibolv_low)
            tag = 0
    if len(bandwidth) == 0:
        bandwidth_max = 0
        bandwidth_all = 0
        xibolv_high = 0
        xibolv_low = 0
        return bandwidth_max, bandwidth_all, xibolv_high, xibolv_low
    elif len(bandwidth) > 0:
        for i in range(len(bandwidth)):
            bandwidth_all += bandwidth[i]
        bandwidth_max = max(bandwidth)
        c = int(np.argmax(bandwidth_max))
        xibolv_high = freq_high[c]
        xibolv_low = freq_low[c]
        print(f"总共带宽为{bandwidth_all}")
        print(f"最大连续带宽为{bandwidth_max}")
        return bandwidth_all, bandwidth_max, xibolv_high, xibolv_low

#获取所需频率点的性能值函数
def maxcd_calculate(f1, f2, sampnum, cd):
    data = np.zeros(5)
    cd = np.array(cd)
    cd = cd.flatten()
    data[0] = np.max(abs(cd))
    i = int(np.argmax(cd))
    data[1] = f1 + i * (f2 - f1) / sampnum
    data[2] = cd[i]
    i = int(np.argmin(cd))
    data[3] = f1 + i * (f2 - f1) / sampnum
    data[4] = cd[i]
    return data

#结果保存函数
def save_select_result(freq, result, name, f1, f2, sampnum, para_data, datalength):
    for i in range(sampnum):
        l = f1 + (f2 - f1) * i / sampnum
        t = np.argmin(abs(freq - l))
        result[i + datalength] = para_data[t]
    try:
        data = np.loadtxt(f"result-{name}.csv", dtype=np.float, delimiter=',', skiprows=0)
        data = np.array(data, ndmin=2)
        data1 = np.array(result)
        data = np.row_stack((data, data1))
        coordinates = pd.DataFrame(np.mat(data))
        coordinates.to_csv(f"result-{name}.csv", header=None, index=0)
    except:
        data = np.reshape(result, (1, -1))
        coordinates = pd.DataFrame(np.mat(data))
        coordinates.to_csv(f"result-{name}.csv", header=None, index=0)
    s = result[datalength:datalength + sampnum]
    return s


def save_result(result, name):
    try:
        data = np.loadtxt(f"result-{name}.csv", dtype=np.float, delimiter=',', skiprows=0)
        data = np.array(data, ndmin=2)
        data1 = np.array(result)
        data = np.row_stack((data, data1))
        coordinates = pd.DataFrame(np.mat(data))
        coordinates.to_csv(f"result-{name}.csv", header=None, index=0)
    except:
        data = np.reshape(result, (1, -1))
        coordinates = pd.DataFrame(np.mat(data))
        coordinates.to_csv(f"result-{name}.csv", header=None, index=0)

#读取CST仿真结果并保存主体函数
def result_post(file_path, rec, f1, f2, sampnum):
    datalength = 0
    #分别读取S11,S22,S12,S21的性能
    for j in [0, 3]:
            project = cst.results.ProjectFile(file_path, allow_interactive=True)
            if j == 0:
                result_path = r"1D Results\S-Parameters\SZmax(1),Zmax(1)"
                smaxmax = project.get_3d().get_result_item(result_path)
                suffix = '11'
            elif j == 1:
                result_path = r"1D Results\S-Parameters\SZmax(2),Zmax(2)"
                smaxmax = project.get_3d().get_result_item(result_path)
                suffix = '22'
            elif j == 2:
                result_path = r"1D Results\S-Parameters\SZmax(1),Zmax(2)"
                smaxmax = project.get_3d().get_result_item(result_path)
                suffix = '12'
            else:
                result_path = r"1D Results\S-Parameters\SZmax(2),Zmax(1)"
                smaxmax = project.get_3d().get_result_item(result_path)
                suffix = '21'

            datas11 = smaxmax.get_data()
            freq = []
            mag = []
            arg = []
            real = []
            imag = []
            result = np.zeros(sampnum)
            datas11 = np.array(datas11)
            #结果提取并将复数分离为实部虚部转换为幅度相位并且分别保存
            for i in range(len(datas11)):
                label = datas11[i, 1]
                freq.append(datas11[i, 0])
                mag1, arg1 = cmath.polar(label)
                phase1 = arg1 * 180 / math.pi
                real1 = label.real
                imag1 = label.imag
                mag.append(mag1)
                arg.append(phase1)
                real.append(real1)
                imag.append(imag1)
            freq = np.array(np.real(freq))
            # print(freq)
            if j == 0:
                s11_mag = save_select_result(freq, result, f"mag{suffix}-{computer_name}", f1, f2, sampnum, mag, datalength)
                s11_phase = save_select_result(freq, result, f"phase{suffix}-{computer_name}", f1, f2, sampnum, arg, datalength)
            elif j == 1:
                s22 = save_select_result(freq, result, f"mag{suffix}-{computer_name}", f1, f2, sampnum, mag, datalength)
            elif j == 2:
                s12_mag = save_select_result(freq, result, f"mag{suffix}-{computer_name}", f1, f2, sampnum, mag, datalength)
                s12_phase = save_select_result(freq, result, f"phase{suffix}-{computer_name}", f1, f2, sampnum, arg, datalength)
            else:
                s21 = save_select_result(freq, result, f"mag{suffix}-{computer_name}", f1, f2, sampnum, mag, datalength)

            save_select_result(freq, result, f"real{suffix}-{computer_name}", f1, f2, sampnum, real, datalength)
            save_select_result(freq, result, f"imag{suffix}-{computer_name}", f1, f2, sampnum, imag, datalength)
    para_filepath = f'para-{computer_name}'
    save_result(rec, para_filepath)
    xibolv = 1 - s11_mag**2
    resultxibolv = np.hstack((rec, xibolv))
    bandwidth = np.zeros((1, datalength + 4), dtype=float)
    bandwidth[0, 0:datalength] = rec[0:datalength]
    #计算吸波带宽
    bandwidth[0, datalength:datalength + 4] = bandwidth_calculate(f1=f1, f2=f2, sampnum=sampnum, xibolv=xibolv,
                                                                xibolv_threshold=0.9)
    #保存吸波带宽结果
    save_result(bandwidth, f"bandwidth-xibolv-{computer_name}")
    save_result(resultxibolv, f"xibolv-{computer_name}")
    reward = float(bandwidth[0, datalength + 1])
    print(f"最大吸波连续带宽为{reward}")
    return s11_mag, s11_phase, s12_mag, s12_phase
if __name__ == '__main__':
    file_name = "model4"
    file_path = "D:\\niurong\\donglin\\"
    print(file_path + file_name + ".cst")
    # para_data = np.loadtxt(f'result-para-{computer_name}.csv', dtype=np.float, delimiter=',', skiprows=0)
    # ceshi_length = np.shape(para_data)[0] #只有一行的时候
    # ceshi_length = np.shape(para_data)[1] #有多行的时候
    # 还不存在结构结果文件

    # result_post(file_path + file_name + ".cst", np.zeros(ceshi_length), 0, 40, 400)