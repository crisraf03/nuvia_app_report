#On this module there are a list of methods created for the use and calculations on the diferents reports on nuvia´s app report.
import pandas as pd
import json
import numpy as np

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Desactivar los warnings temporales
with warnings.catch_warnings():
  warnings.simplefilter("ignore")

print('Loading nuvia module...')
json_path = "scripts\Values_of_products.json"

centers_list= ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE',
    'AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE',
    'SAN ANTONIO OFFICE', 'NASHVILLE OFFICE' , 'ORLANDO OFFICE','CHEVY CHASE OFFICE',
    'MARIETTA OFFICE', 'FORT LAUDERDALE OFFICE',  'DETROIT OFFICE', 'ALEXANDRIA OFFICE', 'TAMPA OFFICE',
    'PHILADELPHIA OFFICE','MINNEAPOLIS OFFICE', 'BELLEVUE OFFICE' , 'CHICAGO OFFICE' , 'PITTSBURGH OFFICE', 'DUBLIN OFFICE', 'FULLERTON OFFICE', 'ALPHARETTA OFFICE']


# Cargar el archivo JSON en una estructura de datos de python3.11
with open(json_path, "r") as json_doc:
  value_per_product = json.load(json_doc)

operation_capacity = 20
days_to_finish_ = {'N2_demo': 5, 'N2_travel': 1, 'N2_single': 8, 'wax_rims': 0.5, 'N3':2 ,'N3_redo':4 ,'N6':35 ,'N6_on_high_p':25}


def clear_data(database, drop = True):
  if drop == True:
    database = database.drop(['due','doctor_comment', 'warranty','warranty_comments'], axis =1)
  
  centers = [x for x in set(database['center']) if 'OFFICE' in x and 'CENTRAL' not in x ]
  database= database[database['center'].isin(centers)]
  database= database[database['product'] != 'PLATFORM FEE']
  database= database[~database['patient'].isin(['Pablo Montes','Mima Testing', 'Mima Testing'])]
  database= database[~database['restorer'].isin(['William Lemus'])]
  database['archs']  = database['archs'].astype('int')
  database['product'].replace( "N3 - Removable Denture With\xa0Fixed Arch", "N3 - Removable Denture With Fixed Arch", inplace=True)
  database.loc[database['product'] == 'N3 - Removable Denture With Fixed Arch' , 'archs'] = 1
  database.loc[database['product'].str.contains('Removable'), 'archs'] = 1
  return database

def  fix_errors(db_errors):
  db_errors = db_errors[~db_errors.index.duplicated(keep='first')]
  return(db_errors)

def check_errors(x_data):
  new_products = []
  x_ = pd.DataFrame()

  def get_default_x(x_row_pro):
    new_products.append(x_row_pro)
    return {'amount': 0, 'arch': [1,2]}

  def property_(row, x_property):
      x = value_per_product.get(row['product'], get_default_x(row['product']))
      return x.get(x_property, None)

  for x_property in ['amount', 'arch']:
      x_[x_property + '_'] = x_data.apply(lambda row, prop=x_property: property_(row, prop), axis=1)

  new_products = set(new_products)
  new_products = [product for product in new_products if product not in value_per_product]

  x_['archs'] = x_data['archs']
  x_['amount'] = x_data['amount']

  x_['error_amount'] = x_['amount_'] * x_['archs']
  x_['error_amount'] = x_['amount'] - x_['error_amount']
  x_['error_arch'] = x_.apply(lambda row: row['archs'] not in row['arch_'], axis=1)

  x_data_copy = x_data.copy()
  x_data_copy[['amount_', 'arch_', 'error_amount', 'error_arch']] = x_[['amount_', 'arch_', 'error_amount', 'error_arch']]

  errors = pd.concat([x_data_copy[x_data_copy['error_amount'] != 0], x_data_copy[x_data_copy['error_arch']]])
  db_corrected = fix_errors(errors)
  x_data_copy = pd.concat([x_data_copy, db_corrected])

  return errors, x_data_copy, new_products

