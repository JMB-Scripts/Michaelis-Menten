import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QFileDialog, QMessageBox, QAbstractItemView, QGridLayout,
                             QCheckBox, QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.stats import linregress
import re
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
################################
#
# GUI definition
#
################################

        self.setWindowTitle("MM-fit - v3.5 -")
        self.resize(1200, 700)  # Taille initiale de la fenêtre

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()

        self.v_data_series = []  # Initialisation de v_data_series comme une liste vide
        self.excluded_data = {}
        
        # Panneau des colonnes à inclure (maintenant en premier dans le layout horizontal)
        self.column_panel = QWidget()
        self.column_layout = QVBoxLayout(self.column_panel)
        self.column_layout.setAlignment(Qt.AlignTop)
        self.column_label = QLabel("Series:")
        self.column_layout.addWidget(self.column_label)
        self.column_checkboxes = {}
        self.main_layout.addWidget(self.column_panel)

        # Table d'entrée des données (à droite du panneau des colonnes)
        self.data_table_widget = QWidget()
        self.data_table_layout = QVBoxLayout(self.data_table_widget)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]0"])
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table_layout.addWidget(self.data_table)
        self.main_layout.addWidget(self.data_table_widget, 1)   
        
        # Zone centrale pour les boutons
        self.buttons_widget = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_widget)
        self.buttons_layout.setAlignment(Qt.AlignTop)

        self.paste_button = QPushButton("1- Paste from Excel")
        self.paste_button.clicked.connect(self.paste_from_excel)
        self.buttons_layout.addWidget(self.paste_button)

        self.fit_button = QPushButton("2- MM-Fit")
        self.fit_button.clicked.connect(self.fit_data)
        self.buttons_layout.addWidget(self.fit_button)
        
        self.lineweaver_burk_button = QPushButton("3- LB plot")
        self.lineweaver_burk_button.clicked.connect(self.show_lineweaver_burk)
        self.buttons_layout.addWidget(self.lineweaver_burk_button)

        self.exclusion_button = QPushButton("(4- Exclude data)")
        self.exclusion_button.clicked.connect(self.open_exclusion_gui)
        self.buttons_layout.addWidget(self.exclusion_button)

        self.save_graph_button = QPushButton("5- Save MM Plot to png")
        self.save_graph_button.clicked.connect(self.save_graph)
        self.buttons_layout.addWidget(self.save_graph_button)

        self.print_button = QPushButton("6- Print")
        self.print_button.clicked.connect(self.print_graph)  # Connecter le bouton à la méthode print_graph
        self.buttons_layout.addWidget(self.print_button)

        self.reset_button = QPushButton("7- Reset")
        self.reset_button.clicked.connect(self.reset_data)
        self.buttons_layout.addWidget(self.reset_button)

        self.quit_button = QPushButton("8- Quit")
        self.quit_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.quit_button)
        
        self.main_layout.addWidget(self.buttons_widget, 0) # Proportion 0 pour les boutons (prend le minimum nécessaire)
        # Zone d'affichage du graphique (à droite)
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_widget)
        self.figure = Figure(figsize=(10, 6), dpi=100) # Taille initiale du graphique augmentée
        self.canvas = FigureCanvas(self.figure)
        self.graph_layout.addWidget(self.canvas)
        self.main_layout.addWidget(self.graph_widget, 2) # Proportion 2 pour le graphique
        self.central_widget.setLayout(self.main_layout)

