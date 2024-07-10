import pandas as pd
import nuvia

print('loading lab metric module')

def transform_data(name_sheet, dates_week, monday_of_the_month):
  db_ = pd.read_excel(name_sheet) 
  db_ = nuvia.create_caracteristics(db_ , mondays=monday_of_the_month)
  db_ = nuvia.assign_week_numbers(db_, dates_week=dates_week)
  return db_

'''METHODS FOR THE COUNT OF ARCHES'''

def create_data_counter(data_ , column_to_check = 'CheckOut'):
    data_ = data_[data_[column_to_check].notna()]
    condition = data_['product class'] == 'N3'
    data_ = data_[condition]

    redos = [x for x in set(data_['product']) if 'edo' in x and 'emovable' not in x]
    condition = data_['product'].isin(redos)
    condition = data_['redo type'] == 'REDO'


    # Inicializar el DataFrame 'x__' con la columna 'center' como índice
    x__ = pd.DataFrame(index=list(set(data_['center'])))

    for material_ in ['24Z', 'G-CAM']:
        condition = data_['material'] == material_
        data = data_[condition]

        for x_ in set(data['arch type']):
            condition = data['arch type'] == x_
            x = data[condition].groupby('center')['archs'].sum()

            x.fillna(0, inplace=True)   
            x_aligned = x.reindex(x__.index, fill_value=0)

            column_name = f'{material_}_{x_}'
            x__[column_name] = x_aligned.values

    x__['N4 arches']  = x__[x__.columns].sum(axis=1)

    #for the calculation of delivery percent
    c1 = data_['product class'] == 'N3'
    c2 = data_['delivery_on_time'] == 1
    c4 = data_['redo type'] == 'SURGERY'
    x__['N_delivery_on_time'] = data_[c1 & c2 & c4].groupby('center')['delivery_on_time'].sum()
    x__['N_surgeries'] = data_[c1 & c4].groupby('center') ['invoice'].count()
    x__.fillna(0, inplace = True)
    return x__


def counter_other_products(data_, finihed_status= ['Post Delivery Record']):
  data_ = data_[data_['status'].isin(finihed_status)]

  products_N3_redo = [x for x in set(data_['product']) if 'N3' in x and 'edo' in x and 'emovable' not in x]
  products_N6 = [x for x in set(data_['product']) if 'N6' in x and 'ummy' not in x and 'eline' not in x and 'edo' not in x]
  products_N6_redo = [x for x in set(data_['product']) if 'N6' in x and 'ummy' not in x and 'eline' not in x and 'edo' in x]

  N3_redo = data_[data_['product'].isin(products_N3_redo)]
  N6 = data_[data_['product'].isin(products_N6)]
  N6_redo = data_[data_['product'].isin(products_N6_redo)]

  N3_redo_count = N3_redo.groupby('center')['archs'].sum().to_frame('N3_redo')
  N6_count = N6.groupby('center')['archs'].sum().to_frame('N6')
  N6_redo_count = N6_redo.groupby('center')['archs'].sum().to_frame('N6_redo')

  reline = data_[data_['material']=='Reline'].groupby('center')['archs'].sum().to_frame('reline_sum')

  counter = pd.concat( [N3_redo_count , N6_count , N6_redo_count, reline] , axis = 1 )
  counter = counter.fillna(0)
  counter['N7_total'] = counter['N6'] + counter['N6_redo']

  #for the calculation of delivery percent
  c1_n3 = data_['product class'].isin(['N3'])
  c1_n6 =data_['product class'].isin(['N6'])
  c2 = data_['redo type'] == 'REDO'
  c3 = data_['delivery_on_time'] == 1

  counter['N_delivery_n3_redos_on_time'] = data_[c1_n3 & c2 & c3].groupby('center')['delivery_on_time'].sum()
  counter['N_delivery_n6_on_time'] = data_[c1_n6 & c3].groupby('center')['delivery_on_time'].sum()

  c4 = data_['product class'].isin(['N3', 'N6'])
  c5 = data_['product class'].isin(['N3']) &  data_['redo type'].isin(['SURGERY'])

  counter['N_surgeries_N3'] = data_[c1_n3].groupby('center') ['invoice'].count()
  counter['N_surgeries_N6'] = data_[c1_n6].groupby('center') ['invoice'].count()
  counter['N_surgeries_other_products'] = data_[c4 & ~c5].groupby('center') ['invoice'].count()
  counter= counter.fillna(0)
  return counter


