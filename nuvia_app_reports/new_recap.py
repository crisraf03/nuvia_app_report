import pandas as pd 
import nuvia 

print('importing new_recap module ....')
#########################################
month_col = 'month_Out'


def count_number_of_orders_N6(recap_data):
    condition_n6 = recap_data['product class'].isin(['N6'])
    index_by_patient = recap_data[condition_n6].groupby(['center','patient'])['invoice'].count().reset_index()

    dic_patients_by_amount_of_products = {}

    for number_of_orders in index_by_patient['invoice'].unique():
        dic_patients_by_amount_of_products[number_of_orders] = index_by_patient[index_by_patient['invoice']== number_of_orders][['center', 'patient']]

        #ahora tomo los pacientes que tienen 1 rx en N6 para separarlos y hacerles el estudio de reasons

        condition_number_orders = recap_data['patient'].isin(dic_patients_by_amount_of_products[number_of_orders]['patient'])
        recap_data.loc[condition_n6 & condition_number_orders , 'number_N6_orders' ] = number_of_orders


def N6_RX_classification(recap_data):
    #ahora necesito una columna que separe los n6 1rx de los n6 redos +2rx
    recap_data.loc[recap_data['number_N6_orders'] == 1 ,'N6 RX' ] = 'N6 1RX'
    recap_data.loc[(recap_data['number_N6_orders'] != 1 ) & (recap_data['product class'] == 'N6'),'N6 RX' ] = 'N6 +2RX'

    #necesito una correcion en las ordenes redo, quiero saber cuales ordenes de los pacientes N6 +2RX no son redo si no que son su primerar orden, min(invoice)

    for each_patient in recap_data[recap_data['N6 RX'] == 'N6 +2RX']['patient'].unique():
        min_invoice = min(recap_data[ (recap_data['N6 RX'] == 'N6 +2RX') & (recap_data['patient'] == each_patient)]  ['invoice'])
        recap_data.loc  [ (recap_data['number_N6_orders'] != 1 ) & (recap_data['N6 RX'] == 'N6 +2RX') & (recap_data['invoice'] == min_invoice),  'N6 RX' ] = 'N6 1RX'

  

def get_last_month(recap_data , month) :
    cols_ = ['invoice','center', 'patient', 'product' , month_col, 'archs']
    N6_1rx_month = recap_data[(recap_data['N6 RX'] == 'N6 1RX') & (recap_data[month_col] == month[1]) & (recap_data[year_col[month_col]] == month[0]) ][cols_]
    N6_1rx_month['n6 reason'] = None

    #separate the redos created on the month 
    N6_redos_month = recap_data[(recap_data['N6 RX'] == 'N6 +2RX') & (recap_data[month_col] == month[1]) & (recap_data[year_col[month_col]] == month[0])][cols_]
    return{'N6' : N6_1rx_month  , 'N6_redo' : N6_redos_month}


def check_month_year(recap_data, months_):
    months_concat = ['-'.join(map(str, year_month_element)) for year_month_element in months_]
    print('year-months : ', months_concat)
    df_recap_data = recap_data[recap_data['year_month'].isin(months_concat)]
    return df_recap_data 


def create_N6_report(N6_redos_month, months_):
    #ahora calculo el promedio de ordenes n6 1rx de los ultimos 6 meses y la suma de los n6 2rx del mes
    recap_data = check_month_year(recap_data , months_)

    #necesito que me seleccione solamente los ultimos 6 meses
    n6_1rx_sum = recap_data[recap_data['number_N6_orders'] == 1].groupby('center')['archs'].sum() 
    n6_1rx_average = n6_1rx_sum / len(months_)

    N6_redos_month_sum = N6_redos_month.groupby('center')['archs'].sum()
    redo_percent = N6_redos_month_sum / n6_1rx_average

    report = pd.concat([n6_1rx_sum , n6_1rx_average , N6_redos_month_sum , redo_percent] , axis=1)
    report.columns = ['n6 1rx sum last 6 months', 'average n6 1 rx' , 'n6 redo month sum' , 'redo percent']
    return report



