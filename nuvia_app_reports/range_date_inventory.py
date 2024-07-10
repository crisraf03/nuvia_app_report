import pandas as pd 
import inventory_report

excel_path = 'data/checkOut_2023.xlsx'
excel_path = 'data/checkIn_all_with_characteristics.xlsx'

months_to_analyse = [7,8,9,10,11,12]
pivot = True
export_excel = True


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
    'CHICAGO OFFICE': 'Alejandra Buitrago'
}

def center_to_regional_(center):
    # Ejemplo de implementación de la función de mapeo
    return center_to_regional.get(center, 'Unknown')

dic_year = {'arches' : [], 'redos': [], 'arch_type': [], 'material': [], 'shape': [], 'orders': []}
data_2023 = pd.read_excel(excel_path)

for month_selector in months_to_analyse:
    data_month = data_2023[data_2023['month_Out'] == month_selector]
    print(f"\n month : {month_selector} shape:  {data_month.shape}")
    dic_month = inventory_report.invetory_report(data_month, pivot=pivot)


    for key, item in dic_month.items():
        item['month_Out'] = month_selector
        if key!= 'orders':

            if pivot == True:
                item['regional_name'] = item.index.get_level_values('center').map(center_to_regional)
            if pivot == False:
                item['regional_name'] = item['center'].map(center_to_regional)
        
        dic_year[key].append(item)


for key, item in dic_year.items():
    dic_year[key] = pd.concat(item)


names_columns_inventory= {'arches' : ['region', 'center', 'product class', 'material', 'archs', 'month_Out', 'regional_name'], 
                          
    'redos': ['region', 'center', 'product class', 'redo type', 'archs', 'month_Out', 'regional_name'], 

    'arch_type': ['region', 'center', 'product class', 'arch type', 'archs', 'month_Out', 'regional_name'], 

    'material': ['region', 'center', 'material', 'archs', 'month_Out', 'regional_name'], 

    'shape': ['region', 'center', 'product class', 'shape', 'archs', 'month_Out', 'regional_name'],

    'orders': ['invoice', 'patient', 'restorer', 'center', 'archs', 'shape', 'size',
    'checkIn', 'CheckOut', 'amount', 'product', 'status', 'date_In', 'date_Out',
    'month_In', 'month_Out', 'time_in', 'hour_in', 'time_out', 'hour_out',
    'diff_days', 'region', 'product_class', 'material', 'arch_type',
    'redo_type', 'diff_hour', 'delivery_on_time', 'month_In_B', 'year_In',
    'month_Out_B', 'year_Out', 'responsable_party'] }

if export_excel == True:
    writer = pd.ExcelWriter(f"results/inventory_report_.xlsx" , engine='xlsxwriter')
    for key, item in dic_year.items():
        item_ = item.reset_index()
        item_ = item_.T.reset_index().T

        if pivot == False:
            item_ = item_.iloc[1:, 1:].reset_index(drop=True)
            item_.columns = names_columns_inventory[key]
        item_.to_excel(writer, sheet_name = key , index = False)
    writer.close()











import linear_regresion_nuvia


def make_linear_regresion(linear_regresion = False):

    if linear_regresion =='pivot':
        df_ = dic_year['arches']
        regresion_by_center = []

        for column_name in [(    'N3','24Z') , (    'N3','G-CAM') , (    'N6','24Z') ,(    'N6','G-CAM')] : 
            for center_ in df_.index.unique():
                df_center_ = df_[df_.index == center_]
                
                #determinate linear regresion
                x = linear_regresion_nuvia.determinate_linear_regresion(df_center_[column_name] ,df_center_[   'month_Out',    ''] )
                x.extend(list(column_name))

                #determinate means values
                x.extend(linear_regresion_nuvia.calculate_mean_std(df_center_, column_name) )

                #add the center name
                x.append(center_)

                # print(x)
                regresion_by_center.append(x)

        regresion_by_center = pd.DataFrame(regresion_by_center)
        regresion_by_center.columns = ['slope' , 'intercept' , 'r_squared', 'product class', 'material', 'mean', 'std_value', 'center']
        # regresion_by_center.index = regresion_by_center['center']

        predicted_month = 13
        regresion_by_center['predicted arches'] = regresion_by_center['slope']* predicted_month + regresion_by_center['intercept']
        regresion_by_center.to_excel('results/regresion_by_center.xlsx', index = False)









