import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

import dashboard_core as dc

# 页面配置
st.set_page_config(
    page_title="5G 信号可视化看板",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-strong {
        color: green;
        font-weight: bold;
    }
    .status-medium {
        color: orange;
        font-weight: bold;
    }
    .status-weak {
        color: red;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-title">📡 5G信号可视化看板</h1>', unsafe_allow_html=True)
st.markdown("### 来自 'Code with AI' 极客探索赛 🚀")

# ==========================================
# 数据加载和处理
# ==========================================
@st.cache_data
def load_data():
    """加载 CSV；路径相对应用工作目录。"""
    return dc.load_signal_data("data/signal_samples.csv")

try:
    df = load_data()
    st.success(f"✅ 成功加载 {len(df)} 条 5G 信号数据")
except FileNotFoundError:
    st.error("❌ 找不到数据文件，请确保 data/signal_samples.csv 存在")
    st.stop()

# ==========================================
# 侧边栏筛选器
# ==========================================
st.sidebar.markdown("## 🔧 筛选器")

# 频段筛选
bands = sorted(df['Band'].unique())
selected_bands = st.sidebar.multiselect(
    "📶 选择频段",
    options=bands,
    default=bands,
    key="band_filter"
)

# RSRP 范围筛选
rsrp_min = float(df['RSRP_dBm'].min())
rsrp_max = float(df['RSRP_dBm'].max())
selected_rsrp_range = st.sidebar.slider(
    "📊 RSRP 信号强度范围 (dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(rsrp_min, rsrp_max),
    step=1.0
)

# 终端类型筛选
terminal_types = df['TerminalType'].unique().tolist()
selected_terminals = st.sidebar.multiselect(
    "📱 选择终端类型",
    options=terminal_types,
    default=terminal_types,
    key="terminal_filter"
)

# 应用筛选器（副本，避免 SettingWithCopy 与下游就地赋值问题）
df_filtered = dc.filter_signals(
    df, selected_bands, selected_rsrp_range, selected_terminals
)

st.sidebar.info(f"📈 当前显示：**{len(df_filtered)}** 条数据（总数：{len(df)}）")

# ==========================================
# 顶部指标卡片
# ==========================================
st.markdown("### 📊 关键指标")
col1, col2, col3, col4, col5 = st.columns(5)

has_rows = len(df_filtered) > 0

with col1:
    st.metric(
        "📍 总数据点",
        len(df_filtered),
        delta=f"{len(df_filtered) - len(df)}" if len(df_filtered) != len(df) else "全部",
    )

with col2:
    if has_rows:
        avg_rsrp = df_filtered["RSRP_dBm"].mean()
        st.metric("📊 平均信号强度", f"{avg_rsrp:.2f} dBm")
    else:
        st.metric("📊 平均信号强度", "—")

with col3:
    if has_rows:
        max_rsrp = df_filtered["RSRP_dBm"].max()
        st.metric("🟢 最强信号", f"{max_rsrp:.2f} dBm")
    else:
        st.metric("🟢 最强信号", "—")

with col4:
    if has_rows:
        min_rsrp = df_filtered["RSRP_dBm"].min()
        st.metric("🔴 最弱信号", f"{min_rsrp:.2f} dBm")
    else:
        st.metric("🔴 最弱信号", "—")

with col5:
    if has_rows:
        avg_speed = df_filtered["Download_Mbps"].mean()
        st.metric("⚡ 平均下载速率", f"{avg_speed:.2f} Mbps")
    else:
        st.metric("⚡ 平均下载速率", "—")

# ==========================================
# 地图和图表布局
# ==========================================
st.markdown("---")
st.markdown("### 🗺️ 信号地图（RSRP 配色 + 3D 柱高 ∝ 下载速率）")

# 准备地图数据：颜色按 RSRP，柱高按 Download_Mbps（米）
map_data = df_filtered.copy()
if len(map_data) > 0:
    map_data["color"] = map_data["RSRP_dBm"].apply(dc.get_color)
    map_data["elevation_m"] = map_data["Download_Mbps"].apply(dc.column_elevation_m)

if len(map_data) > 0:
    # 3D 柱体层：高度表示下载速率
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=map_data,
        get_position=["Longitude", "Latitude"],
        get_elevation="elevation_m",
        get_fill_color="color",
        radius=70,
        elevation_scale=1,
        pickable=True,
        auto_highlight=True,
    )
    # 顶层散点，便于辨认点位中心
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=["Longitude", "Latitude"],
        get_color="color",
        get_radius=35,
        pickable=True,
        auto_highlight=True,
    )

    center_lat = map_data["Latitude"].mean()
    center_lon = map_data["Longitude"].mean()

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=55,
        bearing=-15,
    )

    st.pydeck_chart(
        pdk.Deck(
            # Carto 矢量底图无需 Mapbox Token，便于本地一键运行
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            layers=[column_layer, scatter_layer],
            initial_view_state=view_state,
            tooltip={
                "text": (
                    "📍 ({Latitude:.4f}, {Longitude:.4f})\n"
                    "📶 RSRP: {RSRP_dBm:.2f} dBm\n"
                    "📡 {Band}  |  {TerminalType}\n"
                    "⚡ {Download_Mbps:.1f} Mbps  → 柱高 {elevation_m:.0f} m"
                )
            },
        )
    )
