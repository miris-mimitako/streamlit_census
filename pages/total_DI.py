import streamlit as st
import urllib
import json
from pathlib import Path
import os
import pandas as pd
import plotly.express as px
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent


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

st.markdown(
    """
  ## Cat01: 分野
  
  Cat01は分野の情報です。
  """
)
st.write(df_cat01)

st.markdown(
    """
  ## Cat02: 景気の方向性及び水準
  
  Cat02は現状、未来の景気動向について示されています。
  """
)

st.write(df_cat02)

st.write(df_value)


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
st.write(df_merge)


col1, col2 = st.columns(2)

#
df_merge_lv3 = df_merge[df_merge.category_level == 3][
    df_merge["方向及び水準"] == "景気の現状判断（水準）"
]

min_household_trends_year, max_household_trends_year = st.select_slider(
    "期間を選択してください。",
    options=pd.DatetimeIndex(df_merge_lv3.date).year,
    value=(
        pd.DatetimeIndex(df_merge_lv3.date).year.min(),
        pd.DatetimeIndex(df_merge_lv3.date).year.max(),
    ),
)

min_household_trends = datetime.date(min_household_trends_year, 1, 1)
max_household_trends = datetime.date(max_household_trends_year, 12, 31)


fig_household_trends = px.line(df_merge_lv3, x="date", y="DI", color="分野")
fig_household_trends.update_xaxes(
    title="年月", range=[min_household_trends, max_household_trends]
)
st.plotly_chart(fig_household_trends, use_container_width=True)
