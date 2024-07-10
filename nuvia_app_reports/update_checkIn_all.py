import pandas as pd 
data_in = pd.DataFrame()

#take all the data
years_ = [2022,2023,2024]

for year_ in years_:
    excel_name_ = f"data/{year_}/data_in_{year_}.xlsx"
    data_in_year = pd.read_excel(excel_name_)
    data_in = pd.concat([data_in, data_in_year], axis =0)

path_excel = f"data/checkIn_all.xlsx"
data_in.to_excel(path_excel, index = False)