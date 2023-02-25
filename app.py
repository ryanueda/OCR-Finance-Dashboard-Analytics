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


## HEADER
st.set_page_config(page_title='Dashboard Analytics')
st.header('Personal Finances Dashboard')
st.subheader('Graphs & Analytics')

## SIDEBAR
st.markdown("""
<style>
.big-font {
    font-size: 35px !important;
}

.med-font {
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown('<h1 class="big-font">Upload & Filter</h1>', unsafe_allow_html=True)

## FILE UPLOAD
uploaded_files = st.sidebar.file_uploader("Upload Your Bank Statement", type=['pdf'], accept_multiple_files=True)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read() 


try:
    for pdf in range(len(uploaded_files)):
        pdf_contents = uploaded_file.getvalue()
        pdf_file = io.BytesIO(pdf_contents)
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        with open(f'statements/statement_{pdf+1}.pdf', 'wb') as f:
            f.write(pdf_file.getbuffer())
            print('PDF Saved')

    def parseData(file):
            tables = camelot.read_pdf(f'statements/{file}', flavor='stream', pages='all')
            concat = tables[0].df

            ## concatenate all tables into one
            for i in range(1, len(tables)):
                concat = pd.concat([concat, tables[i].df])

            ## filter out nonsensical data
            concat = concat[~concat.apply(lambda row: row.astype(str).str.contains('about:blank')).any(axis=1)]

            ## reset index of df
            concat = concat.reset_index(drop=True)

            if concat.shape[-1] == 7:
                concat = concat.drop(concat.columns[-1], axis=1)

            ## rename columns
            concat.columns = ['Date', 'Code', 'Reference', 'Debit', 'Credit', 'Extra']

            ## handle bad formatting
            for row in range(len(concat)):
                value = concat.at[row, 'Credit']
                extraVal = concat.at[row, 'Extra']
                
                if value != '':
                    concat.at[row, 'Debit'] = value
                    concat.at[row, 'Credit'] = ''
                
                if extraVal != '':
                    concat.at[row, 'Credit'] = extraVal
                    concat.at[row, 'Extra'] = ''
                    
            ## drop useless column
            concat = concat.drop(columns=['Extra'])

            firstCell = concat.at[0, 'Date']
            secondCell = concat.at[1, 'Debit']
            thirdCell = concat.at[2, 'Debit']
            fourthCell = concat.at[3, 'Debit']

            if firstCell.split(' ')[0] == 'Transaction':
                concat = concat.drop([0])
                
            if secondCell == 'Download':
                concat = concat.drop([1])
                
            if thirdCell == 'Debit':
                concat = concat.drop([2])
                
            if fourthCell == '(Withdrawal)':
                concat = concat.drop([3])
                
            concat = concat.reset_index(drop=True)
            concat['Type'] = ''
            concat = concat.reindex(columns=['Date', 'Code', 'Type', 'Reference', 'Debit', 'Credit'])
            for a in range(len(concat)):
                code = concat.at[a, 'Code']
                steps = 0
                
                if code != '':
                    addArr = []
                    index = a + 1
                    
                    while True:
                        if index > len(concat)-1:
                            break
                            
                        check = concat.at[index, 'Code']
                        if check == '':
                            addArr.append(concat.at[index, 'Reference'])
                            steps += 1
                            index += 1
                        else:
                            break
                        
                    for step in range(steps):
                        if concat.at[a, 'Reference'][-1] == '-' or concat.at[a, 'Reference'][-1].isdigit() == True:
                            concat.at[a, 'Reference'] += concat.at[a+step+1, 'Reference']
                        else:
                            concat.at[a, 'Reference'] += ' ' + concat.at[a+step+1, 'Reference']
                            
                        concat.at[a+step+1, 'Reference'] = ''

            ## remove all empty rows
            concat = concat.loc[~(concat == '').all(axis=1)]
            concat = concat.reset_index(drop=True)

            if concat.at[concat.shape[0]-1, 'Debit'] != '' and concat.at[concat.shape[0]-1, 'Credit'] != '':
                DrBal = concat.at[concat.shape[0]-1, 'Debit']
                CrBal = concat.at[concat.shape[0]-1, 'Credit']
                concat = concat.drop(concat.index[-1])

            for TYPE in range(len(concat)):
                code = concat.at[TYPE, 'Code']
                
                if code == 'MST':
                    concat.at[TYPE, 'Type'] = 'Card Transaction'
                    
                if code == 'ITR' or code == 'ICT':
                    concat.at[TYPE, 'Type'] = 'Funds Transfer'
                    
                if code == 'POS':
                    concat.at[TYPE, 'Type'] = 'Point-Of-Sale'
                    
                if code == 'INT':
                    concat.at[TYPE, 'Type'] = 'Interest Earned'

            concat = concat.reindex(index=concat.index[::-1])
            concat.reset_index(drop=True)

            concat = concat.loc[~((concat['Date'] == 'Date') & (concat['Code'] == 'Code'))]
            concat = concat.loc[~((concat['Debit'] == 'Download') & (concat['Credit'] == 'Print'))]
            concat = concat.loc[~((concat['Debit'] == '(Withdrawal)') & concat['Credit'] == '(Deposit)')]
            concat = concat.replace('', np.nan)
            concat = concat.dropna(thresh=len(concat.columns) - 3)
            concat = concat.reset_index(drop=True)
            concat = concat.loc[~((concat['Date'].str.contains('Transaction History')))]
            concat = concat.reset_index(drop=True)
        
            return concat
        
    ## SET FILE PATH
    directory = os.getcwd()
    path = directory + '/statements'
    filenames = os.listdir(path)
    concatList = []

    for pdf in range(len(filenames)):
        concat = parseData(filenames[pdf])
        concatList.append(concat)

    concat = pd.concat(concatList, axis=0)
    concat = concat.reset_index(drop=True)

    ## WRANGLING
    concat['Balance'] = ''
    final = 204.47
    concat.at[concat.shape[0]-1, 'Balance'] = 'S$' + str(204.47)
    index = concat.shape[0]-2

    totalDr = totalCr = 0
    for agg in range(len(concat)):

        if concat.at[index, 'Debit'] != '':
            if isinstance(concat.at[index, 'Debit'], float) == False:
                update = final - float(concat.at[index, 'Debit'][2:])
                totalDr += float(concat.at[index, 'Debit'][2:])
                concat.at[index, 'Balance'] = 'S$' + str(round(update, 2))

        if concat.at[index, 'Credit'] != '':
            if isinstance(concat.at[index, 'Credit'], float) == False:
                update = final + float(concat.at[index, 'Credit'][2:])
                totalCr += float(concat.at[index, 'Credit'][2:])
                concat.at[index, 'Balance'] = 'S$' + str(round(update, 2))

        if index != 0:
            index -= 1


    def totalDrCr():
        sumDF = concat.copy()
        sumDF['Debit'] = sumDF['Debit'].str[2:]
        sumDF['Credit'] = sumDF['Credit'].str[2:]

        sumDF['Debit'] = sumDF['Debit'].astype(float)
        sumDF['Credit'] = sumDF['Credit'].astype(float)
        sumDF['Date'] = sumDF['Date'].str[-4:]

        years = sumDF['Date'].unique()

        color_map = {'Debit': 'rgb(228,26,28)', 'Credit': 'rgb(55,126,184)'}

        grouped_df = sumDF.groupby('Date').agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()

        # Create a bar chart of total debit and credit amounts by year
        fig = px.bar(grouped_df, x='Date', y=['Debit', 'Credit'], barmode='group', color_discrete_map=color_map)

        # Add axis labels and title
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Amount",
            title="Total Debit and Credit Amounts by Year"
        )


        return fig
    

    def sumDrCr():
        sumDF = concat.copy()
        sumDF['Debit'] = sumDF['Debit'].str[2:]
        sumDF['Credit'] = sumDF['Credit'].str[2:]
        sumDF['Debit'] = sumDF['Debit'].astype(float)
        sumDF['Credit'] = sumDF['Credit'].astype(float)
        dr = round(sumDF['Debit'].sum(), 2)
        cr = round(sumDF['Credit'].sum(), 2)
        return dr, cr
    

    def balSeries():
        sumDF = concat.copy()
        sumDF['Balance'] = sumDF['Balance'].str[2:]
        sumDF['Balance'] = sumDF['Balance'].astype(float)
        # Convert the 'Date' column to a datetime object
        sumDF['Date'] = pd.to_datetime(sumDF['Date'])

        # Group the DataFrame by 'Date'
        grouped_df = sumDF.groupby('Date')['Balance'].max().reset_index()
        fig = px.line(grouped_df, x='Date', y='Balance', title='Time Series Of Bank Balance')

        return fig


    concat.to_excel('check.xlsx')


    fig = px.pie(concat, 'Type')
    fig.update_layout(
            title="Distribution Of Transaction Type"
        )
    
    totalDrCr = totalDrCr()
    dr, cr = sumDrCr()
    st.write('Total Debit: S$' + str(dr))
    st.write('Total Credit: S$' + str(cr))
    linePlot = balSeries()

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
    with col2:
        st.plotly_chart(totalDrCr, use_container_width=True, sharing="streamlit")

    
    st.plotly_chart(linePlot, use_container_width=True, sharing="streamlit")

except Exception as e:
    st.write(e)
    pass