regions_dict = {
  'PACIFIC': ['BELLEVUE OFFICE', 'FULLERTON OFFICE', 'SAN DIEGO OFFICE','ENCINO OFFICE'],
  'INTERMOUNTAIN': ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE'],
  'CENTRAL': ['DETROIT OFFICE', 'NASHVILLE OFFICE', 'CHICAGO OFFICE', 'DUBLIN OFFICE', 'MINNEAPOLIS OFFICE'],
  'TEXAS': ['AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE', 'SAN ANTONIO OFFICE'],
  'SOUTH ATLANTIC': ['FORT LAUDERDALE OFFICE', 'ORLANDO OFFICE', 'MARIETTA OFFICE', 'TAMPA OFFICE', 'MIAMI OFFICE', 'ALPHARETTA OFFICE','JACKSONVILLE OFFICE'],
  'MID ATLANTIC': ['ALEXANDRIA OFFICE', 'PITTSBURGH OFFICE', 'PHILADELPHIA OFFICE', 'CHEVY CHASE OFFICE', 'BALTIMORE OFFICE'],
  'NORTH PACIFIC': ['WESTBURY OFFICE', 'PURCHASE NY OFFICE', 'NEW JERSEY OFFICE', 'WELLESLEY OFFICE']
}

def create_regions(db_, _regions_ = regions_dict):
  for region, offices in _regions_.items():
    db_.loc[db_['center'].isin(offices), 'region'] = region
  return db_


regions_dict_until_june2024 = {
  'INTERMOUNTAIN': ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE'],
  'CENTRAL': ['DETROIT OFFICE', 'NASHVILLE OFFICE', 'CHICAGO OFFICE', 'DUBLIN OFFICE', 'MINNEAPOLIS OFFICE'],
  'TEXAS': ['AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE', 'SAN ANTONIO OFFICE'],
  'SOUTH ATLANTIC': ['FORT LAUDERDALE OFFICE', 'ORLANDO OFFICE', 'MARIETTA OFFICE', 'TAMPA OFFICE', 'MIAMI OFFICE', 'ALPHARETTA OFFICE'],
  'MID ATLANTIC': ['ALEXANDRIA OFFICE', 'PITTSBURGH OFFICE', 'PHILADELPHIA OFFICE', 'CHEVY CHASE OFFICE', 'BALTIMORE OFFICE'],
  'PACIFIC': ['BELLEVUE OFFICE', 'FULLERTON OFFICE', 'SAN DIEGO OFFICE'],
  'NORTH PACIFIC': ['WESTBURY OFFICE', 'PURCHASE NY OFFICE', 'NEW JERSEY OFFICE', 'WELLESLEY OFFICE']
}


def create_regions_labside(db_):
  intermountain = ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE', 'SAN DIEGO OFFICE'] 
  central = ['DETROIT OFFICE',  'NASHVILLE OFFICE', 'CHICAGO OFFICE' , 'DUBLIN OFFICE']
  texas = ['AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE', 'SAN ANTONIO OFFICE','MINNEAPOLIS OFFICE']
  south_atlantic = ['FORT LAUDERDALE OFFICE', 'ORLANDO OFFICE', 'MARIETTA OFFICE', 'TAMPA OFFICE', 'MIAMI OFFICE']
  mid_atlantic = [ 'ALEXANDRIA OFFICE', 'PITTSBURGH OFFICE',  'PHILADELPHIA OFFICE' , 'CHEVY CHASE OFFICE', 'BALTIMORE OFFICE','ALPHARETTA OFFICE']
  pacific = ['BELLEVUE OFFICE', 'FULLERTON OFFICE']
  
  db_.loc[db_['center'].isin(intermountain), 'region'] = 'INTERMOUNTAIN'
  db_.loc[db_['center'].isin(texas), 'region'] =  'TEXAS'
  db_.loc[db_['center'].isin(central), 'region'] =  'CENTRAL'
  db_.loc[db_['center'].isin(south_atlantic), 'region'] =   'SOUTH ATLANTIC'
  db_.loc[db_['center'].isin(mid_atlantic), 'region'] =  'MID ATLANTIC'
  db_.loc[db_['center'].isin(pacific), 'region'] =  'PACIFIC'
  return db_



def create_regions_before_april2024(db_):
  intermountain = ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE', 'BELLEVUE OFFICE', 'FULLERTON OFFICE'] 
  central = ['DETROIT OFFICE',  'NASHVILLE OFFICE', 'MINNEAPOLIS OFFICE' , 'CHICAGO OFFICE' , 'DUBLIN OFFICE']
  texas = ['AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE', 'SAN ANTONIO OFFICE',]
  south_atlantic = ['FORT LAUDERDALE OFFICE', 'ORLANDO OFFICE', 'MARIETTA OFFICE', 'TAMPA OFFICE', 'MIAMI OFFICE']
  mid_atlantic = [ 'ALEXANDRIA OFFICE', 'PITTSBURGH OFFICE',  'PHILADELPHIA OFFICE' , 'CHEVY CHASE OFFICE', 'BALTIMORE OFFICE']

  db_.loc[db_['center'].isin(intermountain), 'region'] = 'INTERMOUNTAIN'
  db_.loc[db_['center'].isin(texas), 'region'] =  'TEXAS'
  db_.loc[db_['center'].isin(central), 'region'] =  'CENTRAL'
  db_.loc[db_['center'].isin(south_atlantic), 'region'] =   'SOUTH ATLANTIC'
  db_.loc[db_['center'].isin(mid_atlantic), 'region'] =  'MID ATLANTIC'
  return db_



