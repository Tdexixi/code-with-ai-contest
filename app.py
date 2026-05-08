import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# 设置页面配置
st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

st.title("📡 5G 信号可视化看板")
st.markdown("欢迎来到 **'Code with AI' 极客探索赛**！")
st.info("💡 **通关提示**：这是基础关卡的完整实现，包含数据加载、地图渲染和图表展示。")

# ==========================================
# 基础关卡：数据加载
# ==========================================
try:
    # 使用 pandas 读取 CSV 数据
    df = pd.read_csv('data/signal_samples.csv')
    st.success(f"✅ 成功加载数据：{len(df)} 条记录")
except FileNotFoundError:
    st.error("❌ 找不到 data/signal_samples.csv 文件，请确保数据文件存在。")
    st.stop()

# ==========================================
# 基础关卡：侧边栏筛选器（进阶功能）
# ==========================================
st.sidebar.header("🔧 筛选器")

# 频段筛选
if 'Band' in df.columns:
    bands = df['Band'].unique()
    selected_bands = st.sidebar.multiselect(
        "选择频段 (Band)",
        options=bands,
        default=bands
    )
    df_filtered = df[df['Band'].isin(selected_bands)]
else:
    df_filtered = df

# RSRP 范围筛选
if 'RSRP_dBm' in df.columns:
    rsrp_min, rsrp_max = float(df['RSRP_dBm'].min()), float(df['RSRP_dBm'].max())
    selected_rsrp_range = st.sidebar.slider(
        "选择 RSRP 范围 (dBm)",
        min_value=rsrp_min,
        max_value=rsrp_max,
        value=(rsrp_min, rsrp_max)
    )
    df_filtered = df_filtered[
        (df_filtered['RSRP_dBm'] >= selected_rsrp_range[0]) &
        (df_filtered['RSRP_dBm'] <= selected_rsrp_range[1])
    ]

st.sidebar.write(f"当前显示 {len(df_filtered)} 条数据")

# ==========================================
# 基础关卡：信号热力/散点地图
# ==========================================
st.subheader("🗺️ 5G 信号热力地图")

# 定义颜色函数：根据 RSRP 信号强度变色
def get_color(rsrp):
    """
    根据 RSRP 信号强度返回 RGB 颜色
    大于 -90dBm 为绿色，小于 -110dBm 为红色，中间为黄色
    """
    if rsrp > -90:
        return [0, 255, 0]  # 绿色 (强信号)
    elif rsrp < -110:
        return [255, 0, 0]  # 红色 (弱信号)
    else:
        # 黄色到红色的渐变
        ratio = (rsrp + 110) / 20  # 0 到 1 的比例
        return [
            int(255 * (1 - ratio)),  # R
            int(255 * ratio),         # G
            0                         # B
        ]

# 为数据添加颜色列
df_filtered['color'] = df_filtered['RSRP_dBm'].apply(get_color)

# 准备地图数据
if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
    map_data = df_filtered[['Latitude', 'Longitude', 'RSRP_dBm', 'color']].copy()
    
    # 使用 pydeck 创建 3D 热力地图
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_data,
        get_position=['Longitude', 'Latitude'],
        get_color='color',
        get_radius=100,
        pickable=True,
        auto_highlight=True,
    )
    
    # 计算地图中心
    center_lat = map_data['Latitude'].mean()
    center_lon = map_data['Longitude'].mean()
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=45,
    )
    
    # 渲染地图
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "RSRP: {RSRP_dBm} dBm"}
        )
    )
else:
    st.warning("⚠️ 数据中缺少经纬度信息 (Latitude/Longitude)")

# ==========================================
# 基础关卡：数据概览图表
# ==========================================
st.subheader("📊 数据统计分析")

col1, col2 = st.columns(2)

# 频段统计
with col1:
    st.write("**各频段基站数量**")
    if 'Band' in df_filtered.columns:
        band_counts = df_filtered['Band'].value_counts()
        st.bar_chart(band_counts)
    else:
        st.info("数据中无频段 (Band) 信息")

# 终端类型统计
with col2:
    st.write("**不同终端类型占比**")
    if 'Device_Type' in df_filtered.columns or 'Terminal_Type' in df_filtered.columns:
        terminal_col = 'Device_Type' if 'Device_Type' in df_filtered.columns else 'Terminal_Type'
        terminal_counts = df_filtered[terminal_col].value_counts()
        st.bar_chart(terminal_counts)
    else:
        # 如果没有终端类型，显示 RSRP 信号强度分布
        st.write("**信号强度分布**")
        rsrp_bins = pd.cut(df_filtered['RSRP_dBm'], bins=5)
        rsrp_dist = rsrp_bins.value_counts().sort_index()
        st.bar_chart(rsrp_dist)

# ==========================================
# 数据表预览
# ==========================================
st.subheader("📋 数据表预览")
st.dataframe(
    df_filtered[['Latitude', 'Longitude', 'RSRP_dBm', 'Band'] 
                + [col for col in df_filtered.columns if col not in ['Latitude', 'Longitude', 'RSRP_dBm', 'Band', 'color']][:5]],
    use_container_width=True
)

st.markdown("---")
st.markdown("✅ **基础关卡完成！** 现在执行以下命令来提交进度：")
st.code("""
git add .
git commit -m "Complete basic level: data loading, signal heatmap, and statistics"
git tag basic-done
git push origin basic-done
""", language="bash")
