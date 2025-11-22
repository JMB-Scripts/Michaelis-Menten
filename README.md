# Michaelis-Menten Equation Fitting Tool
It was written for University Grenoble Alpes (UGA) students for biochemistry practicals in L2, L3, and M1.

This tool allows users to input data for substrate concentration (`S0`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve-fitting results easily. No need of an expansive software to make non linear regression

If you found this project useful, used it, or needed to customize it (e.g., adding more lines or columns), please let me know! 
Your feedback is essential to help me improve and continue this project. 
You can [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).

Stand-alone version for Windows, Mac, Linux are avalible to download at the end of the README

## General Features:

1- Paste kinetic data directly from Excel.
 
2- Select substrate concentration and velocity columns.
 
3- Fit data to the Michaelis-Menten equation using nonlinear regression.
 
4- View fitted V_{\max}, K_m, and plot the fitted curve.
 
5- View Lineweaver-Burk plot and have the lienar regression
    
6- Exclude odd value from the fit for MM and LB
    
7- Clean, interactive GUI built with PyQt5.
 
8- Save plots as PNG or print them MM plot and LB plot  


## Version 5.x Major update
🔄 Version 5.5 — Latest Release

Released: Novembre 2025
Status: Stable

✨ New Features:

1- High-Resolution PDF/Print Reports:

    The simple "Print" function (which just printed a low-res screen capture) has been completely replaced.

    The new "Print Report" button generates a professional, multi-part report on a single A4 page.

    High-Resolution Plot (600 DPI): The Matplotlib figure is saved to an in-memory buffer at 600 DPI and then painted onto the PDF, ensuring a sharp, publication-quality image.

    Data Table on Report: The report now includes the full data table (minus the "Include" column) formatted below the plot.

2- Advanced Data Table Printing:

    The printed table is drawn manually to the PDF canvas for full control.

    Red Highlighting: All excluded data (either from an unchecked row or the "Exclude" dialog) is now printed in red for easy identification.

    Scientific Notation: All numbers in the printed table are formatted in scientific notation (X.XXE-Y) for a tight, clean, and uniform look.

3- Statistical Error Analysis:

    The core fitting logic in fit_data has been upgraded to calculate the standard error (SE) and relative standard error (%RSE) for both Vmax and Km.

    These errors are now displayed directly in the plot legends for both the Michaelis-Menten and Lineweaver-Burk plots, e.g., Vmax = 4.52e-07 (± 1.7e-08 | 4%).

🛠 Improvements :

1- Modern Styling: All buttons now have a modern, flat-style look with CSS-like stylesheets for different states (action, utility, warning, quit).

2- Pastel Colormap: The default viridis colormap has been replaced with the Set2 (pastel) colormap for clearer, more distinct plots.

 
## Dependencies:

The following Python libraries are required:
	•	PyQt5
	•	numpy
	•	pandas
	•	matplotlib
	•	scipy
 
## Installation from the script:

Ensure you have Python installed on your system.

Install the required packages using `pip`:

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv mmfit-env
source mmfit-env/bin/activate
# On Windows use: mmfit-env\Scripts\activate
```

# Install required packages
```bash
pip install PyQt5 numpy pandas matplotlib scipy
```
or 
```bash
conda create -n mmfit-env python=3.12
conda activate mmfit-env
conda install pyqt5 numpy pandas matplotlib scipy
```
# Run the script:
```bash
python MM-fit-v5.x.py
```
## Video tutorial:

https://github.com/user-attachments/assets/711b63c7-8805-4179-b599-67a5e412c16f

## Usage:

1. If python is present on your system then run the script:

```bash
python MM-Fit-v5.x.py
```

or use the stand-alone for Window, Mac.app, or Linux (link below)
double click on the file:

MM-fit-v5.0.exe

2. A window will popup (beware first start is ver very long 40-45 sec):

<img width="1312" height="840" alt="image" src="https://github.com/user-attachments/assets/e5399fe8-e584-432b-a977-c90a83b471b0" />


4. Copy cells in Excel (make sure that values are in scientific format)

<img width="305" height="285" alt="image" src="https://github.com/user-attachments/assets/7dee89df-d6ef-40aa-b69a-305efa6a66e2" />


5. Then on the GUI click on "1- Paste from Excel". Data will appear in the left panel
   
<img width="1312" height="840" alt="image" src="https://github.com/user-attachments/assets/5969a39f-c3e6-4206-ac6b-572d5274e267" />


4. Click on "2- MM-Fit" to fit the Michaelis-Menten equation and visualize the results.

Micahelis Menten representation with the fit (Km and error, Vmax and error, and R^2) :

<img width="1312" height="840" alt="image" src="https://github.com/user-attachments/assets/822fb31a-e628-47ad-9a6e-a7e10128c1a7" />


At the bottom of the plot you can see residuals (Exp values - Fit values) with a color cone for values at +/- 5% from the fit value. 

5. Click LB plot to draw Lineweaver and Burk Plot to get the plot :

<img width="912" height="840" alt="image" src="https://github.com/user-attachments/assets/7b1f0d9b-0410-4654-8b97-4cac3123117b" />

Check on Display linear fit to get values from the linear regression

<img width="912" height="840" alt="image" src="https://github.com/user-attachments/assets/ef4039d6-35c6-49eb-ab16-dadb271f24da" />

Note with the v5.0 you can change the X and Y scale using X or Y max and min box.

You can click on print to print or save as PDF

Close the LB plot window to get back to the GUI 

6. Click on "4- Exclude data" to exclude some value to improve the fit for one or several series. 

<img width="1195" height="722" alt="image" src="https://github.com/user-attachments/assets/7ec6638a-8c05-4ecc-a61b-aabefbd05403" />



   Check the values that seem a bit odd to exclude them for the MM fit and Lineweaver and Burk Plot:
   
   Then click on "Apply and Refit", the new fit appears without the exclude values. 
   Note that exclude values appears as crosses on the plot 

   MM-plot
   
<img width="1312" height="840" alt="image" src="https://github.com/user-attachments/assets/67b8c7ba-b231-4604-80c9-583a0ee61bcf" />



   Or LB plot 

<img width="912" height="840" alt="image" src="https://github.com/user-attachments/assets/ebe6701f-e620-46b8-82b0-afc3e64d840b" />


7. Click on "Reset " to clear all the fields and reset checked checboxes, and start over.
   
9. Click on "Quit" to quit  

## Notes:
1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots i.e. 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
4. It's possible to make an exe file for Windows using "pyinstaller" or "py2app", to distribute the script on computers that don't have Python install:

   ```bash
      pyinstaller -F MM-v5.x.py
   ```

   /!\ For the first run be patient, the embeded matplotlib needs to compile and it takes sometimes /!\ (this should be solve in the 5.5 version)
   
## Stand-alone versions are here v5.x (last release):
   /!\ For the first run be patient, the embeded matplotlib needs to compile and it takes sometimes /!\ (this should be solved in the 5.5 version)

=> For Mac (if it doesn't start go to Privacy & Security and click on open anyway, as I'm an unidentify develloper) :


[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/bgsGDbjHcMdR3fS)

=> For Windows Just one file (it will be a bit slow start (solved in the 5.5 version), but can be place anywhere):

[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/H2GMHR3yLCHNzKY)

=> For Linux (5.0):

[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/cdAbePCEzCoDzrF)
   
Don't hesitate to reach me if you need help setting it up  [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).
