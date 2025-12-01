import pandas as pd

# Load data
df = pd.read_csv('Amazon.csv')

# Basic info
print('Shape:', df.shape)
print('\nColumns:')
print(df.columns.tolist())
print('\n\nFirst 5 rows:')
print(df.head(5))
print('\n\nData types:')
print(df.dtypes)
print('\n\nMissing values:')
print(df.isnull().sum())
print('\n\nBasic statistics:')
print(df.describe())
print('\n\nUnique values in categorical columns:')
for col in ['Category', 'PaymentMethod', 'OrderStatus', 'Country']:
    if col in df.columns:
        print(f'\n{col}: {df[col].nunique()} unique values')
        print(df[col].value_counts().head(10))
