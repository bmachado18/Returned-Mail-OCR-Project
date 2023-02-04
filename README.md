# Returned Mail OCR Project

The Returned Mail OCR project uses [Tesseract OCR Engine](https://github.com/tesseract-ocr/tesseract) to automate the data copying process from a batch of appeal letters to an Excel file.

**As of 27/06/2022, program has support for law appeals, general appeals without a constituent ID, and general appeals with a consituent ID.**

General Appeal Format:

![general appeal format](images\general_appeal.png)

Law Appeal Format:

![law appeal format](images\law_appeal.png)

## Installation

Download the [Anaconda environment file](environment.yml), then use the terminal or an Anaconda prompt to create the environment with the following command:

```
conda env create -f environment.yml
```
The environment will then be created with the name ocr_proj.

## Usage
Firstly activate the environment in terminal or an Anaconda prompt:
```
conda activate ocr_proj
```
Run the main.py file to start the script. Identify the path and follow the prompts in the command line.

Once the process is complete, type "y' to save the output file, or type "n" to continue with another batch of appeals.

There is also a gui version. You can run the gui.py file to open the UI. Below is what the GUI looks like:

![main gui controls](images\GUI.PNG)


Select the pdf containing the batch of returned appeals, then click the "Scan Files" button to begin the program.

The program will terminate and the rows will populate. You can add more batches to the overall program, or you can create the excel file with the button "Create excel file".

The excel file will be stored in the parent folder to the source code. It should contain the Name, Address Line 1, Address Line 2, and Appeal ID. If possible, the Address Line 3 and Constituent ID will be included.

Once the program terminates, a temporary images folder will appear in the parent folder containing the processed images. After verifying the output, you can delete those images with the button "Delete Images". 