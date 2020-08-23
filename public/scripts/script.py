import json
import numpy as np
import glob
import datetime
import pandas as pd
from os import listdir
import csv

#Sacamos los puntos de interes de las manos del JSON en el formato [[x1,y2],[x2,y2],...]
#Le pasas el array de la mano que quieres extraer
def getHandKeypoints(handPointsWithoutFormat, leftHand, rightHand, bodyKeyPoints):
  response = []
  for index in range(0,len(handPointsWithoutFormat),3):
    firstKeyPoint = np.array([handPointsWithoutFormat[index],handPointsWithoutFormat[index+1]])
    response.append(firstKeyPoint)
  return response


#Sacamos los puntos de interes del cuerpo del JSON en el formato [[x1,y2],[x2,y2],...]
def getBodyKeyPoints(bodyPointsWithoutFormat):
  response = []
  ## Cuello
  pointOne = np.array([bodyPointsWithoutFormat[(1*3)],bodyPointsWithoutFormat[(1*3)+1]])
  response.append(pointOne)
  ## Hombro derecho 
  pointTwo = np.array([bodyPointsWithoutFormat[(2*3)],bodyPointsWithoutFormat[(2*3)+1]])
  response.append(pointTwo)
  ## Codo derecho 
  pointThree = np.array([bodyPointsWithoutFormat[(3*3)],bodyPointsWithoutFormat[(3*3)+1]])
  response.append(pointThree)
  ## Muñeca derecha 
  pointFour = np.array([bodyPointsWithoutFormat[(4*3)],bodyPointsWithoutFormat[(4*3)+1]])
  response.append(pointFour)
  ## Hombro izquierdo 
  pointFive = np.array([bodyPointsWithoutFormat[(5*3)],bodyPointsWithoutFormat[(5*3)+1]])
  response.append(pointFive)
  ## Codo izquierdo 
  pointSix = np.array([bodyPointsWithoutFormat[(6*3)],bodyPointsWithoutFormat[(6*3)+1]])
  response.append(pointSix)
  ## Muñeca izquierda 
  pointSeven = np.array([bodyPointsWithoutFormat[(7*3)],bodyPointsWithoutFormat[(7*3)+1]])
  response.append(pointSeven)
  return response

#Calculamos el coeficiente escalar segun la formula
def getScallingCoefficient(bodyKeyPoints):
  counter = np.array([0,0])
  for index in range(0,len(bodyKeyPoints)):
    if(index == 1 or index == 4):
      counter = counter + (abs(bodyKeyPoints[index] - bodyKeyPoints[0]))
    elif index != 0:
      counter = counter + (abs(bodyKeyPoints[index] - bodyKeyPoints[index-1]))
  return 1/counter

#Calculamos el vector regularizado que es restar cada punto con el punto del cuello
#Los parametros estan en la forma de [ [x,y], [x,y] ]
def getRegularizedVector(bodyKeyPoints,leftHandKeyPoints,rightHandKeyPoints):
  response = []
  # response.append(bodyKeyPoints[0])  
  for index in range(1,len(bodyKeyPoints)):
    response.append(bodyKeyPoints[index] - bodyKeyPoints[0])
  
  for index in range(0,len(leftHandKeyPoints)):
    response.append(leftHandKeyPoints[index] - bodyKeyPoints[0])

  for index in range(0,len(rightHandKeyPoints)):
    response.append(rightHandKeyPoints[index] - bodyKeyPoints[0])
  return response
  
#Obtener el vector final (Multiplicar el escalar por el vector regularizado)
def calculateFinalVector(bodyKeyPoints,leftHandKeyPoints,rightHandKeyPoints):
  return getRegularizedVector(bodyKeyPoints,leftHandKeyPoints,rightHandKeyPoints) * getScallingCoefficient(bodyKeyPoints)


  #"../gdrive/My Drive/SeminarioLSB/DataSetLSB/DataSetLSB/NuevosVideos/Resultados/PersonaALaDer/*.json" Ejemplo de entrada
def getFilesFromOneDirectory(directory):
  return glob.glob(directory)

#Devuelve los puntos de las manos y cuerpo tal cual esta en OpenPose con el accuaracy igual DE 1 FRAME
def getCoordinatesInOriginalFormatFromOneFrame(directory,numberOfFrame,body,rightHand,leftHand):
  files = getFilesFromOneDirectory(directory)
  with open(files[numberOfFrame]) as json_file:
    data = json.load(json_file)
    personKeypoints = data['people'][0]
    bodyFromJson = personKeypoints['pose_keypoints_2d']
    rightHandFromJson = personKeypoints['hand_right_keypoints_2d']
    leftHandJson = personKeypoints['hand_left_keypoints_2d']
  body.append(bodyFromJson)
  rightHand.append(rightHandFromJson)
  leftHand.append(leftHandJson)