def recap_report(recap_data, months_, month_col):
    #recap report
    dic_N6_month = get_last_month(recap_data , months_[-1]) #utilizar la nuevacolumna
    # print(dic_N6_month)

    months_concat = ['-'.join(map(str, year_month_element)) for year_month_element in months_]
    print('year-months : ', months_concat)

    report = create_N6_report(dic_N6_month['N6_redo'] , months_)

    cols_to_delete =['time_in'	,'hour_in',	'time_out',	'hour_out',	'diff_days', 'size',	'checkIn',	'CheckOut']
    recap_data  = recap_data.drop(cols_to_delete , axis = 1)

    #export the report of the N6 products 
    writer = pd.ExcelWriter(f'N6_month_recap_{month_col}.xlsx', engine='xlsxwriter')
    report.to_excel(writer, sheet_name="report n6", index = True)
    recap_data[recap_data['product class']=='N6'].to_excel(writer, sheet_name="N6", index = False)

    dic_N6_month['N6'].to_excel(writer, sheet_name = 'N6 1rx month', index = False )
    dic_N6_month['N6_redo'].to_excel(writer, sheet_name = 'N6 redos more 1rx month', index = False )

    writer.close()
    return (dic_N6_month , report)


def update_recap_data(data_recap, month_col = 'month_In', date = (2024,3)):
    year_selector , month_selector = date[0], date[1]
    week_name = {'month_In' :'week'  , 'month_Out': 'week_finished'}
    name_sheet = f"data\{year_selector}\{month_selector}\{week_name[month_col]}_.xlsx"
    df_weeks = pd.read_excel(name_sheet)
    data_recap[~data_recap['invoice'].isin(df_weeks['invoice'])]
    data_recap = pd.concat([data_recap, df_weeks], axis=0)
    return data_recap
 

def clean_recap_data_(month_col, overtibar = True, drop= True, month_to_exclude = ['2024-4']):
    excel_name = f'data/recap/recap_data_{dic_d[month_col]}.xlsx'
    recap_data = pd.read_excel(excel_name) 
    # recap_data = update_recap_data(recap_data, month_col = month_col, date=(2024,3))

    recap_data = nuvia.create_caracteristics(recap_data, drop=drop, removable = True)
    recap_data['year_month'] = recap_data[year_col[month_col]].astype(str) + '-' + recap_data[month_col].astype(str)

    #exclude some months
    condition_exclude = recap_data['year_month'].isin(month_to_exclude)
    recap_data_excluided = recap_data[condition_exclude]
    recap_data = recap_data[~recap_data['invoice'].isin(recap_data_excluided['invoice'])]
    if overtibar == False:
        over_tibar_products = [x for x in set(recap_data['product']) if 'Over Ti-Bar' in x]
        recap_data.loc[recap_data['product'].isin(over_tibar_products) , 'product class'] = 'N6 overtibar'

    count_number_of_orders_N6(recap_data)
    N6_RX_classification(recap_data)
    return recap_data



##############################################################################################


def create_N6_in(recap_data):
    N6_1rx_in = recap_data[recap_data['N6 RX'] == 'N6 1RX'].groupby([year_col[month_col] , month_col,'center'])['archs'].sum()
    N6_2rx_in = recap_data[recap_data['N6 RX'] == 'N6 +2RX'].groupby([year_col[month_col], month_col,'center'])['archs'].sum()

    N6_1rx_in_patient = recap_data[recap_data['N6 RX'] == 'N6 1RX'].groupby([year_col[month_col] , month_col,'center'])['patient'].count()
    N6_2rx_in_patient = recap_data[recap_data['N6 RX'] == 'N6 +2RX'].groupby([year_col[month_col], month_col,'center'])['patient'].count()

    N6_in = pd.concat([N6_1rx_in , N6_2rx_in, N6_1rx_in_patient , N6_2rx_in_patient], axis=1).reset_index()
    N6_in.columns = [ 'year' ,'month', 'center' ,'N6 1RX in' , 'N6 +2RX in','N6 1RX in patient' , 'N6 +2RX in patient']
    N6_in = N6_in.set_index(['year' ,'month', 'center'])
    return (recap_data , N6_in)