def create_regions_old(db_):
  intermountain = ['SALT LAKE CITY OFFICE', 'DENVER OFFICE', 'PHOENIX OFFICE', 'VEGAS OFFICE', 'BELLEVUE OFFICE']
  texas = ['AUSTIN OFFICE', 'DALLAS OFFICE', 'HOUSTON OFFICE', 'FORTWORTH OFFICE', 'SAN ANTONIO OFFICE','NASHVILLE OFFICE',]
  east = ['FORT LAUDERDALE OFFICE', 'ORLANDO OFFICE', 'MARIETTA OFFICE', 'TAMPA OFFICE' , 'DETROIT OFFICE' , 'CHEVY CHASE OFFICE' ,'ALEXANDRIA OFFICE' ,  'PHILADELPHIA OFFICE' , 'MINNEAPOLIS OFFICE'  ]

  db_.loc[db_['center'].isin(intermountain), 'region'] = 'INTERMOUNTAIN'
  db_.loc[db_['center'].isin(texas), 'region'] = 'TEXAS'
  db_.loc[db_['center'].isin(east), 'region'] = 'EAST'
  return db_




def create_hours_and_days(db_):
  db_['checkIn'] = pd.to_datetime(db_['checkIn'], format='ISO8601')
  db_['CheckOut'] = pd.to_datetime(db_['CheckOut'], format='ISO8601')

  # Extract only the date part "year-month-day" of the columns "checkIn" and "CheckOut"
  db_.loc[:, 'date_In'] = db_['checkIn'].dt.strftime('%Y-%m-%d')
  db_.loc[:, 'date_Out'] = db_['CheckOut'].dt.strftime('%Y-%m-%d')

  # Extract the month from the 'checkIn' and 'CheckOut' columns
  db_.loc[:, 'month_In'] = db_['checkIn'].dt.month
  db_.loc[:, 'month_Out'] = db_['CheckOut'].dt.month

  # Update 'checkIn' and 'CheckOut' columns after extracting date and month
  db_['checkIn'] = pd.to_datetime(db_['checkIn'], format='ISO8601')
  db_['CheckOut'] = pd.to_datetime(db_['CheckOut'], format='ISO8601')

  # Extract time and hour from 'checkIn'
  db_.loc[:, 'time_in'] = db_['checkIn'].dt.time
  db_.loc[:, 'hour_in'] = db_['checkIn'].dt.hour

  # Extract time and hour from 'CheckOut'
  db_.loc[:, 'time_out'] = db_['CheckOut'].dt.time
  db_.loc[:, 'hour_out'] = db_['CheckOut'].dt.hour

  # Calculate the difference in days between 'CheckOut' and 'checkIn'
  db_.loc[:,'diff_days'] = (db_['CheckOut'] - db_['checkIn'])
  return db_

def create_product_class(db_, removable = True, overtibar = False):
  db_['product class'] = ''  # Agrega una columna para la clase del producto

  # Crear clases N2, N3, N5 y N6 utilizando str.contains
  db_.loc[db_['product'].str.contains('N2'), 'product class'] = 'N2'
  db_.loc[db_['product'].str.contains('N3|n3') & ~db_['product'].str.contains('Removable|Night|crew'), 'product class'] = 'N3'
  if removable == True :
    db_.loc[db_['product'].str.contains('N3|n3') & db_['product'].str.contains('Removable'), 'product class'] = 'N3 removable'
  db_.loc[db_['product'].str.contains('N5'), 'product class'] = 'N5'
  db_.loc[db_['product'].str.contains('N6') & ~db_['product'].str.contains('eline|ummy'), 'product class'] = 'N6'
  if overtibar == True:
    db_.loc[db_['product'].str.contains('N6|n6') & db_['product'].str.contains('overtibar'), 'product class'] = 'N6 overtibar'

  db_.loc[db_['product'].str.contains('N7') , 'product class'] = 'N7'
  return db_