def calculate_center_percents(Report, operation_capacity = 20):
  # Definir las variables con los nombres
  zir_single = '24Z_Single'
  zir_full_month = '24Z_Full Mouth'
  Redo_n3 = 'N3_redo'
  Redo_n6 = 'N6_redo'
  total_arches = 'Total_arches'
  N_delivery_total = 'N_delivery_on_time_total' 
  N_surgeries_total = 'N_surgeries_total'
  reline_arches = 'reline_sum'

  # creador de porcentajes
  percents = {}

  if len(list(Report[Report['N4 arches'] == 0])) == 0:
    print('Looking for centers with problems ... \n centers with 0 arches : {}'.format(list(Report[Report['N4 arches'] == 0].index)) )

  try:
      percents['zirconia'] = (Report[zir_single] + Report[zir_full_month]) / Report['N4 arches']
  except ZeroDivisionError:
      percents['zirconia'] = 0

  try:
      percents['redo_n3'] = Report[Redo_n3] /  Report[total_arches]
  except ZeroDivisionError:
      percents['redo_n3'] = 0

  try:
      percents['redo_n6'] = Report[Redo_n6] /  Report[total_arches]
  except ZeroDivisionError:
      percents['redo_n6'] = 0

  percents['capacity'] = (Report[total_arches]) / operation_capacity
  Report = pd.concat([Report, pd.DataFrame(percents)], axis=1)

  try:
    Report['delivery'] = Report[N_delivery_total]/Report[N_surgeries_total]
  except ZeroDivisionError:
    Report['delivery'] = 0
  
  try:
    Report['reline'] = Report[reline_arches]/(Report[total_arches] + Report[reline_arches] )
  except ZeroDivisionError:
    Report['reline'] = 0
  
  try:
    Report['surgeries'] = Report['N_surgeries_N3']/(Report['N_surgeries_N3'] + Report['N_surgeries_N6'])
  except ZeroDivisionError:
    Report['surgeries'] = 0

  try:
    Report['material_change'] = Report['N_surgeries_N6']/(Report['N_surgeries_N3'] + Report['N_surgeries_N6'])
  except ZeroDivisionError:
    Report['material_change'] = 0

  return Report


def calculate_region_percents(Report, operation_capacity = 20):
  zir_single = '24Z_Single'
  zir_full_month = '24Z_Full Mouth'
  Redo_n3 = 'N3_redo'
  Redo_n6 = 'N6_redo'
  total_arches = 'Total_arches'
  N_delivery_total = 'N_delivery_on_time_total' 
  N_surgeries_total = 'N_surgeries_total'

  percents_ = {} # it calculate the percents by region
  for id_region in list(set(Report['region'])):
      percenter_by_region = {}
      Report_region = Report[Report['region'] == id_region]

      try :
        percenter_by_region['redo_n3'] = Report_region[Redo_n3].sum() / Report_region[total_arches].sum()
      except ZeroDivisionError:
        percenter_by_region['redo_n3'] = 0

      try :
        percenter_by_region['redo_n6'] = Report_region[Redo_n6].sum() / Report_region[total_arches].sum()
      except ZeroDivisionError:
        percenter_by_region['redo_n6'] = 0

      try:
        percenter_by_region['zirconia'] = Report_region[[zir_single, zir_full_month]].sum().sum() / Report_region['N4 arches'].sum()
      except ZeroDivisionError:
        percenter_by_region['zirconia'] = 0
      
      percenter_by_region['capacity'] = Report_region[['N4 arches', 'N3_redo', 'N7_total']].sum().sum() / (operation_capacity * len(list(Report_region.index)))
      
      
      percenter_by_region['delivery'] = Report_region[N_delivery_total].sum() / Report_region[N_surgeries_total].sum()



      percents_[id_region] = percenter_by_region
  return percents_


