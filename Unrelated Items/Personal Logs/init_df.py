import pandas as pd

PAY = 140

data = {
    'Date': ['2022/05/09'],
    'Amount': [PAY],
    'Hours': [0.42],
    'Hourly Pay': [333.33]
}
df1 = pd.DataFrame(data)

df1.to_csv('')