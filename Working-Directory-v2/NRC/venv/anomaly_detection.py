from pycaret.anomaly import load_model, predict_model
import pandas as pd

UNSEEN_DATA_SIZE = 10000
results_path = '../Files/Results/Messages/'

data = []
timestamps = []
with open('../Files/candump-2022-12-14_100719.log', 'r') as f:
    for line in f:
        line = line.split(" ")
        timestamp = line[0]
        line = line[2]
        line = line.strip("\n")
        data.append(line)

        timestamp = timestamp.strip("\n").strip("(").strip(")")
        timestamps.append(timestamp)

df_unseen = data[-UNSEEN_DATA_SIZE:]
df_unseen = pd.DataFrame(df_unseen, columns=['data'])
timestamps = timestamps[-UNSEEN_DATA_SIZE:]

# print(df_unseen)

#Use saved model to perform predictions
anom_model = load_model('anomaly_detection_model')
predicitons = predict_model(model=anom_model, data=df_unseen)

####

#Numeric Results
results = predicitons['Anomaly'].value_counts()
anom_count = results[1]
anom_percentage = round((anom_count/UNSEEN_DATA_SIZE)*100, 2)

anom_samples = predicitons[predicitons['Anomaly'] == 1]
anom_timestamps = []
for index in anom_samples.index.values.tolist():
    anom_timestamps.append(timestamps[index])
anom_samples['Timestamps'] = anom_timestamps
anom_uniq_count = anom_samples['data'].drop_duplicates().count()
anom_dup_count = anom_count - anom_uniq_count
anom_dup_percentage = round((anom_dup_count/anom_count)*100, 2)

with open(f'{results_path}message_anomaly_results.txt', 'w+') as f:
    f.write(
        f'''Anomalous Percentage: {anom_percentage}% 
        \n{anom_count}/{UNSEEN_DATA_SIZE} messages were predicted to be anomalous.
        \n{anom_dup_count} or {anom_dup_percentage}% of the anomalous messages were duplicates, meaning there were only {anom_uniq_count} unique anomalies.
        \nFactoring in duplicates, that means {anom_uniq_count} or {(anom_uniq_count/UNSEEN_DATA_SIZE)*100}% of the messages were unique and anomalous.
    ''')

####

#Save predictions to csv
predicitons.to_csv(f'{results_path}message_anomaly_predictions.csv', encoding='utf-8')