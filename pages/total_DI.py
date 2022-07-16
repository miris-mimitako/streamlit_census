import streamlit as st
import urllib
import json
from pathlib import Path
import os
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent


if "Users" in __file__:
    with open(os.path.join(BASE_DIR, "secret.json")) as json_file:
        secret_json = json.load(json_file)
    API_KEY = secret_json["API_KEY"]

else:
    API_KEY = st.secrets["API_KEY"]


url = f"http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId={API_KEY}&lang=J&statsDataId=0003348423&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
with urllib.request.urlopen(url) as response:
    data = response.read()
dic_data = json.loads(data.decode())

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
    .rename(columns={"@name": "分野"})
    .drop(columns=["@tab", "@cat01", "@code", "@parentCode"])
)
df_merge = (
    pd.merge(df_merge, df_cat02, left_on="@cat02", right_on="@code", how="outer")
    .rename(columns={"@name": "方向及び水準"})
    .drop(columns=["@cat02", "@code"])
)

st.write(df_merge)
