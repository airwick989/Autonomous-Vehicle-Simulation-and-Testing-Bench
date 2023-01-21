from pycaret.anomaly import *
import pandas as pd

UNSEEN_DATA_SIZE = 10000
data = []
with open('../Files/candump-2022-12-14_100719.log', 'r') as f:
    for line in f:
        line = line.split(" ")
        line = line[2]
        line = line.strip("\n")
        data.append(line)

df_train = data[0:-UNSEEN_DATA_SIZE]
df_train = pd.DataFrame(df_train, columns=['data'])
df_unseen = data[-UNSEEN_DATA_SIZE:]
df_unseen = pd.DataFrame(df_unseen, columns=['data'])

print(df_train)
print(df_unseen)

# anom = setup(data= df_train, silent=True)
# anom_model = create_model(model = 'iforest')
# results = assign_model(anom_model)
# save_model(model = anom_model, model_name='anomaly_detection_model')