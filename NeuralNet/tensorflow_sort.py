import tensorflow.keras
import cv2
import numpy as np
from passwords import Key
import requests, json

# Create SystemLink Functions

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = requests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = requests.get(urlValue,headers=headers).text
          data = json.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          requests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = tensorflow.keras.models.load_model('keras_model.h5')

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Open Preview window
cv2.namedWindow("Preview")
# Instantiate Video Capture class
vc = cv2.VideoCapture(0)

#resize the image to a 224x224 with the same strategy as in TM2:
#resizing the image to be at least 224x224 and then cropping from the center
crop_size = 480
size = (224, 224)
model_classes = ["1x2", "1x3", "2x2", "2x3", "2x4", "None"]

if vc.isOpened():
    rval, image = vc.read()
else:
    rval = False
# Find image center
height = image.shape[0]
width = image.shape[1]
center_x = int(width/2)
center_y = int(height/2)
print(width)
print(height)
print(center_x)
print(center_y)


while rval:
    
    rval, image = vc.read()
    # Crop the image
    crop_image = image[(center_y - int(crop_size/2)):(center_y + int(crop_size/2)), (center_x - int(crop_size/2)):(center_x + int(crop_size/2))]
    crop_image = cv2.resize(crop_image, size, interpolation= cv2.INTER_AREA)
    height = crop_image.shape[0]
    width = crop_image.shape[1]
    
    cv2.imshow("Preview", crop_image)
    # Normalize the array
    normalized_image_array = (crop_image.astype(np.float32) / 127.0) - 1
    # Load the image array into the data
    data[0] = normalized_image_array
    # Run prediction
    prediction = model.predict(data)
    prediction = prediction[0]
    #print(prediction)
    max_predict = 0

    for i in range(len(prediction)):
        if prediction[i] > max_predict:
            max_predict = prediction[i]
            i_max = i
    
    Put_SL("brickType", "STRING", str(i_max))

    print("Most Likely {}".format(model_classes[i_max]))
            
    key = cv2.waitKey(20)
    if key == 27:
        break


cv2.destroyWindow("Preview")