else:
    st.warning("⚠️ 没有符合条件的数据")

# ==========================================
# 统计图表
# ==========================================
st.markdown("---")
st.markdown("### 📈 数据分析")

chart_col1, chart_col2 = st.columns(2)

# 频段统计
with chart_col1:
    st.markdown("#### 各频段基站数量")
    if has_rows:
        band_counts = df_filtered["Band"].value_counts().reset_index()
        band_counts.columns = ["Band", "Count"]
        fig_band = px.bar(
            band_counts,
            x="Band",
            y="Count",
            color="Count",
            color_continuous_scale="Viridis",
            labels={"Count": "基站数量"},
            title="频段分布",
        )
        st.plotly_chart(fig_band, use_container_width=True)
    else:
        st.info("当前筛选下无数据，无法绘制频段统计。")

# 终端类型统计
with chart_col2:
    st.markdown("#### 终端类型分布")
    if has_rows:
        terminal_counts = df_filtered["TerminalType"].value_counts().reset_index()
        terminal_counts.columns = ["TerminalType", "Count"]
        fig_terminal = px.pie(
            terminal_counts,
            names="TerminalType",
            values="Count",
            title="终端类型占比",
        )
        st.plotly_chart(fig_terminal, use_container_width=True)
    else:
        st.info("当前筛选下无数据，无法绘制终端占比。")

# ==========================================
# RSRP分布图
# ==========================================
st.markdown("#### RSRP信号强度分布")
if has_rows:
    rsrp_hist = go.Histogram(
        x=df_filtered["RSRP_dBm"],
        nbinsx=30,
        name="RSRP",
        marker=dict(color="#1f77b4"),
    )

    fig_rsrp = go.Figure(data=[rsrp_hist])
    fig_rsrp.add_vline(
        x=-90,
        line_dash="dash",
        line_color="green",
        annotation_text="强信号 (-90dBm)",
        annotation_position="top left",
    )
    fig_rsrp.add_vline(
        x=-110,
        line_dash="dash",
        line_color="red",
        annotation_text="弱信号 (-110dBm)",
        annotation_position="top right",
    )
    fig_rsrp.update_layout(
        title="RSRP信号强度分布直方图",
        xaxis_title="RSRP (dBm)",
        yaxis_title="频数",
        hovermode="x unified",
    )
    st.plotly_chart(fig_rsrp, use_container_width=True)
else:
    st.info("当前筛选下无数据，无法绘制 RSRP 分布。")

# ==========================================
# 信号强度等级分析
# ==========================================
st.markdown("#### 信号强度等级统计")

