import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import os
import camelot
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
import glob
import plotly.offline as pyo
import plotly.graph_objs as go
import streamlit.components.v1 as components
import re



## HEADER
st.set_page_config(page_title='Data Table', initial_sidebar_state='expanded')
st.set_option("theme", "light")
st.title('Data Table')
st.subheader('All Data Used In Dashboard')
st.write('')

df = pd.read_excel('parsed.xlsx')
st.markdown('<i>For a better viewing experience, view in wide mode</i>', unsafe_allow_html=True)
st.write('')

st.dataframe(df, use_container_width=True, height=900, width=1000)

st.sidebar.markdown('<h2>Download Data</h2>', unsafe_allow_html=True)
with open('parsed.xlsx', 'rb') as f:
            bytes_data = f.read()

st.sidebar.download_button('Download Excel', data=bytes_data, file_name='parsedStatements.xlsx', mime='xlsx')
st.sidebar.download_button('Download CSV', data=bytes_data, file_name='parsedStatements.csv', mime='csv')

st.sidebar.write('')


st.markdown(
'''
<style>

h2 {
    margin-left: 5px;
}

</style>
''', unsafe_allow_html=True)