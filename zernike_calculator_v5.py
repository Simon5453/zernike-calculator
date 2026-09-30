import streamlit as st  # 导入Streamlit库用于构建网页应用
import math             # 导入数学库用于阶乘计算
import numpy as np      # 导入numpy用于数值计算和生成绘图网格
import matplotlib.pyplot as plt  # 导入matplotlib用于绘制二维图像
import plotly.graph_objects as go  # 导入plotly用于绘制交互式三维图像

# 设置页面配置：标题和图标，使用宽屏模式
st.set_page_config(page_title="标准圆域Zernike多项式计算器", page_icon="🔬", layout="wide")
# 页面主标题
st.title("🔬 标准圆域 Zernike 多项式计算器")

# ================= 通用核心计算函数 =================

# 定义核心计算函数：生成径向多项式的字符串表达式
def get_radial_string(n, m):
    expression = ""  # 初始化表达式字符串
    terms = []       # 存储径向表达式各项的列表
    
    for s in range(m + 1):  # 遍历求和公式中的 s，从 0 到 m
        numerator = ((-1) ** s) * math.factorial(n - s)  # 计算分子
        denominator = math.factorial(s) * math.factorial(m - s) * math.factorial(n - m - s)  # 计算分母
        coef = int(numerator / denominator)  # 计算系数并转换为整数
        power = n - 2 * s  # 计算 rho 的指数：n - 2s
        terms.append((coef, power))  # 将系数和指数组成的元组加入列表
        
    for i, (coef, power) in enumerate(terms):  # 遍历所有项，构建代数表达式
        if coef == 0: continue  # 跳过系数为0的项
        
        # 处理符号
        if i == 0 and coef < 0: expression += "-"
        elif i > 0 and coef > 0: expression += " + "
        elif i > 0 and coef < 0: expression += " - "
            
        abs_coef = abs(coef)  # 获取系数绝对值
        coef_str = "" if abs_coef == 1 and power != 0 else str(abs_coef)  # 若系数为1且非常数项，省略1
        
        # 构建带有上标符号的字符（使用 Unicode 替代 LaTeX，适配 HTML 表格）
        if power == 0: 
            expression += str(abs_coef)  # 常数项
        elif power == 1: 
            expression += coef_str + "ρ"  # 一次方省略指数
        else: 
            superscript_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")  # 定义数字到 Unicode 上标的映射
            superscript_power = str(power).translate(superscript_map)  # 将数字转为上标
            expression += coef_str + f"ρ{superscript_power}"  # 拼接
            
    return expression  # 返回构建好的径向表达式字符串

# 定义数值计算径向多项式的函数：用于绘图
def get_radial_value(n, m, rho):
    val = np.zeros_like(rho)  # 初始化与 rho 同形状的全零数组
    for s in range(m + 1):  # 遍历求和公式
        numerator = ((-1) ** s) * math.factorial(n - s)  # 分子计算
        denominator = math.factorial(s) * math.factorial(m - s) * math.factorial(n - m - s)  # 分母计算
        coef = numerator / denominator  # 计算当前项的系数
        val += coef * (rho ** (n - 2 * s))  # 累加各项：系数 * rho^(n-2s)
    return val  # 返回数值数组

# ================= 初始化状态存储 =================
# 使用 st.session_state 保存计算结果，防止因为点击按钮导致页面刷新时结果丢失
if 'single_result' not in st.session_state:  # 检查单阶计算结果是否在状态中
    st.session_state['single_result'] = None  # 初始化单阶结果
if 'batch_result' not in st.session_state:  # 检查批量计算结果是否在状态中
    st.session_state['batch_result'] = None  # 初始化批量结果

# ================= 第一部分：单阶计算器 =================

st.header("单阶 Zernike 多项式计算")  # 模块标题

# 界面输入区域布局（两列）
col1, col2 = st.columns(2)
with col1:
    n_input = st.text_input("请输入 n (阶数，如 0, 1, 2,3, 4 等整数，无上限):", value="4")  # n 的输入框，不限最大值
