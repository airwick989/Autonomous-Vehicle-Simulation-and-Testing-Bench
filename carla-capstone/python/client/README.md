This application will monitor the eyes of the driver and check to see if driver is paying attention or not.
If the driver is not paying attention by not looking at the road ahead then it a alarm sound will be played.
The alarm gets triggered if the face is not detected within frame for more than 3 seconds, or if the eyes are closed for more than 3 seconds. The algorithm uses dlib library and a facial landmark detection model file. We have modified the algorithm by Adrian Rosebrock
to meet our needs. For this application to work it requires the sound file, and facial landmark model file and a webcam. 
For this project we are using a logitech webcam with a 720p resoultion. 

To run this application you need to install dlib. <code>pip install dlib</code>
<br>
Start the application: <code>python capture.py</code>
