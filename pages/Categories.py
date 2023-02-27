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
st.set_page_config(page_title='Categories', initial_sidebar_state='expanded')
st.title('Categories')
st.subheader('Edit Dashboard Categories')
st.write('')

with st.form('form'):
    st.image('images/food.jpg', use_column_width='always')
    st.markdown('<h5>Select Food Outlets</h5>', unsafe_allow_html=True)
    foodOptions = ['McDonalds', 'Burger King', 'Starbucks', 'Subway']
    selectedFood = st.multiselect(label='selectedFood', options=foodOptions, label_visibility='hidden')
    st.text_area('Others...', placeholder='Din Tai Fung, Subway, Wine Connection...')



    ## ONLINE SHOPPING
    st.write('')
    st.image('images/onlineshopping.jpg', use_column_width='always')
    st.markdown('<h5>Select E-Shopping Platforms</h5>', unsafe_allow_html=True)
    shopOptions = ['Shopee', 'Lazada', 'Tao Bao', 'Ebay', 'Amazon', 'Wish']
    selectedShops = st.multiselect(label='selectedShops', options=shopOptions, label_visibility='hidden')

    # shopee = st.checkbox('Shopee')
    # lazada = st.checkbox('Lazada')
    # taobao = st.checkbox('Tao Bao')
    # ebay = st.checkbox('Ebay')
    # amazon = st.checkbox('Amazon')
    # wish = st.checkbox("Wish")
    otherShops = st.text_area(label='Others...', placeholder='Drop, Banggood...')



    ## SUPERMARKETS
    st.write('')
    st.image('images/grocer.jpg', use_column_width='always')
    st.markdown('<h5>Select Grocers</h5>', unsafe_allow_html=True)
    grocerOptions = ['Fairprice/NTUC', 'Cold Storage', 'Marketplace', 'Giant', 'Jasons', "Ryan's"]
    selectedGrocers = st.multiselect(label='selectedGrocers', options=grocerOptions, label_visibility='hidden')

    # ntuc = st.checkbox('Fairprice/NTUC')
    # cs = st.checkbox('Cold Storage')
    # market = st.checkbox('Marketplace')
    # giant = st.checkbox('Giant')
    # jasons = st.checkbox('Jasons')
    # ryans  = st.checkbox("Ryan's Grocery")
    otherGrocers = st.text_area(label='Others...', placeholder="Little Farms, Hao's Supermarket...")



    ## TRANSPORT
    st.write('')
    st.image('images/transport.jpg', use_column_width='always')
    transportLabel = st.markdown('<h5>Select Transport Apps</h5>', unsafe_allow_html=True)
    transportOptions = ['Grab', 'Gojek', 'Comfort Delgro', 'Ta-Da']
    selectedTransport = st.multiselect(label='selectedTransport', options=transportOptions, label_visibility='hidden')

    # grab = st.checkbox('Grab')
    # gojek = st.checkbox('Gojek')
    # cdg = st.checkbox('Comfort Delgro')
    # tada = st.checkbox('Ta-Da')
    otherTransport = st.text_area(label='Others...', placeholder='Ryde, BlueSG...')

    st.markdown('<br><br>', unsafe_allow_html=True)
    st.form_submit_button('Update')


st.markdown("""
<style>

h5 {
    margin-top: 50px;
}

img {
    width: 620px;
    height: 350px;
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 50px;
    margin-bottom: -50px;
}

</style>
""", unsafe_allow_html=True)