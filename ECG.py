import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from tkinter import ttk, filedialog

class ecg_applicaion:
    def __init__(self, mast):
        # Set up the main window and frames.
        self.m = mast
        self.m.title("ECG Analysis")
        self.m.geometry("1200x600")
        self.topF = tk.Frame(self.m, bg="white", height=20)
        self.topF.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.m.grid_rowconfigure(0, weight=1)
        self.lsideF = tk.Frame(self.m, bg="white")
        self.lsideF.grid(row=1, column=0, sticky="nsew")
        self.rsideF = tk.Frame(self.m, bg="lightgray")
        self.rsideF.grid(row=1, column=1, sticky="ns")
        self.m.grid_rowconfigure(1, weight=1)
        self.m.grid_columnconfigure(0, weight=1)
        self.m.grid_columnconfigure(1, weight=0)

        # Variables for  point select.
        self.selected_index = 0
        self.data = None
        self.time_values = None
        self.ecg_values = None
        self.ecg_col = None
        self.selected_marker = None
        self.tooltip = None
        self.heart_line = None  # Var for rand linear line on the heart  graph.
        # Attributes to update
        self.ax1 = None
        self.ax2 = None

        # Intializing functions for graphs
        self.makecontrols()
        self.dographs()

        self.m.bind("<Left>", self.on_left)
        self.m.bind("<Right>", self.on_right)

    def dographs(self, data=None):
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5))
        fig.subplots_adjust(hspace=0.7)
        self.ax1 = a1  # here we are Storing the ECG axis.
        self.ax2 = a2  # Store the Heart Rate axis.

        # For testing purposes, I used CSV data, similar to what was done in SigSync
        if data is not None:
            print("w")
            for col in data.columns:
                if col != 'Time':
                    a1.plot(data['Time'], data[col], label=col)
            a1.set_title("ECG")
            a1.legend()

            self.data = data
            self.time_values = data['Time'].values
            non_time_cols = [col for col in data.columns if col != 'Time']
            if non_time_cols:
                self.ecg_col = non_time_cols[0]
                self.ecg_values = data[self.ecg_col].values
            else:
                self.ecg_col = None
                self.ecg_values = None

            if self.selected_index >= len(self.time_values):
                self.selected_index = 0

            # Adding the red marker at the point.
            x_val = self.time_values[self.selected_index]
            y_val = self.ecg_values[self.selected_index] if self.ecg_values is not None else 0
            self.selected_marker, = a1.plot([x_val], [y_val], 'ro', markersize=8)
            # Adding the text next to the dot// Rounding to the 2nd decimal spot
            self.tooltip = a1.text(x_val, y_val, f'Time: {x_val:.2f}\nAmp: {y_val:.2f}',
                                   fontsize=9, color='black', bbox=dict(facecolor='white', alpha=0.7))
        else:
            print("WHAT")
            a1.set_title("ECG")

        a2.set_title("Heart Rate")

        #  destroying canvas before creating a new one, so we can see new graph
        if hasattr(self, 'c'):
            self.c.get_tk_widget().destroy()

        self.c = FigureCanvasTkAgg(fig, master=self.lsideF)
        self.c.draw()  # New canvas.
        self.c.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Here are mouse events
        if data is not None:
            self.c.mpl_connect("button_press_event", self.on_click)
            self.c.mpl_connect("motion_notify_event", self.on_drag)

    def update_selected_point(self):
        if self.time_values is not None and self.ecg_values is not None:
            x_val = self.time_values[self.selected_index]
            y_val = self.ecg_values[self.selected_index]
            self.selected_marker.set_data([x_val], [y_val])
            # Updating the text and position that is presented
            self.tooltip.set_position((x_val, y_val))
            self.tooltip.set_text(f'Time: {x_val:.2f}\nAmp: {y_val:.2f}')
            self.c.draw()

    def on_click(self, event):
        if event.inaxes is not None and self.time_values is not None:
            x_click = event.xdata
            # Find the index where Time is closest to the click position.
            idx = (np.abs(self.time_values - x_click)).argmin()
            self.selected_index = idx
            self.update_selected_point()
            # Create a random linear line on the Heart Rate graph.
            self.add_random_heart_line()

    def on_drag(self, event):
        if event.inaxes is not None and event.xdata is not None and event.button is not None:
            x_drag = event.xdata
            idx = (np.abs(self.time_values - x_drag)).argmin()
            self.selected_index = idx
            self.update_selected_point()

    def on_left(self, event):
        if self.time_values is not None and self.selected_index > 0:
            self.selected_index -= 1
            self.update_selected_point()

    def on_right(self, event):
        if self.time_values is not None and self.selected_index < len(self.time_values) - 1:
            self.selected_index += 1
            self.update_selected_point()

    def add_random_heart_line(self):
        random_slope = np.random.uniform(-0.5, 0.5)
        random_intercept = np.random.uniform(50, 150)
        if self.heart_line is not None:
            self.heart_line.remove()
        x_vals = np.linspace(*self.ax2.get_xlim(), num=100)
        y_vals = random_slope * x_vals + random_intercept
        self.heart_line, = self.ax2.plot(x_vals, y_vals, color='green', linestyle='-', label='Random Linear')
        self.ax2.legend()
        self.c.draw()

    def makecontrols(self):
        # making UI for the controls
        r = 0
        control_sects = [
            ("Heartbeats", ["Add Heartbeat", "Remove Heartbeat"]),
            ("Data Removal", ["Toggle Removal Mode", "Draw Removal Interval"])
        ]
        for sect_title, button_list in control_sects:
            sectFrame = ttk.LabelFrame(self.rsideF, text=sect_title)
            sectFrame.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
            r += 1
            for button in button_list:
                ttk.Button(sectFrame, text=button).pack(fill=tk.X, padx=5, pady=2)

        viewF = ttk.LabelFrame(self.rsideF, text="View")
        viewF.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1
        ttk.Label(viewF, text="View Window (s)").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Label(viewF, text="ECG Y Limits").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Label(viewF, text="HR Y Limits").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Checkbutton(viewF, text="Show Raw Signal").pack(anchor="w", padx=5)
        ttk.Checkbutton(viewF, text="Show Partial Calculation Area").pack(anchor="w", padx=5)

        upload_btn = ttk.Button(self.rsideF, text="Upload ECG Data", command=self.upload_file)
        upload_btn.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1

        info = ttk.LabelFrame(self.rsideF, text="Session Info")
        info.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1
        ttk.Label(info, text="Session Length (s): 44.05").pack(pady=2)
        ttk.Label(info, text="Sampling Rate (Hz): 1000").pack(pady=2)
        ttk.Label(info, text="Filename:").pack()
        ttk.Label(info, text="Filepath: /Users/devlab...").pack()

        tab = ttk.LabelFrame(self.rsideF, text="Chart Data")
        tab.grid(row=0, column=1, rowspan=len(self.rsideF.winfo_children()), sticky="new", padx=10, pady=5)
        cols = ("Start", "Stop")
        self.tab = ttk.Treeview(tab, columns=cols, show="headings", height=20)
        self.tab.heading("Start", text="Start", anchor="w")
        self.tab.heading("Stop", text="Stop", anchor="w")
        self.tab.column("Start", width=100, anchor="w")
        self.tab.column("Stop", width=100, anchor="w")
        self.tab.pack(side="top", fill=tk.X)

    def upload_file(self):
        filepath = filedialog.askopenfilename(
            title="Select ECG CSV file", filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            self.load_signal_data(filepath)
        else:
            print("No file selected.")

    def load_signal_data(self, what):
        """Load signal data from CSV and store time and data in variables."""
        try:
            df = pd.read_csv(what)
            column_names = df.columns
            print("Columns in the file:", df.columns)

            self.without_time = []

            # Assumign that the first column is the time column.
            self.signal_time = df[column_names[0]].values

            self.signal_data = {}

            for col in column_names:
                self.signal_data[col] = df[col].values

            for col in column_names:
                if col != "Time":
                    self.without_time.append(self.signal_data[col])

            self.signal_data["rest"] = np.transpose(np.array(self.without_time))
            print("Signal time:", self.signal_time)
            print("Rest data (transposed):", self.signal_data["rest"])

            print("Calling method")
            self.nothing()
        except Exception as e:
            print("Error loading signal data:", e)

    def nothing(self):
        """Update the ECG graph with the loaded signal data."""
        data_dict = {"Time": self.signal_time}
        for key in self.signal_data:
            if key not in ["rest"]:
                if key != "Time":
                    data_dict[key] = self.signal_data[key]
        df = pd.DataFrame(data_dict)
        self.dographs(df)

if __name__ == "__main__":
    root = tk.Tk()
    app = ecg_applicaion(root)
    root.mainloop()

