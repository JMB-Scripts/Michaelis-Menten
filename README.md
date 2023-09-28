# Michaelis-Menten Equation Fitting Tool

This tool allows users to input data for substrate concentration (`S`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to input the data and visualize the curve fitting results easily.

## Features:

- Graphical table to manually input data.
- Paste functionality compatible with data copied from Excel.
- Real-time curve fitting to the Michaelis-Menten equation.
- Visual representation of observed data and fitted curve.
- Output of estimated \( V_{max} \) and \( K_m \) parameters in scientific notation.

## Dependencies:

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
python Michaelis-Menten-Fit-vXX.py
```
1. A window will popup:
![image](https://github.com/JMB-Scripts/Michaelis-Menten/assets/20182399/0162d1ca-e50c-4105-a0d0-010c7c2c303c)
2. Use the graphical interface to input data manually or paste it directly from Excel using the "Paste Data from Excel" button.

4. Click on "Save Data and Fit" to fit the Michaelis-Menten equation and visualize the results.
   ![image](https://github.com/JMB-Scripts/Michaelis-Menten/assets/20182399/5e734157-c8b5-42af-860d-24836430ceee)

## Notes:

1. Ensure all values are valid and in the correct format like 12E03  (for 12000 e.g., scientific notation) before fitting. 
2. In principle, it should accept numbers with commas or dots ie 1,2E-03 or 1.2E-03.
3. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
