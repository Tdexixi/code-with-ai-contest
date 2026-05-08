"""
5G 信号看板核心逻辑：数据加载、RSRP 配色、筛选与信号分级。

与 Streamlit UI 解耦，便于单元测试与复用。
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd


def load_signal_data(csv_path: str | Path) -> pd.DataFrame:
    """从 CSV 加载路测数据并丢弃含空值的行。"""
    path = Path(csv_path)
    return pd.read_csv(path).dropna()


def get_color(rsrp: float) -> List[int]:
    """
    按 RSRP(dBm) 返回 pydeck 用 RGBA。
    规则：> -90 绿色，< -110 红色，中间由红向绿插值。
    """
    if rsrp > -90:
        return [0, 255, 0, 200]
    if rsrp < -110:
        return [255, 0, 0, 200]
    ratio = (rsrp + 110) / 20.0
    return [
        int(255 * (1 - ratio)),
        int(255 * ratio),
        0,
        200,
    ]


def classify_signal(rsrp: float) -> str:
    """将 RSRP 映射为中文等级标签。"""
    if rsrp > -90:
        return "优秀"
    if rsrp > -100:
        return "良好"
    if rsrp > -110:
        return "一般"
    return "较弱"


def filter_signals(
    df: pd.DataFrame,
    selected_bands: Iterable[str],
    rsrp_range: Tuple[float, float],
    selected_terminals: Iterable[str],
) -> pd.DataFrame:
    """按频段、RSRP 区间与终端类型筛选，始终返回副本以避免链式赋值告警。"""
    lo, hi = rsrp_range
    mask = (
        df["Band"].isin(list(selected_bands))
        & (df["RSRP_dBm"] >= lo)
        & (df["RSRP_dBm"] <= hi)
        & df["TerminalType"].isin(list(selected_terminals))
    )
    return df.loc[mask].copy()


def column_elevation_m(download_mbps: float, scale: float = 2.0) -> float:
    """将下载速率(Mbps)转为柱体高度(米)，用于 3D ColumnLayer 可视化。"""
    return float(download_mbps) * scale
