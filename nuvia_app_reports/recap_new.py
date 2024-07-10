import pandas as pd 
data_out = pd.DataFrame()


_redo_name_ = 'Redo_cases_studied' 
_n6_name_ = 'material_change_cases_studied' 
_sheet_name_ = 'may'
_month_ = 5


#take all the data
years_ = [2022,2023,2024]

for year_ in years_:
    excel_name_ = f"data/{year_}/data_out_{year_}.xlsx"
    data_out_year = pd.read_excel(excel_name_)
    data_out = pd.concat([data_out, data_out_year], axis =0)

#manage the data según lo conversado 
print('All data catched...')
import nuvia
data_out_wc = nuvia.create_caracteristics(data_out)

## usaras en metodo groupby(year_Out, month_Out, center)
data_out_wc.loc[(data_out_wc['product class']=='N3') & (data_out_wc['redo type']== 'SURGERY'), 'recap_class'] = 'N3 surgery'
data_out_wc.loc[(data_out_wc['product class']=='N3') & (data_out_wc['redo type']== 'REDO'), 'recap_class'] = 'N3 redo'
data_out_wc.loc[data_out_wc['material'].isin(['Removable 24Z', 'Removable G-CAM']) & ~data_out_wc['product'].str.contains('Redo'), 'recap_class'] = 'Fixed arches'
data_out_wc.loc[data_out_wc['material'].isin(['Removable 24Z', 'Removable G-CAM']) & data_out_wc['product'].str.contains('Redo'), 'recap_class'] = 'redo Fixed arches'
data_out_wc.loc[(data_out_wc['product class']=='N6') & (data_out_wc['redo type']== 'SURGERY'), 'recap_class'] = 'N6 surgery'
data_out_wc.loc[(data_out_wc['product class']=='N6') & (data_out_wc['redo type'].isin(['REDO', 'REMAKE'])), 'recap_class'] = 'N6 redo'

#asigno un id unico a cada (patient,center) ngroup()
data_out_wc['ID_patient'] = data_out_wc.groupby(['patient', 'center']).ngroup()

#averiguo cuantas ordenes N3 surgery hay por paciente en todo el historial
surgeries_n3_by_patient = data_out_wc[data_out_wc['recap_class'] == 'N3 surgery'].groupby('ID_patient')['invoice'].count()

# print(surgeries_n3_by_patient)

cols_to_study = ['invoice','ID_patient','patient','center','product','checkIn', 'CheckOut', 'archs','arch type', 'material','month_Out','year_Out']
n3_surgery_2rx = data_out_wc[(data_out_wc['ID_patient'].isin(surgeries_n3_by_patient[surgeries_n3_by_patient != 1].index)) & (data_out_wc['recap_class'] == 'N3 surgery') ][cols_to_study]
min_invoice_n3_surgery = n3_surgery_2rx.groupby('ID_patient')['invoice'].min()

#  print(min_invoice_n3_surgery)

n3_surgery_2rx.loc[n3_surgery_2rx['invoice'].isin(min_invoice_n3_surgery) , 'counter invoice'] = 'first bridge'
n3_surgery_2rx.loc[~n3_surgery_2rx['invoice'].isin(min_invoice_n3_surgery) , 'counter invoice'] = 'first bridge maybe redo'

n3_surgery_2rx = n3_surgery_2rx.sort_values('ID_patient', ascending=False)

#ahora quiero usar el nombre del paciente como indice y clasificar segun counter invoice en columnas
n3_surgery_2rx_merged = pd.merge(n3_surgery_2rx[n3_surgery_2rx['counter invoice']=='first bridge'] , n3_surgery_2rx[n3_surgery_2rx['counter invoice']=='first bridge maybe redo'] , on='ID_patient', how ='outer', suffixes=(' first bridge', ' redo bridge'))