if has_rows:
    df_filtered["Signal_Level"] = df_filtered["RSRP_dBm"].apply(dc.classify_signal)
    signal_dist = df_filtered["Signal_Level"].value_counts().reindex(
        ["优秀", "良好", "一般", "较弱"], fill_value=0
    )

    colors_map = {
        "优秀": "#00FF00",
        "良好": "#FFFF00",
        "一般": "#FFA500",
        "较弱": "#FF0000",
    }
    fig_level = go.Figure(
        data=[
            go.Bar(
                x=signal_dist.index,
                y=signal_dist.values,
                marker=dict(
                    color=[colors_map.get(level, "gray") for level in signal_dist.index]
                ),
            )
        ]
    )
    fig_level.update_layout(
        title="信号质量等级分布",
        xaxis_title="信号等级",
        yaxis_title="数据点数量",
        hovermode="x",
    )
    st.plotly_chart(fig_level, use_container_width=True)
else:
    st.info("当前筛选下无数据，无法绘制等级统计。")

# ==========================================
# 下载速率分析
# ==========================================
st.markdown("#### 频段与下载速率关系")
if has_rows:
    band_speed = (
        df_filtered.groupby("Band")["Download_Mbps"].agg(["mean", "max", "min"]).reset_index()
    )
    fig_speed = px.bar(
        band_speed,
        x="Band",
        y="mean",
        error_y="max",
        color="mean",
        color_continuous_scale="RdYlGn",
        title="各频段平均下载速率",
        labels={"mean": "平均速率 (Mbps)"},
    )
    st.plotly_chart(fig_speed, use_container_width=True)
else:
    st.info("当前筛选下无数据，无法绘制速率对比。")

# ==========================================
# 数据表预览
# ==========================================
st.markdown("---")
st.markdown("### 📋 详细数据表")

# 选择显示的列
display_cols = ['Latitude', 'Longitude', 'CellID', 'Band', 'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps']
df_display = df_filtered[display_cols].copy()
df_display.columns = ['纬度', '经度', '基站ID', '频段', 'RSRP(dBm)', 'SINR(dB)', '终端类型', '下载速率(Mbps)']

page_size = 20
total_pages = max(1, (len(df_display) + page_size - 1) // page_size)
if len(df_display) > 0:
    page = st.selectbox("选择页码", range(1, total_pages + 1), index=0)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(
        df_display.iloc[start_idx:end_idx],
        use_container_width=True,
        height=400,
    )
    st.info(f"📄 共 {len(df_display)} 条数据，第 {page} 页，每页 {page_size} 条")
else:
    st.info("当前筛选下无数据可展示。")

# ==========================================
# 页脚
# ==========================================
st.markdown("---")
st.markdown("""
### 📌 基础关卡完成检查清单

✅ **已实现的功能：**
- ✓ 数据加载（pandas 读取 CSV，`dashboard_core` 可测逻辑）
- ✓ 交互地图（pydeck：RSRP 配色 + **3D ColumnLayer 柱高 ∝ 下载速率**）
- ✓ 数据概览图表（频段柱状图、终端饼图等）
- ✓ 侧边栏联动筛选（频段、RSRP 范围、终端类型），地图与图表联动刷新
- ✓ 单元测试：`pytest tests/`
- ✓ 详细数据表分页展示

### 🎯 提交步骤

```bash
# 1. 添加所有文件
git add .

# 2. 提交代码
git commit -m "Complete basic level: full 5G signal visualization dashboard"

# 3. 打上基础关卡标签
git tag basic-done

# 4. 推送到远程仓库
git push origin main
git push origin basic-done
```
""")

# 显示数据统计摘要
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 数据摘要")
if has_rows:
    sidebar_stats = f"""
- **总记录数：** {len(df)}
- **筛选后：** {len(df_filtered)}
- **RSRP范围：** {df_filtered["RSRP_dBm"].min():.2f} ~ {df_filtered["RSRP_dBm"].max():.2f} dBm
- **平均RSRP：** {df_filtered["RSRP_dBm"].mean():.2f} dBm
- **平均速率：** {df_filtered["Download_Mbps"].mean():.2f} Mbps
- **频段数：** {len(df_filtered["Band"].unique())}
- **终端类型：** {", ".join(df_filtered["TerminalType"].unique())}
"""
else:
    sidebar_stats = f"""
- **总记录数：** {len(df)}
- **筛选后：** 0（请放宽筛选条件）
"""
st.sidebar.markdown(sidebar_stats)
