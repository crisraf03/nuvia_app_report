'''On this script there are the data transformation for the count of the pmma/gcam patients waiting for 24z material change.'''

'''
As a result it export the excel 'waiting_for_24.xlsx' where you fill find 4 sheets:
1. pmma_cases_waiting : This is the count for the pmma patient´s arches waiting for 24z material change by center, date of order creation and date of medition of this quantities.
2. pmma_patients_list: this sheet have the orders of the pmma patients that are waiting for 24z material change
3. regresion_metrics: on this sheet you will find a linear regresion of the behaivor of the pmma patient´s arches for each center as well as the root for extrapolation of this model, that means the month of where the arches will go down to 0 and the rate that each center should be having if they want to raise 0 by the end of the year.
4.waiting_for_24_monthly_by_week : This is a weekly report of this patients by date, center, and material
Also  on this excel there are the list of each patient by center on differents sheets'''

import nuvia 
import pandas as pd
#This script should be count the arches by center and patient´s names

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Desactivar los warnings temporales
with warnings.catch_warnings():
  warnings.simplefilter("ignore")


year = 2023
month = 12
month_to_add_at_the_report = month
max_date_of_the_report = f"{year}-{month}-31"

month_that_should_by_finished_default = 15



name_excel = f"data\checkIn_all.xlsx"
data_ = pd.read_excel(name_excel) #I want to add the information of the most recent month

#select only the orders that not appear on the data_ that have all the orders and add it to this variable data_
data_to_add = pd.read_excel(f"data\{year}\{month_to_add_at_the_report}\week_.xlsx")
data_to_add = data_to_add [~data_to_add['invoice'].isin(data_['invoice'])]

data_ = pd.concat([data_ , data_to_add], axis = 0)
data_ = nuvia.create_caracteristics(data_) #create caracteristic and the month_year column to all the orders 
check_date_column = 'checkIn' #tranform the check_date_column into a datetime 
data_[check_date_column] = pd.to_datetime(data_[check_date_column], format='ISO8601')

month_of_each_year = {'2024' : [ '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11'],
    '2023' :  ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'] , 
    '2022' :  [ '02', '03', '04', '05', '06', '07', '08', '09', '10', '11' , '12']}

waiting_for_24z = []

for year_of_medition in [str(year)] : 
    for month in month_of_each_year[year_of_medition]:

        if month != month_of_each_year[year_of_medition][-1]:
            max_date = '{}-{}-01'.format(year_of_medition , month)

        if month == month_of_each_year[year_of_medition][-1] :
            max_date = max_date_of_the_report

        filter_month_condition = data_[check_date_column] < max_date
        data_of_medition = data_[filter_month_condition]

        x, pmma_df = nuvia.count_GCAM_waiting_to_24Z(data_of_medition , pmma_list=True , columns_to_group= ['year_In', 'month_In_B', 'center'])
        x.loc[:,'month_of_medition'] = int(month)
        x.loc[:, 'year_of_medition'] = int(year_of_medition)
        x['year_In'] = x['year_In'].astype('int')

        waiting_for_24z.append(x)
        if year_of_medition == str(year) and month == '12':
            pmma_df_to_export = pmma_df

df_waiting_for_24z = pd.concat(waiting_for_24z , axis=0)
dic_pmma_by_center = {} #export by center - Create a dicionary and the i'll add to the writer variable

for center_ in pmma_df_to_export['center']:
    dic_pmma_by_center[center_]  = pmma_df_to_export[pmma_df_to_export['center'] == center_]

cols_pmma_df_to_export = ['invoice', 'patient', 'restorer', 'center', 'archs', 'checkIn', 'CheckOut', 'amount',
'product', 'month_In', 'month_Out', 'diff_days', 'region', 'product class', 'material',
'arch type', 'redo type', 'diff_hour', 'delivery_on_time', 'month_In_B', 'year_In', 'month_Out_B', 'year_Out']

pmma_df_to_export = pmma_df_to_export[cols_pmma_df_to_export]



####################################################################################################################################################


# Calculation of the linear regresions

from sklearn.linear_model import LinearRegression
import numpy as np 

def determinate_linear_regresion(x, y):
    model = LinearRegression()
    if len(x) == 0:
        print("No hay muestras para ajustar el modelo de regresión.")
        return [None, None, None]

    # Verify if x is an instance of pd.Series and convert to a matriz 2D if it´s needed
    if isinstance(x, pd.Series):
        x = x.values.reshape(-1, 1)
    elif isinstance(x, (int, float)):  # Additional comprobation in case it´s a scalar variable
        x = np.array(x).reshape(-1, 1)

    model.fit(x,y)
    slope = model.coef_[0]
    intercept = model.intercept_
    r_squared = model.score(x, y)
    return [slope , intercept , r_squared]


# Filter by center, and I want to perform the regression between month_of_medition (x) and the sum of arches (y).
regresion_metrics = {}