#reviso los singles y los full mouth
n3_surgery_2rx_merged.loc[(n3_surgery_2rx_merged['arch type first bridge'] == 'Full Mouth' ) & (n3_surgery_2rx_merged['arch type redo bridge'] == 'Full Mouth' ) , 'arch to arch'] = 'full to full'
n3_surgery_2rx_merged.loc[(n3_surgery_2rx_merged['arch type first bridge'] == 'Full Mouth' ) & (n3_surgery_2rx_merged['arch type redo bridge'] == 'Single' ) , 'arch to arch' ] = 'full to single'
n3_surgery_2rx_merged.loc[(n3_surgery_2rx_merged['arch type first bridge'] == 'Single' ) & (n3_surgery_2rx_merged['arch type redo bridge'] == 'Full Mouth' ) , 'arch to arch' ] = 'single to full'
n3_surgery_2rx_merged.loc[(n3_surgery_2rx_merged['arch type first bridge'] == 'Single' ) & (n3_surgery_2rx_merged['arch type redo bridge'] == 'Single' ) , 'arch to arch'] = 'single to single'


n3_surgery_2rx_merged.loc[~(n3_surgery_2rx_merged['arch to arch']=='single to single') , 'first bridge surgery class']  = 'redo first bridge'
n3_surgery_2rx_merged['diff days'] =  pd.to_datetime(n3_surgery_2rx_merged['checkIn redo bridge'], format ='%Y-%m-%d %H:%M:%S') - pd.to_datetime(n3_surgery_2rx_merged['CheckOut first bridge'], format = '%Y-%m-%d %H:%M:%S') 
n3_surgery_2rx_merged['diff month'] = n3_surgery_2rx_merged['diff days'].dt.days //30
n3_surgery_2rx_merged.loc[ n3_surgery_2rx_merged['diff month'] <= 4,  'first bridge surgery class'] = 'n3 surgery redo first bridge'
n3_surgery_2rx_merged.loc[ n3_surgery_2rx_merged['diff month'] > 4,  'first bridge surgery class'] = 'n3 surgery second bridge'

excel_to_export = []
excel_to_export.append({'name': 'surgeries_more_2rx' , 'df':n3_surgery_2rx_merged , 'index': False})

#una vez clasificados los n3 surgeries y extraidos los invoice redos, pasarlos al recap class como redos
n3_surgery_2rx_merged = n3_surgery_2rx_merged[['invoice redo bridge', 'first bridge surgery class']]
mapped_values= data_out_wc['invoice'].map(n3_surgery_2rx_merged.set_index('invoice redo bridge')['first bridge surgery class'])

data_out_wc.loc[data_out_wc['invoice'].isin(n3_surgery_2rx_merged['invoice redo bridge']) , 'recap_class'] = mapped_values[data_out_wc['invoice'].isin(n3_surgery_2rx_merged['invoice redo bridge'])]





#Trabajo en los fixed arches

fix_arch_patient_filter = data_out_wc['recap_class'].isin(['Fixed arches','redo Fixed arches'])
fixed_arch_patient = data_out_wc[fix_arch_patient_filter][['patient', 'invoice', 'ID_patient']]
recap_list = ['N6 surgery', 'N3 surgery', 'redo second bridge', 'redo within a month', 'redo after one month', 'N6 redo', 'n3 surgery second bridge', 'Fixed arches', 'redo Fixed arches','second bridge 1 rx','second bridge 2 rx']
data_out_wc.loc[(data_out_wc['recap_class'].isin(recap_list)) & (data_out_wc['patient'].isin(fixed_arch_patient['patient'])), 'fixed_consult'] = 'patient with fixed arch'

cols_fixed_study = ['patient','invoice','product','product class','recap_class', 'archs','arch type']
fixed_arches = data_out_wc[data_out_wc['fixed_consult']== 'patient with fixed arch'][cols_fixed_study]

# Ordenar por nombre del paciente y número de registro
fixed_arches.sort_values(by=['patient', 'invoice'], inplace=True)

# Reiniciar el índice después de ordenar
fixed_arches.reset_index(drop=True, inplace=True)

# Enumerar los productos para cada paciente
fixed_arches['product_order'] = fixed_arches.groupby('patient').cumcount() + 1

