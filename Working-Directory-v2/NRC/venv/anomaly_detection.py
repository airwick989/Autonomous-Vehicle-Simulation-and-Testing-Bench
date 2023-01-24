from pycaret.anomaly import load_model, predict_model
import pandas as pd

UNSEEN_DATA_SIZE = 10000
messages_results_path = '../Files/Results/Messages/'
intervals_results_path = '../Files/Results/Intervals/'

#Parse the log file
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

#MESSAGES#####################################################################################################################################################

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
anom_samples = anom_samples.drop('Anomaly', axis=1)
anom_uniq = anom_samples['data'].drop_duplicates()
anom_uniq_count = anom_uniq.count()
anom_dup_count = anom_count - anom_uniq_count
anom_dup_percentage = round((anom_dup_count/anom_count)*100, 2)

str_anom_uniq = "\n"
for anom in anom_uniq:
    str_anom_uniq = str_anom_uniq + str(anom) + "\n"

with open(f'{messages_results_path}message_anomaly_statistics.txt', 'w+') as f:
    f.write(
        f'''Anomalous Percentage: {anom_percentage}% 
        \n{anom_count}/{UNSEEN_DATA_SIZE} messages were predicted to be anomalous.
        \n{anom_dup_count} or {anom_dup_percentage}% of the anomalous messages were duplicates, meaning there were only {anom_uniq_count} unique anomalies.
        \nFactoring in duplicates, that means {anom_uniq_count} or {(anom_uniq_count/UNSEEN_DATA_SIZE)*100}% of the messages were unique and anomalous.
        \nUnique Anomalies Found:{str_anom_uniq}
    ''')

####

#Save predictions to csv
predicitons.to_csv(f'{messages_results_path}message_anomaly_predictions.csv', encoding='utf-8')
anom_samples.to_csv(f'{messages_results_path}message_anomalies.csv', encoding='utf-8')

message_predictions = predicitons
message_anom_samples = anom_samples

print("CAN bus message data processed\n")


#INTERVALS###################################################################################################################################################################



#Prepare the data
df_unseen = timestamps
df_unseen = list(map(float, df_unseen))
for i in range(len(df_unseen) - 1, 0, -1):
    df_unseen[i] = df_unseen[i] - df_unseen[i-1]
del df_unseen[0]
df_unseen = pd.DataFrame(df_unseen, columns=['intervals'])
messages = data[-UNSEEN_DATA_SIZE:]
del messages[0]

#Use saved model to perform predictions
anom_model = load_model('interval_anomaly_detection_model')
predicitons = predict_model(model=anom_model, data=df_unseen)
del timestamps[0]
predicitons['timestamps'] = timestamps

####

#Numeric Results
results = predicitons['Anomaly'].value_counts()
anom_count = results[1]
anom_percentage = round((anom_count/UNSEEN_DATA_SIZE)*100, 2)

anom_samples = predicitons[predicitons['Anomaly'] == 1]
anom_messages = []
for index in anom_samples.index.values.tolist():
    anom_messages.append(messages[index])
anom_samples['Data'] = anom_messages
anom_samples = anom_samples.drop('Anomaly', axis=1)

anom_mean = anom_samples['intervals'].mean()
anom_min_index = anom_samples[anom_samples['intervals'] == anom_samples['intervals'].min()].index[0]
anom_max_index = anom_samples[anom_samples['intervals'] == anom_samples['intervals'].max()].index[0]

with open(f'{intervals_results_path}intervals_anomaly_statistics.txt', 'w+') as f:
    f.write(
        f'''Anomalous Percentage: {anom_percentage}% 
        \n{anom_count}/{UNSEEN_DATA_SIZE} messages were predicted to be anomalous.
        \nThe mean value of an anomalous time interval: {anom_mean}
        \nThe smallest anomalous time interval is: {anom_samples['intervals'][anom_min_index]} (Message: {anom_samples['Data'][anom_min_index]}, Timestamp: {anom_samples['timestamps'][anom_min_index]})
        \nThe largest anomalous time interval is: {anom_samples['intervals'][anom_max_index]} (Message: {anom_samples['Data'][anom_max_index]}, Timestamp: {anom_samples['timestamps'][anom_max_index]})
    ''')

#Save predictions to csv
predicitons.to_csv(f'{intervals_results_path}interval_anomaly_predictions.csv', encoding='utf-8')
anom_samples.to_csv(f'{intervals_results_path}interval_anomalies.csv', encoding='utf-8')

interval_predictions = predicitons
interval_anom_samples = anom_samples

print("CAN bus message intervals processed\n")


#BOTH########################################################################################################################################################################


# #Gives both dataframes a commonly named column to join on
# message_anom_samples = message_anom_samples.rename(columns={"Timestamps": "timestamps"})

# #join both dataframes by common timestamps, because that will ensure they are the exact same sample
# both_anom_samples = pd.merge(message_anom_samples, interval_anom_samples, on="timestamps")

# print(f'anomalous messages:{len(message_anom_samples.index)}')
# print(f'anomalous intervals:{len(interval_anom_samples.index)}')
# print(f'anomalous both:{len(both_anom_samples.index)}')

# #Just double checking that there actually is zero overlap in the data
# common = False
# for item in message_anom_samples['Timestamps']:
#     if item in interval_anom_samples['timestamps'].values:
#         common = True
# print(common)