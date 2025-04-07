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

        # Variables for point select.
        self.selected_index = 0
        self.data = None
        self.time_values = None
        self.ecg_values = None
        self.ecg_col = None
        self.selected_marker = None
        self.tooltip = None
        self.heart_line = None  # Var for rand linear line on the heart  graph.
        self.rect = None
        self.rect_start = None
        self.rect_end = None

        self.rects = []
        self._drawing = None
        self._dragging = None



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
            a1.set_title("ECG")

        a2.set_title("Heart Rate")

        if hasattr(self, 'c'):
            self.c.get_tk_widget().destroy()

        self.c = FigureCanvasTkAgg(fig, master=self.lsideF)
        self.c.draw()  # New canvas.
        self.c.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.c.mpl_connect("pick_event", self.on_pick)

        # Here are mouse events
        if data is not None:
            self.c.mpl_connect("button_press_event", self.on_click)
            self.c.mpl_connect("motion_notify_event", self.on_drag)
            self.c.mpl_connect("button_press_event", self.on_press)
            self.c.mpl_connect("motion_notify_event", self.on_motion)
            self.c.mpl_connect("button_release_event", self.on_release)

    def on_pick(self, event):
        artist = event.artist
        for r in list(self.rects):
            if r['close'] is artist:
                r['patch'].remove()
                r['close'].remove()
                self.rects.remove(r)
                self.c.draw()
                return

    def on_press(self, event):
        if event.inaxes is not self.ax1:
            return
        if event.button == 3:
            self._drawing = (event.xdata, event.ydata)
            return
        # left‑click check for ×
        if event.button == 1:
            for r in list(self.rects):
                tx, ty = r['close'].get_position()
                xh = np.ptp(self.ax1.get_xlim())*0.02
                yh = np.ptp(self.ax1.get_ylim())*0.05
                if abs(event.xdata-tx)<xh and abs(event.ydata-ty)<yh:
                    r['patch'].remove()
                    r['close'].remove()
                    self.rects.remove(r)
                    self.c.draw()
                    return
            for r in self.rects:
                x0,y0 = r['patch'].get_xy()
                w,h  = r['patch'].get_width(), r['patch'].get_height()
                if x0<=event.xdata<=x0+w and y0<=event.ydata<=y0+h:
                    self._dragging = (r, event.xdata, event.ydata, x0, y0)
                    return

    def on_motion(self, event):
        if event.inaxes is not self.ax1:
            return
        if self._drawing:
            x0,y0 = self._drawing
            dx, dy = event.xdata-x0, event.ydata-y0
            if hasattr(self, '_temp'):
                self._temp.remove()
            self._temp = plt.Rectangle((x0,y0), dx, dy,
                                       edgecolor='black', facecolor='none')
            self.ax1.add_patch(self._temp)
            self.c.draw()
        # dragging
        elif self._dragging:
            r, px, py, x0, y0 = self._dragging
            dx, dy = event.xdata - px, event.ydata - py

            new_x, new_y = x0 + dx, y0 + dy
            r['patch'].set_xy((new_x, new_y))

            w, h = r['patch'].get_width(), r['patch'].get_height()
            cx, cy = new_x + w, new_y + h
            r['close'].set_position((cx, cy))

            #  indices
            idxs = np.where((self.time_values >= new_x) &
                            (self.time_values <= new_x + w))[0]
            r['start'] = idxs.min() if idxs.size else None
            r['end'] = idxs.max() if idxs.size else None
            print(f"Covers indices {r['start']} to {r['end']}")
            self.c.draw()

    def on_release(self, event):
        if event.inaxes is not self.ax1:
            return
        if event.button == 3 and self._drawing:
            x0, y0 = self._drawing
            x1, y1 = event.xdata, event.ydata
            xmin, xmax = sorted([x0, x1])
            ymin, ymax = sorted([y0, y1])
            idxs = np.where((self.time_values >= xmin) & (self.time_values <= xmax))[0]
            start = idxs.min() if idxs.size else None
            end = idxs.max() if idxs.size else None

            patch = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                  edgecolor='black', facecolor='blue',alpha=0.3)
            self.ax1.add_patch(patch)  

            close_x = xmin + (xmax - xmin)
            close_y = ymin + (ymax - ymin) + 1

            close = self.ax1.text(
                close_x, close_y, "×",
                color='black', fontsize=5, weight='bold',
                ha='right', va='top',
                bbox=dict(
                    boxstyle="circle,pad=0.2",
                    facecolor="white",
                    edgecolor="gray",
                    linewidth=1
                ),
            picker = True
            )

            self.rects.append({'patch': patch, 'close': close, 'start': start, 'end': end})

            if hasattr(self, '_temp'):
                self._temp.remove()
                del self._temp

            self._drawing = None
            print(f"Rectangle covers indices {start} to {end}")
            self.c.draw()

        if event.button == 1 and self._dragging:
            self._dragging = None

    def on_click(self, event):
        if event.inaxes is not None:
            if self.rect is None:
                self.rect_start = (event.xdata, event.ydata)
                self.rect = self.ax1.add_patch(
                    plt.Rectangle(self.rect_start, 0, 0, linewidth=1, edgecolor='r', facecolor='none'))
            else:
                self.rect_end = (event.xdata, event.ydata)
                self.update_rectangle()
                self.c.draw()

    def on_drag(self, event):
        if self.rect is not None and event.inaxes is not None:
            self.rect_end = (event.xdata, event.ydata)
            self.update_rectangle()
            self.c.draw()

    def update_rectangle(self):
        if self.rect_start is not None and self.rect_end is not None:
            x1, y1 = self.rect_start
            x2, y2 = self.rect_end
            width = x2 - x1
            height = y2 - y1
            self.rect.set_width(width)
            self.rect.set_height(height)
            self.rect.set_xy((min(x1, x2), min(y1, y2)))

    def makecontrols(self):
        # making UI for the controls
        r = 0
        control_sects = [
            ("Heartbeats", ["Add Heartbeat", "Remove Heartbeat"]),
            ("Data Removal", ["Toggle Removal Mode", "Draw Removal Interval"]),
            ("Rectangle Controls", ["Delete Rectangle"])
        ]
        for sect_title, button_list in control_sects:
            sectFrame = ttk.LabelFrame(self.rsideF, text=sect_title)
            sectFrame.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
            r += 1
            for button in button_list:
                ttk.Button(sectFrame, text=button,
                           command=self.delete_rectangle if button == "Delete Rectangle" else None).pack(fill=tk.X,
                                                                                                         padx=5, pady=2)

        # Add more UI elements if needed...

    def delete_rectangle(self):
        """Delete the current rectangle."""
        if self.rect is not None:
            self.rect.remove()
            self.rect = None
            self.rect_start = None
            self.rect_end = None
            self.c.draw()

    def on_left(self, event):
        if self.time_values is not None and self.selected_index > 0:
            self.selected_index -= 1
            self.update_selected_point()

    def on_right(self, event):
        if self.time_values is not None and self.selected_index < len(self.time_values) - 1:
            self.selected_index += 1
            self.update_selected_point()

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

            # Assume the first column is the time column.
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


if __name__ == "__main__":
    root = tk.Tk()
    app = ecg_applicaion(root)
    root.mainloop()