def report_counter_of_arches_for_months(recap_data , N6_in):
    n2 = count_N2_arches(recap_data , month_col)

    condition_n3 = recap_data['product class'].isin(['N3'])
    condition_redo = recap_data['redo type'].isin(['REDO' , 'REMAKE'])

    n3_surgery = recap_data[condition_n3 & ~condition_redo ].groupby([year_col[month_col], month_col, 'center'])['archs'].sum()
    n3_redo = recap_data[condition_n3 & condition_redo].groupby([year_col[month_col], month_col, 'center'])['archs'].sum()

    condition_reline = recap_data['material'] == 'Reline'
    reline = recap_data[condition_reline].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()

    condition_dummy = recap_data['material'] == 'Dummy'
    dummy = recap_data[condition_dummy].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()

    condition_removable = recap_data['material'] == 'Removable'
    condition_mixed_material = recap_data['mixed_material'].isin(['24Z', 'G-CAM'])
    
    removable = recap_data[condition_removable & ~condition_mixed_material].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()
    
    removable = recap_data[condition_removable & ~condition_mixed_material].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()
    removable_with_arch = recap_data[condition_removable & condition_mixed_material].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()

    condition_nightguard = recap_data['material'] == 'Night guard'
    nightguard = recap_data[condition_nightguard].groupby([year_col[month_col] ,month_col, 'center'])['archs'].sum()

    n6_1rx = recap_data[(recap_data['N6 RX']  == 'N6 1RX')].groupby([year_col[month_col],month_col, 'center'])['archs'].sum()
    n6_2rx = recap_data[(recap_data['N6 RX']  == 'N6 +2RX')].groupby([year_col[month_col],month_col, 'center'])['archs'].sum()

    n6_1rx_patient = recap_data[(recap_data['N6 RX']  == 'N6 1RX')].groupby([year_col[month_col],month_col, 'center'])['patient'].count()
    n6_2rx_patient = recap_data[(recap_data['N6 RX']  == 'N6 +2RX')].groupby([year_col[month_col],month_col, 'center'])['patient'].count()

    # n6_overtibar = recap_data[(recap_data['']  == 'N6 +2RX')].groupby([year_col[month_col],month_col, 'center'])['archs'].sum()

    report_months = pd.concat([n3_surgery, n3_redo, reline, n6_1rx, n6_2rx, dummy, removable,removable_with_arch, nightguard, n6_1rx_patient, n6_2rx_patient], axis=1).reset_index()

    report_months.columns  = ['year' ,'month', 'center', 'N3 surgery' , 'N3 redo' , 'Reline' , 'N6 1RX out' , 'N6 +2RX out', 'Dummy', 'Removable dentures','dentures with arch', 'Night guard', 'N6 1RX out patient' , 'N6 +2RX out patient']
    report_months['year'] = report_months['year'].astype(int)
    report_months = report_months.set_index(['year' ,'month', 'center'])
    
    report_months = pd.concat([report_months, N6_in ,n2] ,axis=1)
    return report_months



def count_N2_arches(recap_data, month_col):
    n2 = []
    for material_ in ['Demodenture' , 'Single 24Z Processing' , 'Wax Rims']:
        condition_material = recap_data['material'] == material_
        n2_material = recap_data[condition_material].groupby([year_col[month_col], month_col, 'center'])['archs'].sum()
        n2.append(n2_material)
    n2 = pd.concat(n2, axis=1).reset_index()
    n2.columns = ['year' ,'month', 'center' , 'Demodenture' , 'Single 24Z Processing' , 'Wax Rims']
    n2['year'] = n2['year'].astype(int)
    n2 = n2.set_index(['year' ,'month', 'center'])
    return n2


