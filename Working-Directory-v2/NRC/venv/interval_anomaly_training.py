from pycaret.anomaly import setup, create_model, assign_model, save_model
import pandas as pd

UNSEEN_DATA_SIZE = 10000
results_path = '../Files/Results/Timestamps/'

timestamps = []
with open('../Files/candump-2022-12-14_100719.log', 'r') as f:
    for line in f:
        line = line.split(" ")
        timestamp = line[0]
        timestamp = timestamp.strip("\n").strip("(").strip(")")
        timestamps.append(timestamp)

df_train = timestamps[0:-UNSEEN_DATA_SIZE]
df_train = list(map(float, df_train))
for i in range(len(df_train) - 1, 0, -1):
    df_train[i] = df_train[i] - df_train[i-1]
del df_train[0]
df_train = pd.DataFrame(df_train, columns=['intervals'])
#df_train.to_csv(f'{results_path}test.csv', encoding='utf-8')

# df_unseen = timestamps[-UNSEEN_DATA_SIZE:]
# df_unseen = list(map(float, df_unseen))
# for i in range(len(df_unseen) - 1, 0, -1):
#     df_unseen[i] = df_unseen[i] - df_unseen[i-1]
# del df_unseen[0]
# df_unseen = pd.DataFrame(df_unseen, columns=['intervals'])
# df_unseen.to_csv(f'{results_path}test.csv', encoding='utf-8')


####

#Training and saving the model
anom = setup(data= df_train, silent=True)
anom_model = create_model(model = 'iforest')
results = assign_model(anom_model)
save_model(model = anom_model, model_name='interval_anomaly_detection_model')