''' Report of the new N3 24z, GCAM, and the redos/remakes created arches'''
import pandas as pd
import nuvia 

#add the regional name
center_to_regional = {
'MINNEAPOLIS OFFICE': 'Hermes Castillo',
'HOUSTON OFFICE': 'Dalima Rieder (Mima)',
'PHILADELPHIA OFFICE': 'Andres Reyes',
'MARIETTA OFFICE': 'Andres Reyes',
'CHEVY CHASE OFFICE': 'Andres Reyes',
'PITTSBURGH OFFICE': 'Hermes Castillo',
'NASHVILLE OFFICE': 'Hermes Castillo',
'VEGAS OFFICE': 'Alejandra Buitrago',
'SALT LAKE CITY OFFICE': 'Alejandra Buitrago',
'PHOENIX OFFICE': 'Alejandra Buitrago',
'DENVER OFFICE': 'Alejandra Buitrago',
'ALEXANDRIA OFFICE': 'Andres Reyes',
'FORTWORTH OFFICE': 'Dalima Rieder (Mima)',
'TAMPA OFFICE': 'Cindy Ruiz',
'ORLANDO OFFICE': 'Cindy Ruiz',
'FORT LAUDERDALE OFFICE': 'Cindy Ruiz',
'SAN ANTONIO OFFICE': 'Dalima Rieder (Mima)',
'DALLAS OFFICE': 'Dalima Rieder (Mima)',
'AUSTIN OFFICE': 'Dalima Rieder (Mima)',
'DETROIT OFFICE': 'Hermes Castillo',
'BELLEVUE OFFICE': 'Alejandra Buitrago',
'CHICAGO OFFICE': 'Hermes Castillo',
'MIAMI OFFICE': 'Cindy Ruiz',
'BELLEVUE OFFICE': 'Hermes Castillo',
'BALTIMORE OFFICE': 'Andres Reyes',
'DUBLIN OFFICE': 'Hermes Castillo',
'FULLERTON OFFICE': 'Alejandra Buitrago',
'ALPHARETTA OFFICE':'Andres Reyes',
'SAN DIEGO OFFICE': 'Alejandra Buitrago'
}


#need a way to add new weeks 
selected_month = [6,7]
_year_ = 2024

# Define date ranges for the accountability report
dates_old = [['2023-09-29', '2023-10-06'], ['2023-10-06', '2023-10-13'], ['2023-10-13', '2023-10-20'],
    ['2023-10-20', '2023-10-27'], ['2023-10-27', '2023-11-03'], ['2023-11-03', '2023-11-10'],
    ['2023-11-10', '2023-11-17'] , ['2023-11-17', '2023-11-24'], ['2023-11-24', '2023-12-01'],
    ['2023-12-01', '2023-12-08'], ['2023-12-08', '2023-12-15'], ['2023-12-15', '2023-12-23'],
    ['2023-12-23', '2023-12-31'], ['2024-01-01', '2024-01-05'],['2024-01-05', '2024-01-12'],
    ['2024-01-12', '2024-01-19'],['2024-01-19', '2024-01-26'],['2024-01-26', '2024-02-02'],
    ['2024-02-02', '2024-02-09'], ['2024-02-09', '2024-02-16'], ['2024-02-23', '2024-03-01'],
    ['2024-03-01', '2024-03-08'],['2024-03-08', '2024-03-15'],['2024-03-15', '2024-03-22'] , 
    ['2024-03-22', '2024-03-29'], ['2024-03-29', '2024-04-05'],['2024-04-05', '2024-04-12'],
    ['2024-04-12', '2024-04-19'],['2024-04-19', '2024-04-26'],['2024-04-26', '2024-05-03'],
    ['2024-05-03', '2024-05-10'],['2024-05-10', '2024-05-17'],['2024-05-17', '2024-05-24'],
    ['2024-05-24', '2024-05-31'],['2024-05-31', '2024-06-07'], ['2024-06-07', '2024-06-14'],
    ['2024-06-14', '2024-06-21'] , ['2024-06-21', '2024-06-28'] ]



# Add the 17th when needed (not clear why 17 is added when 16 is desired)
dates = [['2024-06-21', '2024-06-28'], ['2024-06-28', '2024-07-05']   ] # 
print(f'Creating the accountability report for the weeks:\n{dates}')

# Load and filter data for the selected months and date ranges
data_platform = nuvia.load_data(selected_month, year_=_year_)
data_in = nuvia.filter_data(data_platform, 'in', dates)  # Add a condition for non-list elements in 'dates'
data_out = nuvia.filter_data(data_platform, 'out', dates)

counter = {}
index_date = 'date_Out'  # 'category_date'

'''Perform counting by center and export the cases'''
# Conditions for filtering specific cases
condition_n3 = data_out['product class'] == 'N3'
condition_surgery = data_out['redo type'] == 'SURGERY'

condition_zirconia = data_out['material'] == '24Z'
condition_gcam = data_out['material'] == 'G-CAM'
condition_mixed_material_24z = data_out['mixed_material'] == '24Z'
condition_mixed_material_gcam = data_out['mixed_material'] == 'G-CAM'
condition_redo_removable = data_out['redo type'] =='REDO REMOVABLE'

#for the new use, columns to export

data_out.loc[condition_n3 & condition_surgery & condition_zirconia, 'new'] = 'N3 24Z'
data_out.loc[condition_n3 & condition_surgery & condition_gcam, 'new'] = 'N3 G-CAM'
data_out.loc[condition_mixed_material_24z & ~condition_redo_removable, 'new'] = 'removable 24Z'
data_out.loc[condition_mixed_material_gcam & ~condition_redo_removable, 'new'] = 'removable G-CAM' 