def create_materials(db_):
    zirconia = [x for x in set(db_['product']) if '24' in x or 'Zir' in x]
    zirconia = [x for x in zirconia if 'N2' not in x]
    G_CAM = [x for x in set(db_['product']) if 'G-CAM' in x or 'PMMA' in x]
    dummy = [x for x in set(db_['product']) if 'ummy' in x]
    reline = [x for x in set(db_['product']) if 'eline' in x]
    removable = [x for x in set(db_['product']) if 'Removable' in x]
    nightguard = [x for x in set(db_['product']) if 'Night' in x]
    others = [x for x in set(db_['product']) if x not in zirconia + G_CAM + dummy and 'Night' not in x and 'Demo' not in x]
    db_['material'] = np.nan 
    
    db_.loc[db_['product'].isin(zirconia), 'material'] = '24Z'
    db_.loc[db_['product'].isin(G_CAM), 'material'] = 'G-CAM'
    db_.loc[db_['product'].isin(dummy), 'material'] = 'Dummy'
    db_.loc[db_['product class'] == 'N2', 'material'] = 'Demodenture'
    db_.loc[db_['product'].isin(nightguard), 'material'] = 'Night guard'
    db_.loc[db_['product'].isin(others), 'material'] = 'other'
    db_.loc[db_['product'].isin(reline), 'material'] = 'Reline'
    db_.loc[db_['product'].isin(removable), 'material'] = 'Removable'
    db_.loc[db_['product'] == 'STOCKABLE DEMODENTURE', 'material'] = 'STOCK DEMO'
    db_.loc[db_['product'] == 'N2 - Wax Rims', 'material'] = 'Wax Rims'
    db_.loc[db_['product'].isin(['N2 - Single 24Z Processing','N2 -  Single 24Z Processing']), 'material'] = 'Single 24Z Processing'
    db_.loc[db_['product class'].isin(['N5', 'N7']), 'material'] = 'Document'
    return db_


def create_mixed_material(db_):
  #removables
  w_fixed_ = [p for p in set(db_['product']) if 'With Fixed Arch' in p]
  w_fixed_24z = [p for p in set(db_['product']) if 'With Fixed Arch 24Z' in p]
  db_.loc[db_['material'].isin(['Removable']) &  db_['product'].isin(w_fixed_) , 'mixed_material'] = 'G-CAM'
  db_.loc[db_['material'].isin(['Removable']) &  db_['product'].isin(w_fixed_24z) , 'mixed_material'] = '24Z'
  db_.loc[db_['material'].isin(['Removable']) &  ~db_['product'].isin(w_fixed_+ w_fixed_24z) , 'mixed_material'] = 'DENTURE'

  #nightguard
  printed_ = [p for p in set(db_['product']) if 'Printed' in p]
  db_.loc[db_['material'].isin(['Night guard']) &  db_['product'].isin(printed_) , 'mixed_material'] = 'Printed'

  #other
  processing_ = [p for p in set(db_['product']) if 'Processing' in p]
  db_.loc[db_['material'].isin(['other']) &  db_['product'].isin(processing_) , 'mixed_material'] = 'Processing 24Z'
  return db_


def create_arch_type(db_):
    db_.loc[db_['archs'].isin([1]), 'arch type'] = 'Single'
    db_.loc[db_['archs'].isin([2]), 'arch type'] = 'Full Mouth'
    return db_


def create_redo_type(db_):
  redo_products = [x for x in set(db_['product']) if 'edo' in x]
  remake_products = [x for x in set(db_['product']) if 'emake' in x]
  db_.loc[db_['product'].isin(redo_products) , 'redo type'] =  'REDO'
  db_.loc[db_['product'].isin(remake_products) , 'redo type'] = 'REMAKE'
 
  product_class_condition = db_['product class'].isin(['N3', 'N6'])
  db_.loc[product_class_condition & ~db_['product'].isin(redo_products+remake_products) , 'redo type'] = 'SURGERY'
  removable_products = [x for x in set(db_['product']) if 'Removable' in x]
  db_.loc[(db_['redo type'] == 'REDO') & (db_['product'].isin(removable_products)) , 'redo type'] =  'REDO REMOVABLE'
  return db_


def calculate_diff_times(db_, mondays, holidays_plus_one = ['2023-06-20', '2023-07-05', '2023-09-05']):
  #calculation of the diff times on days and hours
  db_.loc[:,'diff_hour'] = db_['diff_days'].dt.days * 24 + db_['diff_days'].dt.seconds // 3600

  # corrections of the diff hours on the weekends 
  condition_n3 = db_['product class'].isin(['N3'])
  db_['x_Out']  = db_['CheckOut'].dt.strftime('%Y-%m-%d')
  condition_xout = db_['x_Out'].isin(mondays)

  db_.loc[condition_n3 & condition_xout , 'diff_hour'] -= 48
  # Ajusta la lista holidays para que coincida con los valores únicos de 'x_Out'
  condition_holidays = db_['x_Out'].isin(holidays_plus_one)
  db_.loc[condition_holidays , 'diff_hour'] -= 24
  db_  = db_.drop(columns=['x_Out'])
  return db_


