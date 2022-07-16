import streamlit as st
import  urllib
import  json
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


if "Users" in __file__:
  with open (os.path.join(BASE_DIR, "secret.json")) as json_file:
    secret_json = json.load(json_file)
  API_KEY = secret_json["API_KEY"]

else:
  API_KEY = st.secrets["API_KEY"]


  
url  =  f"http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId={API_KEY}&lang=J&statsDataId=0003348423&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
with  urllib.request.urlopen(url)  as  response:
    data  =  response.read()
d  =  json.loads(data.decode())

st.write(d)