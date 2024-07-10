import nuvia
import script_weeks
import os 
import pandas as pd
import lab_metric

os.makedirs('results', exist_ok=True)
year_selector = '2024'
year_selector = input('Year selector : ')

month_selector = int(input('At which month you want to make the consult ? : '))
week_of_the_report = int(input('and what week ? : ') )
month_B = script_weeks.month_B[year_selector][str(month_selector)]

print('Starting the lab metric report ... ')
dates_week = script_weeks.dic_dates_week[year_selector][str(month_selector)]
operation_capacity_week = script_weeks.dic_operation_capacity[year_selector][str(month_selector)] 
month_name = month_selector
monday_of_the_month = [day[0] for day in dates_week[1:]]

###########################################################################################################
""" import, transform and separate the data by weeks"""
name_sheet = f"data\{year_selector}\{month_selector}\week_.xlsx"
name_sheet_finished = f'data\{year_selector}\{month_selector}\week_finished_.xlsx'

database_month = lab_metric.transform_data(name_sheet, dates_week, monday_of_the_month) # for the count of the N3 products.
database_finished = lab_metric.transform_data(name_sheet_finished, dates_week, monday_of_the_month) # for the count of the other products : N6 , all redos.

print(set(database_month['date_Out']))

############################################# creation of the report ##############################################################
print('Creation of the weekly report')

"""create the report by week""" 
Total_reports, Total_percents_region, Total_error_cases = lab_metric.generate_weekly_report(database_month, database_finished, dates_week, operation_capacity_week, week_of_the_report)

"""Create the monthly report""" 
Report_month, percents_region_month, error_cases_month = lab_metric.create_monthly_report(database_month, database_finished, month_selector, operation_capacity_week)
print(' '*4 + 'Creation of the Monthly report finished')

"""unification of the monthly database"""
data_in_and_out = lab_metric.unify_monthly_database(database_month, database_finished)

######################################################################################################################
pd.options.mode.chained_assignment = 'warn'

"""GCAM cases"""
gcam_to_export = lab_metric.analyze_gcam_cases(database_month, dates_week, month_B, month_name, path = f"data\{year_selector}\Gcam_cases_studied.xlsx")

""" Redo cases """
redo_to_export = lab_metric.analyze_redo_cases(database_month, database_finished, month_selector, month_B, month_name, path = f"data\{year_selector}\Redo_cases_studied.xlsx")

"""Separate N6 cases"""
material_change_to_export = lab_metric.analyze_material_change_cases(database_month, database_finished, month_selector, month_B, month_name, path = f"data\{year_selector}\material_change_cases_studied.xlsx")

data_to_export = [{'name': 'gcam_false', 'df' :gcam_to_export, 'index':False },
                  {'name': 'redo_false', 'df' :redo_to_export, 'index':False },
                  {'name': 'material_change_false', 'df' :material_change_to_export, 'index':False }]

nuvia.create_multiple_worksheet(data_to_export, f'results/data_cases_for_update_{month_selector}.xlsx')


############################################# further analysis ##############################################################

""" Contar los  G-CAM esperando por 24Z"""
Gcam_total , db_total, db_old =  lab_metric.count_gcam_waiting_for_24z(database_month, month_selector, year_selector=int(year_selector))

"""" Do the N6 Analysis of the history of the patients"""
N6_analysis = nuvia.N6_count_analysis(db_total)
print('N6 Analysis of the history of the patients finished')

"""open orders"""
# data_open_orders = pd.read_excel("data\checkIn_all_with_characteristics.xlsx")
open_orders = nuvia.filter_open_orders(db_old , month_selector, _year_ = int(year_selector), yeison_query=False)

# Antes de la operación que causa la advertencia, establece el atributo is_copy en False
pd.options.mode.chained_assignment = None

############################################# Exporting the data #############################################################

Total_error_cases = Total_error_cases[['invoice', 'patient', 'restorer', 'center', 'checkIn', 'amount', 'archs','product', 'status', 'week_number', 'region', 'amount_', 'arch_', 'error_amount', 'error_arch']]

"""Export report numbers and cases"""

print('Exporting the data ...')
list_to_export = [{ 'name': 'Report' , 'df': Total_reports , 'index': False },
                  { 'name': 'percents_by_region' , 'df': Total_percents_region , 'index': False },
                  { 'name': 'Gcam_to_24z' , 'df': Gcam_total , 'index': False },
                  { 'name': 'monthly_report' , 'df': Report_month , 'index': False },
                  { 'name': 'monthly_percents_regions' , 'df': percents_region_month , 'index': False },
                  { 'name': 'N6_analysis' , 'df':N6_analysis , 'index': False },
                  { 'name': 'database_month_in_and_out' , 'df': data_in_and_out , 'index': False },
                  { 'name': 'open_orders' , 'df': open_orders , 'index': False },
                  { 'name': 'errors' , 'df':Total_error_cases , 'index': False }]

# Crea un objeto ExcelWriter
writer = pd.ExcelWriter('results/Reported_sheet_{}.xlsx'.format(month_name), engine='xlsxwriter')

for each_df in list_to_export:
   df = each_df['df'] 

   if 'center' in df.columns : 
      df['center'] = df['center'].replace('OFFICE', '', regex = True)
   df.to_excel(writer, sheet_name = each_df['name'], index = each_df['index'])
writer.close()

print('End of the Report')