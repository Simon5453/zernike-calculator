import streamlit as st  # 导入Streamlit库用于构建网页应用
import math             # 导入数学库用于阶乘计算
import numpy as np      # 导入numpy用于数值计算和生成绘图网格
import matplotlib.pyplot as plt  # 导入matplotlib用于绘制二维图像
import plotly.graph_objects as go  # 导入plotly用于绘制交互式三维图像

# 设置页面配置：标题和图标
st.set_page_config(page_title="标准圆域Zernike多项式计算器", page_icon="🔬")
# 页面主标题
st.title("🔬 标准圆域 Zernike 多项式计算器")
# 页面说明文字
st.write("输入阶数 n 和角频率 l，计算径向及完整表达式，并绘制图像。")

# 定义核心计算函数：生成径向多项式的字符串表达式
def get_radial_string(n, m):
    expression = ""  # 初始化表达式字符串
    terms = []       # 存储径向表达式各项的列表
    
    for s in range(m + 1):  # 遍历求和公式中的 s，从 0 到 m
        numerator = ((-1) ** s) * math.factorial(n - s)  # 计算分子：(-1)^s * (n-s)!
        denominator = math.factorial(s) * math.factorial(m - s) * math.factorial(n - m - s)  # 计算分母：s! * (m-s)! * (n-m-s)!
        coef = int(numerator / denominator)  # 计算系数并转换为整数
        power = n - 2 * s                    # 计算 rho 的指数：n - 2s
        terms.append((coef, power))  # 将系数和指数组成的元组加入列表
        
    for i, (coef, power) in enumerate(terms):  # 遍历所有项，构建代数表达式
        if coef == 0: continue  # 跳过系数为0的项
        
        if i == 0 and coef < 0: expression += "-"  # 如果是第一项且为负，直接加负号
        elif i > 0 and coef > 0: expression += " + "  # 如果不是第一项且为正，加加号
        elif i > 0 and coef < 0: expression += " - "  # 如果不是第一项且为负，加减号
            
        abs_coef = abs(coef)  # 获取系数绝对值
        coef_str = "" if abs_coef == 1 and power != 0 else str(abs_coef)  # 若系数为1且非常数项，省略1
        
        if power == 0: expression += str(abs_coef)  # 如果指数为0，只写系数（常数项）
        elif power == 1: expression += coef_str + "ρ"  # 如果指数为1，省略指数
        else: expression += coef_str + f"ρ^{{{power}}}"  # 否则写出 ρ 的幂次
            
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

# 界面输入区域布局（两列）
col1, col2 = st.columns(2)
with col1:
    n_input = st.text_input("请输入 n (阶数，如 0, 1，3， 2, 4 等整数):", value="4")  # n 的输入框
with col2:
    l_input = st.text_input("请输入 l (角频率，如 0, ±1，±2, ±3 等整数):", value="2")  # l 的输入框

