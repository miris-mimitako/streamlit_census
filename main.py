import streamlit as st
import urllib
import json
from pathlib import Path
import os
import pandas as pd
import plotly.express as px
import datetime

BASE_DIR = Path(__file__).resolve().parent


with open(os.path.join(BASE_DIR, "secret.json")) as json_file:
    secret_json = json.load(json_file)
API_KEY = secret_json["API_KEY"]

url = f"http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId={API_KEY}&lang=J&statsDataId=0003348423&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
with urllib.request.urlopen(url) as response:
    data = response.read()
dic_data = json.loads(data.decode())

# st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)

# st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)

# tab, 140 = DI

df_cat01 = pd.DataFrame(
    dic_data["GET_STATS_DATA"]["STATISTICAL_DATA"]["CLASS_INF"]["CLASS_OBJ"][1]["CLASS"]
)
df_cat02 = pd.DataFrame(
    dic_data["GET_STATS_DATA"]["STATISTICAL_DATA"]["CLASS_INF"]["CLASS_OBJ"][2]["CLASS"]
)
df_value = pd.DataFrame(
    dic_data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
)

# st.markdown(
#     """
#   ## Cat01: 分野

#   Cat01は分野の情報です。
#   """
# )
# st.write(df_cat01)

# st.markdown(
#     """
#   ## Cat02: 景気の方向性及び水準

#   Cat02は現状、未来の景気動向について示されています。
#   """
# )

# st.write(df_cat02)

# st.write(df_value)


df_merge = (
    pd.merge(df_value, df_cat01, left_on="@cat01", right_on="@code", how="outer")
    .rename(columns={"@name": "分野", "@level": "category_level"})
    .drop(columns=["@tab", "@cat01", "@code", "@parentCode"])
)
df_merge = (
    pd.merge(df_merge, df_cat02, left_on="@cat02", right_on="@code", how="outer")
    .rename(columns={"@name": "方向及び水準"})
    .drop(columns=["@cat02", "@code"])
)

df_merge["date"] = df_merge["@time"].str[:4] + "-" + df_merge["@time"].str[-2:]
df_merge["date"] = pd.to_datetime(df_merge.date)
# df_merge["date"] = df_merge["@time"][:4] + "-" + df_merge["@time"][-2:]

df_merge["DI"] = df_merge["$"].astype("float32")
df_merge["DI_standard"] = df_merge["$"].astype("float32") - 50
df_merge["category_level"] = df_merge["category_level"].astype("int16")
df_merge.sort_values("date", inplace=True)
# st.write(df_merge)


col1, col2 = st.columns(2)

st.markdown(
    """
  ## 景気の現状判断

  DI回答時の景気状況を示す。

  """
)


# Lv1

st.markdown(
    """
  ---

  ### DI結果の現状全体像

  DIは0 ~ 100%の値を示し、50%より小さければ景気は下向き、50%より大きければ景気は上向きとされる。

  全体の結果は、日本国内全体の景気動向を示す。
  """
)


df_merge_lv1 = df_merge[df_merge.category_level == 1][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

min_household_trends_year_lv1, max_household_trends_year_lv1 = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv1.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv1.date).year.min(),
        pd.DatetimeIndex(df_merge_lv1.date).year.max(),
    ),
)

min_household_trends = datetime.date(min_household_trends_year_lv1, 1, 1)
max_household_trends = datetime.date(max_household_trends_year_lv1, 12, 31)


fig_household_trends_lv1 = px.line(df_merge_lv1, x="date", y="DI", color="分野")
fig_household_trends_lv1.update_xaxes(
    title="年月", range=[min_household_trends, max_household_trends]
)
fig_household_trends_lv1.update_yaxes(
    title="DI / %",
)
fig_household_trends_lv1.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_lv1.update_layout(width=None, height=None, autosize=True)
fig_household_trends_lv1.update_layout(
    title={
        "text": "現状判断 - 全体",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)


st.plotly_chart(fig_household_trends_lv1, use_container_width=True)


st.markdown(
    """
  ---

  ### 分野別
  """
)

df_merge_lv2 = df_merge[df_merge.category_level == 2][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

min_household_trends_year_lv2, max_household_trends_year_lv2 = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv2.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv2.date).year.min(),
        pd.DatetimeIndex(df_merge_lv2.date).year.max(),
    ),
)

min_household_trends = datetime.date(min_household_trends_year_lv2, 1, 1)
max_household_trends = datetime.date(max_household_trends_year_lv2, 12, 31)


