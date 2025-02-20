# RCS/rcs.py

import pandas as pd
import os

from streamlit import header

from RCS.rcs_function import generate_rcs_output
import streamlit as st

class RCSHandler:
    def __init__(self, data_dir, images_dir):
        self.data_dir = data_dir
        self.images_dir = images_dir
        self.param_names_file = os.path.join(data_dir, 'param_names.csv')
        self.x_coords_file = os.path.join(data_dir, 'x_coordinates.csv')
        self.params_file = os.path.join(data_dir, 'result-para.csv')
        self.mag11_file = os.path.join(data_dir, 'result-mag11.csv')
        self.phase11_file = os.path.join(data_dir, 'result-phase11.csv')
        self.mag12_file = os.path.join(data_dir, 'result-mag12.csv')
        self.phase12_file = os.path.join(data_dir, 'result-phase12.csv')

        self.param_names = self.load_param_names()
        self.x_coords = self.load_x_coordinates()
        self.params_df = self.load_params()
        self.mag11_df = self.load_images(self.mag11_file)
        self.phase11_df = self.load_images(self.phase11_file)
        self.mag12_df = self.load_images(self.mag12_file)
        self.phase12_df = self.load_images(self.phase12_file)

    def load_param_names(self):
        if os.path.exists(self.param_names_file):
            df = pd.read_csv(self.param_names_file)
            return df.columns.tolist()
        else:
            st.error(f"`{self.param_names_file}` 文件不存在。")
            return []

    def load_x_coordinates(self):
        if os.path.exists(self.x_coords_file):
            df = pd.read_csv(self.x_coords_file, header= None)
            return df.iloc[0].tolist()
        else:
            st.error(f"`{self.x_coords_file}` 文件不存在。")
            return []

    def load_params(self):
        if os.path.exists(self.params_file):
            return pd.read_csv(self.params_file, header=None, names=self.param_names)
        else:
            return pd.DataFrame(columns=self.param_names)

    def load_images(self, file_path):
        if os.path.exists(file_path):
            return pd.read_csv(file_path, header=None)
        else:
            return pd.DataFrame()

    def save_params(self, df):
        df.to_csv(self.params_file, index=False, header=False)

    def save_images(self, df, file_path):
        df.to_csv(file_path, index=False, header=False)

    def add_new_params(self, new_params_float):
        # 保存参数
        self.params_df = pd.concat([self.params_df, pd.DataFrame([new_params_float])], ignore_index=True)
        self.save_params(self.params_df)

        # 生成曲线数据
        y_mag11, y_phase11 = generate_rcs_output(new_params_float, num_points=400)
        y_mag12, y_phase12 = generate_rcs_output(new_params_float, num_points=400)

        if None in [y_mag11, y_phase11, y_mag12, y_phase12]:
            st.error("仿真失败：未能生成有效的曲线数据。")
            return False

        if not (len(y_mag11) == len(self.x_coords) and len(y_phase11) == len(self.x_coords) and
                len(y_mag12) == len(self.x_coords) and len(y_phase12) == len(self.x_coords)):
            st.error(f"生成的曲线数据点数量不正确。应为{len(self.x_coords)}个。")
            return False

        # 保存曲线数据
        self.mag11_df = pd.concat([self.mag11_df, pd.DataFrame([y_mag11])], ignore_index=True)
        self.save_images(self.mag11_df, self.mag11_file)

        self.phase11_df = pd.concat([self.phase11_df, pd.DataFrame([y_phase11])], ignore_index=True)
        self.save_images(self.phase11_df, self.phase11_file)

        self.mag12_df = pd.concat([self.mag12_df, pd.DataFrame([y_mag12])], ignore_index=True)
        self.save_images(self.mag12_df, self.mag12_file)

        self.phase12_df = pd.concat([self.phase12_df, pd.DataFrame([y_phase12])], ignore_index=True)
        self.save_images(self.phase12_df, self.phase12_file)

        st.success("新的参数集已生成并保存。")
        return True