################################
#
# Save the graph button
#
################################

    def save_graph(self):
        """Ouvre une boîte de dialogue pour sauvegarder le graphique."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save plot", "",
                                                   "Images (*.png *.jpg *.jpeg *.pdf)")
        if file_path:
            self.figure.savefig(file_path)
            QMessageBox.information(self, "Plot saved", f"The plot has been saved in : {file_path}")

################################
#
# Paste from Excle button
#
################################

    def paste_from_excel(self):
        """Colle les données depuis le presse-papiers (format Excel) et met à jour l'interface."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        rows = text.strip().split('\n')
        if not rows:
            return

        num_cols = len(rows[0].split('\t')) + 1  # +1 pour la colonne d'inclusion
        self.data_table.setColumnCount(num_cols)

        # Configurer les en-têtes
        headers = ["Inclure"] + [f"v{i}" for i in range(num_cols - 1)]
        if num_cols > 1:
            headers[1] = "[S]"
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            # Ajouter la checkbox pour l'inclusion de la ligne (cochée par défaut)
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.Checked)
            self.data_table.setItem(i, 0, checkbox_item)

            # Ajouter les données collées
            values = row.split('\t')
            for j, value in enumerate(values):
                value = value.replace(',', '.')
                item = QTableWidgetItem(value)
                self.data_table.setItem(i, j + 1, item)

        # Ajuster les colonnes à leur contenu
        self.data_table.resizeColumnsToContents()

        # Mettre à jour le panneau des colonnes à inclure
        self.update_column_panel(headers)
        self.excluded_data = {} # Réinitialiser les exclusions lors du collage
################################
#
# Update checkbox
#
################################

    def update_column_panel(self, headers):
        """Met à jour le panneau des checkboxes pour les colonnes à inclure"""
        # Effacer les checkboxes existantes
        for checkbox in self.column_checkboxes.values():
            self.column_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.column_checkboxes = {}

        # Ajouter une checkbox pour chaque colonne v0
        for col in range(2, self.data_table.columnCount()):
            checkbox = QCheckBox(headers[col])
            checkbox.setChecked(True)  # Cochée par défaut
            self.column_layout.addWidget(checkbox)
            self.column_checkboxes[col] = checkbox

################################
#
# exclude values
# 
################################

    def get_data_for_exclusion_dialog(self):
        """Récupère les données S et v0 pour le dialogue d'exclusion."""
        S_values = []
        v0_values = {}
        num_rows = self.data_table.rowCount()
        num_cols = self.data_table.columnCount()

        for row in range(num_rows):
            s_item = self.data_table.item(row, 1)
            if s_item is not None:
                try:
                    S_values.append(float(s_item.text().replace(',', '.')))
                except ValueError:
                    S_values.append(np.nan)
            else:
                S_values.append(np.nan)

            for col in range(2, num_cols):
                v_item = self.data_table.item(row, col)
                v_value = np.nan
                if v_item is not None:
                    try:
                        v_value = float(v_item.text().replace(',', '.'))
                    except ValueError:
                        pass
                v0_values.setdefault(col - 2, []).append(v_value)

        return S_values, v0_values

    def open_exclusion_gui(self):
        S_values, v0_values = self.get_data_for_exclusion_dialog()

        def on_apply_exclusion(new_exclusions):
            self.excluded_data = new_exclusions
            #print("Update serie excluded :", self.excluded_data)
            self.fit_data() # Refit après exclusion

        dialog = ExclusionDialog(self, S_values, v0_values, self.excluded_data, on_apply_exclusion)
        dialog.exec_()