fig_household_trends_lv2 = px.line(df_merge_lv2, x="date", y="DI", color="分野")
fig_household_trends_lv2.update_xaxes(
    title="年月", range=[min_household_trends, max_household_trends]
)
fig_household_trends_lv2.update_yaxes(
    title="DI / %",
)
fig_household_trends_lv2.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_lv2.update_layout(width=None, height=None, autosize=True)
fig_household_trends_lv2.update_layout(
    title={
        "text": "現状判断 - 分野別",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends_lv2, use_container_width=True)


st.markdown(
    """
  ---

  50% 基準での各数値の相対値

  負の値であれば景気は下向きとなる。
  """
)

df_merge_lv2_standard = df_merge[df_merge.category_level == 2][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

fig_household_trends_lv2_standard = px.line(
    df_merge_lv2_standard, x="date", y="DI_standard", color="分野"
)
fig_household_trends_lv2_standard.update_xaxes(
    title="年月",
    range=[
        min_household_trends,
        max_household_trends,
    ],
)

fig_household_trends_lv2_standard.update_yaxes(
    title="DI / % - 50 standards",
)

fig_household_trends_lv2_standard.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)

fig_household_trends_lv2_standard.update_layout(width=None, height=None, autosize=True)

fig_household_trends_lv2_standard.update_layout(
    title={
        "text": "現状判断 - 分野別 - 50%水準",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)


st.plotly_chart(fig_household_trends_lv2_standard, use_container_width=True)

##
st.markdown(
    """
  ---

  ### 詳細分野別
  """
)


df_merge_lv3 = df_merge[df_merge.category_level == 3][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

min_household_trends_year_lv3, max_household_trends_year_lv3 = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv3.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv3.date).year.min(),
        pd.DatetimeIndex(df_merge_lv3.date).year.max(),
    ),
)

min_household_trends = datetime.date(min_household_trends_year_lv3, 1, 1)
max_household_trends = datetime.date(max_household_trends_year_lv3, 12, 31)


fig_household_trends = px.line(df_merge_lv3, x="date", y="DI", color="分野")
fig_household_trends.update_xaxes(
    title="年月", range=[min_household_trends, max_household_trends]
)
fig_household_trends.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends.update_layout(width=None, height=None, autosize=True)

fig_household_trends.update_layout(
    title={
        "text": "現状判断 - 詳細分野別",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends, use_container_width=True)

##

st.markdown(
    """
  ---

  50% 基準での各数値の相対値

  負の値であれば景気は下向きとなる。
  """
)

df_merge_lv3 = df_merge[df_merge.category_level == 3][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

fig_household_trends = px.line(df_merge_lv3, x="date", y="DI_standard", color="分野")
fig_household_trends.update_xaxes(
    title="年月", range=[min_household_trends, max_household_trends]
)
fig_household_trends.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends.update_layout(width=None, height=None, autosize=True)
fig_household_trends.update_layout(
    title={
        "text": "現状判断 - 詳細分野別 - 50%水準",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)
st.plotly_chart(fig_household_trends, use_container_width=True)


st.markdown(
    """
  ---

  ### 将来方向性のDI結果

  DIは0 ~ 100%の値を示し、50%より小さければ景気は下向き、50%より大きければ景気は上向きとされる。

  将来方向性の結果は、日本国内全体の景気動向を示す。
  """
)


df_merge_lv1_future = df_merge[df_merge.category_level == 1][
    df_merge["方向及び水準"] == "景気の先行き判断（方向性）"
]


(
    min_household_trends_year_lv1_future,
    max_household_trends_year_lv1_future,
) = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv1_future.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv1_future.date).year.min(),
        pd.DatetimeIndex(df_merge_lv1_future.date).year.max(),
    ),
    key="Lv1_future",
)

min_household_trends_lv1_future = datetime.date(
    min_household_trends_year_lv1_future, 1, 1
)
max_household_trends_lv1_future = datetime.date(
    max_household_trends_year_lv1_future, 12, 31
)


fig_household_trends_lv1_future = px.line(
    df_merge_lv1_future, x="date", y="DI", color="分野"
)
fig_household_trends_lv1_future.update_xaxes(
    title="年月", range=[min_household_trends_lv1_future, max_household_trends_lv1_future]
)
fig_household_trends_lv1_future.update_yaxes(
    title="DI / %",
)
fig_household_trends_lv1_future.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_lv1_future.update_layout(width=None, height=None, autosize=True)
fig_household_trends_lv1_future.update_layout(
    title={
        "text": "将来方向性 - 全体",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends_lv1_future, use_container_width=True)


st.markdown(
    """
  ---

  ### 分野別将来の方向性
  """
)

df_merge_lv2_future = df_merge[df_merge.category_level == 2][
    df_merge["方向及び水準"] == "景気の先行き判断（方向性）"
]

(
    min_household_trends_year_lv2_future,
    max_household_trends_year_lv2_future,
) = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv2_future.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv2_future.date).year.min(),
        pd.DatetimeIndex(df_merge_lv2_future.date).year.max(),
    ),
    key="Lv2_future",
)

