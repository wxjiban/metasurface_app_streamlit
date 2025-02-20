# RCS/rcs_function.py

import numpy as np
import streamlit as st
def generate_rcs_output(params, num_points=400):
    """
    根据参数生成 RCS 曲线数据。

    参数:
    - params (dict): 参数字典。
    - num_points (int): 生成的数据点数量（默认400）。

    返回:
    - y_mag (list): 幅度数据。
    - y_phase (list): 相位数据。
    """
    try:
        # 示例逻辑：根据参数生成随机数据
        y_mag = np.random.uniform(0, 1, num_points).tolist()
        y_phase = np.random.uniform(-180, 180, num_points).tolist()
        return y_mag, y_phase
    except Exception as e:
        st.error(f"RCS 数据生成错误: {e}")
        return None, None