################################
#
# The heart of the script 
#  
################################
    def fit_data(self):
        """Performs data fitting, taking into account selected columns and excluded points."""

        s_data_all = []  # Keep all s_data, including excluded
        self.processed_data_series_mm = []
        self.processed_data_series_lb = []

        # Retrieve [S] data for included rows
        for row in range(self.data_table.rowCount()):
            if self.data_table.item(row, 0) is not None and self.data_table.item(row, 0).checkState() == Qt.Checked:
                if self.data_table.item(row, 1) is not None:
                    try:
                        s_data_all.append(float(self.data_table.item(row, 1).text().replace(',', '.')))
                    except ValueError:
                        QMessageBox.warning(self, "Format Error",
                                            f"Non-numeric value found in [S] column at row {row + 1}.")
                        return

        # Process each column
        for col in range(2, self.data_table.columnCount()):
            if col - 2 in self.excluded_data:
                excluded_indices = self.excluded_data[col - 2]
            else:
                excluded_indices = set()

            if col in self.column_checkboxes and self.column_checkboxes[col].isChecked():
                s_fit_for_v = []
                v_data = []
                excluded_s = []
                excluded_v = []
                original_s = []
                original_v = []
                excluded_residuals = []  # To store residuals of excluded points

                for row in range(self.data_table.rowCount()):
                    if self.data_table.item(row, 0) is not None and self.data_table.item(row,
                                                                                       0).checkState() == Qt.Checked:
                        s_val_mm = np.nan
                        v_val_mm = np.nan
                        s_val_lb = np.nan
                        v_val_lb = np.nan

                        s_item = self.data_table.item(row, 1)
                        v_item = self.data_table.item(row, col)

                        if s_item is not None:
                            try:
                                s_val_mm = float(s_item.text().replace(',', '.'))
                                s_val_lb = float(s_item.text().replace(',', '.'))
                            except ValueError:
                                pass

                        if v_item is not None:
                            try:
                                v_val_mm = float(v_item.text().replace(',', '.'))
                                v_val_lb = float(v_item.text().replace(',', '.'))
                            except ValueError:
                                pass

                        if row not in excluded_indices:
                            if not np.isnan(v_val_mm):
                                s_fit_for_v.append(s_val_mm)
                                v_data.append(v_val_mm)
                        else:
                            if not np.isnan(s_val_mm) and not np.isnan(v_val_mm):
                                excluded_s.append(s_val_mm)
                                excluded_v.append(v_val_mm)

                        # For Lineweaver-Burk
                        if not np.isnan(s_val_lb) and not np.isnan(v_val_lb) and s_val_lb != 0 and v_val_lb != 0:
                            original_s.append(s_val_lb)
                            original_v.append(v_val_lb)

                # Filter data for fitting (MM)
                s_fit_data_mm = np.array([s for i, s in enumerate(s_fit_for_v) if not np.isnan(v_data[i])])
                v_fit_data_mm = np.array([v for v in v_data if not np.isnan(v)])
                excluded_s_array = np.array(excluded_s)
                excluded_v_array = np.array(excluded_v)

                # LB - No filtering needed, use original data
                s_fit_data_lb = np.array(original_s)
                v_fit_data_lb = np.array(original_v)
                inv_s_fit_data_lb = 1 / s_fit_data_lb if s_fit_data_lb.size > 0 else np.array([])
                inv_v_fit_data_lb = 1 / v_fit_data_lb if v_fit_data_lb.size > 0 else np.array([])

                if len(s_fit_data_mm) >= 2:
                    col_name = self.data_table.horizontalHeaderItem(col).text()
                    self.processed_data_series_mm.append(
                        (s_fit_data_mm, v_fit_data_mm, col_name, excluded_s_array, excluded_v_array, excluded_residuals))  # Added excluded_residuals
                    self.processed_data_series_lb.append(
                        (inv_s_fit_data_lb, inv_v_fit_data_lb, col_name, s_fit_data_lb, v_fit_data_lb))

        if not self.processed_data_series_mm:
            QMessageBox.warning(self, "Select Data",
                               "Please check at least one velocity series to fit and include data points.")
            return

        self.figure.clear()

        num_series = len(self.processed_data_series_mm)

        mm_height = 4
        residual_height = 1
        height_ratios = [mm_height] + [residual_height] * num_series

        gs = self.figure.add_gridspec(num_series + 1, 1, height_ratios=height_ratios,
                                      hspace=0.25)
        ax_mm = self.figure.add_subplot(gs[0])
        vmax_results = []
        km_results = []
        r_squared_results = []
        residual_axes = []

        best_km = float('inf')  # Initialize with a very high value
        self.Km_best = None  # Initialize Km_best attribute

        for i, (s_fit, v_fit, label, excluded_s, excluded_v, excluded_residuals) in enumerate(self.processed_data_series_mm):  # Added excluded_residuals
            try:
                popt, pcov = curve_fit(self.michaelis_menten, s_fit, v_fit, p0=[np.max(v_fit), np.mean(s_fit)])
                vmax_fit, km_fit = popt

                v_predicted = self.michaelis_menten(s_fit, vmax_fit, km_fit)
                residuals = v_fit - v_predicted

                # Calculate residuals for excluded points
                excluded_residuals = []
                for j in range(len(excluded_s)):
                    excluded_residuals.append(excluded_v[j] - self.michaelis_menten(excluded_s[j], vmax_fit, km_fit))

                ss_res = np.sum(residuals ** 2)
                ss_tot = np.sum((v_fit - np.mean(v_fit)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                vmax_results.append(vmax_fit)
                km_results.append(km_fit)
                r_squared_results.append(r_squared)

                # Check if this Km is the lowest so far
                if km_fit < best_km:
                    best_km = km_fit
                    self.Km_best = (label, km_fit)  # Store label and Km value

                color = plt.cm.viridis(i / num_series)

                ax_mm.scatter(s_fit, v_fit, label=f"Serie {label}", color=color, s=20)

                if len(excluded_s) > 0:
                    #ax_mm.scatter(excluded_s, excluded_v, label=f"Excluded {label}", color=color, marker='x', alpha=0.5, s=20)
                    ax_mm.scatter(excluded_s, excluded_v, color=color, marker='x', alpha=0.5,
                                s=20)
                s_plot = np.linspace(0, np.max(s_fit) * 1.2, 100)
                v_plot = self.michaelis_menten(s_plot, vmax_fit, km_fit)
                ax_mm.plot(s_plot, v_plot, '-',
                          label=f"Fit {label} (Vmax={vmax_fit:.2e}, Km={km_fit:.2e}, R²={r_squared:.3f})", color=color)
                #increase the space for y axis 
                ax_mm.axhline(y=(vmax_fit*1.1), color=color, linestyle='--', alpha=0)
                ax_mm.axvline(x=km_fit, color=color, linestyle='--', alpha=0)
                if i < num_series - 1:
                    ax_mm.tick_params(axis='x', labelbottom=False)

                ax_res = self.figure.add_subplot(gs[i + 1], sharex=ax_mm)
                ax_res.scatter(s_fit, residuals, color=color, s=20)
                if len(excluded_s) > 0:
                    ax_res.scatter(excluded_s, excluded_residuals, color=color, marker='x', alpha=0.5, s=20)  # Plot excluded residuals
                ax_res.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
                tolerance = 0.1 * v_predicted
                ax_res.fill_between(s_fit, -tolerance, tolerance, color=color, alpha=0.15)
                ax_res.set_ylabel("Residuals")
                if i < num_series - 1:
                    ax_res.tick_params(axis='x', labelbottom=False)

                residual_axes.append(ax_res)

            except ValueError:
                QMessageBox.critical(self, "Fitting Error",
                                     f"Error fitting series {label}. Check the data.")
            except RuntimeError:
                QMessageBox.warning(self, "Fitting Error",
                                     f"Fitting for series {label} did not converge.")

        ax_mm.set_xlabel("[S]0")
        ax_mm.set_ylabel("v0")
        ax_mm.set_title("MM-Fit")
        ax_mm.legend(fontsize='small')
        ax_mm.tick_params(axis='x', labelbottom=False)
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-2, 2))  # Show scientific notation when appropriate
        ax_mm.xaxis.set_major_formatter(formatter)
        ax_mm.ticklabel_format(style='sci', axis='x', scilimits=(-2, 2))
        ax_mm.tick_params(axis='x', which='both', labelsize=10)
        
        if residual_axes:
            residual_axes[-1].set_xlabel("[S]0")

        self.figure.tight_layout()

        self.canvas.draw()