condition_new = data_out['new'].isin(['N3 24Z' , 'N3 G-CAM','removable 24Z' , 'removable G-CAM'])


# Merge DataFrames using pivot_table
N3_counter = pd.pivot_table(data_out[condition_new],
                            values='archs',
                            index=['category_date', index_date, 'center'],
                            columns='new',
                            aggfunc='sum',
                            fill_value=0)


# Reset the index to have date and center as columns
N3_counter.reset_index(inplace=True)

# Define columns for export in n3 DataFrame
n3_columns_to_export = ['category_date', 'invoice', 'patient', 'center', 'archs', 'checkIn', 'CheckOut', 'product', 'new']
df_to_export_n3 = data_out[condition_new][n3_columns_to_export]

for name_col_removable in ['removable 24Z', 'removable G-CAM']:
    try:
        N3_counter[name_col_removable] = N3_counter[name_col_removable].fillna(0)
    except KeyError:
        # Manejo del error cuando la columna no está presente
        N3_counter[name_col_removable] = 0

    
N3_counter['regional name'] = N3_counter['center'].map(center_to_regional)
column_names = ['category_date', 'regional name', 'center', 'date_Out', 'N3 24Z' , 'N3 G-CAM','removable 24Z' , 'removable G-CAM']
N3_counter = N3_counter[column_names].fillna(0)

# Store the results in the counter dictionary for 'N3'
counter['N3'] = {'count': N3_counter, 'df': df_to_export_n3}


'''N6 material 24Z'''



condition_n3_redo_out = (data_out['product class']=='N3') & (data_out['redo type'] == 'REDO') & (data_out['material'] == '24Z')
data_out.loc[condition_n3_redo_out, '24z class'] = 'n3 redo out'

condition_redo_removable_out = (data_out['redo type'] == 'REDO REMOVABLE') & (data_out['mixed_material'] == '24Z')
data_out.loc[condition_redo_removable_out, '24z class'] = 'redo removable out'

condition_n6_24z = (data_out['product class'] == 'N6') & (data_out['material'] == '24Z')
data_out.loc[condition_n6_24z, '24z class'] = '24z N6' 

condition_n6_24z = (data_out['material'] == 'Single 24Z Processing')
data_out.loc[condition_n6_24z, '24z class'] = 'Single 24Z Processing' 




N6_columns_to_export = ['category_date', 'invoice', 'patient', 'center', 'archs', 'checkIn', 'CheckOut', 'product', '24z class']
condition_24z_class = data_out['24z class'].isin(['Single 24Z Processing', '24z N6', 'redo removable out', 'n3 redo out'])

df_to_export_n6_24z= data_out[condition_24z_class][N6_columns_to_export]

N6_24z_counter = pd.pivot_table(data_out[condition_24z_class],
                            values='archs',
                            index=['category_date', index_date, 'center'],
                            columns='24z class',
                            aggfunc='sum',
                            fill_value=0).reset_index()


counter['N6 24Z'] = {'count': N6_24z_counter, 'df': df_to_export_n6_24z}



''' Redo accounting '''

index_date = 'date_In'  # 'category_date

# Conditions for filtering specific cases in the 'data_in' DataFrame
condition_n3 = data_in['product class'] == 'N3'
condition_surgery = data_in['redo type'] == 'SURGERY'
condition_mixed_material = data_in['mixed_material'].isin(['G-CAM', '24Z'])
condition_redo_removable = data_in['redo type'].isin(['REDO REMOVABLE'])

# Mark cases for redo accounting
data_in.loc[condition_n3 & ~condition_surgery, 'redo_accounting'] = 'N3 Redo'
data_in.loc[condition_mixed_material & condition_redo_removable, 'redo_accounting'] = 'Redo Removable'
condition_redo_accounting = data_in['redo_accounting'].isin(['N3 Redo' , 'Redo Removable'])

N3_redo = pd.pivot_table(data_in[condition_redo_accounting],
                            values='archs',
                            index=['category_date', index_date, 'center'],
                            columns=['redo_accounting'],
                            aggfunc='sum',
                            fill_value=0)

redo_columns_to_export = ['category_date', 'invoice', 'patient', 'restorer', 'center', 'archs', 'checkIn', 'product', 'material' ,'redo_accounting']
df_to_export_n3_redo = data_in[condition_redo_accounting][redo_columns_to_export]

N3_redo.reset_index(inplace=True)
N3_redo['regional name'] = N3_redo['center'].map(center_to_regional)

try :
    N3_redo = N3_redo[['category_date', index_date,'regional name', 'center','N3 Redo', 'Redo Removable']]
except KeyError:
    N3_redo = N3_redo[['category_date', index_date,'regional name', 'center','N3 Redo']]


counter['redo'] = {'counter': N3_redo, 'df': df_to_export_n3_redo}


# Store the results in the counter dictionary for 'redo'

#Ordenar valores
df_to_export_n3 = df_to_export_n3.sort_values(by='CheckOut', ascending=True)
df_to_export_n3_redo = df_to_export_n3_redo.sort_values(by='checkIn', ascending=True)
df_to_export_n6_24z = df_to_export_n6_24z.sort_values(by='CheckOut', ascending=True)

df_to_export_dic = {'N3 counter': N3_counter , 'N3 orders': df_to_export_n3 , 'N3 redo counter':N3_redo , 'N3 redo orders':df_to_export_n3_redo, '24Z counter': N6_24z_counter , '24Z orders': df_to_export_n6_24z}








# Export results to Excel

writer = pd.ExcelWriter('results/accounting.xlsx', engine='xlsxwriter')
for name_,df_ in df_to_export_dic.items():
    df_['center'] = df_['center'].replace('OFFICE', '', regex = True)
    df_.to_excel(writer, sheet_name= name_, index=False)
writer.close()