def clean_data_(recap):
    condition_PC = recap['material'].isin(['24Z','G-CAM', 'Reline'])
    cols_to_export = ['invoice', 'patient', 'center', 'restorer' , 'archs', 'product' , 'product class' , 'month_In' , 'month_Out' , 'year_In' , 'year_Out' ,'material', 'redo type' , 'number_N6_orders' , 'N6 RX']
    return recap[condition_PC][cols_to_export]


###############################################################################################################

def make_the_report():
    _overtibar_boolean_= True
    month_col = 'month_In'
    recap_data = clean_recap_data_(month_col, overtibar=_overtibar_boolean_)
    recap_data_in, N6_in = create_N6_in(recap_data)

    # now i need to get the way of reproduce the second report
    month_col = 'month_Out'
    recap_data = clean_recap_data_(month_col, overtibar=_overtibar_boolean_)

    all_months_report_out = report_counter_of_arches_for_months(recap_data , N6_in)
    return (all_months_report_out , recap_data_in , recap_data)


def export_the_report(export = False):
    all_months_report_out , recap_data_in , recap_data = make_the_report()

    if export == True: 
        writer = pd.ExcelWriter('report_months.xlsx', engine='xlsxwriter')
        all_months_report_out.reset_index().to_excel(writer, sheet_name = 'report months', index = False)
        clean_data_(recap_data_in).to_excel(writer, sheet_name = 'recap data in', index = False)
        clean_data_(recap_data).to_excel(writer, sheet_name = 'recap data out', index = False)
        recap_data_in.to_excel(writer, sheet_name = 'all columns recap data in', index = False)
        recap_data.to_excel(writer, sheet_name = 'all columns recap data out', index = False)
        writer.close()
        print('Look for your report on the field...')
    recap_information = {'month_In' : recap_data_in, 'month_Out': recap_data}
    return recap_information

dic_d = {'month_In' : 'opened' , 'month_Out': 'ended' }
year_col = {'month_In': 'year_In' , 'month_Out': 'year_Out'}
all_months_ = [(2023, 9), (2023, 10),(2023, 11),(2023, 12),(2024, 1),(2024, 2),(2024, 3)]
months_ = all_months_


recap_information = export_the_report(export=False)

#Toma da la data in, separala en N3 redo y N3 surger. Busca en los redos el invoice y checkout de surgery, realiza delta time, clasifica las N3 orders.
month_col = 'month_In'
data_in = recap_information[month_col]

condition_n3 = data_in['product class'].isin(['N3'])
cols_to_study = ['patient','invoice', 'checkIn', 'CheckOut', 'product', 'archs', 'center', 'arch type']
n3_surgery = data_in[condition_n3 &(data_in['redo type'].isin(['SURGERY']))][cols_to_study].drop_duplicates()

#################################################################################################################################

condition_fixed_arch = (data_in['mixed_material'].isin(['24Z', 'G-CAM'])) &  (data_in['redo type'] != 'REDO REMOVABLE')
n3_fixed_arch = data_in[condition_fixed_arch]

#tomo todas las ordenes de los pacientes que han tenido un fixed arch
patients_fixed_arch = data_in[data_in['patient'].isin(n3_fixed_arch['patient'].unique())][['invoice', 'patient','product','archs','month_In', 'month_Out','product class','material','mixed_material', 'arch type', 'redo type']]

#me quedo solamente con las ordenes que sean N3 y que no sean removable denture
patients_fixed_arch = patients_fixed_arch[(patients_fixed_arch['product class'].isin(['N3','N3 removable'])) & (patients_fixed_arch['mixed_material']!= 'DENTURE')]