with col2:
    l_input = st.text_input("请输入 l (角频率，如 0, ±1, ±2, ±3, ±4 等整数):", value="2")  # l 的输入框

# 单击单阶计算按钮时的逻辑
if st.button("生成 n 阶 Zernike 表格和图像", type="primary", key="btn_batch"):  # 触发批量生成
    with st.spinner('正在计算并绘制所有多项式，请稍候...'):  # 加载动画
        # ---------- 1. 构建 HTML 表格 ----------
        colors = ["#FFFFCC", "#D9E1F2", "#FFF2CC", "#CCFFFF", "#E2F0D9", "#FCE4D6", "#DDEBF7", "#F4CCCC", "#E2EFDA", "#FCE4D6", "#DDEBF7", "#E2F0D9", "#F4CCCC", "#FFF2CC", "#D9E1F2", "#CCFFFF"]  # 颜色池
        
        # 开始拼接 HTML 表格，强制所有列水平居中
        html_table = "<table style='width:100%; text-align:center; border-collapse: collapse; font-size: 16px;'>"
        html_table += "<tr style='background-color: #4B8BBE; color: white;'><th style='border: 1px solid black; padding: 8px;'>n</th><th style='border: 1px solid black; padding: 8px;'>m</th><th style='border: 1px solid black; padding: 8px;'>n-2m</th><th style='border: 1px solid black; padding: 8px;'>Zernike polynomial</th></tr>"
        
        for n in range(max_n + 1):  # 遍历阶数 n
            row_color = colors[n % len(colors)]  # 取颜色
            
            # 修复：m 的取值范围必须是从 0 到 n
            for m_val in range(n + 1):  
                l_val = n - 2 * m_val  # 计算 l，会自然生成正数、零和负数
                radial_expr = get_radial_string(n, m_val)  # 获取径向表达式字符串
                
                # 动态生成角频率项
                if l_val == 1: angular_expr = "sinθ"
                elif l_val == -1: angular_expr = "cosθ"
                elif l_val > 1: angular_expr = f"sin({l_val}θ)"
                elif l_val < -1: angular_expr = f"cos({abs(l_val)}θ)"
                else: angular_expr = "1"  # l=0
                
                # 替换常规字符为 HTML 数学格式
                formatted_radial = radial_expr.replace("ρ²", "<i>ρ</i><sup>2</sup>").replace("ρ³", "<i>ρ</i><sup>3</sup>").replace("ρ⁴", "<i>ρ</i><sup>4</sup>").replace("ρ⁵", "<i>ρ</i><sup>5</sup>").replace("ρ⁶", "<i>ρ</i><sup>6</sup>")
                import re # 导入正则表达式处理更多位数
                formatted_radial = re.sub(r'ρ(\d+)', r'<i>ρ</i><sup>\1</sup>', formatted_radial) # 替换所有上标
                
                if l_val != 0:
                    zernike_str = f"({formatted_radial}) · {angular_expr}"
                else:
                    zernike_str = formatted_radial
                
                # 拼接 HTML
                html_table += f"<tr style='background-color: {row_color};'>"
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{n}</td>"
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{m_val}</td>"
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{l_val}</td>"
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'><i>Z</i><sub>{n}</sub><sup>{l_val}</sup> = {zernike_str}</td>"
                html_table += "</tr>"
        
        html_table += "</table>"  # 闭合表格
        
        # 将表格 HTML 存入状态
        st.session_state['batch_result'] = {'max_n': max_n, 'html_table': html_table}