#estoy buscando aquellos paciente con ordenes fixed arche a: single-fixed arch,  b: fixed arch first product
fixed_arches.loc[(fixed_arches['recap_class'] == 'Fixed arches') & (fixed_arches['product_order'] == 1),'fixed_class'] = 'first bridge fixed'

# print('fixed_arches : ', fixed_arches.columns)
#ahora buscamos por pacientes
patients_second_product_fixed = fixed_arches[(fixed_arches['recap_class'] == 'Fixed arches') & (fixed_arches['product_order'] != 1)]
fixed_arches.loc[(fixed_arches['arch type'] == 'Single') & (fixed_arches['product_order'] == 1) & (fixed_arches['patient'].isin(patients_second_product_fixed['patient'])),'fixed_class'] = 'first bridge fixed'
fixed_arches.loc[fixed_arches['fixed_class']!= 'first bridge fixed', 'fixed_class'] ='redo first bridge fixed'

excel_to_export.append({'name':'fixed arches' , 'df':fixed_arches , 'index':False})



#inicio con la clasificacion de n3 redos
cols_redo_study = ['invoice','ID_patient','center', 'patient', 'product','checkIn','CheckOut','redo type','recap_class']
new_n3_surgery = data_out_wc[data_out_wc['recap_class'].isin(['N3 surgery'])][cols_redo_study]

redos_n3  = data_out_wc[data_out_wc['recap_class'].isin(['N3 redo',  'n3 surgery redo first bridge', 'redo first bridge fixed'])][cols_redo_study]
redos_n3_groupby_patient = redos_n3.groupby('ID_patient')['invoice'].count()

compare_n3_merged = pd.merge(new_n3_surgery, redos_n3, on='ID_patient', how='right', suffixes=(' surgery', ' redo'))
compare_n3_merged['diff days'] = pd.to_datetime(compare_n3_merged['checkIn redo'] , format ='%Y-%m-%d %H:%M:%S' )  - pd.to_datetime(compare_n3_merged['CheckOut surgery'] , format ='%Y-%m-%d %H:%M:%S' )
compare_n3_merged['diff month'] = compare_n3_merged['diff days'].dt.days // 30

def classify_redo(diff_month):
    if diff_month < 1:
        return 'redo within a month'
    elif 1 < diff_month < 4:
        return 'redo after one month'
    elif diff_month > 4:
        return 'redo second bridge'
    else:
        return 'redo second bridge'  # Para los valores NaN

compare_n3_merged['redo_recap_class'] = compare_n3_merged['diff month'].apply(classify_redo)
excel_to_export.append({'name': 'compare n3 products' , 'df':compare_n3_merged, 'index': False})

# añado los valores de redo_recap_class a data_out_wc['recap_class']
compare_n3_merged = compare_n3_merged[['invoice redo', 'redo_recap_class']]
mapped_values= data_out_wc['invoice'].map(compare_n3_merged.set_index('invoice redo')['redo_recap_class'])
data_out_wc.loc[data_out_wc['invoice'].isin(compare_n3_merged['invoice redo']) , 'recap_class'] = mapped_values[data_out_wc['invoice'].isin(compare_n3_merged['invoice redo'])]

# ahora tomo los casos N6 para hacer la clasificacion second bridge
cols_redo_study = ['ID_patient','invoice','center', 'patient', 'product','redo type','recap_class']
n6_orders = data_out_wc[data_out_wc['recap_class'].isin(['n3 surgery second bridge','redo second bridge', 'N6 surgery','N6 redo'])][cols_redo_study]

n6_counter = n6_orders.groupby('ID_patient')['invoice'].count()
# n6_counter = n6_counter.reset_index()

def classify_second_bridge(count_invoices):
    if count_invoices == 1 : 
        return 'second bridge 1 rx'
    elif count_invoices > 1: 
        return 'second bridge 2 rx'

