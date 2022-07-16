import streamlit as st
import  urllib
import  json

API_KEY = st.secrets["API_KEY"]
url  =  f"http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId={API_KEY}&lang=J&statsDataId=0003348423&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
with  urllib.request.urlopen(url)  as  response:
    data  =  response.read()
d  =  json.loads(data.decode())

st.write(d)