def change_to_percent_format(df):
  # Convertir las columnas de decimales a formato porcentual con 0 decimales
  columns_to_convert = ['redo', 'zirconia', 'capacity', 'delivery']

  def decimal_to_percent(value):
      return f'{int(value * 100)}%'

  # Aplicar la función a todas las celdas del DataFrame
  for column in columns_to_convert:
      df[column] = df[column].apply(decimal_to_percent)
  return df


def mean_times_per_center(datetime , products=['N3 - Full Mouth 24Z', 'N3 - G-CAM/tibar'] , status =['Post Delivery Record']):
  x = {}
  datetime = datetime[datetime['status'].isin(status)]
  datetime = datetime[datetime['product'].isin(products)]
  a = datetime.groupby('center')['checkIn'].mean()
  for j in a.index:
   x[j] = a[j].strftime('%H:%M:%S')
  x = pd.Series(x, name= 'times_lab').to_frame().T
  return pd.DataFrame(x)


def creation_of_report(database, data_finished, operation_capacity = nuvia.operation_capacity):
  error_cases, db, new_products = nuvia.check_errors(database)
  print(f'This are the new products to add : {new_products}')

  Report = create_data_counter(database , column_to_check = 'date_Out' )
  
  N3 = [x for x in set(db['product']) if 'N3' in x]
  time_lab = mean_times_per_center(db, products = N3) #add the mean times per center
  Report['Lab time'] = time_lab.T

  other_products = counter_other_products(data_finished)

  Report = pd.merge(Report , other_products ,left_index=True, right_index=True, how ='outer')
  Report = Report.fillna(0)
  
  Report['Total_arches'] = Report['N4 arches'] + Report['N7_total']
  Report['N_delivery_on_time_total']  = Report['N_delivery_on_time'] + Report['N_delivery_n3_redos_on_time'] + Report['N_delivery_n6_on_time']
  Report['N_surgeries_total'] =  Report['N_surgeries'] + Report['N_surgeries_other_products']

  Report = calculate_center_percents(Report, operation_capacity = operation_capacity)

  # creation de regiones
  Report['center'] = Report.index
  Report = nuvia.create_regions(Report).drop(['center'], axis=1)
  percents_region = pd.DataFrame(calculate_region_percents(Report, operation_capacity = operation_capacity)).T
  percents_region['region'] = percents_region.index

  return(Report, percents_region, error_cases)



'''CREATION OF THE REPORT'''

def generate_weekly_report(database_month, database_finished, dates_week, operation_capacity_week, week_of_the_report):
    Total_error_cases = pd.DataFrame()
    Total_reports = pd.DataFrame()
    Total_percents_region = pd.DataFrame()

    for week_number in range(1, week_of_the_report + 1):
        print('_'*80 + '\n Initializing the report for the week {} with the days {}'.format(week_number, dates_week[int(week_number)]))

        data_ = database_month[database_month['week_number'] == week_number]
        data_finished = database_finished[database_finished['week_number_end'] == week_number]

        Report, percents_region, error_cases = creation_of_report(data_, data_finished, operation_capacity=operation_capacity_week[week_number-1])
        Report.loc[:, 'week_number'] = week_number
        percents_region.loc[:, 'week_number'] = week_number

        Total_error_cases = pd.concat([Total_error_cases, error_cases])
        Total_reports = pd.concat([Total_reports, Report])
        Total_percents_region = pd.concat([Total_percents_region, percents_region])

        print('\n {} Report of the week {} finished \n'.format(' '*15, week_number))
    
    Total_reports['center'] = Total_reports.index
    return Total_reports, Total_percents_region, Total_error_cases