n6_counter['n6_recap_class'] = n6_counter.apply(classify_second_bridge)
n6_orders['n6_recap_class'] = n6_orders['ID_patient'].map(n6_counter['n6_recap_class'])

#reajusto el n6_recap_class con el min_invoice
min_n6_invoice = n6_orders.groupby('ID_patient')['invoice'].min()
n6_orders.loc[n6_orders['invoice'].isin(min_n6_invoice), 'n6_recap_class'] = 'second bridge 1 rx'
excel_to_export.append({'name': 'n6 orders', 'df': n6_orders, 'index': False})

#agrego los n6_recap_class en data_out_wc
n6_orders = n6_orders[['invoice', 'n6_recap_class']]
mapped_values= data_out_wc['invoice'].map(n6_orders.set_index('invoice')['n6_recap_class'])
data_out_wc.loc[data_out_wc['invoice'].isin(n6_orders['invoice']) , 'recap_class'] = mapped_values[data_out_wc['invoice'].isin(n6_orders['invoice'])]

# excel_to_export.append({'name':'data_out' , 'df':data_out_wc , 'index':False})

##############################################################################################33

#ahora busco asignar a el invoice el redo/product reason
#uso los redos_cases y los N6_cases(N6 y remakes)
#tomo los redos estudiados y les asigno

redo_name = _redo_name_
n6_name = _n6_name_ 
_sheet_name = _sheet_name_


def read_file_cases(file_name , _sheet_name, year_ = 2024):
    excel_name_ = f"data/{year_}/{file_name}.xlsx"
    df_cases = pd.read_excel(excel_name_, sheet_name=_sheet_name)
    # print(f"{file_name}  : {df_cases.columns}")
    # print(f"{file_name} redo reason : {df_cases['redo reason'].unique()}")
    # print(f"{file_name} product reason : {df_cases['product reason'].unique()}")
    return df_cases

common_cols = ['invoice']
redo_cols = ['redo reason', 'product reason', 'redo cause','responsable party']
redo_cases = read_file_cases(redo_name , _sheet_name)[common_cols + redo_cols]

material_change_cols = ['redo reason','product reason','redo cause','responsable party']
material_change_cases = read_file_cases(n6_name , _sheet_name)[common_cols + material_change_cols]

#ahora agrego las columnas de redo reason, product reason : 1. unifico las redo cause
reasons = pd.concat([redo_cases,material_change_cases], axis=0)

# data_out_merged = pd.merge(data_out_wc , redo_cases , on='invoice', how ='left')
data_out_merged = pd.merge(data_out_wc , reasons , on='invoice', how ='left')

last_month = (data_out_merged['year_Out'] == 2024)  & (data_out_merged['month_Out'] == _month_)
excel_to_export.append({'name':'data_out_merged' , 'df':data_out_merged[last_month] , 'index':False})




#ahora toca calcular los porcentajes y las distintas tablas 

#rename de recap_class on recap_name
recap_class_list = ['N3 surgery','Fixed arches', 'second bridge 1 rx', 'second bridge 2 rx', 'redo within a month', 'redo after one month',  'redo Fixed arches'] # ademas : 'nan'

recap_name = {'N3 surgery' : 'first bridge', 'Fixed arches': 'first bridge', 'second bridge 1 rx' : 'second bridge', 'second bridge 2 rx' : 'second bridge 2rx', 'redo within a month': 'redo first bridge within a month', 'redo after one month':'redo first bridge after one month',  'redo Fixed arches':'redo first bridge after one month'}

data_out_merged['recap_name'] = data_out_merged['recap_class'].map(recap_name)


cols_first_bridge_export = ['center','invoice', 'patient', 'product', 'archs', 'product class', 'recap_class', 'recap_name', 'redo type', 'material', 'mixed_material']

first_bridge = data_out_merged[last_month & (data_out_merged['recap_name'] == 'first bridge')][cols_first_bridge_export]

excel_to_export.append({'name':'first bridge' , 'df':first_bridge , 'index':False})







