# Michaelis-Menten Equation Fitting Tool
It was written for UGA students to use during biochemistry practicals in L2, L3, and M1.

This tool allows users to input data for substrate concentration (`S0`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve-fitting results easily.

If you found this project useful, used it, or needed to customize it (e.g., adding more lines or columns), please let me know! Your feedback is essential to help me improve and continue this project. You can reach out to me directly at [reach out to me via email](jean-marie.bourhis@univ-grenoble-alpes.fr).

Stand-alone version for Windows, Mac, Linux are avalible at the end of the page

The last version of the script is MM-fit-v3.0.py

## Features:

- Graphical table to manually input data.
- Paste functionality compatible with data copied from Excel.
- Real-time curve fitting to the Michaelis-Menten equation.
- Visual representation of observed data and fitted curve.
- Output of estimated \( V_{max} \) and \( K_m \) parameters in scientific notation.

## Dependencies:

- `webbrowser`
- `numpy`
- `tkinter`
- `scipy`
- `matplotlib`

## Installation:

Ensure you have Python installed on your system.

Install the required packages using `pip`:

```bash
pip install numpy scipy matplotlib
```
or conda 
```bash
conda install numpy scipy matplotlib
```

## Usage:

1. Run the script:

```bash
python MM-Fit-vXX.py
```

![image](https://github.com/user-attachments/assets/8ae1db6e-4fbf-4657-8744-4de65acd7025)

or for Window, MAc.app, or Linux (see stand-alone, cause the executable is relatively large around 200Mo)
double click on the file:

MM-fit-v3.0.exe

![image](https://github.com/user-attachments/assets/17b7c625-2fb1-4ed7-8540-0ff23b1fdbfc)


2. A window will popup:
   
<img width="973" alt="image" src="https://github.com/user-attachments/assets/42e46f5b-7388-47eb-a82c-80d10bd4287c">


4. Use the graphical interface to input data manually or paste it directly from cells copy in Excel using the "Paste Data from Excel" button.


![image](https://github.com/user-attachments/assets/539d8df2-01a1-426e-b8d9-90d530a0bb8b)

The GUI after pasting values from Excel
   
<img width="973" alt="image" src="https://github.com/user-attachments/assets/fe30a5dc-d999-4ac4-a610-0777f6c8a9a8">



4. Click on "Fit Michaelis-Menten " to fit the Michaelis-Menten equation and visualize the results.

Micahelis Menten representation with the fit (Km, Vmax, and R^2 to estimate of the quality of the fit) :


<img width="1112" alt="image" src="https://github.com/user-attachments/assets/85dc4407-832b-4be5-9382-aa553de924d3">


Close the MM fit window to get back to the GUI 

5. Click on Draw Lineweaver and Burk Plot to get the representation :

<img width="929" alt="image" src="https://github.com/user-attachments/assets/bccc213a-0d52-4fff-a473-057ca0e8184c">

<img width="1112" alt="image" src="https://github.com/user-attachments/assets/a6d62974-9389-432e-b782-04c3b33e7255">


Close the Lineweaver and Burk Plot window to get back to the GUI 

6. Click on "Exclude data" to exclude some value to improve the fit for one or several series. 

<img width="522" alt="image" src="https://github.com/user-attachments/assets/fa464501-43b3-4a0d-8125-99f0ed0a69c9">

   Check the values that seem a bit odd to exclude them for the fit and Lineweaver and Burk Plot:

<img width="522" alt="image" src="https://github.com/user-attachments/assets/dbb9a045-8072-48ee-bd95-4ad756e60390">

   then click on "Apply and Refit", the new fit appears without the exclude values.
   
<img width="1112" alt="image" src="https://github.com/user-attachments/assets/5af7d587-2cfc-4371-8d7d-88365c3c9416">

7. Click on "Reset Data" to clear all the fields and reset checked checboxes.
   
9. Click on "Quit" to quit  

## Notes:
1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots i.e. 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
4. It's possible to make an exe file for Windows using "pyinstaller", to distribute the script on computers that don't have Python install:

   /!\ python 3.10 environement/!\
   
      ```bash
      conda create -n "py310" python=3.10
      conda activate py310
      conda install matplotlib numpy scipy pyinstaller
      ```
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
      pyinstaller -F MM-vXX.py --hidden-import='PIL._tkinter_finder'
   ```

   /!\ For the first run be patient, the embeded matplotlib needs to compile and it takes sometimes /!\.
   
6. Stand-alone versions are here :
      For Mac (if it doesn't start go to Privacy & Security and click on open anyway) :

https://cloud.univ-grenoble-alpes.fr/s/g7pWB2xpNcJrRmS

     For Windows :
     
https://cloud.univ-grenoble-alpes.fr/s/TerC3LbTkKQKWZ4

      For Linux:

https://cloud.univ-grenoble-alpes.fr/s/amLCax7dQXZrDtn
   