# i want to analyse the single arch products
surgeries = n3_surgery[~n3_surgery['patient'].isin(patients_fixed_arch['patient'])][['invoice', 'patient', 'product','archs', 'arch type']].drop_duplicates()

surgeries['count_products'] = surgeries['patient'].map(n3_surgery.groupby('patient')['product'].count())
surgeries['list_products'] = surgeries['patient'].map(n3_surgery.groupby('patient')['product'].apply(list))

#revisar first arch
surgeries['min_invoice'] = surgeries['patient'].map(n3_surgery.groupby('patient')['invoice'].min())
surgeries.loc[surgeries['min_invoice'] == surgeries['invoice'] , 'min_invoice'] = 'first arch'

#revisar los redo first arch  
surgeries.loc[surgeries['min_invoice']!= 'first arch','min_invoice'] = surgeries[surgeries['min_invoice']!= 'first arch']['patient'].map( n3_surgery[~n3_surgery['invoice'].isin(surgeries[surgeries['min_invoice'] != 'first arch']['invoice'])].groupby('patient')['invoice'].min())

surgeries.loc[surgeries['min_invoice'].isin(surgeries['invoice']), 'min_invoice'] = 'redo first arch'

condition_patient_single_first = (surgeries['min_invoice']=='first arch') & (surgeries['arch type']=='Single')
patient_single = surgeries[condition_patient_single_first]['patient']

surgeries.loc[surgeries['patient'].isin(patient_single), 'previous product'] = 'first product single arch'


#termino de definir la clasificacion de las ordenes en la columnas min_invoice
condition_single_redo = (surgeries['patient'].isin(patient_single)) & (surgeries['min_invoice']=='redo first arch') & (surgeries['arch type']=='Single')
condition_full_redo = (surgeries['patient'].isin(patient_single)) & (surgeries['min_invoice']=='redo first arch') & (surgeries['arch type']=='Full Mouth')

surgeries.loc[condition_single_redo, 'min_invoice'] = 'redo first arch'
surgeries.loc[condition_full_redo, 'min_invoice'] = 'mixed arch'


#creo dos columnas nuevas  para separar los arcos entre surgery y redos
map_first_arches = surgeries[surgeries['min_invoice'].isin(['first arch'])][['invoice', 'archs']].set_index('invoice')
map_redo_first_arches = surgeries[surgeries['min_invoice'].isin(['redo first arch'])][['invoice', 'archs']].set_index('invoice')

surgeries['surgery arches'] = surgeries['invoice'].map(map_first_arches['archs'])
surgeries['redo arches'] = surgeries['invoice'].map(map_redo_first_arches['archs'])

#agrego los arcos mixed usnado loc 

surgeries.loc[surgeries['min_invoice'].isin(['mixed arch']), 'surgery arches'] = 1 
surgeries.loc[surgeries['min_invoice'].isin(['mixed arch']), 'redo arches'] = 1 

# surgeries.to_excel('n3_surgery.xlsx', index = False)

#################################################################################################################################

#NEED TO ADD THE FIX ARCH AS SINGLE ARCHES 
count_products = patients_fixed_arch.groupby('patient')['product'].count()
list_products = patients_fixed_arch.groupby('patient')['product'].apply(list)

patients_fixed_arch['count_products'] = patients_fixed_arch['patient'].map(count_products)
patients_fixed_arch['list_products'] = patients_fixed_arch['patient'].map(list_products)


#take the first order
patients_fixed_arch['min_invoice'] = patients_fixed_arch['patient'].map(patients_fixed_arch.groupby('patient')['invoice'].min())
patients_fixed_arch.loc[patients_fixed_arch['min_invoice'] == patients_fixed_arch['invoice'] , 'min_invoice'] = 'first arch'

condition_second_product_fixed = (patients_fixed_arch['count_products'] == 2) & (~patients_fixed_arch['min_invoice'].isin(['first arch']))
patients_fixed_arch.loc[condition_second_product_fixed, 'min_invoice'] = 'second arch'