def create_monthly_report(database_month, database_finished, month_selector, operation_capacity_week):
    database_month['date_In'] = pd.to_datetime(database_month['date_In'])
    database_month.loc[database_month['date_In'].apply(lambda date: date.month == month_selector), 'created_'] = 1

    database_month['date_Out'] = pd.to_datetime(database_month['date_Out'])
    database_month.loc[database_month['date_Out'].apply(lambda date: date.month == month_selector), 'finished_'] = 1
    database_month_all = database_month[database_month['finished_'] == 1]

    database_finished['date_Out'] = pd.to_datetime(database_finished['date_Out'])
    database_finished.loc[database_finished['date_Out'].apply(lambda date: date.month == month_selector), 'finished_'] = 1
    database_finished_month = database_finished[database_finished['finished_'] == 1]

    Report_month, percents_region_month, error_cases_month = creation_of_report(database_month_all, database_finished_month, operation_capacity=sum(operation_capacity_week))
    Report_month['center'] = Report_month.index # adding the center

    return Report_month, percents_region_month, error_cases_month


def unify_monthly_database(database_month, database_finished):
    # Convert date columns to datetime
    database_month['date_In'] = pd.to_datetime(database_month['date_In'])
    database_month['date_Out'] = pd.to_datetime(database_month['date_Out'])

    database_finished['date_In'] = pd.to_datetime(database_finished['date_In'])
    database_finished['date_Out'] = pd.to_datetime(database_finished['date_Out'])

    # Define common columns for merging
    common_columns = ['invoice', 'patient', 'restorer', 'center', 'archs', 'checkIn', 'CheckOut', 'amount', 'product', 
                      'status', 'date_In', 'date_Out', 'month_In', 'month_Out', 'time_in', 'hour_in', 'time_out', 'hour_out', 
                      'diff_days', 'region', 'product class', 'material', 'arch type', 'redo type', 'diff_hour', 'delivery_on_time', 
                      'week_number', 'week_number_end', 'finished_']

    # Merge the databases based on common columns
    data_in_and_out = pd.merge(database_month[['created_'] + common_columns], database_finished[common_columns], on=common_columns, how='outer')
    
    # Create month_year column
    data_in_and_out = nuvia.create_month_year_column(data_in_and_out)
    
    return data_in_and_out



'''GCAM ANALYSIS'''

list_on_gcam = ['invoice', 'restorer', 'center', 'patient', 'product', 'archs', 'region', 'week_number', 'date_In']

def analyze_gcam_cases(database_month, dates_week, month_B, month_name, path ='lab_metric_report\Gcam_cases_studied.xlsx' ):
    Gcam_cases_of_the_report = separate_gcam_cases(database_month, dates_week)    # Separar los G-CAM cases del reporte
    gcam_to_export = update_gcam_cases(Gcam_cases_of_the_report, month_B, month_name, path) # Actualizar los G-CAM cases
    print('Analysis of the G-CAM cases finished')
    return gcam_to_export

def separate_gcam_cases(database_month, dates_week):
    Gcam_cases_ = database_month[database_month['material'].isin(['G-CAM']) & database_month['redo type'].isin(['SURGERY', 'REDO']) ]
    Gcam_cases_ = nuvia.create_regions(Gcam_cases_)
    Gcam_cases_ = nuvia.assign_week_numbers(Gcam_cases_, dates_week=dates_week)
    Gcam_cases_of_the_report = Gcam_cases_[list_on_gcam + ['date_Out', 'status', 'week_number_end']]
    return Gcam_cases_of_the_report


