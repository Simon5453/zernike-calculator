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
if st.button("开始计算并绘图", type="primary", key="btn_single"):  # 点击按钮触发计算
    try:
        n = int(n_input.strip())  # 获取并转换 n 为整数
        l = int(l_input.strip())  # 获取并转换 l 为整数

        # 校验参数合法性
        if abs(l) > n or (n - l) % 2 != 0:
            st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")  # 提示错误
        else:
            # 计算所有需要的数据
            m = (n - abs(l)) // 2  # 计算 m 值，使用绝对值防止负数阶乘报错

            # 生成极坐标网格数据
            rho = np.linspace(0, 1, 200)  # 径向坐标
            theta = np.linspace(0, 2 * np.pi, 200)  # 角向坐标
            R, T = np.meshgrid(rho, theta)  # 生成网格坐标矩阵

            R_val = get_radial_value(n, m, R)  # 计算径向多项式
            T_val = np.sin(l * T) if l > 0 else np.cos(abs(l) * T)  # 角向部分
            Z = R_val * T_val  # 计算完整的 Zernike 数值矩阵

            X = R * np.cos(T)  # 极坐标转直角坐标 X
            Y = R * np.sin(T)  # 极坐标转直角坐标 Y

            # 动态生成角频率项
            if l == 1: angular_expr = "sin(θ)"
            elif l == -1: angular_expr = "cos(θ)"
            elif l > 1: angular_expr = f"sin({l}θ)"
            elif l < -1: angular_expr = f"cos({abs(l)}θ)"
            else: angular_expr = "1"

            # 构建表达式字符串
            radial_expr = get_radial_string(n, m)  # 获取径向表达式
            full_expr = rf"Z_{{{n}}}^{{{l}}} = \left( {radial_expr} \right) \cdot {angular_expr}"  # 拼接完整表达式

            # 将计算结果打包存入状态，供每次页面重绘时使用
            st.session_state['single_result'] = {
                'n': n, 'l': l, 'm': m,
                'radial_expr': radial_expr,
                'full_expr': full_expr,
                'X': X, 'Y': Y, 'Z': Z
            }

    except ValueError:
        st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")  # 输入非整数时的错误提示