condition_three_product_fixed = (patients_fixed_arch['count_products'] == 3) & (~patients_fixed_arch['min_invoice'].isin(['first arch']))
three_products_second_order = patients_fixed_arch[condition_three_product_fixed].groupby('patient')['invoice'].min()

patients_fixed_arch.loc[patients_fixed_arch['invoice'].isin(three_products_second_order), 'min_invoice'] = 'second arch'
patients_fixed_arch.loc[~patients_fixed_arch['min_invoice'].isin(['second arch', 'first arch']), 'min_invoice'] = 'three arch'

condition_first_order_n3_full = (patients_fixed_arch['product class'] == 'N3') & (patients_fixed_arch['min_invoice'].isin(['first arch'])) & (patients_fixed_arch['arch type'] == 'Full Mouth') 
condition_first_order_n3_single = (patients_fixed_arch['product class'] == 'N3') & (patients_fixed_arch['min_invoice'].isin(['first arch'])) & (patients_fixed_arch['arch type'] == 'Single') 
condition_first_order_n3_fixed_arch = (patients_fixed_arch['product class'] == 'N3 removable') & (patients_fixed_arch['min_invoice'].isin(['first arch'])) 

patients_fixed_arch.loc[(patients_fixed_arch['min_invoice'].isin(['second arch'])) & (patients_fixed_arch['patient'].isin(patients_fixed_arch[condition_first_order_n3_full]['patient'])), 'previous product'] = 'first product Full mouth'
patients_fixed_arch.loc[(patients_fixed_arch['min_invoice'].isin(['second arch'])) & (patients_fixed_arch['patient'].isin(patients_fixed_arch[condition_first_order_n3_fixed_arch]['patient'])), 'previous product'] = 'first product fixed arch'

#definir los arcos en cada mixed arches and made the corrections
patients_fixed_arch.loc[(patients_fixed_arch['previous product'].isin(['first product fixed arch']) &  (patients_fixed_arch['product class'].isin(['N3'])) & (patients_fixed_arch['arch type'].isin(['Full Mouth']))), 'min_invoice'] = 'mixed arch'
patients_fixed_arch.loc[(patients_fixed_arch['previous product'].isin(['first product fixed arch']) &  (patients_fixed_arch['product class'].isin(['N3'])) & (patients_fixed_arch['arch type'].isin(['Single'])) & (patients_fixed_arch['redo type'].isin(['SURGERY']))  ), 'min_invoice'] = 'first arch'

#defino los valores de nuevas columnas para contar los arcos entre surgery y redos 

map_first_arches_fixed = patients_fixed_arch[patients_fixed_arch['min_invoice'].isin(['first arch'])][['invoice', 'archs']].set_index('invoice') 
map_redo_first_arches_fixed = patients_fixed_arch[patients_fixed_arch['min_invoice'].isin(['second arch', 'three arch'])][['invoice', 'archs']].set_index('invoice') 


patients_fixed_arch['surgery arches'] = patients_fixed_arch['invoice'].map(map_first_arches_fixed['archs'])
patients_fixed_arch['redo arches'] = patients_fixed_arch['invoice'].map(map_redo_first_arches_fixed['archs'])


#uso loc para definir los arcos de los productos mixed
patients_fixed_arch.loc[patients_fixed_arch['min_invoice'].isin(['mixed arch']) , 'surgery arches'] = 1
patients_fixed_arch.loc[patients_fixed_arch['min_invoice'].isin(['mixed arch']) , 'redo arches'] = 1
# patients_fixed_arch.to_excel('patients_fixed_arches.xlsx', index=False)

mixed_surgery_orders = pd.concat([surgeries, patients_fixed_arch[list(surgeries.columns)]], axis= 0) 

