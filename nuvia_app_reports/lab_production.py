import pandas as pd

data_out = pd.DataFrame()

#take all the data
years_ = [2022,2023,2024]
month_ = 6


for year_ in years_:
    excel_name_ = f"data/{year_}/data_out_{year_}.xlsx"
    data_out_year = pd.read_excel(excel_name_)
    data_out = pd.concat([data_out, data_out_year], axis =0)

#manage the data según lo conversado 
print('All data catched...')
import nuvia
data_out_wc = nuvia.create_caracteristics(data_out, overtibar = True)

#data el mes 
month_filter = (data_out_wc['year_Out'] == 2024) & (data_out_wc['month_Out'] == month_)
data_out_month = data_out_wc[month_filter].reset_index()

#creation of lab_production_class()
## usaras en metodo groupby(year_Out, month_Out, center)

data_out_month.loc[(data_out_month['material'] == 'Single 24Z Processing'), 'lab_production_class'] = 'Single 24Z Processing'
data_out_month.loc[(data_out_month['material'] == 'Demodenture'), 'lab_production_class'] = 'Demodenture'
data_out_month.loc[(data_out_month['material'] == 'Wax Rims'), 'lab_production_class'] = 'Wax Rims'
data_out_month.loc[(data_out_month['product class']=='N3') & (data_out_month['redo type']== 'SURGERY'), 'lab_production_class'] = 'N3 surgery'
data_out_month.loc[(data_out_month['product class']=='N3') & (data_out_month['redo type']== 'REDO'), 'lab_production_class'] = 'N3 redo'
data_out_month.loc[data_out_month['material'] == 'Reline', 'lab_production_class'] = 'Reline'

data_out_month.loc[data_out_month['material']== 'Dummy', 'lab_production_class'] = 'Dummy'
data_out_month.loc[(data_out_month['material']== 'Removable Single'), 'lab_production_class'] = 'Removable Single'
data_out_month.loc[data_out_month['material'].isin(['Removable 24Z', 'Removable G-CAM']), 'lab_production_class'] = 'Fixed arches'
data_out_month.loc[data_out_month['material']== 'Night guard', 'lab_production_class'] = 'Night guard'

#clasificacion N6

# para el recap primero agrego las N3 redo go to second bridge y luego hago el N6 classification
patient_n6 = data_out_wc[data_out_wc['product class']=='N6'].groupby(['patient','center'])['invoice'].count()
invoice_n6 = data_out_wc[data_out_wc['product class']=='N6'][['patient', 'center','invoice']].set_index(['patient','center'])

invoice_n6['count invoice'] = invoice_n6.index.map(patient_n6)

invoice_n6.loc[ invoice_n6.index.isin(patient_n6[patient_n6 == 1].index), 'N6 rx'] = 'N6 1RX'
invoice_n6.loc[ invoice_n6.index.isin(patient_n6[patient_n6 > 1].index), 'N6 rx'] = 'N6 +2RX'

min_invoice_per_patient = invoice_n6['invoice'].groupby(invoice_n6.index).min()
invoice_n6.loc[invoice_n6['invoice'].isin(min_invoice_per_patient) , 'N6 rx'] = 'N6 1RX'

invoice_n6 = invoice_n6.set_index('invoice')

data_out_month['N6 rx'] = data_out_month['invoice'].map(invoice_n6['N6 rx'])
data_out_month['count N6 rx'] = data_out_month['invoice'].map(invoice_n6['count invoice'])

data_out_month.loc[~data_out_month['N6 rx'].isna() , 'lab_production_class'] = data_out_month[~data_out_month['N6 rx'].isna()]['N6 rx']

#pivot table 
pivot_table = data_out_month.pivot_table(values = 'archs', index='center', columns ='lab_production_class',aggfunc='sum')
pivot_table.reset_index(inplace=True)

#count the N6 patients
patient_table = data_out_month[~data_out_month['N6 rx'].isna()].pivot_table(values='archs', index = 'center', columns = 'N6 rx', aggfunc='count') 
patient_table.reset_index(inplace=True)

merged_table = pd.merge(pivot_table, patient_table , how='outer', on='center', suffixes = ('_arches', '_patient'))

# print(merged_table.columns)

cols_merged_table = ['center', 'N3 surgery', 'N3 redo', 'Reline', 'N6 1RX_arches','N6 +2RX_arches', 'Dummy', 'Removable Single','Fixed arches','Night guard', 'N6 1RX_patient' ,'N6 +2RX_patient', 'Demodenture', 'Single 24Z Processing', 'Wax Rims','nan']
cols_merged_table = ['center', 'N3 surgery', 'N3 redo', 'Reline', 'N6 1RX_arches','N6 +2RX_arches', 'Dummy', 'Removable Single','Fixed arches','Night guard', 'N6 1RX_patient' ,'N6 +2RX_patient', 'Demodenture', 'Single 24Z Processing','nan']



merged_table = merged_table[cols_merged_table]


#sumas 
N3_total = None
N6_total = None
reline_total = None 
N6_total_patients = None 

list_to_export = [{ 'name': 'orders' , 'df': data_out_month , 'index': False },
                  { 'name': 'lab_production_report' , 'df': merged_table , 'index': False }]

nuvia.create_multiple_worksheet(list_to_export, name_excel='results/lab_production.xlsx')

#conteo data para calculo de averages