#################################
#
# LB plot 
#  
################################

    def show_lineweaver_burk(self):
        """Affiche la représentation de Lineweaver-Burk dans une nouvelle fenêtre,
        en tenant compte des points exclus et en utilisant les données pré-calculées,
        avec une option pour afficher l'ajustement linéaire."""
        if not self.processed_data_series_lb:
            QMessageBox.warning(self, "Avertissement", "Veuillez d'abord charger et fitter les données.")
            return

        self.lb_window = QMainWindow(self)
        self.lb_window.setWindowTitle("Lineweaver-Burk plot")
        self.lb_central_widget = QWidget()
        self.lb_window.setCentralWidget(self.lb_central_widget)
        self.lb_layout = QVBoxLayout(self.lb_central_widget)

        self.lb_figure = Figure(figsize=(8, 6), dpi=100)
        self.lb_canvas = FigureCanvas(self.lb_figure)
        self.lb_layout.addWidget(self.lb_canvas)
        self.lb_ax = self.lb_figure.add_subplot(111)

        self.show_fit_checkbox = QCheckBox("Display linear fit")
        self.lb_layout.addWidget(self.show_fit_checkbox)
                # Add print button
        self.print_button = QPushButton("Print")
        self.print_button.clicked.connect(self.print_lb_graph)
        self.lb_layout.addWidget(self.print_button)


        self.show_fit_checkbox.stateChanged.connect(self.update_lineweaver_burk_plot)

        self.lb_data = [] # Stocker les données pour la mise à jour du plot

        for i, (inv_s_fit, inv_v_fit, label, original_s, original_v) in enumerate(self.processed_data_series_lb):
            # Identifier les points exclus (comparer avec les données originales et self.excluded_data)
            excluded_indices = self.excluded_data.get(i, set())
            included_inv_s = []
            included_inv_v = []
            excluded_inv_s = []
            excluded_inv_v = []

            original_data_indices = 0
            for row in range(self.data_table.rowCount()):
                if self.data_table.item(row, 0) is not None and self.data_table.item(row, 0).checkState() == Qt.Checked:
                    s_val = None
                    v_val = None
                    s_item = self.data_table.item(row, 1)
                    v_item = self.data_table.item(row, i + 2) # L'index de la colonne v correspondante

                    if s_item is not None:
                        try:
                            s_val = float(s_item.text().replace(',', '.'))
                        except ValueError:
                            pass
                    if v_item is not None:
                        try:
                            v_val = float(v_item.text().replace(',', '.'))
                        except ValueError:
                            pass

                    if s_val is not None and v_val is not None and s_val != 0 and v_val != 0:
                        if row not in excluded_indices:
                            included_inv_s.append(1 / s_val)
                            included_inv_v.append(1 / v_val)
                        else:
                            excluded_inv_s.append(1 / s_val)
                            excluded_inv_v.append(1 / v_val)
                    original_data_indices += 1

            self.lb_data.append({
                'label': label,
                'included_inv_s': included_inv_s,
                'included_inv_v': included_inv_v,
                'excluded_inv_s': excluded_inv_s,
                'excluded_inv_v': excluded_inv_v,
                'original_s': list(original_s),  # Ajouter original_s (converti en liste pour la sérialisation si nécessaire)
                'original_v': list(original_v)   # Ajouter original_v (converti en liste pour la sérialisation si nécessaire)
                })

        self.update_lineweaver_burk_plot(Qt.Unchecked) # Affichage initial sans la droite de régression
        self.lb_window.resize(800, 600)
        self.lb_window.show()

        ###############
        # cherry on the cake 
        ###############
    
    def update_lineweaver_burk_plot(self, state):
        self.lb_ax.clear()  # Effacer le graphique précédent
        show_fit = (state == Qt.Checked)

        # Listes pour stocker toutes les valeurs pertinentes
        all_inv_s = []  # Pour stocker toutes les valeurs de 1/[S]
        all_inv_v = []
        x_intercepts = []  # Pour stocker les intersections -1/Km
        
        # Process each data series
        for i, data in enumerate(self.lb_data):
            label = data['label']
            included_inv_s = data['included_inv_s']
            included_inv_v = data['included_inv_v']
            excluded_inv_s = data['excluded_inv_s']
            excluded_inv_v = data['excluded_inv_v']
            color = plt.cm.viridis(i / len(self.processed_data_series_lb))
            all_inv_s.extend(included_inv_s)
            all_inv_s.extend(excluded_inv_s)
            all_inv_v.extend(included_inv_v)
            all_inv_v.extend(excluded_inv_v)

            # Tracer les points inclus
            self.lb_ax.scatter(included_inv_s, included_inv_v, label=f"Serie {label}",color=color)

            # Tracer les points exclus
            self.lb_ax.scatter(excluded_inv_s, excluded_inv_v, color=color, alpha=0.5, marker='x')
            #self.lb_ax.scatter(excluded_inv_s, excluded_inv_v, label=f"Data {label} (exclus)", color=color, alpha=0.5, marker='x')

            # Calculer et afficher l'ajustement linéaire si la case est cochée
            if show_fit and included_inv_s:
                try:
                    slope, intercept, r_value, p_value, std_err = linregress(included_inv_s, included_inv_v)

                    # Calculer Km et Vmax à partir de la régression
                    lb_vmax = 1 / intercept if intercept != 0 else np.inf
                    lb_km = slope / intercept if intercept != 0 else np.inf
                    
                    # Important: calculer l'intersection avec l'axe X
                    x_intercept = -1 / lb_km if lb_km != 0 else 0
                    x_intercepts.append(x_intercept)
                    
                    # Définir une plage qui s'étend suffisamment dans les valeurs négatives
                    min_inv_s_local = 1.5 * x_intercept if x_intercept < 0 else -1000  # S'assurer que nous allons bien au-delà de -1/Km
                    max_inv_s_local = max(included_inv_s) * 1.2 if included_inv_s else 3000
                    
                    inv_s_plot = np.linspace(min_inv_s_local, max_inv_s_local, 100)
                    inv_v_plot = slope * inv_s_plot + intercept
                    
                    self.lb_ax.plot(inv_s_plot, inv_v_plot, '-', color=color, 
                                label=f"Fit {label} (1/Vmax={intercept:.2e}, Km/Vmax={slope:.2e}, Vmax={lb_vmax:.2e}, Km={lb_km:.2e}, R²={r_value**2:.3f})")
                    
                    # Marquer clairement l'intercept -1/Km
                    self.lb_ax.axvline(x=x_intercept, color='gray', linestyle='--', alpha=0)
                    
                except ValueError:
                    QMessageBox.warning(self, "Warning LB", f"Linear regression error for serie {label} .")

        # Configurer explicitement les limites des axes
        min_x = -1000  # Valeur par défaut
        #add the min_x as the lowest KM from MM-fit
        if self.Km_best:
            best_label, lowest_km = self.Km_best
            #print(f"The series with the lowest Km is: {best_label} with Km = {lowest_km:.3e}")
            min_x = ((-1/lowest_km)*1.2)
        else:
            print("No valid Km values were found during fitting.")
        if x_intercepts:
            # Définir min_x pour inclure tous les points d'intersection avec une marge
            min_val = min(x_intercepts)
            min_x = min_val * 1.2 if min_val < 0 else min_val * 0.8  # Ajouter 20% de marge dans la bonne direction
            
        # Définir max_x basé sur les données
        max_x = max(all_inv_s) * 1.2 if all_inv_s else 3000
        
        # Définir les limites de l'axe Y
        if all_inv_v:
            min_y = min(0, min(all_inv_v))
            max_y = max(all_inv_v) * 1.2
            self.lb_ax.set_ylim(min_y, max_y)
        
        # Ajouter les axes x=0 et y=0
        self.lb_ax.axvline(x=0, color='black', linewidth=1.5)
        self.lb_ax.axhline(y=0, color='black', linewidth=1.5)
        
        self.lb_ax.set_xlabel("1/[S]0")
        self.lb_ax.set_ylabel("1/v0")
        self.lb_ax.set_title("Lineweaver-Burk plot")
        self.lb_ax.legend(fontsize='small')
        self.lb_ax.grid(True)
        
        # Régler les limites AVANT tight_layout
        self.lb_ax.set_xlim(min_x, max_x)
        
        self.lb_figure.tight_layout()
        
        # Régler les limites APRÈS tight_layout pour s'assurer qu'elles ne sont pas modifiées
        self.lb_ax.set_xlim(min_x, max_x)
        
        self.lb_canvas.draw()
        
    def print_lb_graph(self):
        """Ouvre une boîte de dialogue d'impression et imprime le graphique Lineweaver-Burk."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setResolution(300)

        dialog = QPrintDialog(printer, self.lb_window)  # Use lb_window as parent
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.lb_canvas.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.lb_canvas.rect())
            self.lb_canvas.render(painter)
            painter.end()
 
   
#################################
#
# Print data 
#  
################################

    def print_graph(self):
        """Ouvre une boîte de dialogue d'impression et imprime le graphique."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setResolution(300)  # DPI personnalisé (points par pouce)

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.canvas.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.canvas.rect())
            self.canvas.render(painter)
            painter.end()