def getOneFrame(files, numberOfFrame):
  for index in range(0,len(files)):
    #print(files[index][10:])
    numberOfFile = files[index][-27:-15]
    if numberOfFrame == int(numberOfFile):
      #print(files[index][-27:-15])
      return files[index]
  return "Not Found"

#Devuelve los puntos de la mano y cuerpo en formato [[x,y],[x,y]] sin accuaracy DE 1 FRAME
def getCoordinatesFromOneFrame(directory,numberOfFrame,bodyKeyPoint,rightHandKeyPoint,leftHandKeyPoint):
  files = getFilesFromOneDirectory(directory)
  with open(getOneFrame(files, numberOfFrame)) as json_file:
    data = json.load(json_file)
    personKeypoints = data['people'][0]
    body = personKeypoints['pose_keypoints_2d']
    rightHand = personKeypoints['hand_right_keypoints_2d']
    leftHand = personKeypoints['hand_left_keypoints_2d']
  bodyKeyPoint.append(getBodyKeyPoints(body))
  rightHandKeyPoint.append(getHandKeypoints(rightHand,0,1,body)) #, bodyKeyPoint[0][3] ))  ## Comentar el ultimo parametro si usas la forma normal de extraer keypoints
  leftHandKeyPoint.append(getHandKeypoints(leftHand,1,0,body)) #, bodyKeyPoint[0][6] ))

#Devuelve los puntos de la mano y cuerpo en formato [ [[x,y],[x,y]], [[x,y],[x,y]] ] 3 dimenciones porque seran varios frames sin accuaracy DE TODOS LOS FRAMES DE UN VIDEO O DIRECTORIO
def getCoordinatesFromOneDirectory(directory):
  files = getFilesFromOneDirectory(directory)
  numberOfFrames = len(files)
  response = []
  bodyKeyPoint = []
  rightHandKeyPoint = []
  leftHandKeyPoint = []
  for index in range(0,numberOfFrames):
    getCoordinatesFromOneFrame(directory,index,bodyKeyPoint,rightHandKeyPoint,leftHandKeyPoint)
    aux = []
    aux.append(bodyKeyPoint[0])
    aux.append(leftHandKeyPoint[0])
    aux.append(rightHandKeyPoint[0])
    response.append(aux)
    bodyKeyPoint = []
    rightHandKeyPoint = []
    leftHandKeyPoint = []
  return response

def getAllXAndYCoordinatesFromOneDirectory(directory, xCoordinates, yCoordinates):
  coordinates = getCoordinatesFromOneDirectory(directory)
  files = getFilesFromOneDirectory(directory)
  numberOfFrames = len(files)
  for index in range(0,numberOfFrames):
    finalVector = getRegularizedVector(coordinates[index][0],coordinates[index][1],coordinates[index][2]) * getScallingCoefficient(coordinates[index][0])
    xCoordinates.append(getXCoordinatesForPlotting(finalVector))
    yCoordinates.append(getYCoordinatesForPlotting(finalVector))

def transform_vec(vec):
  vec_ = []
  for v in vec:
    vec_.append(v[0])
    vec_.append(v[1])
  return vec_

def readDirectoryContent(directory_path):
    content_names = [f for f in listdir(directory_path)]
    return content_names
def saveVectorCsv(vec, output_csv_path):
  #print("Vector a guardar:")
  #print(vec)
  with open(output_csv_path, 'a+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(vec)

def createHeader(tam, output_csv_path_):
  names = []
  for i in range(tam):
    names.append("Input-KP" + str(i))
  names.append("Output")
  saveVectorCsv(names, output_csv_path_)

def getOutputsFromCsvDataSet(direction, numerOfClasses):
  responseCounters = np.zeros(numerOfClasses, dtype=int)
  dataset = pd.read_csv(direction)
  labelsAux = dataset['Output'].values
  for index in range(0,len(labelsAux)):
    responseCounters[labelsAux[index]] = responseCounters[labelsAux[index]] + 1
  return responseCounters

input_path =  '../jsons-temporal/'
output_csv_path_ = './public/results/result.csv'

output_size = 480
number_frames = 5
createHeader(output_size, output_csv_path_)

count = 0
json_names = readDirectoryContent(input_path)
ratio = len(json_names) / number_frames
aux = 0
vecs = []

for i in range(number_frames):
  bodyKeyPoints = []
  leftHandKeyPoints = []
  rightHandKeyPoints = []
  direction = input_path + "/*.json"
  getCoordinatesFromOneFrame(direction,round(aux),bodyKeyPoints,rightHandKeyPoints,leftHandKeyPoints)  # Es el vector completo --> [ [Keypoints del cuerpo], [Keypoints de la mano iz], [Keypoints de la mano der] ]
  response = calculateFinalVector(bodyKeyPoints[0],leftHandKeyPoints[0],rightHandKeyPoints[0])
  
  nor_vec = transform_vec(response)
  vecs = vecs + nor_vec
  aux = aux + ratio

print(vecs)
saveVectorCsv(vecs, output_csv_path_)