#pivot table with the redos percentajes and the values
recap_counter = pd.pivot_table(data_out_merged[last_month], values='archs', index='center', columns='recap_name', aggfunc='sum', fill_value=0)

def calculate_percentaje(df, name_new_col, name_part_col, name_base_col):
    df[name_new_col] = df[name_part_col] / df[[name_part_col , name_base_col]].sum(axis=1).replace(0, 1)

calculate_percentaje(recap_counter, 'redo within a month percent', 'redo first bridge within a month' , 'first bridge')
calculate_percentaje(recap_counter, 'redo after month percent', 'redo first bridge after one month' , 'first bridge')


#Now i need to calculate the values of the last six month for the second bridge percentaje

#create a year-month col
data_out_merged['year_month_out'] = data_out_merged['CheckOut'].dt.to_period('M')
from datetime import datetime, timedelta

# Calcular el período correspondiente a los últimos 6 meses
last_month_number = data_out_merged['year_month_out'].max()
six_months_before = last_month_number - 5  # Restamos 5 para obtener los últimos 6 meses

# Filtrar el DataFrame para obtener solo las filas correspondientes a los últimos 6 meses
last_six_months = data_out_merged['year_month_out'] >= six_months_before

#quiero calcular el average de los 6 meses de second bridge
recap_six_month = pd.pivot_table(data_out_merged[last_six_months & (data_out_merged['recap_name'] == 'second bridge')], values='archs', index='center', columns='year_month_out', aggfunc='sum', fill_value=0)

columns_date = recap_six_month.columns

import numpy as np

def mean_with_sigma_filter(data, sigma=2, axis=0):
    """
    Calculate the mean of the data after applying a sigma filter.
    
    Parameters:
        - data: pandas DataFrame or Series containing the data.
        - sigma: Value of sigma for the filter. Default is sigma=1.
        - axis: Axis along which to calculate the mean. Default is axis=0 (columns).
        
    Returns:
        - Series or DataFrame with the means calculated after applying the sigma filter.
    """
    # Calculate the mean and standard deviation of the data
    mean = data.mean(axis=axis)
    std_dev = data.std(axis=axis)
 
    # Calculate the limits for the sigma filter
    lower_limit = mean - (sigma * std_dev)
    upper_limit = mean + (sigma * std_dev)

    table_values= pd.concat([mean,std_dev,lower_limit,upper_limit], axis = 1)
    table_values.columns = ['mean','std_dev', 'lower_limit', 'upper_limit']

    filtered_data = data.apply(lambda x: x[(x >= lower_limit[x.name]) & (x <= upper_limit[x.name])], axis=axis) # Apply the sigma filter
    

    # Compare original data with filtered data to find months that didn't meet the condition
    months_not_meeting_condition = data[~data.isin(filtered_data)]
    
    non_nan_dates_per_center = months_not_meeting_condition.apply(lambda row: [str(col)  for col, val in row.items() if not pd.isnull(val)], axis=1)
    filtered_mean = filtered_data.mean(axis=axis) # Calculate the mean of the filtered values

    filtered_mean = pd.concat([table_values, filtered_mean, non_nan_dates_per_center], axis=1)
    filtered_mean.columns = ['mean','std_dev', 'lower_limit', 'upper_limit'] + ['means_', 'excluided months']
    return filtered_mean

means_ = mean_with_sigma_filter(recap_six_month, sigma=1, axis=1)
recap_six_month = pd.concat([recap_six_month,means_], axis=1)




excel_to_export.append({'name':'table second bridge analysis' , 'df':recap_six_month, 'index':True})

#ahora regreso al recap_counter
recap_counter['second bridge mean'] = recap_counter.index.map(recap_six_month['means_'])
calculate_percentaje(recap_counter, 'redo second bridge percent', 'second bridge 2rx' , 'second bridge mean')

excel_to_export.append({'name':'table percentajes' , 'df':recap_counter, 'index':True})


nuvia.create_multiple_worksheet(excel_to_export, name_excel='results/recap_files/recap_study_new_2.xlsx')