# 渲染批量生成结果
if st.session_state['batch_result'] is not None:
    res_batch = st.session_state['batch_result']  # 获取状态中的数据
    max_n = res_batch['max_n']  # 获取最大阶数
    
    st.write(f"### {max_n} 阶及以下的所有 Zernike 多项式表达式")
    st.markdown(res_batch['html_table'], unsafe_allow_html=True)  # 渲染表格 HTML
    
    st.write(f"### {max_n} 阶标准圆域 Zernike 图像金字塔")
    
    # 设定网格尺寸
    rows = max_n + 2
    cols = 2 * max_n + 1
    
    # 创建大画布
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.2, rows * 1.2))  
    fig.patch.set_facecolor('white')
    plt.subplots_adjust(left=0.05, right=0.95, top=0.82, bottom=0.05, wspace=0.05, hspace=0.05)
    
    # 准备极坐标网格数据
    rho_grid = np.linspace(0, 1, 80)
    theta_grid = np.linspace(0, 2 * np.pi, 80)
    R_grid, T_grid = np.meshgrid(rho_grid, theta_grid)
    
    # 遍历绘制所有子图
    for n in range(max_n + 1):
        # 先绘制本行的所有图像
        for l in range(-n, n + 1, 2):
            m_val = (n - abs(l)) // 2
            col_idx = max_n + l
            ax = axes[n][col_idx]
            
            R_val = get_radial_value(n, m_val, R_grid)
            T_val = np.sin(l * T_grid) if l > 0 else np.cos(abs(l) * T_grid)
            Z_vals = R_val * T_val
            
            X_grid = R_grid * np.cos(T_grid)
            Y_grid = R_grid * np.sin(T_grid)
            
            ax.pcolormesh(X_grid, Y_grid, Z_vals, cmap='jet', shading='auto', vmin=-np.max(np.abs(Z_vals)), vmax=np.max(np.abs(Z_vals)))
            
            circle = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=0.8)
            ax.add_artist(circle)
            
            ax.set_aspect('equal')
            ax.axis('off')
            
        # 获取该行第一个子图的真实垂直中心，用于放置文本
        ax_ref = axes[n][0]
        pos = ax_ref.get_position()
        row_y_center = (pos.y0 + pos.y1) / 2
        
        # 放置左侧 "Radial Order n" 文本
        fig.text(0.02, row_y_center, f"n={n}", fontsize=12, fontweight='bold', va='center')
        
        # 构建右侧 n, l 组合文本
        if n == 0:
            n_l_str = "n=0, l=0"
        else:
            unique_abs_l = list(range(n, 0, -2))
            l_terms = [f"±{v}" for v in unique_abs_l]
            if n % 2 == 0:
                l_terms.append("0")
                l_terms.reverse()
            n_l_str = f"n={n}, l={', '.join(l_terms)}"
        
        # 放置右侧 "n, l" 文本
        fig.text(0.98, row_y_center, n_l_str, fontsize=10, va='center', ha='right')
    
    # 隐藏多余空格子
    for n in range(rows):
        for col in range(cols):
            if n > max_n:
                axes[n][col].axis('off')
                continue
            l_val = col - max_n
            if abs(l_val) > n or (n - l_val) % 2 != 0:
                axes[n][col].axis('off')
                
    # 在顶部开辟区域绘制坐标轴
    ax_axis = fig.add_axes([0.05, 0.85, 0.90, 0.10])
    ax_axis.set_xlim(-max_n - 0.5, max_n + 0.5)
    ax_axis.set_ylim(0, 1)
    ax_axis.axis('off')
    
    # 绘制主横线和刻度
    ax_axis.plot([-max_n - 0.5, max_n + 0.5], [0.5, 0.5], color='blue', lw=2)
    for l_val in range(-max_n, max_n + 1):
        ax_axis.plot([l_val, l_val], [0.45, 0.55], color='blue', lw=1.5)
        ax_axis.text(l_val, 0.6, str(l_val), ha='center', va='bottom', fontweight='bold', fontsize=10)
        
    # 添加横轴标题
    ax_axis.text(0, 1.1, "Angular Frequency, l = n - 2m", ha='center', va='bottom', color='blue', fontweight='bold', fontsize=12)
    
    st.pyplot(fig)
