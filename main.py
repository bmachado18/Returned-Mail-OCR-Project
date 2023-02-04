from tkinter import N
import pandas as pd
import preproc
import readtext
import GetAppeal
import os

"""
The 3 main modules I've created are preproc and readtext.
"""
def start(APPEAL_FILEPATH, APPEAL_DATAFRAME):
    # preproccessing
    appeal_path = preproc.convert_and_split(APPEAL_FILEPATH,'tmp\\app')
    preproc.rotate(appeal_path)
    preproc.seperate(appeal_path)

    # extracting data
    df_appeal_info = readtext.extract_data(appeal_path)
    APPEAL_DATAFRAME = pd.concat([APPEAL_DATAFRAME, df_appeal_info])
    return APPEAL_DATAFRAME


"""
Comment this out if wanting to run program through gui.py. Otherwise continue.
"""
def main():
    
    APPEAL_DATAFRAME = pd.DataFrame()

    while(1):
        APPEAL_FILEPATH = input("\nEnter an appeal pdf filepath: ")

        print("Starting script with " + APPEAL_FILEPATH)

        APPEAL_DATAFRAME = start(APPEAL_FILEPATH, APPEAL_DATAFRAME)

        option = input("Script successful. Type 'y' if you want to store the output, or type 'n' if you want to continue with another pdf: ")
        if option == 'y':
            break
   
    APPEAL_DATAFRAME.to_excel(os.path.dirname(APPEAL_FILEPATH) + r"\returned_mail_output.xlsx",index=False)
    print("Created "+ os.path.dirname(APPEAL_FILEPATH) + r"\returned_mail_output.xlsx")
    print("Enjoy!")
if __name__=="__main__":
    main()