def update_gcam_cases(Gcam_cases_of_the_report, month_B, month_name, path):
    # Update the G-CAM cases
    gcam_cases_studied = pd.read_excel(path, sheet_name='gcam_cases_{}'.format(month_B))
    # gcam_cases_studied = gcam_cases_studied[list_on_gcam + ['why G-CAM ?', '24z processed?']]     
    
    Gcam_cases_of_the_report['date_In'] = pd.to_datetime(Gcam_cases_of_the_report['date_In'])
    # gcam_cases_studied['date_In'] = pd.to_datetime(gcam_cases_studied['date_In'])
    
    gcam_to_export = pd.merge(gcam_cases_studied[['invoice' , 'why G-CAM ?', '24z processed?']], Gcam_cases_of_the_report, on = 'invoice', how = 'outer')
    # gcam_to_export.to_excel('results/Gcam_cases_studied_false_{}.xlsx'.format(month_name), sheet_name='gcam_cases', index=False)
    return gcam_to_export


'''REDO ANALYSIS'''

def analyze_redo_cases(database_month, database_finished, month_selector, month_B, month_name , path = 'lab_metric_report\Redo_cases_studied.xlsx'):
  list_on_redos = ['invoice', 'patient', 'restorer', 'center', 'archs', 'amount', 'product', 'product class', 'region', 'material', 
                  'arch type', 'redo type', 'diff_hour', 'delivery_on_time', 'week_number', 'week_number_end']

  redo_cases = extract_redo_cases(database_month, month_selector, list_on_redos)
  redo_cases_finished = extract_finished_redo_cases(database_finished, month_selector, list_on_redos)

  redo_cases_saved = pd.read_excel(path, sheet_name=month_B)
  redo_cases_saved = redo_cases_saved[['invoice', 'redo cause', 'responsable party', 'redo form','redo reason', 'invoice surgery', 'date out surgery', 'diff months', 'recap class']]

  redo_cases_merged = pd.concat([redo_cases, redo_cases_finished])
  redo_cases_with_history_status = assign_history_status(redo_cases_merged, redo_cases_saved)
  redo_cases_with_history_status = redo_cases_with_history_status.drop_duplicates()
  # redo_cases_with_history_status.to_excel('results/Redo_cases_false_{}.xlsx'.format(month_name), index=False)
  print('Analysis of the Redo cases finished')
  return redo_cases_with_history_status

def extract_redo_cases(database_month, month_selector, list_on_redos):
  redo_cases = database_month[(database_month['redo type'] == 'REDO') & (database_month['product'] != 'N3 Redo-Removable Denture')]
  redo_cases = redo_cases[list_on_redos + ['status', 'checkIn', 'CheckOut']]
  redo_cases.loc[:, 'created_on_month'] = 1

  redo_cases['CheckOut'] = pd.to_datetime(redo_cases['CheckOut'])
  redo_cases.loc[redo_cases['CheckOut'].dt.month == month_selector, 'finished_on_month'] = 1
  return redo_cases

def extract_finished_redo_cases(database_finished, month_selector, list_on_redos):
  redo_cases_finished = database_finished[database_finished['redo type'] == 'REDO']
  redo_cases_finished = redo_cases_finished[list_on_redos + ['status', 'checkIn', 'CheckOut']]

  redo_cases_finished['checkIn'] = pd.to_datetime(redo_cases_finished['checkIn'])
  redo_cases_finished = redo_cases_finished[redo_cases_finished['checkIn'].dt.month != month_selector]
  redo_cases_finished.loc[:, 'finished_on_month'] = 1
  return redo_cases_finished


def assign_history_status(redo_cases_merged, redo_cases_saved):
    redo_cases_merged.loc[~redo_cases_merged['invoice'].isin(redo_cases_saved['invoice']), 'history-status'] = 'new'
    redo_cases = pd.merge(redo_cases_merged, redo_cases_saved, on='invoice', how='left')
    return redo_cases


'''GCAM/PMMA WAITING FOR 24Z'''

def load_old_database(name_old_database = f"data\checkIn_all.xlsx"  ):
    return pd.read_excel(name_old_database)


