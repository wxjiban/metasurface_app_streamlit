import os
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
class WebPlotter:
    def __init__(self):
        pass

    def display_static_plot(self, image_path, caption="", use_column_width=True, clamp=True):
        """
        直接读取并显示已经存在的图像文件。

        参数:
            image_path (str): 图像文件的完整路径。
            caption (str): 图像说明文字（可选）。
            use_column_width (bool): 是否按照列宽度自适应显示图像，默认为 True。
            clamp (bool): 是否对图像进行裁切处理（防止自动缩放），默认为 True。
        """
        if os.path.exists(image_path):
            st.image(image_path, caption=caption, use_container_width=use_column_width, clamp=clamp)
        else:
            st.error(f"图像文件 {image_path} 不存在。")

    def draw_dynamic_plot(self, x, y, plot_type="line", title="", xlabel="X", ylabel="Y",
                          figsize=(6, 4), grid=True, **kwargs):
        """
        根据传入数据绘制动态图，并在 Streamlit 中显示。

        参数:
            x (list or array): X 轴数据。
            y (list or array): Y 轴数据，或者是多个曲线组成的列表，例如 [y1, y2, ...]。
            plot_type (str): 绘图类型，目前支持 "line"（折线图）和 "bar"（柱状图），默认为 "line"。
            title (str): 图形标题。
            xlabel (str): X 轴标签。
            ylabel (str): Y 轴标签。
            figsize (tuple): 图像大小，默认为 (6, 4)。
            grid (bool): 是否显示网格，默认为 True。
            **kwargs: 其他 matplotlib 绘图参数，如颜色、线型等。

        返回:
            None（直接调用 st.pyplot 显示图像）
        """
        fig, ax = plt.subplots(figsize=figsize)
        if plot_type == "line":
            # 如果 y 为二维（多条曲线），则遍历绘制
            if isinstance(y[0], (list, tuple)) or (hasattr(y[0], '__iter__') and not isinstance(y[0], str)):
                for curve in y:
                    ax.plot(x, curve, **kwargs)
            else:
                ax.plot(x, y, **kwargs)
        elif plot_type == "bar":
            ax.bar(x, y, **kwargs)
        else:
            st.error(f"不支持的绘图类型: {plot_type}")
            return

        ax.set_title(title, fontsize=14)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        if grid:
            ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    def create_combined_png_with_numbers(self, matrix, png0_path="RCS_array/image/unit0.png", png1_path="RCS_array/image/unit1.png",
                                         output_path="RCS_array/image/combined_image.png"):
        """
        根据矩阵生成一个大PNG文件，包含图片拼接、颜色像素格和数字标注

        :param matrix: 6x6的0 1矩阵
        :param png0_path: PNG文件0的路径
        :param png1_path: PNG文件1的路径
        :param output_path: 最终生成的大PNG文件保存路径
        """
        # 单元宽高（需要根据实际输入PNG调整）
        unit_width = 100
        unit_height = 100
        # 大图尺寸
        rows, cols = matrix.shape
        big_width = cols * unit_width
        big_height = rows * unit_height

        # 创建大图
        total_width = big_width
        total_height = big_height
        combined_image = Image.new("RGB", (total_width, total_height), "white")
        draw = ImageDraw.Draw(combined_image)

        # 加载单元图像
        unit0_img = Image.open(png0_path).resize((unit_width, unit_height))
        unit1_img = Image.open(png1_path).resize((unit_width, unit_height))


        font = ImageFont.load_default()
        font_size = int(unit_width / 3)
        font = ImageFont.truetype("arial.ttf", font_size)
        # 图片拼接部分
        for i in range(rows):
            for j in range(cols):
                x = j * unit_width
                y = i * unit_height
                # 根据矩阵选择对应的PNG文件
                if matrix[i, j] == 0:
                    combined_image.paste(unit0_img, (x, y))
                else:
                    combined_image.paste(unit1_img, (x, y))
        combined_image.save(output_path, "PNG")
        return output_path

# 示例用法
if __name__ == "__main__":
    # 示例1：显示已有图像
    plotter = WebPlotter()
    # 请修改为实际图片路径
    example_image_path = "path/to/your/static_image.png"
    plotter.display_static_plot(example_image_path, caption="静态图示例")

    # 示例2：绘制动态折线图
    x = list(range(10))
    y = [xi**2 for xi in x]
    plotter.draw_dynamic_plot(x, y, plot_type="line", title="折线图示例", xlabel="X轴", ylabel="Y轴", color="green", linestyle="--")