# en este punto buscare definir un redo recap column en donde classifique los productos N3 entre first arch or redo arch
mixed_surgery_orders.loc[mixed_surgery_orders['min_invoice'].isin(['first arch']) , 'redo recap'] = 'surgery recap'
mixed_surgery_orders.loc[~mixed_surgery_orders['min_invoice'].isin(['first arch']) , 'redo recap'] = 'redo recap'

#ahora agrego este estudio a las columnas del recap que contienen todos los redos y redo removable
# mixed_surgery_orders.to_excel('mixed_surgery_orders.xlsx')

cols_to_mixed_surgery = ['count_products', 'min_invoice','previous product', 'surgery arches', 'redo arches', 'redo recap']
mixed_surgery_orders = mixed_surgery_orders[['invoice'] + cols_to_mixed_surgery]

data_in = pd.merge(data_in , mixed_surgery_orders , on= 'invoice', how= 'outer' )

#agrego los productos n3 redo a los redo recap
condition_redo_n3_not_considered = (data_in['product class'].isin(['N3', 'N3 removable']) ) & (data_in['redo type'].isin(['REDO', 'REDO REMOVABLE']) ) & (~data_in['invoice'].isin(mixed_surgery_orders['invoice']))
data_in.loc[condition_redo_n3_not_considered , 'redo recap'] = 'redo recap'


#hacemos map de los arcos redos sobre la  columna redo arches
data_in['redo arches'] = data_in['invoice'].map(data_in[condition_redo_n3_not_considered][['invoice', 'archs']].set_index('invoice')['archs'])


#################################################################################################################################

#en este punto tomo todos los productos recap product class que son redo recap y los linkeo con sus surgery recap, calculo la diferencia entre su redo-surgery.  Nota: si existen mas de 2 redos para un paciente tomare la diferencia con el dia se la first arch surgery y asi clasificarla dentro de los redo recap first arch
cols_match_orders = cols_to_study + cols_to_mixed_surgery
n3_surgery_recap = data_in[data_in['redo recap'] == 'surgery recap'][cols_match_orders]
n3_redo_recap = data_in[data_in['redo recap'] =='redo recap'][cols_match_orders]

n3_match_orders = pd.merge(n3_redo_recap, n3_surgery_recap, on = 'patient', how='left', suffixes=('_redo', '_surgery'))

for col_date_name in ['checkIn_redo', 'CheckOut_redo', 'checkIn_surgery', 'CheckOut_surgery']:
    n3_match_orders[col_date_name] = pd.to_datetime(n3_match_orders[col_date_name], format='ISO8601')

n3_match_orders['diff_time'] = n3_match_orders['checkIn_redo'] - n3_match_orders['CheckOut_surgery']
n3_match_orders['diff_arches'] = n3_match_orders['archs_redo'] - n3_match_orders['archs_surgery']

n3_match_orders['diff_time (days)'] = n3_match_orders['diff_time'].dt.days
n3_match_orders['diff_time (months)'] = round(n3_match_orders['diff_time (days)'] /30 )

recap_class_redo_first_arch = {0: 'redo with in a month'  ,1:'redo with in a month'   , 2 : 'redo after one month'  , 3: 'redo after one month' }

n3_match_orders.loc[n3_match_orders['diff_time (months)'].isin([-1,0,1]),'recap class'] = 'redo with in a month'
n3_match_orders.loc[n3_match_orders['diff_time (months)'].isin([2,3]),'recap class'] = 'redo after one month'
n3_match_orders.loc[~n3_match_orders['diff_time (months)'].isin([0,1,2,3]),'recap class'] = 'second arch'


condition_surgery_not_found = (n3_match_orders['redo recap_redo'].isin(['redo recap']) ) & (n3_match_orders['invoice_surgery'].isna())

n3_match_orders.loc[condition_surgery_not_found, 'recap class'] = 'second arch' #existe tambien redo first arch with in a month and after one month
# n3_match_orders.to_excel('n3_match_orders.xlsx', index= True)


