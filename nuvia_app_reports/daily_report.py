import nuvia

data_out = nuvia.pd.DataFrame()

#take all the data
years_ = [2024]
months_ = [2,3,4,5]

for year_ in years_:
    excel_name_ = f"data/{year_}/data_out_{year_}.xlsx"
    data_out_year = nuvia.pd.read_excel(excel_name_)
    data_out = nuvia.pd.concat([data_out, data_out_year], axis =0)

#agregar el ultimo mes
excel_name_ = f"data/2024/5/week_finished_.xlsx"
data_month = nuvia.pd.read_excel(excel_name_)
data_out = nuvia.pd.concat([data_out, data_month])


data_out = nuvia.create_caracteristics(data_out)
print('All data catched...')

data_out.loc[data_out['product class'].isin(['N3']) , 'daily report'] = 'N3'
data_out.loc[(data_out['product class'].isin(['N3'])) & (data_out['redo type'].isin(['REDO'])) , 'daily report'] = 'N3 REDO'
data_out.loc[data_out['mixed_material'].isin(['24Z', 'G-CAM']) , 'daily report'] = 'Fixed arch'
data_out.loc[(data_out['product class'].isin(['N6']))  , 'daily report'] = 'N6'
data_out.loc[(data_out['product class'].isin(['N6'])) & (data_out['redo type'].isin(['REDO', 'REMAKE'])) , 'daily report'] = 'N6 REDO'
data_out.loc[data_out['material'].isin(['Reline']) , 'daily report'] = 'Reline'
data_out.loc[data_out['material'].isin(['Dummy']) , 'daily report'] = 'Dummy'
data_out.loc[data_out['material'].isin(['Single 24Z Processing']) , 'daily report'] = 'Single 24Z Processing'
data_out.loc[data_out['material'].isin(['Night guard']) , 'daily report'] = 'Night guard'

data_out.loc[data_out['material'].isin(['Demodenture']) , 'daily report'] = 'Demodenture'
data_out.loc[data_out['material'].isin(['Wax Rims']) , 'daily report'] = 'Wax Rims'
data_out.loc[data_out['material'].isin(['Removable Single']) , 'daily report'] = 'Removable Single'
data_out.loc[data_out['material'].isin(['STOCK DEMO']) , 'daily report'] = 'STOCK DEMO'

data_out.loc[data_out['product'].isin(['N3 - Screw Retained']) , 'daily report'] = 'Screw'


pivot_table = data_out.pivot_table(values = 'archs', index=['center','month_Out', 'date_Out'], columns ='daily report',aggfunc='sum')
pivot_table.reset_index(inplace=True)
pivot_table['day_of_week'] = nuvia.pd.to_datetime(pivot_table['date_Out']).dt.strftime('%A')

cols_ = ['center','month_Out','day_of_week', 'date_Out', 'N3', 'N3 REDO','Fixed arch', 'N6', 'N6 REDO', 'Dummy', 'Night guard', 'Reline', 'Single 24Z Processing', 'Demodenture', 'Wax Rims', 'Removable Single' , 'STOCK DEMO', 'Screw']
pivot_table = pivot_table[cols_]


centers_ = ['DETROIT OFFICE']
pivot_table = pivot_table[pivot_table['center'].isin(centers_)]
pivot_table = pivot_table[pivot_table['month_Out'].isin(months_)]
pivot_table = pivot_table[pivot_table['day_of_week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
# pivot_table = pivot_table[pivot_table['date_Out'].dt.year == 2024]


df_to_exports = []
df_to_exports.append({'name':'detroit' , 'df':pivot_table, 'index':False })

nuvia.create_multiple_worksheet(df_to_exports,f"results/daily_report_.xlsx")

