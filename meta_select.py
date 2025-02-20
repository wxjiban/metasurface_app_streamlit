import streamlit as st
from app import page_RCS_performance_view
custom_top_bar = """
<style>
/* 1. 隐藏 Streamlit 原生头部（包括菜单） */
[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
    max-height: 0;
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
    background-color: #ADD8E6;
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
    height: 50px; 
    background-color: #FFFFFF; 
    border-bottom: 1px solid #CCC; 
    z-index: 9999; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
">
    超材料RCS仿真与计算软件
</div>
"""





if __name__ == "__main__":

    meta_select()