#################################################################################################################################
data_in['recap class'] = data_in['invoice'].map( n3_match_orders[['invoice_redo', 'recap class']].set_index('invoice_redo')['recap class'] ) 
data_in.loc[data_in['redo recap'].isin(['surgery recap']), 'recap class'] = 'first arch'

repetead_arches_orders = data_in['product class'].isin(['N6','N6 overtibar'])
data_in.loc[repetead_arches_orders, 'recap class'] = 'second arch to study'

condition_repetead_second_arches = data_in['recap class'].isin(['second arch', 'second arch to study'])
count_repetead_second_arches = data_in[condition_repetead_second_arches].groupby('patient')['invoice'].count()

data_in['count second arch products'] = data_in[condition_repetead_second_arches]['patient'].map(count_repetead_second_arches)
select_second_arch = data_in[condition_repetead_second_arches].groupby('patient')['invoice'].min()


data_in.loc[(condition_repetead_second_arches) & (~data_in['invoice'].isin(select_second_arch)), 'recap class'] = 'three or more RX'


data_in.to_excel('data_in_para_mirarla.xlsx', index= False)


### ahora importo las columnas de redo reason, responsable party, redo cause, etc junto con su invoice y se las agrego al recap_out

#importar  the data where the redo reason is in
year_selector = 2024
name_excel, sheet_name_ = f"data\{year_selector}\Redo_cases_studied.xlsx" , 'march'
cols_redo_information = ['redo cause', 'responsable party','redo form']
redo_reason_data = pd.read_excel(name_excel , sheet_name=sheet_name_) [['invoice'] + cols_redo_information]

print(redo_reason_data.head(4))




cols_not_to_drop = ['invoice', 'patient', 'restorer', 'center', 'archs', 'product', 'date_In', 'date_Out', 'month_In', 'month_Out', 'product class', 'material',  'arch type', 'redo type', 'year_In',  'year_Out', 'responsable party_x', 'mixed_material', 'year_month', 'number_N6_orders', 'N6 RX','count_products', 'min_invoice', 'previous product', 'surgery arches', 'redo arches', 'redo recap', 'recap class', 'count second arch products', 'redo cause',    'responsable party_y', 'redo form']
data_in = pd.merge(data_in , redo_reason_data, on='invoice', how='left')[cols_not_to_drop]
repetead_arches = data_in[~data_in['recap class'].isna()]
print(data_in[data_in['recap class'].isna()]['product class'].unique())
repetead_arches.to_excel('repetead_arches_in.xlsx', index = False)





#agrego la recap class y los reason redo. Tambien la exporto a un excel para ir llenandolo.
month_col = 'month_Out'
data_out = recap_information[month_col]

data_out.to_excel('data_out_to_look.xlsx', index = False)
data_out['recap class'] = data_out['invoice'].map(data_in[['invoice', 'recap class']].set_index('invoice')['recap class'])

cols_in_to_out = ['invoice', 'count_products', 'min_invoice', 'previous product', 'surgery arches', 'redo arches', 'redo recap', 'count second arch products']
data_out = pd.merge(data_out , data_in[cols_in_to_out] , on='invoice' , how='left')

data_out = pd.merge(data_out , redo_reason_data, on='invoice', how='left')[cols_not_to_drop]
repetead_arches = data_out[~data_out['recap class'].isna()]

print(repetead_arches['year_Out'].unique() , repetead_arches['month_Out'].unique())

condition_dates = (repetead_arches['year_Out'] == 2024) & (repetead_arches['month_Out'] == 3)
repetead_arches[condition_dates].to_excel('repetead_arches.xlsx', index = False)

#calculo los números respectivos de cada recap class por sus centros y con sus product reason

# data_classificated_by_recap_data = {}
# for recap_data_value in data_out['recap data'].unique():
#     data_ = data_out[data_out['recap data']== recap_data_value]
#     data_classificated_by_recap_data[recap_data_value] = data_




#Finalmente exporto el recap in and out junto con sus numeros