# 计算结果和显示逻辑
if st.button("开始计算并绘图", type="primary"):  # 点击按钮触发计算
    try:
        n = int(n_input.strip())  # 获取并转换 n 为整数
        l = int(l_input.strip())  # 获取并转换 l 为整数
        
        # 校验参数合法性
        if abs(l) > n or (n - l) % 2 != 0:
            st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")  # 提示错误
        else:
            m = (n - l) // 2  # 根据公式计算 m 值
            
            # 第一行：输出用户输入的 n, l 和计算得到的 m
            st.write(f"### 您现在输入的 n = {n}, l = {l}, l = n - 2m,对应的 m = {m}")
            
            # 第二行：径向表达式展示
            st.write("### 完整径向表达式为：")
            # 展示图片2中的通式
            st.latex(r"R_n^l(\rho) = \sum_{s=0}^{(n-|l|)/2} \frac{(-1)^s (n-s)!}{s! \left(\frac{n+|l|}{2}-s\right)! \left(\frac{n-|l|}{2}-s\right)!} \rho^{n-2s}")
            
            radial_expr = get_radial_string(n, m)  # 调用函数获取特定径向表达式
            st.write("代入n,l值后的径向表达式为：")  # 提示文本
            st.latex(rf"R_{{{n}}}^{{{l}}}(\rho) = {radial_expr}")  # 使用 LaTeX 渲染特定表达式
            
            # 第三行：完整 Zernike 表达式
            st.write("### 泽尼克多项式为：")
            st.write("### 用n,l表示的泽尼克多项式为：")
            # 展示用 n,l 表示的通式
            st.latex(r"Z_n^l(\rho, \theta) = R_n^l(\rho) \cdot \begin{cases} \sin(|l|\theta) & l > 0 \\ \cos(|l|\theta) & l \le 0 \end{cases}")
            st.write("### 用n,m表示的泽尼克多项式为：")
            # 展示用 n,m 表示的通式
            st.latex(r"Z_n^{n-2m}(\rho, \theta) = R_n^{n-2m}(\rho) \cdot \begin{cases} \sin((n-2m)\theta) & n-2m > 0 \\ \cos((n-2m)\theta) & n-2m \le 0 \end{cases}")
            
                       # 根据 l 的值动态生成角频率项
            if l == 1:  # 特判 l=1 的情况
                angular_expr = "sin(θ)"  # 省略系数 1，直接写 sin(θ)
            elif l == -1:  # 特判 l=-1 的情况
                angular_expr = "cos(θ)"  # 省略系数 1，直接写 cos(θ)
            elif l > 1:  # 如果 l 大于 1
                angular_expr = f"sin({l}θ)"  # 正常显示 sin(lθ)
            elif l < -1:  # 如果 l 小于 -1
                angular_expr = f"cos({abs(l)}θ)"  # 正常显示 cos(|l|θ)
            else:  # l = 0 的情况
                angular_expr = "1"  # 角频率项为 1

            # 拼接完整的泽尼克表达式
            full_expr = rf"Z_{{{n}}}^{{{l}}} = \left( {radial_expr} \right) \cdot {angular_expr}"  
                
            st.write("代入n,l后的泽尼克表达式为：")  # 提示文本
            st.latex(full_expr)  # 渲染特定公式
            
            # 第四行：Zernike 图像绘制（二维和三维并排）
            st.write("### 标准圆域泽尼克图像为：")  # 标题
            
            # 生成极坐标网格数据
            rho = np.linspace(0, 1, 200)  # 径向坐标 0 到 1，分为 200 个点（减少点数以保证三维流畅）
            theta = np.linspace(0, 2 * np.pi, 200)  # 角向坐标 0 到 2π，分为 200 个点
            R, T = np.meshgrid(rho, theta)  # 生成网格坐标矩阵
            
            R_val = get_radial_value(n, m, R)  # 计算径向多项式在网格上的值
            
            if l > 0:  # 根据条件选取角向部分
                T_val = np.sin(l * T)  # 取正弦
            else:
                T_val = np.cos(abs(l) * T)  # 取余弦
                
            Z = R_val * T_val  # 计算完整的 Zernike 数值矩阵
            
            # 极坐标转换为直角坐标，用于绘图
            X = R * np.cos(T)  # X = ρ * cos(θ)
            Y = R * np.sin(T)  # Y = ρ * sin(θ)
            
                       # 第四行：Zernike 图像绘制（二维和三维上下分布，均居中显示）
            
            # --- 1. 绘制二维图像 ---
            st.write("### Zernike 多项式二维图像")  # 二维图标题
            # 使用三列布局（中间宽，两边窄）来实现二维图像居中
            col_2d_1, col_2d_2, col_2d_3 = st.columns([1, 1.5, 1])
            with col_2d_2:  # 图像放在中间列
                fig2d, ax = plt.subplots(figsize=(4.5, 4.5))  # 创建二维图像对象，稍微调整长宽比使其看起来更适中
                ax.set_title(f"n = {n}, l = {l}", fontsize=14, pad=15)  # 在图像上方标注 n, l 值
                
                # 绘制二维伪彩色图
                mesh = ax.pcolormesh(X, Y, Z, cmap='jet', shading='auto', vmin=-np.max(np.abs(Z)), vmax=np.max(np.abs(Z)))
                
                # 调窄颜色条（将 fraction 从默认的 0.046 改为 0.03，配合更小的 pad）
                cbar = fig2d.colorbar(mesh, ax=ax, fraction=0.03, pad=0.04) 
                cbar.set_label('Z Value', fontsize=10)  # 颜色条标签字体调小
                cbar.ax.tick_params(labelsize=8)        # 颜色条刻度字体调小
                
                # 绘制单位圆边界线
                circle = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=1)
                ax.add_artist(circle)
                
                ax.set_aspect('equal')  # 保证比例一致
                ax.axis('off')          # 隐藏坐标轴
                
                st.pyplot(fig2d)        # 渲染二维图像

            # --- 2. 绘制三维图像 ---
            st.write("### Zernike 多项式三维图像")  # 三维图标题
            # 同样使用三列布局使三维图居中
            col_3d_1, col_3d_2, col_3d_3 = st.columns([1, 1.5, 1])
            with col_3d_2:  # 图像放在中间列
                # 创建 Plotly 三维曲面图
                fig3d = go.Figure(data=[
                    go.Surface(
                        x=X, y=Y, z=Z,
                        colorscale='Jet',
                        # 调窄三维图的颜色条：设置 thickness 尺寸（默认通常是30）
                        colorbar=dict(title='Z Value', len=0.6, thickness=15), 
                        showscale=True
                    )
                ])
                
                fig3d.update_layout(
                    title=f"n = {n}, l = {l}",
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z (Amplitude)',
                        aspectmode='manual',
                        aspectratio=dict(x=1, y=1, z=0.8),
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
                    ),
                    margin=dict(l=0, r=0, b=0, t=30)
                )
                
                # 渲染三维图像（use_container_width=True 会自适应中间列的宽度）
                st.plotly_chart(fig3d, use_container_width=True)
                
    except ValueError:
        # 输入非整数时的错误提示
        st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")
