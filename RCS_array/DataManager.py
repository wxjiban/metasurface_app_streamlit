import os
import numpy as np
import pandas as pd
import streamlit as st


class DataManager:
    """
    DataManager 类负责对 app 数据的读取、操作、检查以及添加注释。
    包括：
      - 使用 numpy 读取 param_names.csv（单元参数名称）
      - 使用 numpy/pandas 读取 x_coordinates.csv（电磁性能的频率区间）
      - 对每个单元对应的 5 个 CSV 文件进行操作：
            result-para.csv —— 单元参数的数值
            result-totalmag0.csv, result-totalmag1.csv,
            result-totalphase0.csv, result-totalphase1.csv —— 单元4个性能
            selected_unit_data.csv —— 被选的单元的4个性能
      - 对阵列排布对应的 2 个 CSV 文件进行操作：
            array_states.csv —— 阵列排布
            rcsr.csv —— 阵列的RCSR性能
      - 同时提供添加新结果的方法：
            add_new_unit_result(unit_params)：对于新的单元参数，
                先检查是否已存在（不需要计算则直接返回已有性能数据），
                否则调用计算函数获得新的 4 个性能数据，并追加到 5 个文件最后一行。
            add_new_array_result(array_state)：对于新的阵列状态，
                先检查是否已有相应数据，若无则调用计算函数获得新的 rcsr 性能，追加到文件最后一行。
    """

    def __init__(self, base_dir):
        """
        初始化 DataManager 类

        参数:
            base_dir (str): 数据文件所在的根目录
        """
        self.base_dir = base_dir

        # 文件路径定义
        self.param_names_file = os.path.join(base_dir, "param_names.csv")
        self.x_coords_file = os.path.join(base_dir, "x_coordinates.csv")

        # 单元相关文件（每一行对应一个单元）
        self.result_para_file = os.path.join(base_dir, "result-para.csv")
        self.totalmag0_file = os.path.join(base_dir, "result-totalmag0.csv")
        self.totalmag1_file = os.path.join(base_dir, "result-totalmag1.csv")
        self.totalphase0_file = os.path.join(base_dir, "result-totalphase0.csv")
        self.totalphase1_file = os.path.join(base_dir, "result-totalphase1.csv")
        self.selected_unit_data_file = os.path.join(base_dir, "selected_unit_data.csv")

        # 阵列相关文件（每一行对应一个阵列排布）
        self.array_states_file = os.path.join(base_dir, "array_states.csv")
        self.rcsr_file = os.path.join(base_dir, "rcsr.csv")

        # 预先加载数据
        self.param_names = self.load_param_names()  # 使用 numpy 读取
        self.x_coords = self.load_x_coordinates()  # 使用 numpy 读取
        self.unit_params_df = self.load_dataframe(self.result_para_file)  # 每一行为一个单元参数（数值）
        self.totalmag0_df = self.load_dataframe(self.totalmag0_file)
        self.totalmag1_df = self.load_dataframe(self.totalmag1_file)
        self.totalphase0_df = self.load_dataframe(self.totalphase0_file)
        self.totalphase1_df = self.load_dataframe(self.totalphase1_file)
        self.selected_unit_df = self.load_dataframe(self.selected_unit_data_file)

        self.array_states_df = self.load_dataframe(self.array_states_file)
        self.rcsr_df = self.load_dataframe(self.rcsr_file)

    def load_param_names(self):
        """
        读取 param_names.csv 文件（单元参数的名称），使用 numpy 直接读取

        返回:
            list: 参数名称列表
        """
        if os.path.exists(self.param_names_file):
            try:
                # 假设csv文件中所有名称在一行，逗号分隔
                names = np.genfromtxt(self.param_names_file, delimiter=',', dtype=str)
                # 如果读取得到的是二维数组，则取第1行
                if names.ndim == 2:
                    names = names[0]
                return list(names)
            except Exception as e:
                st.error(f"读取 {self.param_names_file} 时出错: {e}")
                return []
        else:
            st.error(f"文件 {self.param_names_file} 不存在。")
            return []

    def load_x_coordinates(self):
        """
        读取 x_coordinates.csv 文件（电磁性能的频率区间），使用 numpy 直接读取

        返回:
            list: 频率点列表
        """
        if os.path.exists(self.x_coords_file):
            try:
                # 假设csv文件中所有频率在一行，无表头
                coords = np.genfromtxt(self.x_coords_file, delimiter=',')
                # 如果coords是一维，则直接返回，否则取第一行
                if coords.ndim > 1:
                    coords = coords[0]
                return coords.tolist()
            except Exception as e:
                st.error(f"读取 {self.x_coords_file} 时出错: {e}")
                return []
        else:
            st.error(f"文件 {self.x_coords_file} 不存在。")
            return []

    def load_dataframe(self, file_path):
        """
        使用 pandas 读取一个 csv 文件，返回 DataFrame

        参数:
            file_path (str): CSV 文件路径。

        返回:
            pd.DataFrame: 文件对应的 DataFrame，如果文件不存在则返回空 DataFrame。
        """
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, header=None)
                return df
            except Exception as e:
                st.error(f"读取 {file_path} 时出错: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def append_row(self, file_path, row):
        """
        追加一行数据到指定的 CSV 文件

        参数:
            file_path (str): CSV 文件路径。
            row (list): 要追加的一行数据
        """
        df = pd.DataFrame([row])
        # 如果文件存在则追加，否则直接保存
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', index=False, header=False)
        else:
            df.to_csv(file_path, index=False, header=False)

    # ---------------------------
    # 以下为添加新结果的占位函数
    # ---------------------------

    def compute_unit_performance(self, unit_params):
        """
        占位函数，根据 unit_params 计算新的单元性能。
        返回4个性能数组，每个数组长度与 self.x_coords 一致。

        参数:
            unit_params (list of float): 单元参数数值列表

        返回:
            tuple: (totalmag0, totalmag1, totalphase0, totalphase1)
                   每个为长度为 len(self.x_coords) 的数组
        """
        n = len(self.x_coords)
        # 这里用随机数据代替真实逻辑，实际请替换为您的计算逻辑
        totalmag0 = np.random.uniform(0, 1, n)
        totalmag1 = np.random.uniform(0, 1, n)
        totalphase0 = np.random.uniform(-3, 3, n)
        totalphase1 = np.random.uniform(-3, 3, n)
        return (totalmag0, totalmag1, totalphase0, totalphase1)

    def compute_rcsr(self, x_Amp, sampled_mag0, sampled_arg0, sampled_mag1, sampled_arg1):
        # 参转换和初始变量设置
        p = 8.5
        D = p * 1e-3
        theta = np.arange(0, np.pi, 0.03125 * np.pi, dtype=np.float32)
        phi = np.arange(0, 2 * np.pi, 0.03125 * np.pi, dtype=np.float32)
        Nx = 6
        Ny = 6
        c = 3e+8

        # 定义阵元下标（从1开始，对应论文中 (Ny_0-1/2) 与 (Nx_0-1/2) 的计算）
        # 这里直接用 np.arange(1,Ny+1) 减去0.5 得到等效结果
        # 同理，对 Nx
        ny_indices = np.arange(1, Ny + 1, dtype=np.float32)  # shape (6,)
        nx_indices = np.arange(1, Nx + 1, dtype=np.float32)  # shape (6,)

        # 预设输出：每个频率对应一个 RCSR 值，最后输出 shape 为 (len(sampled_freq), 1)
        RCSR_all = np.zeros((len(self.x_coords), 1), dtype=np.float32)

        # 将 x_Amp 转换为 NumPy 数组，并取前36个元素重塑为 (6,6) 复数矩阵（这里 x_Amp 本身应为 NumPy 数组）
        PSI = np.array(x_Amp, dtype=np.complex64)[:36].reshape((6, 6))

        # 对每个采样频率计算 RCSR
        for kk in range(len(self.x_coords)):
            # 频率单位转换 GHz -> Hz
            f = self.x_coords[kk] * 1e9
            lamda = c / f
            k = 2 * np.pi / lamda

            # 根据 x_Amp 的实部是否等于 1 分别赋值相位和幅值
            # 注意：这里 PSI.real 的数值作为判定条件，与原始代码中 torch.where(PHI==1,...) 对应
            PHI = np.where(PSI.real == 1, sampled_arg1[kk], sampled_arg0[kk]).astype(np.float32)
            AMP = np.where(PSI.real == 1, sampled_mag1[kk], sampled_mag0[kk]).astype(np.float32)

            # 初始化 A 与 A_metal，每个的形状为 (len(theta), len(phi))
            A = np.zeros((len(theta), len(phi)), dtype=np.complex64)
            A_metal = np.zeros((len(theta), len(phi)), dtype=np.complex64)

            # 对每个 (theta, phi) 角组合计算阵列响应
            for ii in range(len(theta)):
                for jj in range(len(phi)):
                    # 计算左侧向量：对应 y 方向的相位贡献，形状 (6,)
                    # 这里用 ny_indices-0.5 替代原来的 (Ny_0-1/2)
                    left_vec = np.exp(1j * k * D * np.sin(theta[ii] - np.pi / 2) *
                                      ((ny_indices - 0.5)) * np.sin(phi[jj]))
                    # 计算右侧向量：对应 x 方向的相位贡献，形状 (6,)
                    right_vec = np.exp(1j * k * D * (nx_indices - 0.5) *
                                       (np.sin(theta[ii] - np.pi / 2) * np.cos(phi[jj]) - np.sin(0.0)))
                    # 中间矩阵为振幅和相位构成的 6x6 阵列因子
                    mid_matrix = AMP * np.exp(1j * PHI)

                    # 计算 A[ii, jj] = left_vec @ mid_matrix @ right_vec
                    A[ii, jj] = np.dot(left_vec, np.dot(mid_matrix, right_vec))

                    # 对于金属反射面，阵列因子全部置 1
                    mid_matrix_metal = np.ones((6, 6), dtype=np.complex64)
                    A_metal[ii, jj] = np.dot(left_vec, np.dot(mid_matrix_metal, right_vec))

            # 求取 A 和 A_metal 内部的最大幅值
            A_max = np.abs(A).max()
            A_max_metal = np.abs(A_metal).max()
            # 计算 RCSR 的 dB 值
            RCSR_dB = 20 * np.log10(A_max / A_max_metal)
            RCSR_all[kk, 0] = RCSR_dB

        return RCSR_all

    def unit_exists(self, new_unit_params):
        """
        遍历 result-para.csv 文件，判断新的单元参数是否已经存在。
        参数:
            new_unit_params (list): 新的单元参数（列表格式，与 result-para.csv 每行数据一致）
        返回:
            int 或 None：如果存在则返回对应行索引；否则返回 None。
        """
        if self.unit_params_df.empty:
            return None
        for idx, row in self.unit_params_df.iterrows():
            # 如果每个参数相等，则认为已存在（这里简单使用==比较，可根据具体情况调整）
            if list(row) == new_unit_params:
                return idx
        return None

    def add_new_unit_result(self, unit_params):
        """
        添加新的单元参数结果：
          - 检查新的 unit_params 是否已存在，如果已存在直接返回对应的性能数据；
          - 若不存在，则调用 compute_unit_performance(unit_params) 得到新的4个性能数组，
            然后将新的单元参数和性能数据追加到相应 CSV 文件的最后一行，
            并返回新的性能数据（字典格式）。

        参数:
            unit_params (list of float): 新的单元参数

        返回:
            dict: {"totalmag0": ..., "totalmag1": ..., "totalphase0": ..., "totalphase1": ...}
                  每个键对应的值为与 self.x_coords 长度一致的数组；若计算失败则返回 None。
        """
        idx = self.unit_exists(unit_params)
        if idx is not None:
            st.info("该单元参数已存在，直接返回已有性能数据。")
            totalmag0 = self.totalmag0_df.iloc[idx].tolist()
            totalmag1 = self.totalmag1_df.iloc[idx].tolist()
            totalphase0 = self.totalphase0_df.iloc[idx].tolist()
            totalphase1 = self.totalphase1_df.iloc[idx].tolist()
            return {
                "totalmag0": totalmag0,
                "totalmag1": totalmag1,
                "totalphase0": totalphase0,
                "totalphase1": totalphase1
            }
        else:
            performance = self.compute_unit_performance(unit_params)
            if performance is None:
                st.error("仿真失败：未能生成有效的性能数据。")
                return None
            # 将新的单元参数追加到 result-para.csv
            self.append_row(self.result_para_file, unit_params)
            # 对应的性能数组追加到各 CSV 文件（由于新性能数据为 numpy 数组，转换为列表再追加）
            self.append_row(self.totalmag0_file, performance[0].tolist())
            self.append_row(self.totalmag1_file, performance[1].tolist())
            self.append_row(self.totalphase0_file, performance[2].tolist())
            self.append_row(self.totalphase1_file, performance[3].tolist())
            return {
                "totalmag0": performance[0].tolist(),
                "totalmag1": performance[1].tolist(),
                "totalphase0": performance[2].tolist(),
                "totalphase1": performance[3].tolist()
            }

    def array_exists(self, new_array_state):
        """
        遍历 array_states.csv 文件，判断新的阵列状态是否已经存在。
        参数:
            new_array_state (list): 新的阵列排布状态（列表格式）
        返回:
            int 或 None：如果存在则返回对应行索引；否则返回 None。
        """
        if self.array_states_df.empty:
            return None
        for idx, row in self.array_states_df.iterrows():
            if list(row) == new_array_state:
                return idx
        return None

    def add_new_array_result(self, new_array_state):
        """
        添加新的阵列状态结果。
        如果 new_array_state 在 array_states.csv 中已存在，则直接返回对应的 RCSR 性能数据。
        否则：
            调用计算函数获得新的 rcsr 性能数据，并追加到 rcsr.csv 文件最后一行，
            同时将 new_array_state 追加到 array_states.csv。
        返回:
            float: 新的 rcsr 性能数据。
        """
        index = self.array_exists(new_array_state)
        if index is not None:
            st.info("该阵列状态已存在，直接返回已有性能数据。")
            rcsr_value = self.rcsr_df.iloc[index].tolist()[0]
            return rcsr_value
        else:
            rcsr_value = self.compute_rcsr(new_array_state)
            # 追加阵列状态到 array_states.csv
            self.append_row(self.array_states_file, new_array_state)
            # 追加 rcsr_value 到 rcsr.csv（作为单行一个性能值）
            self.append_row(self.rcsr_file, [rcsr_value])
            return rcsr_value


# 示例用法
if __name__ == "__main__":
    # 假设数据文件都在 "data" 文件夹下
    base_dir = "data"
    dm = DataManager(base_dir)

    # 测试读取
    print("参数名称：", dm.param_names)
    print("频率坐标：", dm.x_coords)
    print("单元参数：", dm.unit_params_df)

    # 测试添加新单元（用示例参数列表）
    new_unit = [0.5, 1.2, 3.4, 2.2, 5.6]  # 示例，应根据实际单元参数数目调整
    # 这里仅作示例，实际单元参数的维度应与 result-para.csv 中一致
    result = dm.add_new_unit_result(new_unit)
    print("新单元性能：", result)

    # 测试添加新阵列状态
    new_array = [1, 0, 1, 1, 0]  # 示例，实际维度取决于 array_states.csv
    rcsr_val = dm.add_new_array_result(new_array)
    print("新阵列的RCSR性能：", rcsr_val)
