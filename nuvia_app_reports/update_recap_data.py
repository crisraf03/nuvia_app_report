import pandas as pd
import nuvia 

"""Monthly data"""
year_selector = 2024
month_selector = 3
name_sheet = f"data\{year_selector}\{month_selector}\week_.xlsx"
name_sheet_finished = f'data\{year_selector}\{month_selector}\week_finished_.xlsx'


data_month = {'month_In' :pd.read_excel(name_sheet)  , 'month_Out': pd.read_excel(name_sheet_finished)}



"""Data of the old recap"""
dic_d = {'month_In' : 'opened' , 'month_Out': 'ended' }
year_col = {'month_In': 'year_In' , 'month_Out': 'year_Out'}


for month_col in ['month_In', 'month_Out']: # we do it twice
    excel_name = f'data/recap/_recap_data_{dic_d[month_col]}.xlsx'

    data_recap = pd.read_excel(excel_name)

    data_month_ = data_month[month_col]
    data_recap = data_recap[~data_recap['invoice'].isin(data_month_['invoice'])]

def update_recap_data(data_recap, month_col = 'month_In'):
    week_name = {'month_In' :'week'  , 'month_Out': 'week_finished'}
    name_sheet = f"data\{year_selector}\{month_selector}\{week_name[month_col]}_.xlsx"
    df_weeks = pd.read_excel(name_sheet)

    data_recap[~data_recap['invoice'].isin(df_weeks['invoice'])]
    data_recap = pd.concat([data_recap, df_weeks], axis=0)
    return data_recap








