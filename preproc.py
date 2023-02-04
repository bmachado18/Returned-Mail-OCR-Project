#import modules
from pdf2image import convert_from_path
import os
import shutil, sys
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter
import pytesseract
import re

"""page_split
Isolates each page from filepath pdf's and converts them to png,
making a temporary folder to store the new images

params: FILEPATH: filepath to the envelope/appeal pdf
        output_path: path to temporary folder

returns: the relative filepath to the temporary images
"""
def convert_and_split(FILEPATH, output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    os.makedirs(output_path)
    images = convert_from_path(FILEPATH)
    for i, im in enumerate(images):
        im.save(output_path + '\{}-{}.jpg'.format("tmp",i))
    return output_path


"""rotate
purpose: Rotates the batch of arbituary images in 90 degree increments
 to the upright orientation by using the character orientation. rewrites the temporary images

params: directory: the path to the folder of temporary images, in this project is always tmp/env or tmp/app

returns: nothing
"""
def rotate(directory):
    rotate = 0
    #loop through every temporary jpg
    for image_name in os.listdir(directory):
        name, extension = os.path.splitext(image_name)
        if extension != '.jpg':
            continue
        image = cv2.imread(directory + '\\' + image_name)
            
        if("0" in name):
            
            osd = pytesseract.image_to_osd(cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE))
            
            if('Orientation in degrees: 0' in osd):
                rotate = cv2.ROTATE_90_COUNTERCLOCKWISE
            elif('Orientation in degrees: 90' in osd):
                rotate = cv2.ROTATE_180
            elif('Orientation in degrees: 180' in osd):
                rotate = cv2.ROTATE_90_CLOCKWISE
        
        if (rotate!=0):
            image = cv2.rotate(image, rotate)
            
        cv2.imwrite(os.path.join(directory, image_name), image)

"""seperate
purpose: given an image, seperates the image if it is needed with text patterns

params: directory: relative filepath to the folder of temporary images, in this project it is always tmp/env or tmp/app

returns: nothing
"""
def seperate(directory):
    #Begin Looping through every jpg
    for image_path in os.listdir(directory):
        name, extension = os.path.splitext(image_path)
        if extension != '.jpg':
             continue
        
        #open image
        image = cv2.imread(os.path.join(directory, image_path))
        
        #convert to grayscale
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        yCoords = []
        crops = []

        #quickly scan the pdf
        data = pytesseract.image_to_data(imageGray, output_type="dict")
        
        #checking how many times this word in particular repeats. if more than once, we will split the envelope at this particular word.
        #use words in the headers, things you don't need but are good positions to crop
        pattern = r"support"
        word_occurences = [ i for i, word in enumerate(data["text"]) if re.match(pattern.lower(),word.lower())]
        #if it never found the first pattern, try to check the second word
        if len(word_occurences) == 0:
            pattern = r"University"
            word_occurences = [ i for i, word in enumerate(data["text"]) if re.match(pattern.lower(),word.lower())]
        for occ in word_occurences:
            yCoords.append(data["top"][occ])
        
        #identifying the position of occurances of the particular words.
        for i in range(len(yCoords)):
            if i+1 < len(yCoords)-1:
                if yCoords[i+1] - yCoords[i] > 500:
                    crops.append(yCoords[i])
            elif len(crops) < 2:
                crops.append(yCoords[i])
        if(len(crops) == 2):
            if(abs(crops[0] - crops[1]) < 100):
                crops = np.delete(crops, 1)
        
        #actually cropping the image and splitting it into two.
        if len(crops) == 2:
            p1_top = crops[0]
            p1_bot = crops[1]
            p2_top = crops[1]
            p2_bot = crops[1] + 1000
            left_side=0
            right_side = image.shape[1]
            p1 = image[p1_top:p1_bot, left_side:right_side]
            p2 = image[p2_top:p2_bot, left_side:right_side]
            cv2.imwrite(os.path.join(directory, 'top_' + image_path), p1)
            cv2.imwrite(os.path.join(directory, 'bot_' + image_path), p2)
            os.remove(os.path.join(directory, image_path))

