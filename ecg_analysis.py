import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import ttk



class ecg_applicaion:
    def __init__(self, mast):
        # this is setting up the ECG analysis.
        self.m = mast
        self.m.title("ECG Analysis")
        self.m.geometry("1200x600")  # window size
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

        self.makecontrols()
        self.dographs()


    def dographs(self):
        # Plotting
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5))
        fig.subplots_adjust(hspace=0.7)


        x_vals = np.linspace(0, 13, 1000)
        sig = 300 * np.sin(2 * np.pi * 1.5 * x_vals)
        a1.plot(x_vals, sig, label="Raw")
        a1.set_title("ECG")
        a1.legend()
        a1.set_yticks([-600, -400, -200, 0, 200, 400, 600])
        a1.annotate("X", xy=(0.5, -0.4), xycoords= 'axes fraction', ha= 'center', va= 'center')

        # Heart rate
        hr = 150 + 50 * np.sin(0.5 * np.pi * x_vals)
        a2.plot(x_vals, hr, label= "Heart Rate")
        a2.set_title("Heart Rate")
        a2.set_yticks([50, 100, 150, 200])
        a2.annotate("X", xy=(0.5, -0.4), xycoords= 'axes fraction', ha= 'center', va= 'center')

        self.c = FigureCanvasTkAgg(fig, master=self.lsideF)
        self.c.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def makecontrols(self):
        r = 0
        # Control section
        control_sects = [
            ("Heartbeats", ["Add Heartbeat", "Remove Heartbeat"]),
            ("Data Removal", ["Toggle Removal Mode", "Draw Removal Interval"])
        ]

        for sects_title, btttnList in control_sects:
            sectFrame = ttk.LabelFrame(self.rsideF, text=sects_title)
            sectFrame.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
            r += 1
            for button in btttnList:
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





        info = ttk.LabelFrame(self.rsideF, text="Session Info")
        info.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1

        # will make this dynamic later (when incorporating functionality)
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
        self.tab.pack(side="top", fill="x")



if __name__ == "__main__":
    root = tk.Tk()
    app = ecg_applicaion(root)
    root.mainloop()
