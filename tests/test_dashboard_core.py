"""dashboard_core 模块单元测试。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import dashboard_core as dc

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "signal_samples.csv"


def test_load_signal_data_smoke():
    df = dc.load_signal_data(CSV_PATH)
    assert len(df) > 0
    expected_cols = {
        "Latitude",
        "Longitude",
        "CellID",
        "Band",
        "RSRP_dBm",
        "SINR_dB",
        "TerminalType",
        "Download_Mbps",
    }
    assert expected_cols.issubset(df.columns)


@pytest.mark.parametrize(
    "rsrp,expected_rgb",
    [
        (-85.0, (0, 255, 0)),
        (-120.0, (255, 0, 0)),
    ],
)
def test_get_color_extremes(rsrp: float, expected_rgb: tuple[int, int, int]):
    c = dc.get_color(rsrp)
    assert tuple(c[:3]) == expected_rgb
    assert c[3] == 200


def test_get_color_mid_gradient_monotonic():
    """中间段应随 RSRP 升高绿色分量增大、红色分量减小。"""
    low = dc.get_color(-109.0)
    high = dc.get_color(-91.0)
    assert high[1] > low[1]  # more green
    assert high[0] < low[0]  # less red


def test_classify_signal_buckets():
    assert dc.classify_signal(-80) == "优秀"
    assert dc.classify_signal(-95) == "良好"
    assert dc.classify_signal(-105) == "一般"
    assert dc.classify_signal(-115) == "较弱"


def test_filter_signals_returns_copy_and_subset():
    df = dc.load_signal_data(CSV_PATH)
    one_band = [sorted(df["Band"].unique().tolist())[0]]
    rsrp_lo = float(df["RSRP_dBm"].min())
    rsrp_hi = float(df["RSRP_dBm"].max())
    terms = df["TerminalType"].unique().tolist()
    out = dc.filter_signals(df, one_band, (rsrp_lo, rsrp_hi), terms)
    assert set(out["Band"].unique()).issubset(set(one_band))
    assert len(out) <= len(df)
    assert len(out) < len(df) or df["Band"].nunique() == 1


def test_column_elevation_m_positive():
    assert dc.column_elevation_m(100.0, scale=2.0) == 200.0