def create_delivery_on_time(db_, days_to_finish = days_to_finish_):
  #qualification of the delivery time
  condition_n2 = db_['product class'].isin(['N2'])

  n2_single_product = [x for x in set(db_[condition_n2]['product']) if 'ingle' in x]
  condition_n2_single = db_['product'].isin(n2_single_product)
  condition_time_n2_single = db_['diff_hour'] <= 24 * days_to_finish['N2_single']
  db_.loc[condition_n2_single & condition_time_n2_single, 'delivery_on_time'] = 1

  n2_travel_product = [x for x in set(db_[condition_n2]['product']) if 'Travel' in x]
  condition_n2_travel = db_['product'].isin(n2_travel_product)
  condition_time_n2_travel = db_['diff_hour'] <= 24 * days_to_finish['N2_travel']
  db_.loc[condition_n2_travel & condition_time_n2_travel, 'delivery_on_time'] = 1

  condition_time_n2 = db_['diff_hour'] <= 24 * days_to_finish['N2_demo']
  db_.loc[condition_n2 & ~condition_n2_single & ~condition_n2_travel & condition_time_n2, 'delivery_on_time'] = 1


  #### N3 ####
  condition_n3 = db_['product class'].isin(['N3'])
  condition_redo = db_['redo type'] == 'REDO'
  condition_time_n3 = db_['diff_hour'] <= 24 * days_to_finish['N3']
  db_.loc[condition_n3 & ~condition_redo & condition_time_n3, 'delivery_on_time'] = 1

  condition_time_n3_redo = db_['diff_hour'] <= 24 * days_to_finish['N3_redo']
  db_.loc[condition_n3 & condition_redo & condition_time_n3_redo, 'delivery_on_time'] = 1


  #### N6 ####
  condition_n6 = db_['product class'].isin(['N6'])
  condition_time_n6 = db_['diff_hour'] <= 24 * days_to_finish['N6']
  db_.loc[condition_n6 & condition_time_n6, 'delivery_on_time'] = 1

  condition_time_n6_on_hp = db_['diff_hour'] <= 24 * days_to_finish['N6_on_high_p']
  db_.loc[condition_n6 & condition_time_n6_on_hp, 'delivery_on_time'] = 2
  return db_


def create_responsable_party(data_redos):
  condition1 = data_redos['amount'] == 0
  condition2 = data_redos['redo type'].isin(['REDO' ,'REMAKE'])
  data_redos.loc[condition1 & condition2, 'responsable party'] = 'lab'
  data_redos.loc[~condition1 & condition2, 'responsable party'] = 'clinic'
  return data_redos

def create_month_year_column(db_):
  db_['checkIn'] = pd.to_datetime(db_['checkIn'], format='ISO8601')
  db_.loc[:, 'month_In_B'] = db_['checkIn'].dt.strftime('%B')
  db_.loc[: ,'year_In'] = db_['checkIn'].dt.strftime('%Y')
  db_['checkIn'] = pd.to_datetime(db_['checkIn'], format='ISO8601')

  db_['CheckOut'] = pd.to_datetime(db_['CheckOut'], format='ISO8601')
  db_.loc[: , 'month_Out_B'] = db_['CheckOut'].dt.strftime('%B')
  db_.loc[: ,'year_Out'] = db_['CheckOut'].dt.strftime('%Y')
  db_['CheckOut'] = pd.to_datetime(db_['CheckOut'], format='ISO8601')

  db_['year_In'] = db_['year_In'].astype(int)
  db_['year_Out']  =   db_['year_Out'].fillna(0)
  db_['year_Out'] = db_['year_Out'].astype(int)
  return db_


def recalculate_removable_products(db_):
  #change redo type
  removable_surgery = db_['mixed_material'].isin(['24Z', 'G-CAM'])
  db_.loc[removable_surgery, 'redo type'] = 'surgery'

  removable_redo = (db_['redo type']=='REDO REMOVABLE') & (db_['mixed_material'].isin(['24Z', 'G-CAM']))
  db_.loc[removable_redo, 'redo type'] = 'redo'

  db_.loc[db_['mixed_material']=='DENTURE', 'redo type']  = 'denture'

  #change material
  db_.loc[db_['mixed_material']=='24Z', 'material']  = 'Removable 24Z'
  db_.loc[db_['mixed_material']=='G-CAM', 'material']  = 'Removable G-CAM'
  db_.loc[db_['mixed_material']=='DENTURE', 'material']  = 'Removable Single'

  #shape
  db_.loc[db_['shape'] =='not found', 'shape'] = ''
  return db_

