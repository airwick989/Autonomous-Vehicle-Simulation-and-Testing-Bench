import time
import requests
import cv2
import operator
import numpy as np
import csv

#_url = 'https://emotiondetectorcapstone.cognitiveservices.azure.com/emotion/v1.0/recognize'
_url = 'https://cloud-assignment2.cognitiveservices.azure.com/face/v1.0/detect?returnFaceId=false&returnFaceLandmarks=false&returnFaceAttributes=emotion&recognitionModel=recognition_02&returnRecognitionModel=false&detectionModel=detection_01'
_key = 'e0916204a5014ca7ad6101b42e12573e'
_maxNumRetries = 10

def processRequest( json, data, headers, params ):

    retries = 0
    result = None

    while True:

        response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

        if response.status_code == 429: 

            print( "Message: %s" % ( response.json()['error']['message'] ) )

            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
                result = None 
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
                if 'application/json' in response.headers['content-type'].lower(): 
                    result = response.json() if response.content else None 
                elif 'image' in response.headers['content-type'].lower(): 
                    result = response.content
        else:
            print( "Error code: %d" % ( response.status_code ) )
            print( "Message: %s" % ( response.json()['error']['message'] ) )

        break
        
    return result

oldtime = time.time()

while True:
	if time.time() - oldtime > 45:
		pathToFileInDisk = r'face.jpeg'
		with open( pathToFileInDisk, 'rb' ) as f:
			data = f.read()

		headers = dict()
		headers['Ocp-Apim-Subscription-Key'] = _key
		headers['Content-Type'] = 'application/octet-stream'

		json = None
		params = None

		result = processRequest( json, data, headers, params )
	
		if result is not None:
			try:
				ts = time.localtime()
				currFace = result[0]['faceAttributes']['emotion']
				print("got results")
				emotionList = currFace.keys()
				emotionValueList = currFace.values()
				maxValue = max(emotionValueList)
				emotion = (list(currFace.keys())[list(currFace.values()).index(maxValue)])
				#print("emotion:",emotion,"value:",maxValue)
				#write currEmotion to csv file
				with open(r'emotions.csv', 'a', newline='') as csvfile:
					fieldnames = ['Emotions','Timestamp']
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					writer.writerow({'Emotions':emotion, 'Timestamp':time.strftime("%Y-%m-%d %H:%M:%S", ts)})
				oldtime = time.time()
				print("file saved\n")
			except:
				oldtime = time.time()
				pass
	
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break