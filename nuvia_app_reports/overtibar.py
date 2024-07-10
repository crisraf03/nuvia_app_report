
import pandas as pd
import new_recap

'''REPORTE OVERTIBAR MIMA'''


dic_d = {'month_In' : 'opened' , 'month_Out': 'ended' }
year_col = {'month_In': 'year_In' , 'month_Out': 'year_Out'}

month_col = 'month_Out'
df = new_recap.clean_recap_data_(month_col, overtibar=False)


cols_iwant = ['invoice', 'patient', 'restorer', 'center', 'archs', 'product', 'status', 'date_In',
       'date_Out', 'product class', 'material',  'redo type', 'year_month']

df = df[cols_iwant]

df.loc[df['product'].str.contains('Rx3'), 'material'] = 'demo (Rx3)'
df.loc[df['product'].str.contains('Rx7'), 'material'] = 'mc (Rx7)'
aesthetic_dummy = [x for x in set(df[df['material'] == 'Dummy']['product']) if 'Aesthetic' in x]
df.loc[df['product'].isin(aesthetic_dummy) , 'material'] = 'aesthetic dummy'




df.loc[df['product class'].isin(['N6']), 'overtibar_order'] = 1
df.loc[df['material'].isin(['mc (Rx7)']), 'overtibar_order'] = 1


#averiguar los dummy y screw que le hagan falta su N6 overtibar
condition_material = df['material'].isin(['aesthetic dummy'])
condition_overtibar = df['product class'].isin(['N6 overtibar'])
df.loc[condition_material, 'overtibar_order'] = 1
df.loc[condition_overtibar, 'overtibar_order'] = 1
condition_overtibar_report = df['overtibar_order'] == 1


patients_material_ = [patient for patient in df[condition_material]['patient'].unique()]
condition_patient_material = df['patient'].isin(patients_material_)

patients_overtibar_ = [patient for patient in df[condition_overtibar]['patient'].unique()]


condition_mc = df['product class'].isin(['N6'])
patients_mc = [patient for patient in df[condition_mc]['patient'].unique()]

condition_patient_mc = df['patient'].isin(patients_overtibar_)
df.loc[condition_material & condition_patient_mc , 'did_it_on_material_change'] = 1

condition_patient_overtibar = df['patient'].isin(patients_overtibar_ + patients_mc)
df.loc[condition_material & ~condition_patient_overtibar  , 'waiting_overtibar'] = 1

df.loc[condition_patient_material & condition_overtibar_report, 'not_overtibar'] = df[condition_patient_material & condition_overtibar_report][['did_it_on_material_change', 'waiting_overtibar']].sum(axis=1)



#hacer el conteo

overtibar_count = df[df['product class'] == 'N6 overtibar'].groupby(['center', 'year_month'])['archs'].sum()
aesthetic_dummy_count = df[df['material'] == 'aesthetic dummy'].groupby(['center', 'year_month'])['archs'].sum()
did_it_on_mc = df[df['did_it_on_material_change'] == 1].groupby(['center', 'year_month'])['archs'].sum()
waiting_overtibar = df[df['waiting_overtibar'] == 1].groupby(['center', 'year_month'])['archs'].sum()

report_mima = pd.concat([overtibar_count , aesthetic_dummy_count , did_it_on_mc , waiting_overtibar], axis = 1)
report_mima = report_mima.reset_index()
report_mima.columns = ['center' , 'year_month' , 'overtibar' , 'aesthetic dummy' , 'did it on mc' , 'waiting overtibar']

cols_fillna = ['aesthetic dummy' , 'did it on mc' , 'waiting overtibar']
report_mima[cols_fillna] = report_mima[cols_fillna].fillna(0)
report_mima['did it on overtibar'] = report_mima['aesthetic dummy'] - report_mima['did it on mc'] - report_mima['waiting overtibar']

dallas = report_mima[report_mima['center'] == 'DALLAS OFFICE']
dallas_orders = df[df['center'] == 'DALLAS OFFICE']


#overtibar in process
month_col = 'month_In'
df_open = new_recap.clean_recap_data_(month_col, overtibar=False)
df_open = df_open[cols_iwant]




writer = pd.ExcelWriter('_mima_report.xlsx', engine='xlsxwriter')
report_mima.to_excel(writer, sheet_name='mimas report', index = False )
df[(df['overtibar_order'] == 1) & (df['product class'] != 'N6' )].to_excel(writer, sheet_name ='orders', index = False)
dallas.to_excel(writer, sheet_name ='dallas', index = False)
dallas_orders[(dallas_orders['overtibar_order'] == 1) & (dallas_orders['product class'] != 'N6' )].to_excel(writer, sheet_name ='dallas orders', index = False)
df_open[(df_open['product class'] == 'N6 overtibar') & (~df_open['status'].isin(['Post Delivery Record', 'Lab Check Out', 'Discharge Form' ]))].to_excel(writer,'open_overtibar_orders', index = False)
writer.close()

 























