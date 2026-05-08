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

# 数据清洗：删除包含 NaN 的行
df_clean = df.dropna()

# ==========================================
# 基础关卡：侧边栏筛选器（进阶功能）
# ==========================================
st.sidebar.header("🔧 筛选器")

# 频段筛选
if 'Band' in df_clean.columns:
    bands = sorted(df_clean['Band'].unique())
    selected_bands = st.sidebar.multiselect(
        "选择频段 (Band)",
        options=bands,
        default=bands
    )
    df_filtered = df_clean[df_clean['Band'].isin(selected_bands)]
else:
    df_filtered = df_clean

# RSRP 范围筛选
if 'RSRP_dBm' in df_filtered.columns:
    rsrp_min = float(df_filtered['RSRP_dBm'].min())
    rsrp_max = float(df_filtered['RSRP_dBm'].max())
    selected_rsrp_range = st.sidebar.slider(
        "选择 RSRP 范围 (dBm)",
        min_value=rsrp_min,
        max_value=rsrp_max,
        value=(rsrp_min, rsrp_max),
        step=1.0
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
        return [0, 255, 0, 180]  # 绿色 (强信号)
    elif rsrp < -110:
        return [255, 0, 0, 180]  # 红色 (弱信号)
    else:
        # 黄色到红色的渐变
        ratio = (rsrp + 110) / 20  # 0 到 1 的比例
        return [
            int(255 * (1 - ratio)),  # R
            int(255 * ratio),        # G
            0,                       # B
            180                      # 透明度
        ]

# 为数据添加颜色列
df_filtered_copy = df_filtered.copy()
df_filtered_copy['color'] = df_filtered_copy['RSRP_dBm'].apply(get_color)

# 准备地图数据
if 'Latitude' in df_filtered_copy.columns and 'Longitude' in df_filtered_copy.columns:
    # 检查数据有效性
    valid_data = df_filtered_copy[
        (df_filtered_copy['Latitude'].notna()) &
        (df_filtered_copy['Longitude'].notna()) &
        (df_filtered_copy['RSRP_dBm'].notna())
    ].copy()
    
    if len(valid_data) > 0:
        # 使用 pydeck 创建散点地图
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=valid_data,
            get_position=['Longitude', 'Latitude'],
            get_color='color',
            get_radius=80,
            pickable=True,
            auto_highlight=True,
        )
        
        # 计算地图中心
        center_lat = valid_data['Latitude'].mean()
        center_lon = valid_data['Longitude'].mean()
        
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=30,
        )
        
        # 渲染地图
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "text": "RSRP: {RSRP_dBm} dBm\nBand: {Band}\nLatitude: {Latitude}\nLongitude: {Longitude}"
                }
            )
        )
    else:
        st.warning("⚠️ 没有有效的地理位置数据")
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
        band_counts = df_filtered['Band'].value_counts().sort_values(ascending=False)
        st.bar_chart(band_counts)
    else:
        st.info("数据中无频段 (Band) 信息")

# 终端类型统计
with col2:
    st.write("**不同终端类型占比**")
    if 'TerminalType' in df_filtered.columns:
        terminal_counts = df_filtered['TerminalType'].value_counts()
        st.bar_chart(terminal_counts)
    else:
        st.info("数据中无终端类型信息")

# RSRP 信号强度分布
st.write("**信号强度分布**")
rsrp_bins = pd.cut(df_filtered['RSRP_dBm'], bins=8)
rsrp_dist = rsrp_bins.value_counts().sort_index()
st.bar_chart(rsrp_dist)

# ==========================================
# 数据表预览
# ==========================================
st.subheader("📋 数据表预览")
display_cols = ['Latitude', 'Longitude', 'RSRP_dBm', 'Band', 'TerminalType', 'Download_Mbps']
st.dataframe(
    df_filtered[display_cols],
    use_container_width=True,
    height=300
)

st.markdown("---")
st.markdown("✅ **基础关卡完成！** 现在执行以下命令来提交进度：")
st.code("""
git add .
git commit -m "Complete basic level: data loading, signal heatmap, and statistics charts"
git tag basic-done
git push origin basic-done
""", language="bash")

# 底部统计信息
st.markdown("---")
st.markdown("### 📈 数据统计摘要")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总记录数", len(df_filtered))
with col2:
    st.metric("平均 RSRP", f"{df_filtered['RSRP_dBm'].mean():.2f} dBm")
with col3:
    st.metric("最强信号", f"{df_filtered['RSRP_dBm'].max():.2f} dBm")
with col4:
    st.metric("最弱信号", f"{df_filtered['RSRP_dBm'].min():.2f} dBm")
