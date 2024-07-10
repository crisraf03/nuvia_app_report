import pandas as pd 

# year = 2023
# year = int(input('Please write the year of the query : '))

month_B_dic = {
    '1': 'JANUARY',    '2': 'FEBRUARY',
    '3': 'MARCH',    '4': 'APRIL',
    '5': 'MAY',    '6': 'JUNE',
    '7': 'JULY',    '8': 'AUGUST',
    '9': 'SEPTEMBER',    '10': 'OCTOBER',
    '11': 'NOVEMBER',    '12': 'DECEMBER',
    '13': 'JANUARY_2024', '14':'FEBRUARY_2024',
    '15':'MARCH_2024', '16':'APRIL_2024','17':'MAY_2024'
}

print('Please considere, month_B_dic : ' , month_B_dic)

month_selector = '17'
day_plus = '10'

#necesito corregir lo de los nombres de las columnas... para que sea automatico.




#clinic data
month_B = month_B_dic[month_selector]
sheet_name = 'Sheet0'

#necesito poder extraer la informacion de cada mes de manera mas sencilla
name_clinic_sheet = f"data\clinic_data\Production+By+Center_{month_B}.xlsx"
clinic_data = pd.read_excel(name_clinic_sheet , sheet_name=sheet_name)
print(f"Making the query on the file : {name_clinic_sheet} , sheet : {sheet_name} ...")

# lab data     
#necesito extraer al informacion de financial checkin de un mes y los primeros 5 o 6 dias siguientes del siguiente mes.

excel_name = f"checkout_to_{month_selector}_{day_plus}"
excel_folder = 'other_queries'

name_lab_sheet = f"data\{excel_folder}\{excel_name}.xlsx"
lab_sheet_name = 'Hoja de reporte 1'
lab_data = pd.read_excel(name_lab_sheet, sheet_name=lab_sheet_name)

print(f"Making the query on the file : {name_lab_sheet} , sheet : {lab_sheet_name} ... \n")

n3_products = [x for x in set(lab_data['product']) if 'N3' in x and'ight' not in x ]
# n3_products = [x for x in n3_products if x != 'N3 - Removable Denture'] 
lab_data = lab_data[lab_data['product'].isin(n3_products)]

#drop duplicates
lab_patients = lab_data[['patient' , 'product']].drop_duplicates()
clinic_patients = clinic_data[['patient' , 'Production Center']].drop_duplicates()

# Eliminar filas con valores NaN
lab_patients = lab_patients.dropna()
clinic_patients = clinic_patients.dropna()

from difflib import SequenceMatcher

def calcular_porcentaje_similitud(nombre1, nombre2):
    # Verificar que ambos parámetros sean cadenas
    if not isinstance(nombre1, str):
        print(nombre1)
        raise ValueError(f"nombre1 debe ser una cadena, pero se recibió el nombre {nombre1} y es tipo {type(nombre1).__name__}")
    if not isinstance(nombre2, str):
        print(nombre2)
        raise ValueError(f"nombre2 debe ser una cadena, pero se recibió el nombre {nombre2} y es tipo {type(nombre2).__name__}")
    
    similaridad = SequenceMatcher(None, nombre1, nombre2).ratio()
    porcentaje_similitud = round(similaridad * 100, 2)
    return porcentaje_similitud

def comparar_listas_nombres(lista1, lista2):
    resultados = []
    for nombre1 in lista1:
        mejor_coincidencia = {"name": "", "percent": 0}
        for nombre2 in lista2:
            porcentaje = calcular_porcentaje_similitud(nombre1, nombre2)
            if porcentaje > mejor_coincidencia["percent"]:
                mejor_coincidencia["name"] = nombre2
                mejor_coincidencia["percent"] = porcentaje

        resultados.append({
            "clinic_name": nombre1,
            "lab_name": mejor_coincidencia["name"],
            "similitud_percentaje": mejor_coincidencia["percent"]
        })

    return resultados

# Ejemplo de uso
pats_clinic = list( clinic_patients['patient'].str.upper().drop_duplicates() )
pat_lab = list( lab_patients['patient'].str.upper().drop_duplicates() )
print('N3 clinic patients : ' ,  len(pats_clinic) , 'N3 lab patients:' , len(pat_lab), '\n')
resultados = pd.DataFrame(comparar_listas_nombres(pats_clinic, pat_lab))

