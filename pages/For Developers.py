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
st.markdown('''<p>
This page consists of a more in-depth overview of how the program operates and its processes. If you intend to adapt this project, please read this page.
</p>''', unsafe_allow_html=True)
st.write('')

st.sidebar.markdown('<h1>Want To Contribute?</h1>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="contribute">If you have any ideas to improve this website, feel free to drop me an email at <a href="ryanueda34@gmail.com">ryanueda34@gmail.com</a> along with your proposed implementation.</p>', unsafe_allow_html=True)


st.markdown('<h4>Why Scrape PDF Data</h4>', unsafe_allow_html=True)
st.markdown('''<p>
Most banks such as UOB and Citibank allow for transaction history to be downloaded as a whole, single CSV file. However, for DBS and POSB, CSV files can only be downloaded for each page of
transaction history shown. As a result, this process becomes very troublesome. Hence, by downloading it in PDF format, we are able to capture all transaction history within the specified time
range without the hassle.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>How Is This Done</h4>', unsafe_allow_html=True)
st.markdown('''<p>
Banks display transaction history in the form of tables, usually with columns such as Date, Reference, Debit, Credit, and sometimes Transaction Code. To extract this tabled data from the PDF
bank statements, we use Optical Character Recognition libraries such as PyPDF2 and camelot. This helps us extract the transaction history for further analysis and visualization.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>The Issue With This Approach</h4>', unsafe_allow_html=True)
st.markdown('''<p>
Even with the specification of table areas and regions, not all data can be captured properly. Certain PDFs return dataframes consisting of 6 columns after being read, while some return 7.
Additionally, the data returned is not formatted properly, and is quite messy. Because of this, alot of data wrangling and pre-processing is required to asjust the data to a usable state. <br>

Furthermore, in certain statements, data such as balance does not exist, or cannot be extracted effectively. This means that for these statements, users have to manually input their final bank balance,
to allow for the program to work backwards and calculate the balance for each transaction. Not only is this slightly troublesome, it can be slightly computationally expensive if transactions are abundant.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>Data Wrangling & Pre-processing</h4>', unsafe_allow_html=True)
st.markdown('''<p>
After reading the data off the PDF files, a series of transformations and permutations have to be performed on the dataframes. Due to the improper formatting, we have to get rid of useless columns and re-arrange
which data belongs to which columns. We then have to concatenate rows that belong to the same date, as some transactions are recorded across multiple rows in the dataframe. The more data there is, the more
expensive the computational cost.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>Data Analysis & Visualization</h4>', unsafe_allow_html=True)
st.markdown('''<p>
In order to make useful analysis and visualizations of the transaction data, more preprocessing has to be done to the data in order to allow for it to be visualized. This includes processes such as datatype
conversion, string formatting, summing, and other statistical methods such as Simple Moving Average (SMA) for time series data.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>How To Keep The Processes Low On Computational Cost</h4>', unsafe_allow_html=True)
st.markdown('''<p>
Streamlit comes with a built in caching function, which allows us to cache certain functions in the browser once they have been run at least once. To make full use of this function, we have to segregate specific
operations into their own functions. This ensures that all the data extraction and data processing is not re-run everytime a design change is made by the user to the display of the visualizations generated. <br>

The use of these caching functions creates a stark difference in processing times after loading data for the first time. Processes that would usually take up to a minute can now be achieved in under 5 seconds.
</p>''', unsafe_allow_html=True)


st.markdown('<h4>Contributions & Improvements</h4>', unsafe_allow_html=True)
st.markdown('''<p>
This website is still in development and lacking in many areas. One main area of concern is the efficiency of categorization of transactions. This refers to categorizing transaction data into baskets such as:
<i>food, transport, shopping, etc.</i> One way this can be improved would be through the use of a suitable Machine Learning model, likely regressive in nature. <br>

If any developers are keen to contributing to this project, please drop me an email along with your implementation/proposal at <a href="ryanueda34@gmail.com">ryanueda34@gmail.com.
</p>''', unsafe_allow_html=True)
