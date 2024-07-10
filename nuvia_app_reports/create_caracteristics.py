import nuvia 
import pandas as pd

'''On this script you have the option to create the diferents columns with caracteristics for and order-list dataframe on nuvias platform'''

year_selector_default = 2024
month_selector_default = 4

# Setting default values
year_selector = year_selector_default
month_selector = month_selector_default

# Asking user for default or custom
default = input(f"If you want to create characteristics by default (year = {year_selector_default}, month = {month_selector_default}), please write 'D'. If not, press ENTER:")

if default != 'D':
    # Custom selection
    print(f'Please choose a year (e.g. {year_selector_default}): ')
    year_selector = input('Year: ')

    if year_selector:
        print(f'Please choose a month (e.g. {month_selector_default}): ')

        month_selector = input('Month: ')

# Creating file names
name_excel_created = f"data/{year_selector}/{month_selector}/week_"
name_excel_finished = f"data/{year_selector}/{month_selector}/week_finished_"
name_list = [name_excel_created, name_excel_finished]

if not month_selector or not year_selector:
    # Handling single Excel file case
    excel_file = input('Write the Excel file: ')
    name_list = [excel_file] if excel_file else []

for name_excel in name_list:
    try:
        print(f"Please wait. Creating the {name_excel}_with_characteristics file ... ")
        data_ = pd.read_excel(f"{name_excel}.xlsx")
        data_ = nuvia.create_caracteristics(data_)  # Assuming nuvia is defined elsewhere
        alt_name_excel = name_excel

        cols_to_export = ['invoice', 'patient', 'restorer', 'center', 'archs', 'shape', 'amount', 'product', 'status', 'month_In','month_Out',  'region', 'product class', 'material', 'arch type', 'redo type', 'year_In', 'responsable party','mixed_material']
        cols_to_export = cols_to_export + ['date_In', 'date_Out']
        data_[cols_to_export].to_excel(f"{alt_name_excel}_with_characteristics.xlsx", index=False)

        
        print(f"{alt_name_excel}_with_characteristics.xlsx created successfully.")
        month_selector = None
    except FileNotFoundError:
        print(f"Error: {name_excel}.xlsx not found.")

if month_selector:
    print(f"Look for the exported Excel files in nuvia_app_reports/data/{year_selector}/{month_selector} folder.")
else:
    print(f"Look for the file with_characteristics in the current working directory.")