list_of_exportables = []
list_of_exportables.append({'name':f'comparative_clinic_lab_{month_selector}', 'df':resultados , 'index':False})


#por arreglar : 
# tiene problemas con el match de pacientes con mayusculas/minusculas ; LISTO
# el match si el paciente tiene invertido el nombre y apellido ;
#  se tomara la data hasta el 5 del siguiente mes para no tener que batallar con las fechas ; 
# agregar el n3-single 24Z tener en cuenta esto porque no esta contando este producto como n3 !!!

import nuvia
lab_data = nuvia.create_caracteristics(lab_data)
cols_lab = ['invoice', 'patient', 'restorer', 'center', 'archs', 'checkIn', 'CheckOut', 'amount', 'product', 'status', 'product class' , 'month_In', 'month_Out', 'year_In', 'year_Out']
lab_data = lab_data[cols_lab]

lab_data = lab_data.rename(columns = {'patient':'patient_lab'})
lab_data['lab_name'] = lab_data['patient_lab'].str.upper()

cols_clinic = ['Surgery Type', 'Surgeon (Use for Now)', 'Production Center', 'Surgery Date.1',
       'Case Name','Proposed Treatment Pathway','Actual Treatment Pathway','Treatment Plan', 'Alveoloplasty',
       'Arch Count (Case)', 'patient']
clinic_data = clinic_data[cols_clinic]

clinic_data = clinic_data.rename(columns={'patient': 'patient_clinic'})
clinic_data['clinic_name'] = clinic_data['patient_clinic'].str.upper()


resultados = pd.merge(resultados, lab_data, on='lab_name', how='inner')
resultados = pd.merge(resultados, clinic_data, on='clinic_name', how='inner')

resultados['center'] = resultados['center'].replace(' OFFICE', '', regex = True)
resultados['Production Center'] = resultados['Production Center'].str.upper() 
resultados.loc[resultados['center'] == resultados['Production Center'], 'same center'] = 1

resultados['day_In'] = resultados['checkIn'].dt.day
resultados['day_Out'] = resultados['CheckOut'].dt.day
resultados['day_surgery'] = resultados['Surgery Date.1'].dt.day
resultados['diff days in'] = resultados['day_In'] - resultados['day_surgery']
resultados['diff days out'] = resultados['day_Out'] - resultados['day_surgery']

resultados.loc[resultados['similitud_percentaje']> 85, 'correct match'] = 1
resultados['year_Out'] = resultados['year_Out'].astype(int)
resultados.loc[resultados['center'] == resultados['Production Center'],'same center'] = 1 


# resultados.to_excel('results/final_data_comparation.xlsx', index = False) # exportable
list_of_exportables.append({'name':'final_data_comparation', 'df':resultados , 'index':False})


clinic_data_not_in_report = clinic_data[~clinic_data['clinic_name'].isin(resultados['clinic_name'])] 
clinic_data.loc[~clinic_data['clinic_name'].isin(resultados['clinic_name']), 'not_in_report'] = 1
list_of_exportables.append({'name':'clinic_data', 'df':clinic_data , 'index':True})



#tercera parte


information_ = list_of_exportables[1]['df'] #exportable

#tomare los pacientes del lab que no aparecen en la clinica 
invoices_faltantes = lab_data[~lab_data['invoice'].isin(information_['invoice'])]
pats_lab_not_in_clinic = lab_data[~lab_data['lab_name'].isin(information_['lab_name'])]



list_of_exportables.append({'name':'not_in_clinic_patients', 'df':invoices_faltantes , 'index':True})
list_of_exportables.append({'name':'not_in_clinic_invoices', 'df':pats_lab_not_in_clinic , 'index':True})



def create_multiple_worksheet(list_with_dic_to_export, name_excel):
  writer = pd.ExcelWriter(name_excel, engine='xlsxwriter')
  for each_df in list_with_dic_to_export:
   df = each_df['df'] 
   print(each_df['name'])

   if 'center' in df.columns : 
      df['center'] = df['center'].replace(' OFFICE', '', regex = True)
   df.to_excel(writer, sheet_name = each_df['name'], index = each_df['index'])
  writer.close()

  print('End of the Report')


create_multiple_worksheet(list_of_exportables, name_excel='results/statements.xlsx')

