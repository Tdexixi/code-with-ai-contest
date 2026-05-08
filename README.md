# 5G 信号可视化看板

基于 **Streamlit** 的本地 Web 看板，读取路测 CSV，在地图上展示采样点，并联动统计图表。本仓库来自「Code with AI」海选赛题实践；赛题原文见上游 [besa-2026/code-with-ai-contest](https://github.com/besa-2026/code-with-ai-contest)。

---

## 主要功能

| 模块 | 说明 |
|------|------|
| **数据加载** | 使用 **pandas** 读取 `data/signal_samples.csv`（经纬度、小区、频段、RSRP、SINR、终端类型、下载速率等）。 |
| **交互地图** | **pydeck**：散点 + **3D ColumnLayer**，点颜色按 **RSRP_dBm** 分级（优于 -90 dBm 偏绿，劣于 -110 dBm 偏红；中间过渡）；柱高与 **Download_Mbps** 成正比，可旋转视角查看。 |
| **侧边栏筛选** | 频段多选、RSRP 范围滑块、终端类型多选；筛选后地图与下方图表**同步刷新**；无数据时有提示，避免报错。 |
| **统计图表** | **Plotly**：各频段样本量柱状图、终端类型占比饼图、RSRP 分布与信号等级、频段与速率关系等。 |
| **数据表** | 筛选结果分页表格（中文列名）。 |
| **工程化** | 可复用逻辑集中在 **`dashboard_core.py`**（含注释）；**`pytest tests/`** 覆盖加载、配色、筛选等核心函数。 |

---

## 运行环境

- **Python** 3.10+（推荐 3.11；依赖见 `requirements.txt`，已固定主要包版本）。
- 浏览器访问本地 **http://localhost:8501**（Streamlit 默认端口）。

---

## 安装与运行

```bash
git clone https://github.com/Tdexixi/code-with-ai-contest.git
cd code-with-ai-contest
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**Windows**：若命令行中 `streamlit` 无法识别，请始终使用 **`python -m streamlit run app.py`**，或直接双击项目根目录下的 **`run.bat`**。

---

## 单元测试

```bash
python -m pytest tests/ -q
```

---

## 仓库结构（摘录）

| 路径 | 作用 |
|------|------|
| `app.py` | Streamlit 入口与页面布局 |
| `dashboard_core.py` | 加载、RSRP 配色、筛选、柱高等纯逻辑 |
| `data/signal_samples.csv` | 示例路测数据 |
| `tests/` | 单元测试 |
| `AI_PROMPTS.md` | Agent 交互日志（赛方交付物） |
| `screenshots/` | 运行截图（示例见目录内 PNG） |

---

## 交付与赛方标签（如需参赛登记）

赛题要求提交源码、`README`、截图、`AI_PROMPTS.md` 等；完赛打标签示例：

```bash
git tag basic-done && git push origin basic-done
git tag advanced-done && git push origin advanced-done
```

具体规则以主办方说明为准。
