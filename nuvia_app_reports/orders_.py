import pandas as pd 
import nuvia

path  = 'data/other_queries/'
data_open = pd.read_excel(f'{path}open_2024.xlsx')
data_end = pd.read_excel(f'{path}end_2024.xlsx')

excel_name = 'data/other_queries/all_2024.xlsx'
orders = {'open': data_open, 'end':data_end}

month_name = '_2024'
writer =  pd.ExcelWriter('results/Redo_remakes_{}.xlsx'.format(month_name), engine='xlsxwriter')

for name_, df in orders.items():
    df = nuvia.create_caracteristics(df)
    df[df['redo type'].isin(['REDO' ,'REMAKE'])].to_excel(writer, sheet_name = name_, index = False)
writer.close()

