'''This script ... made this and that...'''
import pandas as pd
import nuvia_flux

print ('Initializating Flux analysis ...')

year_default = 2023
month_start_default , month_finish_default = 11 , 12





group_months = {} # Nueva lista para almacenar las parejas resultantes

year_selector = input(f"Please select a year. If you don´t select any and click Enter, it will by {year_default} by default : ")
if year_selector == '':
    year_selector = year_default


month_start = input(f"Please add the started month for the flux report. If you don´t select any and click Enter, it will by {month_start_default} by default : ")
month_finish = input(f"Please add the finished month for the flux report. If you don´t select any and click Enter, it will by {month_finish_default} by default :  ")

if month_start == '':
    month_start = month_start_default
if month_finish == '':
    month_finish = month_finish_default

year_selector = int(year_selector)
month_start = int(month_start)
month_finish = int(month_finish)




# External loop to iterate through each sublist in group_months
group_months = nuvia_flux.generate_month_groups(month_start , month_finish)

# Select the columns 'date' and the data selection
checkout_column = 'CheckOut'
data_selector = 'Out'
description_column_selector_default = 'center'


description_column_selector_option = ['center' , 'restorer']

description_column_number = input('Please select the description column number of the report like this.\n(1: center 2: restorer ):  ')

if description_column_number in ['0','1']:
    description_column_selector = description_column_selector_option[int(description_column_number) - 1]
else:
    print('Select 0 or 1. Not other option is avaible. We will use center as a default description column...')
    description_column_selector = description_column_selector_default


print('Creating the flux report for : ' , description_column_selector)

# Use forward slashes or raw string for file paths

file_path = f"data/checkIn_all"

import os 

if os.path.isfile(file_path+"_with_characteristics.xlsx"):

    data_cold = pd.read_excel(file_path+"_with_characteristics.xlsx")
    print(f'The month will be analyzed with this months interconections {group_months} , also you will find the redo orders of each month on the exported excel.')

else:
    import unittest.mock
    with unittest.mock.patch('builtins.input', side_effect=['', '', file_path]):
        print('Loading create_caracteristics script ...')
        import create_caracteristics

    data_cold = pd.read_excel(file_path+"_with_characteristics.xlsx")
    print(f'The month will be analyzed with this months interconections {group_months} , also you will find the redo orders of each month on the exported excel.')
        


def add_month_columns(df, selected_month_start , selected_month_end):
    df.loc[:, 'month start'] = selected_month_start 
    df.loc[:, 'month end'] = selected_month_end      
    return df




month_reports = {}

for  month , months_lists in group_months.items(): # Use .items() to iterate over dictionary keys and values
    month_information = {'report' : [] , 'db_nx_patients' : [] , 'redos_month' : []}

    for month_position in months_lists:
        selected_month_start, selected_month_end = month_position
        report, redos_month, db_nx_patient = nuvia_flux.process_data_for_month(data_cold, checkout_column, year_selector, data_selector, selected_month_start, selected_month_end ,description_column=description_column_selector)

        month_information['report'].append( add_month_columns(report , selected_month_start ,selected_month_end ) )
        month_information['db_nx_patients'].append( add_month_columns(db_nx_patient , selected_month_start ,selected_month_end ) )
 
    month_information['report'] = pd.concat(month_information['report'] , axis= 0).reset_index()
    month_information['db_nx_patients'] = pd.concat(month_information['db_nx_patients'], axis=0).reset_index()
    month_information['redos_month'] = add_month_columns(redos_month , selected_month_start ,selected_month_end )

    month_reports[month]  = month_information




import os

# Folder path
folder_path = "results/flux_reports"

# Check if the folder exists
if not os.path.exists(folder_path):
    # If it doesn't exist, create it
    os.makedirs(folder_path)

for month_key, df in month_reports.items():
    writer = pd.ExcelWriter(f"results/flux_reports/flux_report_month_{month_key}_{description_column_selector}.xlsx", engine='xlsxwriter') # Crea un objeto ExcelWriter
    df['report'].to_excel(writer, sheet_name = 'report', index=False)
    df['db_nx_patients'].to_excel(writer, sheet_name = 'db_nx_patients', index=False)
    df['redos_month'].drop(['month end'], axis = 1).to_excel(writer, sheet_name = 'redos_month', index=False)
    writer.close()




