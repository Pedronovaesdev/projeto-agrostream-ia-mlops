import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data.csv', sep=";", decimal=",")
print(df.head())

#feature de risco
cond1 = (df['greenhous_temperature_celsius'] > 32 ) & (df['greenhouse_humidity_percentage'] < 40)
cond2 = (df['greenhouse_equivalent_co2_ppm'] > 2000)
df['stress_risk'] = (cond1 | cond2).astype(int)

print("Valores ausentes:")
print(df.isnull().sum())
print("\n Estatísica Descritiva: ")
stats_summary = df.describe()
print(stats_summary)
stats_summary.to_csv('../extracted_features/stats_summary.csv')


# Análise Univariada (Distribuições)
fig, axes = plt.subplot(2, 2, figsize=(14,10))
sns.histplot(df['greenhous_temperature_celsius'], ax=axes[0,0], color='salmon')
axes[0,0].set_title('Distribuição de Temperatura')

sns.histplot(df['greenhouse_humidity_percentage'], ax=axes[0,1], color='skyblue')
axes[0,1].set_title('Distribuição de Umidade')

sns.histplot(df['greenhouse_equivalent_co2_ppm'], ax=axes[1,0], color='lightgreen')
axes[1,0].set_title('Distribuição de CO2')

sns.histplot(df['online_temperature_celsius'], kde=True, ax=axes[1, 1], color='gray')
axes[1, 1].set_title('Distribuição da Temperatura (Online/Externa)')

plt.tight_layout()
plt.savefig("../extracted_features/univariante.png")
plt.close()

# Análise Bivariada
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x='greenhous_temperature_celsius',
    y='greenhouse_humidity_percentage',
    hue='stress_risk',
    style='stress_risk',
    palette={0: 'blue', 1: 'red'},
    markers={0: 'o', 1: 's'},
    s=100,
    alpha=0.7
)
plt.title('Risco de Estresse por Temperatura e Umidade')
plt.xlabel('Temperatura (°C)')
plt.ylabel('Umidade (%)')
plt.legend(title='Risco de Estresse', loc='upper right')
plt.savefig("../extracted_features/bivariante.png")
plt.close()

# 4. Análise Multivariada (Correlação)
plt.figure(figsize=(10, 8))
num_df = df.select_dtypes(include=['float64', 'int64', 'int32']).drop(columns=['id', 'stress_risk'])
corr_matrix = num_df.corr()

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1, linewidths=0.5)
plt.title('Multivariada: Matriz de Correlação')
plt.tight_layout()
plt.savefig('3_multivariada.png')
plt.close()

print("\nImagens geradas com sucesso.")