min_household_trends_lv2_future = datetime.date(
    min_household_trends_year_lv2_future, 1, 1
)
max_household_trends_lv2_future = datetime.date(
    max_household_trends_year_lv2_future, 12, 31
)


fig_household_trends_lv2_future = px.line(df_merge_lv2, x="date", y="DI", color="分野")
fig_household_trends_lv2_future.update_xaxes(
    title="年月", range=[min_household_trends_lv2_future, max_household_trends_lv2_future]
)
fig_household_trends_lv2_future.update_yaxes(
    title="DI / %",
)
fig_household_trends_lv2_future.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_lv2_future.update_layout(width=None, height=None, autosize=True)
fig_household_trends_lv2_future.update_layout(
    title={
        "text": "将来方向性 - 分野別",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends_lv2_future, use_container_width=True)


st.markdown(
    """
  ---

  50% 基準での各数値の相対値

  負の値であれば景気は下向きとなる。
  """
)

df_merge_lv2_standard_future = df_merge[df_merge.category_level == 2][
    df_merge["方向及び水準"] == "景気の先行き判断（方向性）"
]

fig_household_trends_lv2_standard_future = px.line(
    df_merge_lv2_standard_future, x="date", y="DI_standard", color="分野"
)
fig_household_trends_lv2_standard_future.update_xaxes(
    title="年月", range=[min_household_trends_lv2_future, max_household_trends_lv2_future]
)

fig_household_trends_lv2_standard_future.update_yaxes(
    title="DI / % - 50 standards",
)

fig_household_trends_lv2_standard_future.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)

fig_household_trends_lv2_standard_future.update_layout(
    width=None, height=None, autosize=True
)

fig_household_trends_lv2_standard_future.update_layout(
    title={
        "text": "将来方向性 - 分野別 - 50%水準",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends_lv2_standard_future, use_container_width=True)


##
st.markdown(
    """
  ---

  ### 詳細分野別
  """
)

df_merge_lv3_future = df_merge[df_merge.category_level == 3][
    df_merge["方向及び水準"] == "景気の先行き判断（方向性）"
]

(
    min_household_trends_year_lv3_future,
    max_household_trends_year_lv3_future,
) = st.select_slider(
    "グラフの表示期間を選択してください。(単位：年)",
    options=pd.DatetimeIndex(df_merge_lv3_future.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv3_future.date).year.min(),
        pd.DatetimeIndex(df_merge_lv3_future.date).year.max(),
    ),
    key="Lv3_future",
)

min_household_trends_lv3_future = datetime.date(
    min_household_trends_year_lv3_future, 1, 1
)
max_household_trends_lv3_future = datetime.date(
    max_household_trends_year_lv3_future, 12, 31
)


fig_household_trends_lv3_future = px.line(df_merge_lv3, x="date", y="DI", color="分野")
fig_household_trends_lv3_future.update_xaxes(
    title="年月", range=[min_household_trends_lv3_future, max_household_trends_lv3_future]
)
fig_household_trends_lv3_future.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_lv3_future.update_layout(width=None, height=None, autosize=True)

fig_household_trends_lv3_future.update_layout(
    title={
        "text": "将来方向性 - 詳細分野別",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

st.plotly_chart(fig_household_trends_lv3_future, use_container_width=True)

##

st.markdown(
    """
  ---

  50% 基準での各数値の相対値

  負の値であれば景気は下向きとなる。
  """
)

df_merge_lv3_standard = df_merge[df_merge.category_level == 3][
    df_merge["方向及び水準"] == "景気の先行き判断（方向性）"
]

fig_household_trends_standard_lv3_future = px.line(
    df_merge_lv3_standard, x="date", y="DI_standard", color="分野"
)
fig_household_trends_standard_lv3_future.update_xaxes(
    title="年月", range=[min_household_trends_lv3_future, max_household_trends_lv3_future]
)
fig_household_trends_standard_lv3_future.update_layout(
    legend=dict(x=0.0, y=-0.2, xanchor="left", yanchor="top")
)
fig_household_trends_standard_lv3_future.update_layout(
    width=None, height=None, autosize=True
)
fig_household_trends_standard_lv3_future.update_layout(
    title={
        "text": "将来方向性 - 詳細分野別 - 50%水準",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)
st.plotly_chart(fig_household_trends_standard_lv3_future, use_container_width=True)
