# Michaelis-Menten Equation Fitting Tool
It was written for UGA students to use during biochemistry practicals in L2, L3, and M1.

This tool allows users to input data for substrate concentration (`S0`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve-fitting results easily.

If you found this project useful, used it, or needed to customize it (e.g., adding more lines or columns), please let me know! 
Your feedback is essential to help me improve and continue this project. 
You can reach out to me directly at [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).

Stand-alone version for Windows, Mac, Linux (is coming) are avalible at the end of the page
The last version of the script is MM-fit-Qt-v3.5.py

## Version 3.5 Major update
🔄 Version 3.5 — Latest Release

Released: April 2025
Status: Stable

✨ New Features
	•	Multi-column selector: Added a dropdown to select both substrate concentration and velocity columns.
	•	Dynamic Excel-style paste: Replaced fixed input system with an Excel-compatible “Paste” button  that auto-         parses tabular data.
	•	Clear separation between data and control: UI is now split more clearly into a table area and a control             panel on the right.
	•	Autoscale on plot: The plot now autoscales and includes dynamic titles and axis labels based on selected columns.
	•	Output display: Fit results for V_{\max} and K_m are now shown in a clear text box.
	•	Save plot functionality: Added a “Save Plot” button to export the fit graph as a PNG image.

🛠 Improvements
	•	GUI layout rewritten using QGridLayout and QVBoxLayout for better readability and structure.
	•	Error handling for non-numeric or missing data is now more robust.
	•	Fitting function supports NaN filtering and pre-checks for fit quality.

🧼 UI Enhancements
		•	Simplified and modernized plot aesthetics.

## Features:

	•	Paste kinetic data directly from Excel.
	•	Select substrate concentration and velocity columns.
	•	Fit data to the Michaelis-Menten equation using nonlinear regression.
	•	View fitted V_{\max}, K_m, and plot the fitted curve.
   •  View Lineweaver-Burk plot and have the liear regression
   •  Exclude odd value from the fit for MM and LB
	•	Clean, interactive GUI built with PyQt5.
	•	Save plots as PNG.
   •  Possibility to print MM plot and LB plot    
 
## Dependencies:

The following Python libraries are required:
	•	PyQt5
	•	numpy
	•	pandas
	•	matplotlib
	•	scipy
 
## Installation:

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
conda install pyqt numpy pandas matplotlib scipy
```

## Usage:

1. If python is present on your system then run the script:

```bash
python MM-Fit-vXX.py
```

![image](https://github.com/user-attachments/assets/8ae1db6e-4fbf-4657-8744-4de65acd7025)

or use the stand-alone for Window, Mac.app, or Linux 
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

At the bottom of the plot you can see residuals (Exp values - Fit values) with a cone of +/- 10% from the fit value. 

5. Click LB plot to draw Lineweaver and Burk Plot to get the plot :

![image](https://github.com/user-attachments/assets/38529ea9-a89b-49f3-83c1-0e765ed9dcd8)


Check on Display linear fit to get values from the linear regression

![image](https://github.com/user-attachments/assets/7d5c320f-3328-48ac-be38-93f00f821962)

you can click on print to print or save as PDF

Close the Lineweaver and Burk Plot window to get back to the GUI 

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


7. Click on "Reset " to clear all the fields and reset checked checboxes.
   
9. Click on "Quit" to quit  

## Notes:
1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots i.e. 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
4. It's possible to make an exe file for Windows using "pyinstaller" or "py2app", to distribute the script on computers that don't have Python install:

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
   
6. Stand-alone versions are here :

     For Mac :

coming soon

(if it doesn't start go to Privacy & Security and click on open anyway) 

     For Windows :
     
coming soon

      For Linux:

coming soon
   
Don't hesitate to reach me if you need help setting it up  [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).
