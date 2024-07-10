import pandas as pd 

redo_study = pd.read_excel('data/2024/Redo_cases_studied.xlsx', sheet_name='january') 
inventory = pd.read_excel('data/january_inventory.xlsx', sheet_name='january')


# print(redo_study.columns , inventory.columns)




# # Set 'named' column as index in df2
# redo_study.set_index('invoice', inplace=True)

# # Create a dictionary to map values from df1 to df2
# mapping_dict = redo_study.to_dict()


# # Map values from df1 to df2 using the 'named' column
# for name_ in ['redo cause','responsable party', 'redo form', 'redo reason']:
#     inventory.loc[inventory['redo type']== 'REDO', name_] = inventory.loc[inventory['redo type']== 'REDO','invoice'].map(mapping_dict[name_])

# inventory.to_excel('new_inventory.xlsx')




new_invetory = pd.read_excel('results/_new_inventory.xlsx')


df = inventory
main_df = new_invetory


df.set_index('invoice', inplace=True)
mapping_dict = df.to_dict()

cols_ = ['redo reason']

for name_ in cols_:
    main_df.loc[main_df['redo type']== 'REMAKE', name_] = main_df.loc[main_df['redo type']== 'REMAKE','invoice'].map(mapping_dict[name_])

main_df.to_excel('results/final_inventory.xlsx',sheet_name="January")