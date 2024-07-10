import pandas as pd 
import nuvia 

start_date , finish_date = '2023-06-30', '2023-12-01'


name_excel = 'data/checkIn_all.xlsx'
db_checkIn_all = pd.read_excel(name_excel)
db_checkIn_all = nuvia.create_caracteristics(db_checkIn_all)

date_filter_start = db_checkIn_all['date_Out'] > start_date
db_checkIn_all = db_checkIn_all[date_filter_start]

date_filter_stop = db_checkIn_all['date_Out'] < finish_date
db_checkIn_all = db_checkIn_all[date_filter_stop]



product_condition  = {'n3': ['N3'] , 'n6': ['N6'] , 'total' : ['N3' , 'N6']}

def material_counter ( db_ , name_group = 'restorer'):

    list_x_ = []
    for name, N in product_condition.items() :
        product_filter = db_['product class'].isin(N)
        x_  = db_[product_filter].groupby(['year_Out' , 'month_Out_B' , 'center', name_group])['archs'].sum().to_frame(f'arches {name}')
        list_x_.append(x_)
        redo_filter = db_['redo type'].isin(['REDO'])
        redo_x_  = db_[product_filter & redo_filter].groupby(['year_Out' , 'month_Out_B' ,'center', name_group])['archs'].sum().to_frame(f'redo arches {name}')
        list_x_.append(redo_x_)


    count_ = pd.concat(list_x_ , axis=1).reindex().reset_index()
    count_['year_Out'] = count_['year_Out'].astype(int)
    count_['n6/n3 ratio'] = count_['arches n6'] / count_['arches n3'] 
    return count_


def calculate_redo_percent(count_):

    for name , N in product_condition.items():
        count_[f'redo percent {name}'] = count_[f'redo arches {name}'] / count_[f'arches {name}']
    
    count_['center'].replace( "OFFICE", "", inplace=True)
    count_ = nuvia.create_regions(count_)
    return count_.fillna(0)

x_counter = material_counter(db_checkIn_all)
x_counter = calculate_redo_percent(x_counter)



#now i want to took the orders of each restorer that have redo > 0.1

def took_orders(row, db_ = db_checkIn_all):
    year_, month_B, restorer_ = row [['year_Out', 'month_Out_B' , 'restorer']]
    # print(f"Year: {year_}, Month: {month_B}, Restorer: {restorer_}")
    
    product_filter = db_['product class'].isin(['N3' , 'N6'])
    db_ = db_[product_filter]
    column_list_names =['restorer', 'invoice' , 'patient', 'center' , 'product' ,  'material' , 'archs'   , 'month_Out_B' , 'year_Out' ]
    restorer_orders = db_[(db_['year_Out'] == str(year_)) & (db_['restorer'] == restorer_)][column_list_names]
    
    restorer_orders['year_Out'] = restorer_orders['year_Out'].astype(int)
    return restorer_orders


filter_by_redo_percent = x_counter['redo percent total'] > 0.1
orders_by_restorer = [took_orders(row) for index, row in x_counter[filter_by_redo_percent].iterrows()]

column_names = ['year_Out', 'month_Out_B', 'region',  'center', 'restorer', 'arches total', 
    'redo arches total', 'n6/n3 ratio', 'redo percent total' ]

# 'arches_n3',  'redo_arches_n3', 'arches_n6', 'redo_arches_n6', 'redo_percent_n3', 'redo_percent_n6'



writer = pd.ExcelWriter('results/restorer_counter_archs.xlsx', engine='xlsxwriter')
x_counter[column_names].to_excel(writer, sheet_name = 'restorer_counter_arches', index = False)
 
for each_item in orders_by_restorer:
    restorer_value = list(set(each_item['restorer']))[0]
    each_item.to_excel(writer , sheet_name = restorer_value  , index = False)
writer.close()