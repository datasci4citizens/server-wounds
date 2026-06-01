import pandas as pd

df = pd.read_csv('identification_model/labels.csv')
data_unique = df['tissue_type'].unique()
print(data_unique)

label_counts = df['tissue_type'].value_counts()
print(label_counts)
