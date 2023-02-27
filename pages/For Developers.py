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
st.set_page_config(page_title='For Developers', initial_sidebar_state='expanded')
st.title('For Developers')
st.subheader('Information For Other Developers')
st.write('')


st.markdown('<h4>Why Scrape PDF Data</h4>', unsafe_allow_html=True)