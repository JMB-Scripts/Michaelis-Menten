# Michaelis-Menten Equation Fitting Tool
It was written for University of Grenoble ALpes (UGA) students for biochemistry practicals in L2, L3, and M1.

This tool allows users to input data for substrate concentration (`S0`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve-fitting results easily.(no need of expansive software)

If you found this project useful, used it, or needed to customize it (e.g., adding more lines or columns), please let me know! 
Your feedback is essential to help me improve and continue this project. 
You can [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).

Stand-alone version for Windows, Mac, Linux (is coming) are avalible at the end of the page

The last version of the script is MM-fit-v5.0.py

## General Features:

1- Paste kinetic data directly from Excel.
 
2- Select substrate concentration and velocity columns.
 
3- Fit data to the Michaelis-Menten equation using nonlinear regression.
 
4- View fitted V_{\max}, K_m, and plot the fitted curve.
 
5- View Lineweaver-Burk plot and have the lienar regression
    
6- Exclude odd value from the fit for MM and LB
    
7- Clean, interactive GUI built with PyQt5.
 
8- Save plots as PNG or print them MM plot and LB plot  


## Version 5.0 Major update
🔄 Version 5.0 — Latest Release

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
python MM-fit-v5.0.py
```
## Video tutorial:

https://github.com/user-attachments/assets/711b63c7-8805-4179-b599-67a5e412c16f

## Usage:

1. If python is present on your system then run the script:

```bash
python MM-Fit-vXX.py
```

![image](https://github.com/user-attachments/assets/8ae1db6e-4fbf-4657-8744-4de65acd7025)

or use the stand-alone for Window, Mac.app, or Linux (link below)
double click on the file:

MM-fit-Qt-v3.5.exe

![image](https://github.com/user-attachments/assets/17b7c625-2fb1-4ed7-8540-0ff23b1fdbfc)

2. A window will popup:
   
![image](https://github.com/user-attachments/assets/479bd06b-3035-472b-a6d3-3d96dfb1216d)

4. Copy cells in Excel (make sure that values are in scientific format)

![image](https://github.com/user-attachments/assets/539d8df2-01a1-426e-b8d9-90d530a0bb8b)

5. Then on the GUI click on "1- Paste from Excel"
   
![image](https://github.com/user-attachments/assets/ec6441c5-dc20-4d84-88d7-c6fd767aefb3)

4. Click on "2- MM-Fit" to fit the Michaelis-Menten equation and visualize the results.

Micahelis Menten representation with the fit (Km, Vmax, and R^2) :


<img width="960" alt="image" src="https://github.com/user-attachments/assets/f9973e38-fea9-4a9a-891a-4ffda44d029d" />

At the bottom of the plot you can see residuals (Exp values - Fit values) with a color cone for values at +/- 10% from the fit value. 

5. Click LB plot to draw Lineweaver and Burk Plot to get the plot :

![image](https://github.com/user-attachments/assets/38529ea9-a89b-49f3-83c1-0e765ed9dcd8)


Check on Display linear fit to get values from the linear regression

![image](https://github.com/user-attachments/assets/7d5c320f-3328-48ac-be38-93f00f821962)

you can click on print to print or to save as PDF

Close the LB plot window to get back to the GUI 

6. Click on "4- Exclude data" to exclude some value to improve the fit for one or several series. 

![image](https://github.com/user-attachments/assets/241a2da7-ecb9-4a4c-a2c1-4cdc7ff61475)


   Check the values that seem a bit odd to exclude them for the MM fit and Lineweaver and Burk Plot:

![image](https://github.com/user-attachments/assets/3ec5faeb-17bb-43ac-9091-bc093fad8af2)
   
   Then click on "Apply and Refit", the new fit appears without the exclude values. 
   Note that exclude values appears as crosses on the plot 

   MM-plot
   
![image](https://github.com/user-attachments/assets/ff7b2275-4092-41e2-bb0c-a8689f0440a7)


   Or LB plot 

<img width="960" alt="image" src="https://github.com/user-attachments/assets/6a0fb587-aeca-413e-8bff-27b5c9d5aee4" />

7. Click on "Reset " to clear all the fields and reset checked checboxes, and start over.
   
9. Click on "Quit" to quit  

## Notes:
1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots i.e. 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
4. /!\ TAke only the values not the text /!\.
5. It's possible to make an exe file for Windows using "pyinstaller" or "py2app", to distribute the script on computers that don't have Python install:

   For windows
   ```bash
      pyinstaller -F MM-vXX.py
   ```
   For Mac
   ```bash
      pyinstaller -F MM-vXX.py
   ```
   For Linux
   ```bash
      pyinstaller -F MM-vXX.py 
   ```

   /!\ For the first run be patient, the embeded matplotlib needs to compile and it takes sometimes /!\.
   
6. Stand-alone versions are here for the old v3.5 the 5.0are coming:

=> For Mac :

[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/DTTYdZw3HcfoTG2)

(if it doesn't start go to Privacy & Security and click on open anyway) 

=> For Windows :

Just one file (it will be slow start, but can be place anywhere)

[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/y93FMDka3WsZaCS)

(the exe files plus one folder for libraries (start faster, but you need to keep the exe close to the libraries folder)

[Get it from Here](https://cloud.univ-grenoble-alpes.fr/s/y93FMDka3WsZaCS)

=> For Linux:

coming soon
   
Don't hesitate to reach me if you need help setting it up  [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).