def create_caracteristics(db_, mondays = ['2023-09-04'] , drop = True, removable = True, overtibar = False):
  db_ = clear_data(db_, drop= drop)
  db_ = create_hours_and_days(db_)
  db_ = create_regions(db_)
  db_ = create_product_class(db_, removable=removable, overtibar = overtibar)
  db_ = create_materials(db_)
  db_ = create_arch_type(db_)
  db_ = create_redo_type(db_)
  db_ = calculate_diff_times(db_, mondays)
  db_ = create_delivery_on_time(db_)
  db_ = create_month_year_column(db_)
  db_ = create_responsable_party(db_)
  db_ = create_mixed_material(db_)
  if  removable: #esta es una medida para evitar conflictos con otros codigos, sin embargo es mala, toca revisar y reformar para hacer mas escalable. Nota: Cambios importantes en reclasificacion y calculos de otros parametros es mejor iniciarlos desde 0 en caso no pueda los modulos como cajas negras.
    db_ = recalculate_removable_products(db_)
  return db_ 


def dic_caracteristics(db_):
  caracteristics_types = {}
  for x in db_.columns:
      caracteristics_types[x] = set()
      for value in db_[x]:
          # Verificar si el valor no es NaN o None antes de agregarlo al conjunto
          if value is not None and not pd.isna(value):
              caracteristics_types[x].add(value)
  return caracteristics_types


def look_products(db_, product_class_=None, arch_type_=None, material_=None, redo_type=None):
    if product_class_:
        db_ = db_[db_['product class'].isin(product_class_)]
    if arch_type_:
        db_ = db_[db_['arch type'].isin(arch_type_)]
    if material_:
        db_ = db_[db_['material'].isin(material_)]
    if redo_type == True:
        db_ = db_[db_['redo type'] == 'REDO']
    elif redo_type == False:
        db_ = db_[db_['redo type'] != 'REDO']
    return set(db_['product'])


def count_GCAM_waiting_to_24Z(data_lab, pmma_list= False , columns_to_group = ['year_Out', 'month_Out_B', 'center']):
    max_order_per_patient = data_lab[data_lab['product class'].isin(['N3', 'N6'])].groupby(['patient'])['invoice'].max().reset_index()

    condition_a = data_lab['invoice'].isin(max_order_per_patient['invoice'])
    condition_b = data_lab['material'].isin(['G-CAM'])

    if not data_lab.index.empty:
      data_lab = data_lab.copy()
      data_lab.loc[ condition_a & condition_b , 'waiting24z'] = 1

      condition_waiting = data_lab['waiting24z'] == 1
      
      data_lab.loc[:,'CheckOut'] = pd.to_datetime(data_lab['CheckOut'] , format='ISO8601')
      condition_pmma = data_lab['CheckOut'] < '2023-07-01'

      pmma_counter = data_lab[condition_waiting & condition_pmma].groupby(columns_to_group)['archs'].sum().to_frame('arches')
      if not pmma_counter.index.empty:
        pmma_counter.loc[:, 'material'] = 'PMMA'
        pmma_counter = pmma_counter.reset_index() # Resetting index to make it explicit
        

      gcam_counter = data_lab[condition_waiting & ~condition_pmma].groupby(columns_to_group)['archs'].sum().to_frame('arches')
    
      if not gcam_counter.index.empty:
        gcam_counter.loc[:, 'material'] = 'G-CAM'
        gcam_counter = gcam_counter.reset_index() # Resetting index to make it explicit

      # Merging the DataFrames on the common columns
      result_df = pd.concat([pmma_counter, gcam_counter], axis=0)

      pmma_df = []
      if pmma_list == True:
        pmma_df = data_lab[condition_waiting & condition_pmma]

    else:
       result_df, pmma_df = pd.DataFrame(index=[0]), pd.DataFrame(index=[0])
    return (result_df, pmma_df)


