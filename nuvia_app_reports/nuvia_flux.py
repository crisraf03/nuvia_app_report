import pandas as pd
import os
print('loading nuvia flux module')

def generate_month_groups(month_start, month_finish):
    group_months = {}

    for sublist in range(month_start, month_finish + 1):
        group_months[str(sublist)] = []

        for num in range(sublist, month_finish + 1):
            group_months[str(sublist)].append((sublist, num))

    return group_months


def counter_arches_(db_,  description_column = 'center'):
    N3_condition = db_['product class'].isin(['N3'])
    gcam_condition = db_['material'].isin(['G-CAM'])
    redo_condition = db_['redo type'].isin(['REDO' , 'REMAKE'])
    responsable_party_condition = db_['amount'] != 0

    arches_ = db_[N3_condition].groupby(description_column)['archs'].sum().to_frame('arches')
    gcam_ = db_[N3_condition & gcam_condition].groupby(description_column)['archs'].sum().to_frame('G-CAM arches')
    redo_arches = db_[N3_condition & redo_condition].groupby(description_column)['archs'].sum().to_frame('redo arches')

    columns_to_export = ['patient' , 'center' , 'restorer', 'material', 'product', 'archs']
    redos_month = db_[N3_condition & redo_condition][columns_to_export]

    redo_arches_clinic = db_[N3_condition & redo_condition & responsable_party_condition].groupby(description_column)['archs'].sum().to_frame('redo arches clinic')
    report = pd.concat( [arches_ , gcam_ , redo_arches , redo_arches_clinic ], axis = 1)
    return report, redos_month


def counter_becomes_arches_(db_ , db_next_month , description_columns = 'center'):
    N3_condition = db_['product class'].isin(['N3'])
    db_n3 = db_[N3_condition]

    patient_condition = db_next_month['patient'].isin(db_n3['patient'])
    db_nx_patient = db_next_month [patient_condition]
    
    redo_condition = db_nx_patient['redo type'] == 'REDO'
    remake_condition = db_nx_patient['redo type'] == 'REMAKE'
    dummy_condition = db_nx_patient['material'] == 'Dummy'
    reline_condition = db_nx_patient['material'] == 'Reline'
    N6_condition = db_nx_patient['product class'] == 'N6'
    N5_condition = db_nx_patient['product class'] == 'N5'

    becomes_redo = db_nx_patient[redo_condition].groupby(description_columns)['archs'].sum().to_frame('becomes redo')
    becomes_remake = db_nx_patient[remake_condition].groupby(description_columns)['archs'].sum().to_frame('becomes remake')
    becomes_dummy = db_nx_patient[dummy_condition].groupby(description_columns)['archs'].sum().to_frame('becomes dummy')
    becomes_reline = db_nx_patient[reline_condition].groupby(description_columns)['archs'].sum().to_frame('becomes reline')
    becomes_mc = db_nx_patient[N6_condition].groupby(description_columns)['archs'].sum().to_frame('becomes material change')
    becomes_two_weeks_record = db_nx_patient[N5_condition].groupby(description_columns)['archs'].sum().to_frame('becomes two weeks records')

    report_materials = pd.concat( [becomes_redo , becomes_remake , becomes_dummy , becomes_reline ,becomes_mc, becomes_two_weeks_record] ,axis = 1)
    return report_materials , db_nx_patient


def generate_report_(data_finished, data_finished_next_month , description_column = 'center'):
    report_ , redos_month = counter_arches_(data_finished,  description_column = description_column )
    report__ , db_nx_patient = counter_becomes_arches_(data_finished , data_finished_next_month , description_columns = description_column)
    y_ = pd.concat([report_ , report__] , axis=1)
    return y_ , redos_month , db_nx_patient


def process_data_for_month(data_cold, checkout_column, year_selector, data_selector, selected_month_start, selected_month_end, description_column = 'center'):
       
    data_cold[checkout_column] = pd.to_datetime(data_cold[checkout_column])
    data_cold.loc[data_cold[checkout_column].dt.year == year_selector, f"year_{data_selector}"] = pd.to_datetime(data_cold[checkout_column]).dt.year
    data_cold = data_cold[data_cold[f'year_{data_selector}'] == year_selector]

    data_finished_on_month = data_cold[data_cold['month_Out'] == selected_month_start]
    data_finished_next_month = data_cold[data_cold['month_Out'] == selected_month_end]

    report, redos_month, db_nx_patient = generate_report_(data_finished_on_month, data_finished_next_month, description_column= description_column) 
    return report, redos_month, db_nx_patient



