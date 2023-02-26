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
st.set_page_config(page_title='Dashboard Analytics')
st.title('Personal Finances Dashboard')
st.subheader('Graphs & Analytics')
st.write('')


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
st.sidebar.subheader('')


try:
    ## FILE UPLOAD
    uploaded_files = st.sidebar.file_uploader("Upload Your Bank Statement", type=['pdf'], accept_multiple_files=True)
    st.sidebar.write('')
    final = st.sidebar.text_input('Enter Final Bank Balance :moneybag:', placeholder="Your Bank Balance")
    bank = st.sidebar.radio('Bank', options=['DBS', 'POSB'])

    if uploaded_files != '':
        directory = os.getcwd()
        path = directory + '/statements'
        files = os.listdir(path)

        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)


    if final == '':
        final = 204.67
    else:
        if not re.match("^[0-9]+(\.[0-9]*)?$", final):
            st.warning("Please enter a valid float or integer value.")

    final = float(final)

    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read() 

    directory = os.getcwd()
    path = directory + '/statements'
    for pdf in range(len(uploaded_files)):
        pdf_contents = uploaded_file.getvalue()
        pdf_file = io.BytesIO(pdf_contents)
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        if bank == 'posb':
            bankName = 'posb'
        else:
            bankName = 'dbs'

        with open(f'{path}/{bankName}_statement_{pdf+1}.pdf', 'wb') as f:
            f.write(pdf_file.getbuffer())
            print('PDF Saved')

    # @st.cache_data
    def parsePOSBData(file):
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
    

    def parseDBSData(file):
        tables = camelot.read_pdf(f'statements/{file}', flavor='stream', pages='all')
        concat = tables[0].df

        for i in range(1, len(tables)):
            concat = pd.concat([concat, tables[i].df])

        concat = concat.drop(index=0)
        concat = concat.drop(index=1)
        concat = concat.reset_index(drop=True)
        concat.columns = ['Date', 'Extra', 'Code', 'Reference', 'Debit', 'Extra2', 'Credit']
        concat = concat.drop(columns=['Extra'])
        concat = concat.drop(index=0)
        concat = concat.drop(index=1)
        concat.columns = ['Date', 'Code', 'Reference', 'Debit', 'Extra', 'Credit']
        concat = concat.reset_index(drop=True)

        for row in range(len(concat)):
            debit = concat.at[row, 'Debit']
            credit = concat.at[row, 'Credit']
            extraVal = concat.at[row, 'Extra']

            if debit == '' and credit != '':
                concat.at[row, 'Debit'] = credit
                concat.at[row, 'Credit'] = ''
            
            if credit == '' and extraVal != '':
                concat.at[row, 'Credit'] = extraVal
                concat.at[row, 'Extra'] = ''

        concat = concat.drop(columns=['Extra'])

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

            if code == 'ADV':
                concat.at[TYPE, 'Type'] = 'PayLah'

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
        concat = concat.reindex(columns=['Date', 'Code', 'Type', 'Reference', 'Debit', 'Credit'])
    
        return concat


        
    ## SET FILE PATH
    directory = os.getcwd()
    path = directory + '/statements'
    try:
        filenames = os.listdir(path)
        progress = st.progress(0)
        status = st.empty()
        concatList = []


        for pdf in range(len(filenames)):
            status.text(f'Analysing File {pdf+1}...')
            if filenames[pdf][:3] == 'posb':
                concat = parsePOSBData(filenames[pdf])

            if filenames[pdf][:3] == 'dbs':
                concat = parseDBSData(filenames[pdf])
            concatList.append(concat)
            noFiles = len(filenames)
            progVal = int(80/noFiles)
            progress_value = ((pdf+1)*progVal)
            progress.progress(progress_value)
            


        concat = pd.concat(concatList, axis=0)
        concat = concat.reset_index(drop=True)

        ## WRANGLING
        concat['Balance'] = ''
        # final = 204.47
        concat.at[concat.shape[0]-1, 'Balance'] = 'S$' + str(final)
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

            sumDF['Date'] = pd.to_datetime(sumDF['Date']).dt.year
            # sumDF['Date'] = sumDF['Date'].str[-4:]

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
            show_trendline = st.sidebar.checkbox('Show Trendline', value=True)
            if not show_trendline:
                fig = px.scatter(grouped_df, x='Date', y='Balance', title='Time Series Of Bank Balance')
            else:
                fig = px.scatter(grouped_df, x='Date', y='Balance', trendline="rolling", trendline_options=dict(window=5), trendline_scope='overall', trendline_color_override='red', title='Time Series Of Bank Balance')
            fig.update_traces(mode='lines')

            return fig


        concat['Date'] = pd.to_datetime(concat['Date'])
        concat = concat.sort_values(by=['Date'])

        concat.to_excel('parsed.xlsx')
        with open('parsed.xlsx', 'rb') as f:
            bytes_data = f.read()

        st.sidebar.write('')
        st.sidebar.write('Download Excel File')
        st.sidebar.download_button('Download Excel', data=bytes_data, file_name='parsedStatements.xlsx', mime='xlsx')
        st.sidebar.write('')

        st.sidebar.markdown('<h3>Display Options</h3>', unsafe_allow_html=True)



        fig = px.pie(concat, 'Type')
        fig.update_layout(
                title="Distribution Of Transaction Type"
            )
        
        totalDrCr = totalDrCr()
        dr, cr = sumDrCr()
        if dr == 2548.24 and cr == 2498.06:
            st.markdown('Below Is A Sample File & Dashboard', unsafe_allow_html=True)
        st.write('')

        column1, column2, column3 = st.columns(3)
        with column1:
            st.markdown(f'''
                        <div class="stats"><b>Total Debit</b</div>
                        <h3>${dr}</h3>
                        ''', unsafe_allow_html=True)
        with column2:
            st.markdown(f'''
                        <div class="stats"><b>Total Credit</b</div>
                        <h3>${cr}</h3>
                        ''', unsafe_allow_html=True)
        with column3:
            st.markdown(f'''
                        <div class="stats"><b>Current Balance</b</div>
                        <h3>${final}</h3>
                        ''', unsafe_allow_html=True)
        st.markdown("""
<style>
.stats {
    width: 200px;
    height: 70px;
    border: 1px solid #d3d3d3;
    border-radius: 15px;
    background-color: white;
    text-align: center;
    transition: all 0.2s ease-in-out;
    margin-bottom: 20%;
}

.stats:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

b {
    font-family: 'Century Gothic', serif;
    font-weight: 800;
    text-align: center;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

        linePlot = balSeries()

        # if show_trendline:
        #     linePlot.update_traces(trendline='lowess', trendline_scope='overall', trendline_options=dict(frac=0.1), trendline_color_override='red')
        # else:
        #     linePlot.update_traces(trendline=None)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
        with col2:
            st.plotly_chart(totalDrCr, use_container_width=True, sharing="streamlit")

        
        st.plotly_chart(linePlot, use_container_width=True, sharing="streamlit")



        progress.progress(100)
        status.text('Done !')
    except Exception as e:
        st.write(e)
        pass
   

except FileNotFoundError:
    pass