def count_gcam_waiting_for_24z(database_month, month_selector, year_selector = 2023):
    specific_date = f"{year_selector}-{month_selector}-01"
    db_old = load_old_database( name_old_database = f"data\checkIn_all.xlsx"  )
    db_old['checkIn'] = pd.to_datetime(db_old['checkIn'], format='ISO8601')
    db_old = db_old[db_old['checkIn'] < specific_date]

    db_old = nuvia.create_caracteristics(db_old)

    db_total = pd.concat([database_month, db_old])
    db_total['date_Out'] = pd.to_datetime(db_total['date_Out'])

    Gcam_total, pmma_df = nuvia.count_GCAM_waiting_to_24Z(db_total)
    Gcam_total = nuvia.create_regions(Gcam_total)

    print('Counting the G-CAM cases waiting for 24z arches finished')
    return Gcam_total , db_total, db_old


'''N6 cases studied'''

def extract_material_change_cases(database_month, month_selector, list_on_redos):
  material_change_cases = database_month[ (database_month['product class']=='N6') & (database_month['redo type'].isin(['SURGERY','REMAKE'])) ]
  material_change_cases = material_change_cases[list_on_redos + ['status', 'checkIn', 'CheckOut']]
  material_change_cases.loc[:, 'created_on_month'] = 1

  material_change_cases['CheckOut'] = pd.to_datetime(material_change_cases['CheckOut'])
  material_change_cases.loc[material_change_cases['CheckOut'].dt.month == month_selector, 'finished_on_month'] = 1
  return material_change_cases

def extract_finished_material_change_cases(database_finished, month_selector, list_on_redos):
  material_change_cases_finished = database_finished[ (database_finished['product class']=='N6') & (database_finished['redo type'].isin(['SURGERY','REMAKE'])) ]
  material_change_cases_finished = material_change_cases_finished[list_on_redos + ['status', 'checkIn', 'CheckOut']]

  material_change_cases_finished['checkIn'] = pd.to_datetime(material_change_cases_finished['checkIn'])
  material_change_cases_finished = material_change_cases_finished[material_change_cases_finished['checkIn'].dt.month != month_selector]
  material_change_cases_finished.loc[:, 'finished_on_month'] = 1
  return material_change_cases_finished


def assign_history_status_material_change(material_change_cases_merged, material_change_cases_saved):
    material_change_cases_merged.loc[~material_change_cases_merged['invoice'].isin(material_change_cases_saved['invoice']), 'history-status'] = 'new'
    material_change_cases = pd.merge(material_change_cases_merged, material_change_cases_saved, on='invoice', how='left')
    return material_change_cases


def analyze_material_change_cases(database_month, database_finished, month_selector, month_B, month_name , path = 'lab_metric_report\material_change_cases_studied.xlsx'):
  list_on_n6 = ['invoice', 'patient', 'restorer', 'center', 'archs', 'amount', 'product', 'product class', 'region', 'material', 
                  'arch type', 'redo type', 'diff_hour', 'delivery_on_time', 'week_number', 'week_number_end']

  n6_cases = extract_material_change_cases(database_month, month_selector, list_on_n6)
  n6_cases_finished = extract_finished_material_change_cases(database_finished, month_selector, list_on_n6)

  n6_cases_saved = pd.read_excel(path, sheet_name=month_B)
  n6_cases_saved = n6_cases_saved[['invoice', 'redo cause', 'responsable party', 'redo reason', 'invoice surgery', 'date out surgery', 'diff months', 'recap class']]

  n6_cases_merged = pd.concat([n6_cases, n6_cases_finished])
  n6_cases_with_history_status = assign_history_status_material_change(n6_cases_merged, n6_cases_saved)
  n6_cases_with_history_status = n6_cases_with_history_status.drop_duplicates()
  # n6_cases_with_history_status.to_excel('results/material_change_cases_false_{}.xlsx'.format(month_name), index=False)
  print('Analysis of the material_change cases finished')
  return n6_cases_with_history_status










