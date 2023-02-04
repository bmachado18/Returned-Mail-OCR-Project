from ast import Return
import os
import cv2
import numpy as np
import pytesseract
import re
import pandas as pd

"""extract_data
extracts constituent information and appeal id from the appeal letter

params: batch_path: relative filepath to the folder of temporary images, in this project it is always tmp/app

returns: extracted data from returned appeal letter
"""
def extract_data(batch_path):
    # creating the intial dataframe for the batch
    appeal_data_df = pd.DataFrame(columns=['Name', 'Address Line 1', 'Address Line 2', 'Address Line 3', "Appeal_ID", "Consituent_ID"])

    # loop through every image in the batch
    for image_path in os.listdir(batch_path):

        name, extension = os.path.splitext(image_path)

        # skip an interation if the file is not the .jpg extension - cannot use cv2 on non-image files
        if extension != '.jpg':
            continue
        
        # contouring algorithm is found here: https://stackoverflow.com/questions/46003033/extract-contours-from-bounding-box

        # load the image into the program from the path
        image = cv2.imread(batch_path + '\\' + image_path)

        # grayscale the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # thresholding smoothens the pixels for preparation into the findcontours function
        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # morphological operations better defines the letters based on the pixel surrounding the black pixels - dilation accentuates features
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (25,25))
        dilate = cv2.dilate(thresh, kernal, iterations = 1)

        # draws contour lines on each detected edge of the dilated image
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts=cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key = lambda x : cv2.boundingRect(x)[0])
        
        #m ake a copy of the image
        copy = image.copy()

        constituent_info = None
        appeal_id = None

        # loop on each contour line of single appeal
        for c in cnts:
            
            # get the bounding rectangle coordinates of the contour line
            x, y, w, h = cv2.boundingRect(c)

            # cropping the exact position of the box
            cropped = copy[y:y + h, x:x + w]
            
            # found that there is a lot of contour boxes in between the two important areas - we can skip everything in between each loop based on the x position
            if (constituent_info != None and x < 1000):
                continue
            
            # if the width is not too big and we haven't found the constituent info, test the box; this is usually one of the first boxes as it moves from top to bottom
            if constituent_info == None and w < 800:
                constituent_info = constituent_info_test(cropped)
            elif x > 1000: # otherwise test for the appeal after 1000 - there is only 1 or two boxes after 1000 in the x dimension
                appeal_id = appeal_id_test(cropped)
                # if we found the appeal_id, no need to keep looping
                if appeal_id != None:
                    break
        # the information has been extracted, and we now need to organize and place into the dataframe for the batch
        appeal_data_df = enter_data_to_df(appeal_data_df, constituent_info, appeal_id)

        

    return appeal_data_df

"""constituent_info_test
test the constituent info using very specific text information

params: cropped: the cropped image from contour algorithm

returns: either the constituent_info or None

"""
def constituent_info_test(cropped):
    # read the text within the cropped contour area
    text = pytesseract.image_to_string(cropped)
    non_empty_lines = "".join([s for s in text.splitlines(True) if s.strip()]) # removes the empty lines
    text = non_empty_lines.splitlines() # split the lines into a list
    line_length = len(text) 
    
    # uses features of the constituent info gathered to identify what is needed - gathered from testing in jupyternotebook and may need to update
    if line_length >= 3 and line_length <= 4: #constituent info is always between 3 and 4 (inclusive) lines long
        if text[0][0].isupper() and (text[1][0].isupper() or text[1][0].isdigit()): # first letter of first line always capitalized , and second letter is either capital letter or digit
            return text
    
    return

"""appeal_id_test
test the appeal id based on format of typical scan

params: cropped:the cropped image from the contour algorithm

returns: either the constituent_info or None
"""
def appeal_id_test(cropped):
    # read the text within the cropped contour area
    text = pytesseract.image_to_string(cropped)
    non_empty_lines = "".join([s for s in text.splitlines(True) if s.strip()]) # removes the empty lines
    text = non_empty_lines.splitlines() # split the lines into a list
    line_length = len(text)
    # uses features of the constituent info gathered to identify what is needed - gathered from testing in jupyternotebook and may need to update
    # this is also designed to work with the law appeals, which have a slightely different format
    if line_length == 1: # if the extracted text has only one line, it is possible that it is an appeal with only the appeal id
        if len(text[0]) >= 5: # avoids index error in if statement below
            if "-" in text[0][-5:-1] or text[0][-5:].isupper(): # one of the last five digits on the line should be a dash or last 5 digits all uppercase
                return text
    elif line_length >= 2: # f extracted text is more than 1 line, possible that it is an appeal with both appeal id and constituent id
        if len(text[1]) >= 5: # avoids index error in if statement below
            if "-" in text[1][-4:-1] or "-" in text[0][-4:-1]: # possible that both could be the appeal id with the dash at the end, so check both lines
                return text
    else:
        return

"""enter_data_to_df
enters/organizes the data extracted from each contoured area into a row, then into the dataframe for the entire

params: appeal_data_df: the dataframe for the entire batch
constituent_info: the extracted constituent name, addr1, addr2, addr3 from the appeal
appeal_id: the extracted appeal id, and constituent id from the appeal

returns: the new dataframe containing all old contoured data and the new row
"""
def enter_data_to_df(appeal_data_df, constituent_info, appeal_id):
    # can remove these if you do not want to see each extraction
    print(constituent_info)
    print(appeal_id)
    # initialize new row which is almost always constant
    if appeal_id == None:
        new_row = [constituent_info[0],constituent_info[1] , constituent_info[2], None, None, None]
    else:
        new_row = [constituent_info[0],constituent_info[1] , constituent_info[2], None, appeal_id[0], None]
    
    # if there are equal to or more than four lines in constituent_info, then there is one more address line to set
    if len(constituent_info) >= 4:
        new_row[3] = constituent_info[3]
    # if there are two or more lines in appeal_id, then need to check which line is appeal id and constituent info
    if appeal_id != None:
        if len(appeal_id) >= 2:
            if ' ' in appeal_id[1]: # found through testing that with law appeal, index 0 of list was useless, and index two had both pieces of information seperated by a space
                new_row[5], new_row[4] = appeal_id[1].split() # seperates the string between a space into a tuple where first is constituent id and second is appeal id
            else:
                new_row[5] = appeal_id[1] # if no space in last row, then the second element is the the constituent info
    
    # adding the new row into the dataframe - might be a better way to do this
    new_row_df = pd.DataFrame([new_row], columns=['Name', 'Address Line 1', 'Address Line 2', 'Address Line 3', "Appeal_ID", "Consituent_ID"])
    appeal_data_df = pd.concat([new_row_df, appeal_data_df])
    
    return appeal_data_df