def N6_count_analysis(db_old_):
  N6 = db_old_[db_old_['product class'] == 'N6']
  N6_mc = N6[N6['redo type'] != 'REDO'][ ['invoice', 'center' , 'patient', 'product class']]
  N6_redo = N6[N6['redo type'] == 'REDO'] [['invoice', 'center' , 'patient', 'product class']]
  dummy = db_old_[db_old_['material'] == 'Dummy'][['invoice','center' , 'patient', 'material']]
  reline = db_old_[db_old_['material'] == 'Reline'][['invoice','center' , 'patient', 'material']]

  n6_to_dummy = pd.merge(N6_mc, dummy, on=['center','patient'], how='inner')
  n6_to_reline = pd.merge(N6_mc, reline, on=['center','patient'], how='inner')
  n6_to_redo = pd.merge(N6_mc, N6_redo, on=['center','patient'], how='inner')

  n6_to_dummy['num'] = n6_to_dummy['invoice_y'] - n6_to_dummy['invoice_x']
  n6_to_reline['num'] = n6_to_reline['invoice_y'] - n6_to_reline['invoice_x']
  n6_to_redo['num'] = n6_to_redo['invoice_y'] - n6_to_redo['invoice_x']

  df0 =  N6_mc.groupby('center')['patient'].nunique().to_frame(name='mc')
  df1 =  n6_to_dummy[n6_to_dummy['num'] > 0].groupby('center')['patient'].nunique().to_frame(name='mc_dummy')
  df2 =  n6_to_reline[n6_to_reline['num'] > 0].groupby('center')['patient'].nunique().to_frame(name='mc_reline')
  df3 =  n6_to_redo[n6_to_redo['num'] > 0].groupby('center')['patient'].nunique().to_frame(name='mc_redo')

  merged_df = pd.merge(df0, df1, left_index=True, right_index=True, how='outer')
  merged_df = pd.merge(merged_df, df2, left_index=True, right_index=True, how='outer')
  merged_df = pd.merge(merged_df, df3, left_index=True, right_index=True, how='outer')
  merged_df.fillna(0, inplace=True)
  merged_df['center'] = merged_df.index
  merged_df = create_regions(merged_df)
  return(merged_df)



def filter_open_orders(data_, selected_month, _year_ = 2024, yeison_query=True) :
  opens = data_[(data_['CheckOut'].isnull() )]
  selected_month = [selected_month]

  # Load and filter data for the selected months and date ranges
  data_platform = load_data(selected_month, year_=_year_)
  data_in = data_platform['created']
  data_out = data_platform['finished']

  opens_month = create_caracteristics(data_in[~data_in['invoice'].isin(data_out['invoice'])])
  opens = opens[~opens['invoice'].isin(data_out['invoice'])]
  total_opens = pd.concat([opens, opens_month]).drop_duplicates()

  column_names = ['invoice', 'patient', 'restorer', 'center', 'archs', 'shape', 'size',
                  'checkIn', 'amount', 'product', 'status', 'date_In', 'month_In',
                  'month_Out', 'time_in', 'hour_in', 'region', 'product class', 'material',
                  'arch type', 'redo type', 'month_In_B', 'year_In']


  if yeison_query == True:
    path_yeison_query = 'data/ordenessinfirmar.xlsx'
    open_orders_yeison_query = pd.read_excel(path_yeison_query)
    total_opens.loc[total_opens['invoice'].isin(open_orders_yeison_query['rx']), 'in yeison query'] = True
    total_opens.loc[~total_opens['invoice'].isin(open_orders_yeison_query['rx']), 'in yeison query'] = False
    total_opens.loc[total_opens['product'] == 'N7 - Delivery Adjustment Records' , 'product class'] = 'N7'
    total_opens[column_names + ['in yeison query']].to_excel('results/total_opens.xlsx', index=False)
    return total_opens[column_names + ['in yeison query']]
  else:
     return total_opens[column_names]


def assign_week_numbers(df, dates_week):
    for i, week_dates in enumerate(dates_week):
        week_mask_in = df['date_In'].isin(week_dates)
        df.loc[week_mask_in, 'week_number'] = i 

        week_mask_out = df['date_Out'].isin(week_dates)
        df.loc[week_mask_out, 'week_number_end'] = i 
    return df


def g_cam_counter(db_, month = 2 ,year = 2023, date_column = 'date_In'): # this method didnt work for the counter of the pmma, take that in count and don´t use it for now
    #this method can count the number of arches and the number of invoices, how many patients on gcam and on 24z
    condition_product_class = db_['product class'].isin(['N3' , 'N6'])
    condition_month = db_[date_column].dt.month == month
    condition_year = db_[date_column].dt.year == year
    db_aux = db_[condition_product_class & condition_month & condition_year]

    condition_material = db_['material'] == 'G-CAM'
    # Calcula los totales para 'g_cam_arches' y 'g_cam_patients'
    db_gcam = db_[condition_material]
    g_cam_totals = db_gcam.groupby('center')['archs'].agg(arches_g_cam='sum', patients_g_cam='count')


    condition_material = db_aux['material'] == '24Z'
    # Calcula los totales para '24z_arches' y '24Z_patients'
    db_zir = db_aux[condition_material]
    zir_totals = db_zir.groupby('center')['archs'].agg(arches_24z='sum', patients_24z='count')

    totals = pd.concat([g_cam_totals , zir_totals] , axis=1)
    totals['month'] = month
    totals['year'] = year
    #total give the information of how the orders were created
    return (totals , db_aux)


