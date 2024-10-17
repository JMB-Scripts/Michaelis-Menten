# Michaelis-Menten Equation Fitting Tool

This tool allows users to input data for substrate concentration (`S0`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve-fitting results easily.
The last version of the script is MM-fit-v16

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

or for Window (upon request, cause the executable is relatively large around 200Mo)
double click onthe file:

MM-fit-v16.exe

![image](https://github.com/user-attachments/assets/17b7c625-2fb1-4ed7-8540-0ff23b1fdbfc)


2. A window will popup:

<img width="1042" alt="image" src="https://github.com/user-attachments/assets/41b00e00-3484-43de-b025-e7733e18e333">

3. Use the graphical interface to input data manually or paste it directly from cells copy in Excel using the "Paste Data from Excel" button.


![image](https://github.com/user-attachments/assets/539d8df2-01a1-426e-b8d9-90d530a0bb8b)


<img width="1042" alt="image" src="https://github.com/user-attachments/assets/51ca9a08-43e4-4fcb-bd49-b6dcc4164485">


4. Click on "Save Data and Fit" to fit the Michaelis-Menten equation and visualize the results.

Micahelis Menten representation with the fit and a measure of the quality of the fit :


<img width="1112" alt="image" src="https://github.com/user-attachments/assets/85dc4407-832b-4be5-9382-aa553de924d3">

Lineweaver and Burk representation :

<img width="1112" alt="image" src="https://github.com/user-attachments/assets/4a959aa9-404f-4244-81ec-a7f5ea4b98d5">


5. Click on "Exclude data" to exclude some value to improve the fit for one or several series. 

<img width="522" alt="image" src="https://github.com/user-attachments/assets/fa464501-43b3-4a0d-8125-99f0ed0a69c9">

   Check the values that seem a bit odd to exclude them for the fit:

<img width="522" alt="image" src="https://github.com/user-attachments/assets/dbb9a045-8072-48ee-bd95-4ad756e60390">


   then click on "Apply and Refit", the new fit appears without the exclude values.
   
<img width="1112" alt="image" src="https://github.com/user-attachments/assets/5af7d587-2cfc-4371-8d7d-88365c3c9416">



## Notes:

1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots i.e. 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
4. It's possible to make an exe file for Windows using "pyinstaller", to distribute the script on computers that don't have Python install.
5. I can also provide upon request the stand-alone version for Windows (MM-fit-v16.exe).    