#################################
#
# Reset data 
#  
################################

    def reset_data(self):
        """Efface toutes les données du tableau et réinitialise l'interface."""
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]"])

        # Supprimer toutes les checkboxes des colonnes
        for checkbox in self.column_checkboxes.values():
            self.column_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.column_checkboxes = {}
        self.excluded_data = {}
        # Effacer la figure et redessiner le canvas
        self.figure.clear()
        self.canvas.draw()

################################ 
# 
# The principle function for the fit
#  
################################     
  
    def michaelis_menten(self, s, vmax, km):
        """Fonction de Michaelis-Menten."""
        return (vmax * s) / (km + s)
    
#################################
#
# get the exclusion window
#  
################################

# === Exclusion Dialog ===
class ExclusionDialog(QDialog):
    def __init__(self, parent, S_values, v0_values, excluded_data_init, apply_callback):
        super().__init__(parent)
        self.setWindowTitle("Exclude v0")
        self.apply_callback = apply_callback
        self.checkboxes = []

        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid = QGridLayout()

        grid.addWidget(QLabel("[S]0"), 0, 0)
        num_v0_cols = len(v0_values)
        for v_idx in range(num_v0_cols):
            grid.addWidget(QLabel(f"Serie-{v_idx+1}"), 0, 1 + v_idx * 2, 1, 2, alignment=Qt.AlignCenter)

        max_rows = max(len(S_values), max(len(v_list) for v_list in v0_values.values()) if v0_values else 0)

        for idx in range(max_rows):
            s_label_text = f"{S_values[idx]:.2E}" if idx < len(S_values) else ""
            grid.addWidget(QLabel(s_label_text), idx + 1, 0)
            for v_idx in range(num_v0_cols):
                v_value = ""
                is_excluded = idx in excluded_data_init.get(v_idx, set())
                cb = QCheckBox()
                cb.setChecked(is_excluded)
                self.checkboxes.append((v_idx, idx, cb))

                if v_idx in v0_values and idx < len(v0_values[v_idx]):
                    v_value = f"{v0_values[v_idx][idx]:.2E}"

                grid.addWidget(cb, idx + 1, 1 + v_idx * 2, alignment=Qt.AlignCenter)
                grid.addWidget(QLabel(v_value), idx + 1, 2 + v_idx * 2)

        scroll_widget.setLayout(grid)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply and Fit")
        apply_button.clicked.connect(self.apply_exclusion)
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.resize(600, 400)

    def apply_exclusion(self):
        new_excluded_data = {}
        for v_idx, idx, cb in self.checkboxes:
            if cb.isChecked():
                new_excluded_data.setdefault(v_idx, set()).add(idx)
        self.apply_callback(new_excluded_data)
        self.accept()

################################
#
# The end
#  
################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())