def month_checker(db_, month_):
    db_['checkIn'] = pd.to_datetime(db_['checkIn'], format='ISO8601')
    db_['CheckOut'] = pd.to_datetime(db_['CheckOut'],format='ISO8601')

    month_condition_in = db_['checkIn'].dt.month == month_
    month_condition_out = db_['CheckOut'].dt.month == month_

    db_.loc[month_condition_in , 'created_on_month'] = 1
    db_.loc[month_condition_out , 'finished_on_month'] = 1
    return db_


def load_data(months, year_ = 2023):
  # This method loads the data on the folder data of the created and finished orders by the months given on a list
  data_in = []
  data_out = []

  for month_selector in months:
      data_in_month = pd.read_excel('data/{}/{}/week_.xlsx'.format(year_, month_selector))
      data_out_month = pd.read_excel('data/{}/{}/week_finished_.xlsx'.format(year_, month_selector))

      data_in.append(data_in_month)
      data_out.append(data_out_month)

  # Concatenate and reindex
  data_in = pd.concat(data_in, axis=0).reset_index(drop=True)
  data_out = pd.concat(data_out, axis=0).reset_index(drop=True)

  # Drop duplicates based on the 'invoice' column
  data_in = data_in.drop_duplicates(subset='invoice').reset_index(drop=True)
  data_out = data_out.drop_duplicates(subset='invoice').reset_index(drop=True)
  data_lab = {'created': data_in, 'finished': data_out}
  return data_lab


def filter_data(data_lab, data_selector, filter_dates):
  if data_selector == 'out':
      data_ = data_lab['finished']
      check_column = 'CheckOut'
  elif data_selector == 'in':
      data_ = data_lab['created']
      check_column = 'checkIn'
  else:
      raise ValueError("Invalid data_selector. Use 'in' or 'out'.")

  data_ = data_.copy()
  data_[check_column] = pd.to_datetime(data_[check_column], format='ISO8601')
  
  data_to_export = []

  for [start_date, end_date] in filter_dates:
      date_condition_start = start_date <= data_[check_column]
      date_condition_end = data_[check_column] < end_date
      
      end_date = pd.to_datetime(end_date, format='ISO8601') - pd.Timedelta(days=1)
      end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')

      data_selection = data_[date_condition_start & date_condition_end]
      data_selection.loc[:,'category_date'] = '{}_to_{}'.format(start_date, end_date)
      data_to_export.append(data_selection)

  data_to_export = pd.concat(data_to_export, axis=0).reindex()
  data_to_export = create_caracteristics(data_to_export)
  return data_to_export

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def match_patients_(list1 , list2 , threshold = 85, columns_name= ['Case Name', 'patient']):
    patient_mapping = {}
    for name1 in list1:
        result = process.extractOne(name1[10:], list2, scorer = fuzz.token_set_ratio)
        closest_match = result[0]
        similarity = result[1]
        if similarity >= threshold:  # Adjust the similarity threshold as needed
            patient_mapping[name1] = closest_match
    df = pd.DataFrame(patient_mapping.items(), columns=columns_name)
    return df


def unificate_two_db(db_in , db_out, col_unificator = 'invoice'):
    condition = db_out[col_unificator].isin(db_in[col_unificator])
    db_aux = db_out[~condition]
    db_ = pd.concat([db_in , db_aux] , axis=0)
    return db_



"""waiting for 24z methods"""


def calculate_waiting_for_24z(data, weeks):
  """
  Calculate the number of items waiting for 24Z for each week in monthly.

  Parameters:
  - data: DataFrame containing the relevant data.
  - weeks: List of lists, where each inner list represents the start and end dates of a week.

  Returns:
  - pmma_monthly_by_week: DataFrame with the count of items waiting for 24Z for each week in monthly.
  """
  pmma_monthly_by_week = []

  for week in weeks:
      week_filter = data['checkIn'] <= week[1]
      data_week = data[week_filter]
      x_week, pmma_df_week = count_GCAM_waiting_to_24Z(data_week, pmma_list=True)
      x_week.loc[:, 'week'] = '{}_to_{}'.format(week[0], week[1])
      pmma_monthly_by_week.append(x_week)

  pmma_monthly_by_week = pd.concat(pmma_monthly_by_week, axis=0)

  x_ = pmma_monthly_by_week[pmma_monthly_by_week['material'] == 'PMMA'].groupby('week')['arches'].sum()
  print(f'The number on the alex´s report are:\n {x_}')
  return pmma_monthly_by_week



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

