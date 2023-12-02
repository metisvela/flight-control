import tkinter as tk
from flight_control import FlightControl

 
if __name__ == "__main__":

    root = tk.Tk()
    app = FlightControl(root)
    root.mainloop()
    