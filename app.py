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


## HEADER
st.set_page_config(page_title='Dashboard Analytics')
st.header('Personal Finances Dashboard')
st.subheader('Graphs & Analytics')


## FILE UPLOAD
uploaded_files = st.file_uploader("Upload Your Bank Statement", type=['pdf'], accept_multiple_files=True)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)

try:
    for pdf in range(len(uploaded_files)):
        pdf_contents = uploaded_file.getvalue()
        pdf_file = io.BytesIO(pdf_contents)
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        with open(f'statements/statement_{pdf+1}.pdf', 'wb') as f:
            f.write(pdf_file.getbuffer())
            print('PDF Saved')


    ## SET FILE PATH
    directory = os.getcwd()
    path = directory + '\statements'
    filenames = os.listdir(path)


    concat = []
    for pdf in range(len(filenames)):
        tables = camelot.read_pdf(f'statements/{filenames[pdf]}', flavor='stream', pages='all')

        ## create concat df
        temp = tables[0].df.copy()

        ## concatenate all tables into one
        for i in range(1, len(tables)):
            temp = pd.concat([temp, tables[i].df])

        if pdf != len(filenames)-1:
            temp = temp.drop(temp.index[-1])
            
        concat.append(temp)
    concat = pd.concat(concat)


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

    concat['Balance'] = ''
    final = 204.47
    concat.at[concat.shape[0]-1, 'Balance'] = 'S$' + str(204.47)
    index = concat.shape[0]-2

    for agg in range(len(concat)):

        if concat.at[index, 'Debit'] != '':
            if isinstance(concat.at[index, 'Debit'], float) == False:
                update = final - float(concat.at[index, 'Debit'][2:])
                concat.at[index, 'Balance'] = 'S$' + str(round(update, 2))

        if concat.at[index, 'Credit'] != '':
            if isinstance(concat.at[index, 'Credit'], float) == False:
                update = final + float(concat.at[index, 'Credit'][2:])
                concat.at[index, 'Balance'] = 'S$' + str(round(update, 2))


        if index != 0:
            index -= 1


    def pie():
        TYPE = concat['Type']
        counts = TYPE.value_counts()
        names = counts.index.tolist()
        
        plt.pie(counts, labels=names, autopct='%1.1f%%')
        plt.legend()
        plt.show()
        
    def totalDrCr():
        dr = float(DrBal[2:].replace(',', ''))
        cr = float(CrBal[2:].replace(',', ''))

        vals = [dr, cr]
        names = ['Debit', 'Credit']
        plt.bar(x=names, height=vals)
        plt.legend()
        plt.show()

    def timeSeries():
        line = concat['']


    def saveToCSV():
        saveDF = concat.copy()
        date = saveDF.at[saveDF.shape[0]-1, 'Date']

        newRow = {
            'Date': date, 
            'Code': 'TTL', 
            'Type': 'Running Total', 
            'Reference': 'Total Dr/Cr',
            'Debit': DrBal,
            'Credit': CrBal}
        
        saveDF = saveDF.append(newRow, ignore_index=True)
        saveDF.to_excel('parsed.xlsx')

    concat.to_csv('check.csv')
    fig = px.pie(concat, 'Type')
    st.plotly_chart(fig)

except:
    pass