# 渲染单阶计算结果（不管按钮状态如何，只要状态里有结果就渲染）
if st.session_state['single_result'] is not None:
    res = st.session_state['single_result']  # 从状态中取出结果
    st.write(f"### 您现在输入的 n = {res['n']}, l = {res['l']}, 对应的 m = {res['m']}")  # 输出基本信息

    st.write("### 径向表达式为：")  # 径向表达式标题
    st.latex(r"R_n^l(\rho) = \sum_{s=0}^{(n-|l|)/2} \frac{(-1)^s (n-s)!}{s! \left(\frac{n+|l|}{2}-s\right)! \left(\frac{n-|l|}{2}-s\right)!} \rho^{n-2s}")  # 展示通式
    st.write("代入 n, l 后的表达式为：")  # 提示文本
    st.latex(rf"R_{{{res['n']}}}^{{{res['l']}}}(\rho) = {res['radial_expr']}")  # 渲染特定表达式

    st.write("### 泽尼克多项式为：")  # 泽尼克多项式标题
    st.latex(r"Z_n^l(\rho, \theta) = R_n^l(\rho) \cdot \begin{cases} \sin(|l|\theta) & l > 0 \\ \cos(|l|\theta) & l \le 0 \end{cases}")  # n,l通式
    st.write("代入 n, l 后的表达式为：")  # 提示文本
    st.latex(res['full_expr'])  # 渲染特定公式

    st.write("### Zernike 多项式二维图像")  # 二维图标题
    col_2d_1, col_2d_2, col_2d_3 = st.columns([1, 1.5, 1])  # 利用列布局居中
    with col_2d_2:
        fig2d, ax = plt.subplots(figsize=(4.5, 4.5))  # 创建图像
        ax.set_title(f"n = {res['n']}, l = {res['l']}", fontsize=14, pad=15)  # 标题
        mesh = ax.pcolormesh(res['X'], res['Y'], res['Z'], cmap='jet', shading='auto', vmin=-np.max(np.abs(res['Z'])), vmax=np.max(np.abs(res['Z'])))  # 绘图
        cbar = fig2d.colorbar(mesh, ax=ax, fraction=0.03, pad=0.04)  # 颜色条
        cbar.set_label('Z Value', fontsize=10)  # 标签
        circle = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=1)  # 边界圆
        ax.add_artist(circle)  # 添加圆
        ax.set_aspect('equal')  # 等比例
        ax.axis('off')  # 隐藏坐标轴
        st.pyplot(fig2d)  # 渲染图像

    st.write("### Zernike 多项式三维图像")  # 三维图标题
    col_3d_1, col_3d_2, col_3d_3 = st.columns([1, 1.5, 1])  # 居中
    with col_3d_2:
        fig3d = go.Figure(data=[go.Surface(x=res['X'], y=res['Y'], z=res['Z'], colorscale='Jet', colorbar=dict(title='Z Value', len=0.6, thickness=15), showscale=True)])  # 三维图
        fig3d.update_layout(title=f"n = {res['n']}, l = {res['l']}", scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z', aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.8)), margin=dict(l=0, r=0, b=0, t=30))  # 布局
        st.plotly_chart(fig3d, use_container_width=True)  # 渲染三维图

# ================= 第二部分：指定阶数 N 批量生成 =================

st.markdown("---")  # 分割线
st.header("n阶泽尼克批量生成")  # 模块标题

# 用户输入最大阶数 N，将最大值放宽到 15
max_n = st.number_input("请输入阶数 n（将计算 0 到 n 阶的所有 Zernike 多项式，最高支持15阶，计算量较大）:", min_value=0, max_value=15, value=4, step=1)  # 输入最大阶数
if st.button("生成 n 阶 Zernike 表格和图像", type="primary", key="btn_batch"):  # 触发批量生成按钮
    with st.spinner('正在计算并绘制所有多项式，请稍候...'):  # 显示加载动画，防止用户以为卡死
        # ---------- 1. 构建 HTML 表格 ----------
        # 定义颜色池，用于区分不同阶数 n 所在行的背景色
        colors = ["#FFFFCC", "#D9E1F2", "#FFF2CC", "#CCFFFF", "#E2F0D9", "#FCE4D6", "#DDEBF7", "#F4CCCC", "#E2EFDA", "#FCE4D6", "#DDEBF7", "#E2F0D9", "#F4CCCC", "#FFF2CC", "#D9E1F2", "#CCFFFF"]  
        
        # 开始拼接 HTML 表格，style 中强制所有内容水平居中
        html_table = "<table style='width:100%; text-align:center; border-collapse: collapse; font-size: 16px;'>"
        # 拼接表头行
        html_table += "<tr style='background-color: #4B8BBE; color: white;'><th style='border: 1px solid black; padding: 8px;'>n</th><th style='border: 1px solid black; padding: 8px;'>m</th><th style='border: 1px solid black; padding: 8px;'>n-2m</th><th style='border: 1px solid black; padding: 8px;'>Zernike polynomial</th></tr>"
        
        for n in range(max_n + 1):  # 遍历阶数 n，从 0 到用户输入的最大阶数
            row_color = colors[n % len(colors)]  # 根据 n 的值循环分配该行的背景颜色
            
            # 修复核心：m 的取值范围必须是从 0 到 n（绝不能用 m_max = n // 2）
            for m_val in range(n + 1):  # 遍历 m，从 0 到 n
                l_val = n - 2 * m_val  # 计算 l 的值，这样会自然生成正数、零和负数三种情况
                radial_expr = get_radial_string(n, (n - abs(l_val)) // 2)  # 修复：径向多项式只与|l|有关，必须用绝对值的m来调用
                
                # 动态生成角频率项（根据 l 的正负决定是 sin 还是 cos）
                if l_val == 1: angular_expr = "sinθ"  # 特判 l=1 省略系数 1
                elif l_val == -1: angular_expr = "cosθ"  # 特判 l=-1 省略系数 1
                elif l_val > 1: angular_expr = f"sin({l_val}θ)"  # l>1 正常显示
                elif l_val < -1: angular_expr = f"cos({abs(l_val)}θ)"  # l<-1 正常显示
                else: angular_expr = "1"  # 当 l=0 时，角频率项为 1
                
                # 替换常规字符为 HTML 数学格式（使用 <i> 和 <sup> 标签模拟数学排版）
                formatted_radial = radial_expr.replace("ρ²", "<i>ρ</i><sup>2</sup>").replace("ρ³", "<i>ρ</i><sup>3</sup>").replace("ρ⁴", "<i>ρ</i><sup>4</sup>").replace("ρ⁵", "<i>ρ</i><sup>5</sup>").replace("ρ⁶", "<i>ρ</i><sup>6</sup>")
                import re # 导入正则表达式库处理更复杂的情况
                formatted_radial = re.sub(r'ρ(\d+)', r'<i>ρ</i><sup>\1</sup>', formatted_radial) # 正则替换所有上标（处理大于9的指数）
                
                if l_val != 0:  # 如果 l 不为 0，拼接径向部分和角向部分
                    zernike_str = f"({formatted_radial}) · {angular_expr}"
                else:  # 如果 l 为 0，只有径向部分（角向部分为 1 乘以径向部分）
                    zernike_str = formatted_radial
                
                # 拼接当前这一行的 HTML 内容
                html_table += f"<tr style='background-color: {row_color};'>"  # 应用背景色
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{n}</td>"  # 写入 n
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{m_val}</td>"  # 写入 m
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{l_val}</td>"  # 写入 n-2m (即 l)
                html_table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'><i>Z</i><sub>{n}</sub><sup>{l_val}</sup> = {zernike_str}</td>"  # 写入多项式公式
                html_table += "</tr>"  # 结束当前行
        
        html_table += "</table>"  # 闭合整个 HTML 表格
        
        # 将表格 HTML 存入 session_state（状态存储），防止点击其他按钮时结果丢失
        st.session_state['batch_result'] = {'max_n': max_n, 'html_table': html_table}

# ================= 渲染批量生成结果（仅当状态中有结果时执行） =================
if st.session_state['batch_result'] is not None:  # 检查状态中是否存在批量生成结果
    res_batch = st.session_state['batch_result']  # 从状态中取出结果
    max_n = res_batch['max_n']  # 获取最大阶数 n
    
    st.write(f"### {max_n} 阶及以下的所有 Zernike 多项式表达式")  # 显示表格标题
    st.markdown(res_batch['html_table'], unsafe_allow_html=True)  # 将 HTML 表格渲染到网页上
    
    st.write(f"### {max_n} 阶标准圆域 Zernike 图像金字塔")  # 显示图像金字塔标题
    
    # 设定网格尺寸：行数为 max_n + 2（多出一行用于放置顶部坐标轴），列数为 2 * max_n + 1
    rows = max_n + 2
    cols = 2 * max_n + 1
    
    # 创建大画布，根据行列数动态计算画布大小
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.2, rows * 1.2))  
    fig.patch.set_facecolor('white')  # 设置画布背景色为白色
    # 调整子图间距，预留顶部空间用于绘制横轴 (top=0.82)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.82, bottom=0.05, wspace=0.05, hspace=0.05)
    
    # 准备极坐标网格数据，用于数值计算
    rho_grid = np.linspace(0, 1, 80)  # 径向坐标 0 到 1，共 80 个点（减少点数避免卡顿）
    theta_grid = np.linspace(0, 2 * np.pi, 80)  # 角向坐标 0 到 2π，共 80 个点
    R_grid, T_grid = np.meshgrid(rho_grid, theta_grid)  # 生成极坐标网格
    
    # 遍历绘制所有子图（圆形图像）
    for n in range(max_n + 1):  # 遍历每一行
        # 先绘制本行的所有图像
        for l in range(-n, n + 1, 2):  # 遍历该行的每个 l 值（步长为 2）
            m_val = (n - abs(l)) // 2  # 计算对应的 m 值
            col_idx = max_n + l  # 计算该 l 值对应在网格中的列索引
            ax = axes[n][col_idx]  # 获取对应的子图对象
            
            # 计算 Zernike 多项式在该网格上的数值
            R_val = get_radial_value(n, m_val, R_grid)  # 计算径向部分数值
            T_val = np.sin(l * T_grid) if l > 0 else np.cos(abs(l) * T_grid)  # 计算角向部分数值
            Z_vals = R_val * T_val  # 径向部分乘以角向部分得到完整数值
            
            # 将极坐标转换为直角坐标，用于绘图
            X_grid = R_grid * np.cos(T_grid)
            Y_grid = R_grid * np.sin(T_grid)
            
            # 绘制二维伪彩色图（使用 Jet 颜色映射）
            ax.pcolormesh(X_grid, Y_grid, Z_vals, cmap='jet', shading='auto', vmin=-np.max(np.abs(Z_vals)), vmax=np.max(np.abs(Z_vals)))
            
            # 绘制单位圆黑色边框
            circle = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=0.8)
            ax.add_artist(circle)
            
            ax.set_aspect('equal')  # 保证 X 和 Y 轴比例一致，使圆形不拉伸
            ax.axis('off')  # 隐藏坐标轴边框和刻度
            
        # 获取该行第一个子图的实际位置，用于精确计算该行的垂直中心线
        ax_ref = axes[n][0]  # 取该行第一列子图作为参考
        pos = ax_ref.get_position()  # 获取该子图框的边界位置 (x0, y0, width, height)
        row_y_center = (pos.y0 + pos.y1) / 2  # 计算垂直中心坐标（完美对齐的关键）
        
        # 在该行垂直中心处放置左侧 "Radial Order n" 文本
        fig.text(0.02, row_y_center, f"n={n}", fontsize=12, fontweight='bold', va='center')
        
        # 构建右侧显示的 n, l 组合文本
        if n == 0:
            n_l_str = "n=0, l=0"  # 第 0 行特殊情况
        else:
            unique_abs_l = list(range(n, 0, -2))  # 获取非零绝对值列表（如 n=4 则为 [4, 2]）
            l_terms = [f"±{v}" for v in unique_abs_l]  # 格式化为 ±数字 的形式
            if n % 2 == 0:  # 如果 n 是偶数，说明包含 l=0 的情况
                l_terms.append("0")  # 追加 0
                l_terms.reverse()  # 调整顺序，变成 l=0, ±2, ±4 这种更符合直觉的排列
            n_l_str = f"n={n}, l={', '.join(l_terms)}"  # 拼接最终字符串
        
        # 在该行垂直中心处放置右侧 "n, l" 文本
        fig.text(0.98, row_y_center, n_l_str, fontsize=10, va='center', ha='right')
    
    # 隐藏没有对应多项式的空白子图
    for n in range(rows):  # 遍历所有行（包含顶部预留行）
        for col in range(cols):  # 遍历所有列
            if n > max_n:  # 如果是顶部预留行
                axes[n][col].axis('off')  # 直接隐藏
                continue  # 跳过后续判断
            l_val = col - max_n  # 计算该列对应的 l 值
            if abs(l_val) > n or (n - l_val) % 2 != 0:  # 如果 l 不满足条件（超出范围或奇偶性不符）
                axes[n][col].axis('off')  # 隐藏该子图
                
    # 在顶部专门开辟一块区域绘制坐标轴，避免与图像重叠
    ax_axis = fig.add_axes([0.05, 0.85, 0.90, 0.10])  # [左, 底, 宽, 高]
    ax_axis.set_xlim(-max_n - 0.5, max_n + 0.5)  # 限制横轴显示范围
    ax_axis.set_ylim(0, 1)  # 限制纵轴显示范围
    ax_axis.axis('off')  # 隐藏边框
    
    # 绘制主横线（蓝色）
    ax_axis.plot([-max_n - 0.5, max_n + 0.5], [0.5, 0.5], color='blue', lw=2)
    
    # 绘制刻度和数值
    for l_val in range(-max_n, max_n + 1):  # 遍历所有 l 值
        ax_axis.plot([l_val, l_val], [0.45, 0.55], color='blue', lw=1.5)  # 绘制垂直短线作为刻度
        ax_axis.text(l_val, 0.6, str(l_val), ha='center', va='bottom', fontweight='bold', fontsize=10)  # 添加刻度数值
        
    # 添加横轴标题
    ax_axis.text(0, 1.1, "Angular Frequency, l = n - 2m", ha='center', va='bottom', color='blue', fontweight='bold', fontsize=12)
    
    st.pyplot(fig)  # 将绘制好的大图渲染到网页上