import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt

# Cargar los datos desde un archivo CSV
df = pd.read_excel('data/diff_measures.xlsx', sheet_name='diff_values')

# Reestructurar el DataFrame para ANOVA
df_melt = pd.melt(df, id_vars=['center'], value_vars=['diff lab-design loer right posterior', 'diff lab-design lower left posterior', 'diff lab-design upper right posterior', 'diff lab-design upper left posterior'])
df_melt.columns = ['center', 'variable', 'value']

# Ajustar el modelo ANOVA
model = ols('value ~ C(variable) + C(center)', data=df_melt).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

# Mostrar los resultados
print(anova_table)

# Crear un boxplot para visualizar las distribuciones
# plt.figure(figsize=(10, 6))
boxplot = df_melt.boxplot(column='value', by='variable', grid=True)
plt.title('Distribución de valores por variable')
# plt.suptitle('')
plt.xlabel('Center')
plt.ylabel('Valor')
plt.show()
