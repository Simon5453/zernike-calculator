import streamlit as st  # 导入Streamlit库用于构建网页UI
import math  # 导入数学库用于阶乘计算

# 页面配置：设置网页标题和图标
st.set_page_config(page_title="Zernike 径向多项式计算器", page_icon="🔬")
st.title("🔬 Zernike 径向多项式计算器")  # 页面主标题
st.write("输入阶数 n 和角频率 l，计算标准圆域 Zernike 径向多项式表达式。")  # 页面说明文字

# 核心计算函数（复用之前的逻辑）
def calculate_zernike_expression(n, l):
    if abs(l) > n: return None  # 校验绝对值条件
    if (n - l) % 2 != 0: return None  # 校验同奇偶性
        
    s_max = (n - abs(l)) // 2  # 求和上限
    terms = []  # 存储项
    
    for s in range(s_max + 1):
        numerator = ((-1) ** s) * math.factorial(n - s)  # 分子
        denominator = math.factorial(s) * math.factorial((n + abs(l)) // 2 - s) * math.factorial((n - abs(l)) // 2 - s)  # 分母
        coef = int(numerator / denominator)  # 计算系数
        power = n - 2 * s  # 计算rho的指数
        terms.append((coef, power))  # 添加到列表
        
    expression = ""  # 初始化表达式字符串
    for i, (coef, power) in enumerate(terms):
        if coef == 0: continue  # 忽略系数为0的项
        
        # 符号处理
        if i == 0 and coef < 0: expression += "-"
        elif i > 0 and coef > 0: expression += " + "
        elif i > 0 and coef < 0: expression += " - "
            
        abs_coef = abs(coef)  # 系数绝对值
        coef_str = "" if abs_coef == 1 and power != 0 else str(abs_coef)  # 如果系数是1且不是常数项，省略1
        
        # 拼接rho的幂次，转换为LaTeX格式以在网页端完美渲染
        if power == 0: 
            expression += str(abs_coef)
        elif power == 1: 
            expression += coef_str + r"\rho"
        else: 
            expression += coef_str + rf"\rho^{{{power}}}"
            
    return expression  # 返回最终表达式字符串

# 使用两列布局放置输入框，让界面更整齐
col1, col2 = st.columns(2)
with col1:
    n_input = st.text_input("请输入 n (阶数，如 2, 4 等整数):", value="2")  # n的输入框
with col2:
    l_input = st.text_input("请输入 l (角频率，如 0, -2 等整数):", value="0")  # l的输入框

# 添加一个计算按钮
if st.button("计算表达式", type="primary"):
    try:
        # 尝试将输入转换为整数，如果输入的是小数或字母，int()会报错
        n = int(n_input.strip())
        l = int(l_input.strip())
        
        # 调用计算函数
        result = calculate_zernike_expression(n, l)
        
        if result is None:  # 参数校验失败
            st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")  # 严格按要求的错误提示
        else:  # 计算成功
            st.success(f"成功计算 n={n}, l={l} 的径向多项式：")
            # 使用st.latex渲染带rho的优美数学公式
            st.latex(rf"R_{{{n}}}^{{{l}}}(\rho) = {result}")
            
    except ValueError:
        # 捕获不能转为整数的错误（如用户输入了2.5或abc）
        st.error("n、l 只能取整数值；n、l应该同奇偶；且l≤n.请重新输入")

# 添加一段底部的解释说明
st.markdown("---")
st.markdown(r"*注：$\rho$ 为径向坐标，范围在 $0 \le \rho \le 1$。该表达式用于光学波前像差分析。*")