material_filter = df_waiting_for_24z['material'] == 'PMMA'
month_of_medition_filter = df_waiting_for_24z['month_of_medition'] > 5

for center_ in df_waiting_for_24z['center'].unique():
    center_filter = df_waiting_for_24z['center'] == center_
    data_center = df_waiting_for_24z[material_filter & center_filter & month_of_medition_filter]
    A =  data_center.groupby('month_of_medition')['arches'].sum().reset_index()
    regresion_metric_by_center  =  determinate_linear_regresion( A['month_of_medition'] , A['arches'])
    regresion_metrics[center_]  = regresion_metric_by_center

regresion_metrics = pd.DataFrame(regresion_metrics).T 
regresion_metrics.columns = ['rate of change' , 'arches at the start of the year' , 'r2']


####################################################################################################################################################

#Now i want to calculate the roots of the linear regresions
def division(row):
    if row[0] is not None and row[1] is not None and row[1] != 0:
        return row[0] / row[1]
    else:
        return None
    
regresion_metrics.loc[:,'x_intercept'] = - regresion_metrics[['arches at the start of the year' , 'rate of change' ]].apply(division, axis=1)
regresion_metrics.loc[:,'year'] = year
regresion_metrics.loc[:, 'month']  = 0

#I want to know the month and year when each center will finish the pmma arches at the rate they are going.
def update_year_month(row):
    plus_year, plus_month = divmod(row['x_intercept'], 12)

    # Verificar si plus_year es un valor válido antes de convertirlo a entero
    if not pd.isna(plus_year):
        row['year'] += int(plus_year)
    else:
        # Si plus_year es NaN, puedes manejarlo de alguna manera, por ejemplo, asignar un valor predeterminado
        row['year'] = 0  # O cualquier valor que desees asignar en este caso

    # Verificar si plus_month es un valor válido antes de convertirlo a entero
    if not pd.isna(plus_month):
        row['month'] += int(plus_month)
    else:
        # Si plus_month es NaN, puedes manejarlo de alguna manera, por ejemplo, asignar un valor predeterminado
        row['month'] = 0  # O cualquier valor que desees asignar en este caso
    return row

regresion_metrics = regresion_metrics.apply(update_year_month, axis=1)



####################################################################################################################################################

#Extrapolations 

# Now i want to calculate the rate that each center should have if They should finished all the patients on the last 3 Months

id_month = month_to_add_at_the_report

month_that_should_by_finished = int(input("At which on the pmma cases should be finished? '1' means 2023-01 so 15 should mean 2024-03 :")) # 1 means 2023-01-01

if not month_that_should_by_finished :
    month_that_should_by_finished = month_that_should_by_finished_default


material_filter = df_waiting_for_24z['material'] == 'PMMA'
month_of_medition_filter = df_waiting_for_24z['month_of_medition'] == id_month

# Filtrar datos y convertir 'month_of_medition' a tipo numérico si es necesario
filtered_data = df_waiting_for_24z[material_filter & month_of_medition_filter]

# Calcular la tasa objetivo por centro
rate_goal = (0 - filtered_data.groupby('center')['arches'].sum()) / (month_that_should_by_finished - id_month)

# Crear un DataFrame a partir del resultado y transponer
rate_goal_df = pd.DataFrame({'rate_goal': rate_goal})

regresion_metrics = pd.concat([regresion_metrics, rate_goal], axis=1)

####################################################################################################################################################

"""Weekly counter waiting for 24z"""

weeks_ =[ ['2023-09-29', '2023-10-05'] , ['2023-10-06', '2023-10-12'], ['2023-10-13', '2023-10-19'],  ['2023-10-20', '2023-10-26'], ['2023-10-27', '2023-11-02'], ['2023-11-03', '2023-11-09'], ['2023-11-10', '2023-11-16'], ['2023-11-17', '2023-11-23'], ['2023-11-24', '2023-11-30'], ['2023-11-01', '2023-12-07'],['2023-12-08', '2023-12-14']] 
pmma_monthly_by_week = nuvia.calculate_waiting_for_24z(data_, weeks_)




#Export to an unique excel 
writer = pd.ExcelWriter('results/waiting_for_24z.xlsx', engine='xlsxwriter')
df_waiting_for_24z.to_excel(writer, 'pmma_cases_waiting_' , index = False)
pmma_df_to_export.to_excel(writer , 'pmma_patients_list' , index= False)
regresion_metrics.to_excel(writer, 'regresion_metrics' , index = True)
pmma_monthly_by_week.to_excel(writer, 'waiting_24z_monthly_by_week' , index = False)

for center_, df_center_ in dic_pmma_by_center.items():
    df_center_[['patient' , 'center' , 'archs' , 'date_Out' , 'arch type']].to_excel(writer, center_ , index = False)

writer.close()
