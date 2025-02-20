import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from RCS_array.DataManager import DataManager
from RCS_array.WebPlotter import WebPlotter
import math
import os
from RCS.rcs import RCSHandler
import time
import json
from PIL import Image
from io import StringIO, BytesIO
# 定义数据和图片目录
RCS_DATA_DIR = os.path.join('RCS', 'data')
RCS_IMAGES_DIR = os.path.join('RCS', 'images')
# 实例化处理器
rcs_handler = RCSHandler(RCS_DATA_DIR, RCS_IMAGES_DIR)
USERNAME = "admin"
PASSWORD = "123"
# --------------- 自定义顶部栏 + 隐藏 Streamlit 默认头部 ---------------
# 淡蓝色 F0F8FF 浅米色 FAF9F6 浅绿色 #F0FFF0 浅灰色（ #F5F5F5 或 #F0F0F0）
custom_top_bar = """
<style>
/* 1. 隐藏 Streamlit 原生头部（包括菜单） */
[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
    max-height: 0;
}
[data-testid="stSidebar"] div.stButton button {
    background-color: #F0F8FF;
    width: 180px;
}
[data-testid="stHeader"]::before {
    content: "";
    display: none;
}

/* 2. 给页面根元素留出一定上边距，避免固定顶栏遮挡内容 */
#root > div:nth-child(1) {
    margin-top: 60px;
}

/* 3. 页面背景色（淡蓝色） */
[data-testid="stAppViewContainer"] {
    background-color: #FAF9F6;
}

/* 4. 按钮大小、字体 */
div[data-testid="stButton"] > button {
    font-size: 2rem !important;
    padding: 1rem 3rem !important;
    margin-top: 20px !important;
}
</style>

<!-- 顶部栏：白色背景、灰色边框，Flex布局，文字居中 -->
<div style="
    position: fixed;
    top: 0; left: 0; right: 0; 
    height: 80px; 
    background-color: #FFFFFF; 
    border-bottom: 1px solid #CCC; 
    z-index: 9999; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 18px ; /* 调整字体大小 */
    font-weight: bold ; /* 加粗字体 */
">
    超表面仿真与计算软件-司黎明教授课题组
</div>
"""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
def login():
    """
    第1界面：欢迎页面
    """
    st.markdown(custom_top_bar, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.image("logo.png", use_container_width=True)
    with col2:
        st.image("logo2.png", use_container_width=True)
    st.markdown("""
        <h1 style="text-align: center; font-size: 3rem; margin-top: 30px;">
            超表面雷达散射截面仿真与计算软件
        </h1>
        <h1 style="text-align: center; font-size: 3rem; margin-top: 10px;">
            司黎明教授课题组
        </h1>
    """, unsafe_allow_html=True)

    # 在标题与按钮间增加一些间距
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("登录成功!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("用户名或密码错误")
    col3, col4 = st.columns(2)
    with col3:
        st.image("image1.png", use_container_width=True)
    with col4:
        st.image("image2.png", width= 250, use_container_width=False)

def display_parameters(params_dict):
    """
    显示结构参数。
    """
    st.subheader("当前结构参数")
    params_display = pd.DataFrame([params_dict])
    st.dataframe(params_display.style.set_properties(**{'text-align': 'left'}))

@st.fragment
def display_performance_data(labels, data_list, x_coords):
    """
    显示性能数据表格。
    """
    for label, data in zip(labels, data_list):
        st.markdown(f"#### {label}")
        output_df = pd.DataFrame([data], columns=x_coords)
        st.dataframe(output_df.style.set_properties(**{'text-align': 'left'}))

@st.fragment
def plot_curves(x_coords, labels, data_list, x_limit,
                y_limits_mag=(0, 1), y_limits_phase=(-180, 180),
                y_ticks_mag=None, y_ticks_phase=None):
    """
    绘制幅度和相位曲线图。
    """
    if st.button("性能曲线图"):
        num_curves = len(labels)

        # 根据曲线数量调整布局：每行最多2个图
        plots_per_row = 2
        rows = (num_curves + plots_per_row - 1) // plots_per_row

        for row in range(rows):
            cols = st.columns(plots_per_row)
            for col in range(plots_per_row):
                plot_idx = row * plots_per_row + col
                if plot_idx < num_curves:
                    label = labels[plot_idx]
                    data = data_list[plot_idx]
                    with cols[col]:
                        color = 'blue' if 'mag' in label else 'red'
                        fig, ax = plt.subplots(figsize=(5, 3))  # 统一的图大小
                        ax.plot(x_coords, data, linestyle='-', color=color)
                        ax.set_xlabel('Frequency (GHz)', fontsize=12)
                        ax.set_ylabel('Magnitude' if 'mag' in label else 'Phase (°)', fontsize=12)
                        ax.set_ylim(y_limits_mag if 'mag' in label else y_limits_phase)
                        ax.set_xlim(x_limit)
                        if 'mag' in label and y_ticks_mag is not None:
                            ax.set_yticks(y_ticks_mag)
                        elif 'phase' in label and y_ticks_phase is not None:
                            ax.set_yticks(y_ticks_phase)
                        ax.tick_params(axis='both', which='major', labelsize=10)
                        ax.grid(True)
                        ax.set_title(label, fontsize=14)
                        st.pyplot(fig)
                        plt.close(fig)

@st.fragment
def display_and_plot_performance(handler, index, x_limit,
                                 y_limits_mag=(0, 1), y_limits_phase=(-180, 180),
                                 y_ticks_mag=None, y_ticks_phase=None):
    """
    显示性能数据并绘制曲线图。
    """
    # 判断数据处理器类型
    if isinstance(handler, RCSHandler):
        # RCSHandler 使用 result-mag11, result-phase11, result-mag12, result-phase12
        y_mag11 = handler.mag11_df.iloc[index].tolist()
        y_phase11 = handler.phase11_df.iloc[index].tolist()
        y_mag12 = handler.mag12_df.iloc[index].tolist()
        y_phase12 = handler.phase12_df.iloc[index].tolist()

        labels = ["result-mag11", "result-phase11", "result-mag12", "result-phase12"]
        data_list = [y_mag11, y_phase11, y_mag12, y_phase12]
    else:
        st.error("未知的数据处理器类型。")
        return

    # 显示性能数据
    if st.button("查看结果", key="step1"):
        for label, data in zip(labels, data_list):
            st.markdown(f"#### {label}")
            output_df = pd.DataFrame([data], columns=handler.x_coords)
            st.dataframe(output_df.style.set_properties(**{'text-align': 'left'}))

        # 绘制曲线图
        plot_curves(
            handler.x_coords,
            labels,
            data_list,
            x_limit=x_limit,
            y_limits_mag=y_limits_mag,
            y_limits_phase=y_limits_phase,
            y_ticks_mag=y_ticks_mag,
            y_ticks_phase=y_ticks_phase
        )
class App:
    def __init__(self):
        # 在侧边栏创建一个选择框，用于页面导航
        # 定义登录页面以及不同的功能页面
        self.login_page = st.Page(login, title="登录")
        self.meta_select_page = st.Page(self.meta_data_select_page, title="超表面选择")
        self.page0 = st.Page(self.page_concept, title="基本概念")
        self.page1 = st.Page(self.page_RCS_performance_view, title="6参数圆环形超表面性能")
        self.page2 = st.Page(self.page_RCS_CST_simulation, title="6参数圆环形超表面仿真")
        self.page3 = st.Page(self.page_array_RCS_performance_calculation, title="6参数圆环形超表面阵列性能")
        self.page4 = st.Page(self.page_11para_RCS_performance_view, title="11参数超表面性能")
        self.page5 = st.Page(self.page_11para_RCS_CST_simulation, title="11参数超表面仿真")
        self.data_manager = DataManager('RCS_array/data')
        self.plotter = WebPlotter()
    def run(self):
        # 根据侧边栏的选择调用对应的界面函数
        # RCS 数据查看
        pg = st.navigation([self.login_page])
        if st.session_state.logged_in:
            st.logo('logo_siderbar_1.png', icon_image='logo_siderbar_2.png', size='large')
            if st.sidebar.button("首页", icon="🔥"):
                st.session_state.logged_in = False
                st.rerun()
            st.sidebar.link_button("司黎明教授课题组", "https://ice.bit.edu.cn/szdw/jsfc/05afa698bf7342298c646d9d4fcdb04b.htm", icon=":material/thumb_up:")
            st.sidebar.write('联系邮箱:lms@bit.edu.cn')
            pg = st.navigation(
                {
                    "功能": [self.page0, self.meta_select_page],
                    "6参数超表面(圆环形拓扑)": [self.page1, self.page2, self.page3],
                    "11参数超表面(多边形拓扑)": [self.page4, self.page5]
                }
            )

        pg.run()
    def page_concept(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        st.title("基本概念")
        st.header("超表面概念")
        st.write('''电磁超表面是脱胎于电磁超材料的一种二维周期性平面人工电磁结构，具有灵活调控电磁波传播和电磁场分布的独特电磁特性，以及低剖面、
        易加工和易集成的结构特性，为天线和波束调控等创新研究带来了巨大的机遇，得到了学术界和工业界的广泛关注，目前已成为多学科领域的创新源地。电磁超表面技术也成为连接物理概念和工程实践的桥梁，不仅为天线性能提升和波束任意调控提
        供新思路，也为通信、雷达、成像、隐身和能量传输等系统应用提供新方案。随着电磁理论的不断发展和工程问题的层出叠现，新的表征方法、调制机理、建模
        方法、优化和设计方法等日新月异，促进了电磁超表面理论和技术的蓬勃发展。''')
        st.header("雷达散射截面(RCS)概念")
        st.write('''雷达散射截面（Radar Cross Section, RCS）是衡量目标对雷达波反射能力的物理量，通常用σ表示，单位为平方米（m²）。它反映了目标在雷达接收方向上的反射强度。''')
        st.subheader('''''')
    @st.fragment
    def download_0(self, csv_data):
        if st.download_button(
            label="性能数据导出",
            data=csv_data,
            file_name="metasurface_performance.csv",
            mime="text/csv"):
            st.info('参数下载成功')
    @st.fragment
    def download_1(self, json_data):
        if st.download_button(
            label="结构参数导出",
            data=json_data,
            file_name="metasurface_paras.txt",
            mime="application/json"):
            st.info('性能数据下载成功')
    @st.fragment
    def download_2(self, img_bytes):
        if st.download_button(
            label="结构图片导出",
            data=img_bytes,
            file_name="downloaded_image.png",  # 默认文件名
            mime="image/png"  # 文件类型
        ):
            st.info('图片下载成功')
    @st.fragment
    def array_input(self):
        # 第一行：显示最上侧的列标签
        header_cols = st.columns(6)  # 第一列为空，用于左侧行号
        header_cols[0].write("")  # 左上角为空
        # for j in range(6):
        #     header_cols[j + 1].write(f"{j + 1}")
        matrix_values = []  # 用于保存每一行的输入值
        # 循环生成每一行
        for i in range(6):
            row_cols = st.columns(6)  # 第一列显示行号，其余 6 列为输入单元
            # # 第一列显示行号
            # row_cols[0].write(f"{i + 1}")
            row_values = []
            # 后面 6 个格子，每个使用 selectbox 输入 0 或 1
            for j in range(6):
                value = row_cols[j].selectbox(
                    label="1",  # label 为空
                    options=[0, 1],
                    key=f"cell_{i}_{j}", label_visibility="hidden"
                )
                row_values.append(value)
            matrix_values.append(row_values)
        # 将输入的矩阵转换为 DataFrame 便于展示
        state_matrix_df = pd.DataFrame(matrix_values, columns=[f"Col{j + 1}" for j in range(6)])
        return state_matrix_df
    @st.fragment
    def meta_data_select_page(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        # 展示不同形状的超表面以及跳转选项
        st.header("多边形类超表面")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("\u00A0 \u00A0 2参数超表面 \u00A0 \u00A0(正方形)")
            st.image("meta_images/2_para_meta.png", use_container_width=True)
        with col2:
            st.button("\u00A0 \u00A03参数超表面\u00A0 \u00A0(矩形)")
            st.image("meta_images/3_para_meta_1.png", use_container_width=True)
        with col3:
            st.button("\u00A0 \u00A03参数超表面\u00A0 \u00A0(方框)")
            st.image("meta_images/3_para_meta_2.png", use_container_width=True)
        col4, col5, col6 = st.columns(3)
        with col4:
            st.button("\u00A0 \u00A05参数超表面\u00A0 \u00A0(十字)")
            st.image("meta_images/5_para_meta.png", width=400)
        with col5:
            st.button("\u00A0 \u00A05参数超表面\u00A0 \u00A0(十字架)")
            st.image("meta_images/5_para_meta_2.png", width=300)
        with col6:
            if st.button("\u00A0 \u00A011参数超表面\u00A0 \u00A0(多边形拓扑)"):
                st.switch_page(self.page4)
            st.image("meta_images/11_para_meta.png", width=300)
        st.header("圆形类超表面")
        col7, col8, col9 = st.columns(3)
        with col7:
            st.button("\u00A0 \u00A02参数超表面\u00A0 \u00A0(圆形)")
            st.image("meta_images/2_para_meta_2.png", width=300)
        with col8:
            st.button("\u00A0 \u00A03参数超表面\u00A0 \u00A0(圆环)")
            st.image("meta_images/3_para_meta_3.png", width=300)
        with col9:
            st.button("\u00A0 \u00A06参数超表面\u00A0 \u00A0(圆环形拓扑)")
            st.image("meta_images/6_para_meta.png", width=300)
    @st.fragment
    def curve_6_para(self, mag0, mag1, phase0, phase1):
        if st.button("性能曲线图", key="step2"):
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(self.data_manager.x_coords, mag0, marker='o', linestyle='-', color="red")
                ax.set_xlabel("Frequency (GHz)", fontsize=12)
                ax.set_ylabel("Reflection amplitude", fontsize=12)
                ax.set_ylim(0, 1)
                ax.set_xlim(2, 20)
                ax.set_title("totalmag0", fontsize=14)
                ax.grid(True)
                st.pyplot(fig)
                plt.close(fig)
            with col2:
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(self.data_manager.x_coords, phase0, marker='o', linestyle='-', color="blue")
                ax.set_xlabel("Frequency (GHz)", fontsize=12)
                ax.set_ylabel("Reflection phase", fontsize=12)
                ax.set_xlim(2, 20)
                # ax.set_ylim(math.pi, math.pi)
                ticks = [-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi]
                labels = [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$']
                ax.set_yticks(ticks)
                ax.set_yticklabels(labels)
                ax.set_title("totalphase0", fontsize=14)
                ax.grid(True)
                st.pyplot(fig)
                plt.close(fig)
            # 第二行：左边为 totalmag1（红色线），右边为 totalphase1（蓝色线）
            col3, col4 = st.columns(2)
            with col3:
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(self.data_manager.x_coords, mag1, marker='o', linestyle='-', color="red")
                ax.set_xlabel("Frequency (GHz)", fontsize=12)
                ax.set_ylabel("Reflection amplitude", fontsize=12)
                ax.set_ylim(0, 1)
                ax.set_xlim(2, 20)
                ax.set_title("totalmag1", fontsize=14)
                ax.grid(True)
                st.pyplot(fig)
                plt.close(fig)
            with col4:
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(self.data_manager.x_coords, phase1, marker='o', linestyle='-', color="blue")
                ax.set_xlabel("Frequency (GHz)", fontsize=12)
                ax.set_ylabel("Reflection phase", fontsize=12)
                ax.set_xlim(2, 20)
                # ax.set_ylim(math.pi, math.pi)
                ticks = [-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi]
                labels = [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$']
                ax.set_yticks(ticks)
                ax.set_yticklabels(labels)
                ax.set_title("totalphase1", fontsize=14)
                ax.grid(True)
                st.pyplot(fig)
                plt.close(fig)
    @st.fragment
    def plot_performance(self, mag0, mag1, performance_data, performance_labels, phase0, phase1):
        if st.button("查看结果", key="step1"):
            display_performance_data(performance_labels, performance_data, self.data_manager.x_coords)
            # 在页面中插入一条黑色分割线
            # 绘制4个曲线图，2×2 布局
            # 第一行：左边为 totalmag0（改为红色线），右边为 totalphase0（蓝色线）
            self.curve_6_para(mag0, mag1, phase0, phase1)
    @st.fragment
    def page_RCS_performance_view(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        st.title("6参数超表面(圆环形拓扑)性能查看")
        # 显示结构示意图：调用 WebPlotter 的 display_static_plot 方法
        self.plotter.display_static_plot("meta_images/6_para_meta.png")
        # 加载图片
        image_path = "meta_images/6_para_meta.png"  # 替换为你图片的路径
        image = Image.open(image_path)
        # 将图片保存到 BytesIO 对象
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        # 在页面中插入一条黑色分割线
        st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
        # 构造下拉框选项，从 self.data_manager.unit_params_df（无表头）中取每一行数据，并根据 self.data_manager.param_names 生成字符串
        options = []
        for _, row in self.data_manager.unit_params_df.iterrows():
            # 使用索引遍历 param_names 中的每个参数，与 row 中相应的列值配对
            parts = [f"{self.data_manager.param_names[i]}:{round(row[i],2)}" for i in range(len(self.data_manager.param_names))]
            options.append(" ".join(parts))

        selected_option = st.selectbox("请选择单元参数集", options=options)
        selected_index = options.index(selected_option)

        # 获取选中行的单元参数
        selected_params = self.data_manager.unit_params_df.iloc[selected_index]

        # 格式化显示，所有数字保留两位小数，
        # 前 3 个参数后附 " mm"，后 2 个参数后附 " °"，其它仅显示数字（可根据实际需求调整）
        formatted_params = {}
        num_params = len(self.data_manager.param_names)
        for i, param in enumerate(self.data_manager.param_names):
            try:
                value = float(selected_params[i])
            except:
                value = selected_params[i]
            formatted_value = f"{value:.2f}"
            if i < 3:
                formatted_value += " mm"
            elif i >= num_params - 2:
                formatted_value += " °"
            formatted_params[param] = formatted_value
        st.subheader("当前单元参数")
        # 使用 Pandas Styler 设置背景色为黑色，文字颜色为白色
        df_styled = pd.DataFrame([formatted_params]).style.set_properties(**{
            'background-color': 'white',
            'color': 'black'
        })
        # 将 Styler 传递给 st.dataframe
        st.dataframe(df_styled)
        # 获取对应的性能数据（4个CSV文件均以每行对应一个单元）
        try:
            mag0 = self.data_manager.totalmag0_df.iloc[selected_index].tolist()
            phase0 = self.data_manager.totalphase0_df.iloc[selected_index].tolist()
            mag1 = self.data_manager.totalmag1_df.iloc[selected_index].tolist()
            phase1 = self.data_manager.totalphase1_df.iloc[selected_index].tolist()
        except Exception as e:
            st.error(f"读取性能数据时出错: {e}")
            return
        performance_labels = ["result-totalmag0", "result-totalphase0", "result-totalmag1", "result-totalphase1"]
        performance_data = [mag0, phase0, mag1, phase1]
        st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
        df = pd.DataFrame(performance_data, index=performance_labels, columns=self.data_manager.x_coords)
        # 创建 CSV 文件的内存数据
        csv_buffer = StringIO()
        df.to_csv(csv_buffer)
        csv_data = csv_buffer.getvalue()
        # 创建 JSON 文件的内存数据
        json_buffer = StringIO()
        json.dump(formatted_params, json_buffer, indent=4)
        json_data = json_buffer.getvalue()
        self.plot_performance(mag0, mag1, performance_data, performance_labels, phase0, phase1)
        st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
        self.download_0(csv_data)
        self.download_1(json_data)
        self.download_2(img_bytes)
    @st.fragment
    def page_RCS_CST_simulation(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        st.title("6参数超表面(圆环形拓扑)电磁仿真")
        # 显示结构示意图：调用 WebPlotter 的 display_static_plot，图片路径为 "image/para.png"
        self.plotter.display_static_plot("meta_images/6_para_meta.png", caption="结构示意图")
        # 加载图片
        image_path = "meta_images/6_para_meta.png"  # 替换为你图片的路径
        image = Image.open(image_path)
        # 将图片保存到 BytesIO 对象
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        st.markdown("### 请输入单元参数：")
        # 在一个表格中显示输入框，表头为 self.data_manager.param_names
        # 注意：由于 unit参数输入需要保留5个数值（假设这里一共5个参数），且要求显示两位小数，
        # 前3个参数加单位 " mm"，后2个参数加单位 " °"
        input_values = {}
        cols = st.columns(len(self.data_manager.param_names))
        for i, param in enumerate(self.data_manager.param_names):
            # 初始值设为 "0"
            # 输入框返回字符串，我们后续转换成数字，并保留两位小数格式显示到表格中
            input_values[param] = cols[i].text_input(label=param, value="0", key=f"input_{param}")
        submitted = st.button(label="保存并仿真")
        if submitted:
            # 将输入值转为浮点数（若转换失败则报错）
            try:
                unit_params = [float(input_values[param]) for param in self.data_manager.param_names]
            except Exception as e:
                st.error("请输入有效的数字格式！")
                return
            # 调用 add_new_unit_result 方法传入新的 unit_params（列表）
            performance = self.data_manager.add_new_unit_result(unit_params)
            if performance is None:
                st.error("仿真计算失败！")
                return
            else:
                st.success("仿真成功！")
                st.markdown("### 当前单元参数")
                # 显示单元参数表格，保留两位小数，前3个参数后加 " mm"，后2个加 " °"
                formatted_params = {}
                total = len(self.data_manager.param_names)
                for i, param in enumerate(self.data_manager.param_names):
                    # 格式化数值，保留两位小数
                    try:
                        val = float(unit_params[i])
                    except:
                        val = unit_params[i]
                    formatted_value = f"{val:.2f}"
                    if i < 3:
                        formatted_value += " mm"
                    elif i >= total - 2:
                        formatted_value += " °"
                    formatted_params[param] = formatted_value
                st.dataframe(formatted_params)
                performance_labels = ["result-totalmag0", "result-totalphase0", "result-totalmag1",
                                      "result-totalphase1"]
                performance_data = [performance['totalmag0'], performance['totalphase0'], performance['totalmag1'], performance['totalphase1']]
                mag0, mag1, phase0, phase1 = performance['totalmag0'], performance['totalmag1'], performance['totalphase0'], performance['totalphase1']

                st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
                df = pd.DataFrame(performance_data, index=performance_labels, columns=self.data_manager.x_coords)
                # 创建 CSV 文件的内存数据
                csv_buffer = StringIO()
                df.to_csv(csv_buffer)
                csv_data = csv_buffer.getvalue()
                # 创建 JSON 文件的内存数据
                json_buffer = StringIO()
                json.dump(formatted_params, json_buffer, indent=4)
                json_data = json_buffer.getvalue()
                # 绘制4个曲线图（2行2列布局）
                # x轴数据为 self.data_manager.x_coords，范围固定为 (2,20)
                self.plot_performance(mag0, mag1, performance_data, performance_labels, phase0, phase1)
                st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
                self.download_0(csv_data)
                self.download_1(json_data)
                self.download_2(img_bytes)
    @st.fragment
    def page_array_RCS_performance_calculation(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        st.title("6参数超表面(圆环形拓扑)阵列RCS\u00A0 \u00A0减缩计算")

        # —— 单元参数选择部分  ——
        options = []
        for _, row in self.data_manager.unit_params_df.iterrows():
            parts = [f"{self.data_manager.param_names[i]}:{round(row[i])}" for i in range(len(self.data_manager.param_names))]
            options.append(" ".join(parts))

        selected_option = st.selectbox("请选择单元参数集", options=options)
        selected_index = options.index(selected_option)

        # 显示选择的单元参数（格式化为两位小数，前3个参数后加" mm"，后2个加" °"）
        selected_params = self.data_manager.unit_params_df.iloc[selected_index].tolist()
        formatted_params = {}
        total = len(self.data_manager.param_names)
        for i, param in enumerate(self.data_manager.param_names):
            try:
                value = float(selected_params[i])
            except:
                value = selected_params[i]
            formatted_value = f"{value:.2f}"
            if i < 3:
                formatted_value += " mm"
            elif i >= total - 2:
                formatted_value += " °"
            formatted_params[param] = formatted_value
        st.subheader("选择的单元参数")
        df_styled = pd.DataFrame([formatted_params]).style.set_properties(**{
            'background-color': 'white',
            'color': 'black'
        })
        # 将 Styler 传递给 st.dataframe
        st.dataframe(df_styled)
        # 读取对应的单元性能数据：4个文件（每个文件每行为一个单元性能，长度与 x_coords 相同）
        try:
            totalmag0 = self.data_manager.totalmag0_df.iloc[selected_index].tolist()
            totalphase0 = self.data_manager.totalphase0_df.iloc[selected_index].tolist()
            totalmag1 = self.data_manager.totalmag1_df.iloc[selected_index].tolist()
            totalphase1 = self.data_manager.totalphase1_df.iloc[selected_index].tolist()
        except Exception as e:
            st.error(f"读取单元性能数据时出错: {e}")
            return

        st.markdown("### 单元性能曲线图")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(self.data_manager.x_coords, totalmag0, marker='o', linestyle='-', color="red")
            ax.set_xlabel("Frequency (GHz)", fontsize=12)
            ax.set_ylabel("Reflection amplitude", fontsize=12)
            ax.set_xlim(2, 20)
            ax.set_ylim(0, 1)
            ax.set_title("totalmag0", fontsize=14)
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)
        with col2:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(self.data_manager.x_coords, totalphase0, marker='o', linestyle='-', color="blue")
            ax.set_xlabel("Frequency (GHz)", fontsize=12)
            ax.set_ylabel("Reflection phase", fontsize=12)
            ax.set_xlim(2, 20)
            ticks = [-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi]
            labels = [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$']
            ax.set_yticks(ticks)
            ax.set_yticklabels(labels)
            ax.set_title("totalphase0", fontsize=14)
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(self.data_manager.x_coords, totalmag1, marker='o', linestyle='-', color="red")
            ax.set_xlabel("Frequency (GHz)", fontsize=12)
            ax.set_ylabel("Reflection amplitude", fontsize=12)
            ax.set_xlim(2, 20)
            ax.set_ylim(0, 1)
            ax.set_title("totalmag1", fontsize=14)
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)
        with col4:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(self.data_manager.x_coords, totalphase1, marker='o', linestyle='-', color="blue")
            ax.set_xlabel("Frequency (GHz)", fontsize=12)
            ax.set_ylabel("Reflection phase", fontsize=12)
            ax.set_xlim(2, 20)
            ticks = [-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi]
            labels = [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$']
            ax.set_yticks(ticks)
            ax.set_yticklabels(labels)
            ax.set_title("totalphase1", fontsize=14)
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)

        # —— 阵列RCS性能计算部分  ——
        st.markdown("### RCS阵列性能")

        # 简单表格输入6×6 01矩阵, 这里用 st.experimental_data_editor 展示默认全0的6×6矩阵
        st.markdown("### 请填写 6×6 矩阵 (每个格子选择 0 或 1)")
        state_matrix_df = self.array_input()
        if st.button("计算阵列RCS减缩性能"):
            st.markdown("### 您输入的矩阵为：")
            st.dataframe(state_matrix_df)
            # 将编辑表格转换为二维列表
            state_matrix = np.reshape(np.array(state_matrix_df.values.tolist()),(6,6))
            # 调用 WebPlotter 中创建组合图片的方法，传入矩阵，生成组合图片后展示（此方法需在 WebPlotter 类中实现）
            combined_filename = self.plotter.create_combined_png_with_numbers(state_matrix)
            st.image(combined_filename, caption="组合阵列图", use_container_width=True)
            # 加载图片
            image_path = combined_filename  # 替换为你图片的路径
            image = Image.open(image_path)
            # 将图片保存到 BytesIO 对象
            img_bytes = BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            # 调用 DataManager 的 compute_rcsr 方法，传入状态矩阵和4个单元性能数据
            rcsr = self.data_manager.compute_rcsr(state_matrix, totalmag0, totalphase0, totalmag1, totalphase1)
            if rcsr is None:
                st.error("RCSR 计算失败！")
            else:
                st.success("RCSR 计算成功！")
                st.markdown("### 阵列 RCSR 性能")
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.plot(self.data_manager.x_coords, rcsr, marker='o', linestyle='-', color="purple")
                ax.set_xlabel("Frequency (GHz)", fontsize=12)
                ax.set_ylabel("RCSR (dB)", fontsize=12)
                ax.set_xlim(2, 20)
                ax.grid(True)
                ax.set_title("RCSR", fontsize=14)
                st.pyplot(fig)
                plt.close(fig)
                df = pd.DataFrame(rcsr, index=self.data_manager.x_coords, columns=['RCSR'])
                # 创建 CSV 文件的内存数据
                csv_buffer = StringIO()
                df.to_csv(csv_buffer)
                csv_data = csv_buffer.getvalue()
                # 创建 JSON 文件的内存数据
                json_buffer = StringIO()
                # 将 JSON 数据写入 StringIO，确保每行保持 6 个数
                json.dump(state_matrix.tolist(), json_buffer, indent=4, separators=(',', ': '))
                # 获取 JSON 字符串
                json_data = json_buffer.getvalue()
                st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
                self.download_0(csv_data)
                self.download_1(json_data)
                self.download_2(img_bytes)
    @st.fragment
    def page_11para_RCS_performance_view(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        # 页面标题
        st.title("11参数超表面(多边形拓扑)\u00A0 \u00A0 \u00A0 \u00A0 \u00A0 \u00A0 \u00A0 \u00A0 \u00A0 \u00A0性能查看")
        # 新增展示区：仅显示图片，按列高等比缩放并居中
        st.markdown("### 结构参数")
        image_col, _ = st.columns([1, 1])
        with image_col:
            image_path = os.path.join(RCS_IMAGES_DIR, 'display_image.jpg')  # 请确保此图片存在于项目目录中
            if os.path.exists(image_path):
                # 使用 Streamlit 的内置方法保持图片等比缩放，并裁切
                st.image(image_path, caption="RCS 结构图", use_container_width=True, clamp=True)
            else:
                st.warning(f"图片 `{image_path}` 未找到。请确保图片存在于项目目录中。")
        # 加载图片
        image = Image.open(image_path)
        # 将图片保存到 BytesIO 对象
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        st.markdown("### 请输入单元参数：")
        st.header("性能数据查看")
        if rcs_handler.params_df.empty:
            st.info("暂无参数集可展示。请在侧边栏选择 'RCS CST仿真' 进行添加。")
        else:
            # 创建带有行号和前两个参数的标签
            def generate_labels_rcs(row):
                if len(row) >= 2:
                    return f"{row.name} - {rcs_handler.param_names[0]}: {row[rcs_handler.param_names[0]]}, {rcs_handler.param_names[1]}: {row[rcs_handler.param_names[1]]}"
                else:
                    return f"{row.name}"

            labels = rcs_handler.params_df.apply(generate_labels_rcs, axis=1).tolist()

            # 选择要展示的参数集
            selected_label = st.selectbox("选择展示数据", options=labels)
            selected_index = labels.index(selected_label)

            # 获取对应的参数数据
            selected_params = rcs_handler.params_df.iloc[selected_index].to_dict()

            # 显示参数数据
            display_parameters(selected_params)

            # 获取并显示性能数据及曲线图
            if (not rcs_handler.mag11_df.empty and selected_index < len(rcs_handler.mag11_df) and
                    not rcs_handler.phase11_df.empty and selected_index < len(rcs_handler.phase11_df) and
                    not rcs_handler.mag12_df.empty and selected_index < len(rcs_handler.mag12_df) and
                    not rcs_handler.phase12_df.empty and selected_index < len(rcs_handler.phase12_df)):
                performance_labels = ["result-mag11", "result-totalphase11", "result-mag12",
                                      "result-phase12"]
                performance_data = [rcs_handler.mag11_df.iloc[selected_index].values, rcs_handler.phase11_df.iloc[selected_index].values, rcs_handler.mag12_df.iloc[selected_index].values, rcs_handler.phase12_df.iloc[selected_index].values]
                st.markdown(
                    """
                    <hr style="border:1px solid black;">
                    """,
                    unsafe_allow_html=True
                )
                df = pd.DataFrame(performance_data, index=performance_labels, columns=rcs_handler.x_coords)
                # 创建 CSV 文件的内存数据
                csv_buffer = StringIO()
                df.to_csv(csv_buffer)
                csv_data = csv_buffer.getvalue()
                # 创建 JSON 文件的内存数据
                json_buffer = StringIO()
                json.dump(selected_params, json_buffer, indent=4)
                json_data = json_buffer.getvalue()
                # 使用封装的函数显示性能数据和绘图
                display_and_plot_performance(
                    handler=rcs_handler,
                    index=selected_index,
                    x_limit=(0, 40)
                )
                st.markdown("""<hr style="border:1px solid black;">""", unsafe_allow_html=True)
                self.download_0(csv_data)
                self.download_1(json_data)
                self.download_2(img_bytes)
            else:
                st.warning("对应的曲线数据不存在。")
    @st.fragment
    def page_11para_RCS_CST_simulation(self):
        st.markdown(custom_top_bar, unsafe_allow_html=True)
        st.title("11参数超表面(多边形拓扑)电磁\u00A0 \u00A0 \u00A0 \u00A0仿真")
        # 获取最后一行的参数数据作为默认值
        if not rcs_handler.params_df.empty:
            last_params = rcs_handler.params_df.iloc[-1].to_dict()
        else:
            last_params = {param: "0" for param in rcs_handler.param_names}
        # 表单用于添加新参数集

        st.write("填写以下参数的数值。")

        # 设置每行5列
        cols_per_row = 5
        total_params = len(rcs_handler.param_names)
        rows = (total_params + cols_per_row - 1) // cols_per_row  # 向上取整

        new_params = {}

        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col in range(cols_per_row):
                param_idx = row * cols_per_row + col
                if param_idx < total_params:
                    param = rcs_handler.param_names[param_idx]
                    new_params[param] = cols[col].text_input(
                        f"{param}:",
                        value=str(last_params.get(param, "0")),
                        key=f"new_rcs_{param}"
                    )

        # 提交按钮
        if st.button("保存并仿真"):
            # 检查所有参数是否已填写
            if any(value.strip() == "" for value in new_params.values()):
                st.error("请填写所有参数的数值。")
            else:
                try:
                    # 将参数值转换为浮点数
                    new_params_float = {k: float(v) for k, v in new_params.items()}
                except ValueError:
                    st.error("所有参数值必须是有效的浮点数。请检查输入。")
                    st.stop()

                # 由于 RCS 不涉及编码映射，这里直接添加新参数集
                success = rcs_handler.add_new_params(new_params_float)
                if success:
                    # 显示参数和输出数据
                    display_parameters(new_params_float)
                    y_mag11 = rcs_handler.mag11_df.iloc[-1].tolist()
                    y_phase11 = rcs_handler.phase11_df.iloc[-1].tolist()
                    y_mag12 = rcs_handler.mag12_df.iloc[-1].tolist()
                    y_phase12 = rcs_handler.phase12_df.iloc[-1].tolist()

                    performance_labels = ["result-mag11", "result-phase11", "result-mag12", "result-phase12"]
                    performance_data = [y_mag11, y_phase11, y_mag12, y_phase12]
                    display_performance_data(performance_labels, performance_data, rcs_handler.x_coords)
                    # 绘制曲线图
                    plot_curves(
                        rcs_handler.x_coords,
                        performance_labels,
                        performance_data,
                        x_limit=(0, 40)
                    )
                    st.markdown(
                        """
                        <hr style="border:1px solid black;">
                        """,
                        unsafe_allow_html=True
                    )
                    df = pd.DataFrame(performance_data, index=performance_labels, columns=rcs_handler.x_coords)
                    # 创建 CSV 文件的内存数据
                    csv_buffer = StringIO()
                    df.to_csv(csv_buffer)
                    csv_data = csv_buffer.getvalue()
                    # 创建 JSON 文件的内存数据
                    json_buffer = StringIO()
                    json.dump(new_params_float, json_buffer, indent=4)
                    json_data = json_buffer.getvalue()
                    self.download_0(csv_data)
                    self.download_1(json_data)
                elif rcs_handler.params_df.empty:
                    st.info("暂无参数集，请通过 'RCS CST仿真' 添加新的参数集。")
def main():
    app = App()
    app.run()
if __name__ == "__main__":
    main()
