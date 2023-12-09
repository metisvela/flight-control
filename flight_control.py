import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from os.path import basename
import numpy as np
import json
import pandas as pd
from config import *

class FlightControl:
    def __init__(self, root):

        self.root = root
        self.root.title("Flight Control Application")
        self.root.geometry(WINDOW_SIZE)

        self.label_coordinates = tk.Label(self.root, text="Click inside the frame.")
        self.label_coordinates.pack(pady=0)

        # Label to display real-time mouse coordinates
        self.label_real_time_coordinates = tk.Label(self.root, text="Mouse Coordinates: (0, 0)")
        self.label_real_time_coordinates.pack(pady=0)

        # Entry widget for the textbox
        self.textbox_entry = tk.Text(root, height=1, width=40, wrap='word', fg='grey')
        self.textbox_entry.insert("1.0", 'Function name')
        self.textbox_entry.bind('<FocusIn>', self.on_text_click)
        self.textbox_entry.pack(pady=10)


        self.canvas = tk.Canvas(self.root, width=CANVA_WIDTH, height=CANVA_HEIGHT, bg=CANVA_BG)
        self.canvas.pack()

        self.points = []  # To store the clicked points
        self.drawn_points = []  # To store references to the drawn points on the canvas

        # Bind left-click event to the canvas
        self.canvas.bind("<Button-1>", self.track_mouse)

        # Flag to indicate if a point is being dragged
        self.dragging = False
        self.currently_dragged_point = None

        # Bind left-button drag event to the canvas
        self.canvas.bind("<B1-Motion>", self.drag_point)

        # Bind mouse motion to update real-time coordinates
        self.canvas.bind("<Motion>", self.update_real_time_coordinates)

        # Bind the canvas resizing event
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        

        # Button to delete the last drawn point
        self.delete_button = tk.Button(self.root, text="Delete Last Point", command=self.delete_last_point)
        self.delete_button.pack(side="left", padx=5, pady=10)

        # Reset button to clear all points and drawn curve
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_canvas)
        self.reset_button.pack(side="right", padx=5, pady=10)

        # Show/Hide Table button
        self.table_button = tk.Button(self.root, text="Show Table", command=self.show_hide_table)
        self.table_button.pack(side="right", padx=5, pady=10)

        # Print json button
        self.print_json = tk.Button(self.root, text="Print_json", command=self.create_json_package)
        self.print_json.pack(side="right", padx=15, pady=10)

        # Save function button
        self.save_function = tk.Button(self.root, text="Save Function", command=self.save_function)
        self.save_function.pack(side="left", padx=5, pady=10)

        # Load function button
        self.load_function = tk.Button(self.root, text="Load Function", command=self.load_function)
        self.load_function.pack(side="left", padx=5, pady=10)

        # Create a new window for the table
        self.table_window = tk.Toplevel(self.root)
        self.table_window.title("Drawn points")
        self.table_window.withdraw()

        # Create a Treeview widget for the table
        self.table = ttk.Treeview(self.table_window, columns=("x", "y"), show="headings")
        self.table.heading("x", text="X Values")
        self.table.heading("y", text="Y Values")
        self.table.pack()

        # Bind the double-click event to edit the cell
        # self.table.bind("<Double-1>", self.edit_cell)

        # Schedule the draw_grid method after the main loop starts
        self.root.after(1, self.draw_grid)

        # Initialize the array for data to store in json package
        self.jsondata = [[],[]]


    def on_canvas_resize(self, event):
        # Redraw the grid on canvas resize
        self.draw_grid()

    def draw_grid(self):
        # Clear previous grid
        self.canvas.delete("grid")

        # Get the canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Space between grid lines
        space = GRID_SPACE

        # Draw grid
        for x in range(space, canvas_width - space, 20):
            self.canvas.create_line(x, 0, x, canvas_height, fill=GRID_COLOR, width=1, tags="grid")

        for y in range(space, canvas_height - space, 20):
            self.canvas.create_line(0, y, canvas_width, y, fill=GRID_COLOR, width=1, tags="grid")

    def track_mouse(self, event):
        x, y = event.x, event.y

        # Check if any point is close enough to being clicked
        clicked_point = self.find_closest_point(x, y)

        if clicked_point is not None:
            self.dragging = True
            self.currently_dragged_point = clicked_point
        else:
            # Draw a red point at the clicked coordinates
            point_id = self.canvas.create_oval(x-POINT_RADIUS, y-POINT_RADIUS, x+POINT_RADIUS, y+POINT_RADIUS, fill=POINT_COLOR, outline=POINT_COLOR)

            # Add the point to the lists
            self.points.append((x, y))
            self.drawn_points.append(point_id)

            # Display the coordinates
            coordinates_text = f"Mouse Clicked at ({x}, {y})"
            self.label_coordinates.config(text=coordinates_text)

            # Update the polynomial curve
            self.update_polynomial_curve()

            # Update the table
            self.update_table()
        
    def find_closest_point(self, x, y):
        # Check if the mouse is close to any existing point
        for point_id in self.drawn_points:
            x_point, y_point, _, _ = self.canvas.coords(point_id)
            distance = np.sqrt((x - x_point)**2 + (y - y_point)**2)
            if distance < PICKABLE_RADIUS:
                return point_id
        return None

    def drag_point(self, event):
        if self.dragging and self.currently_dragged_point is not None:
            # Update the coordinates of the dragged point
            x, y = event.x, event.y
            self.canvas.coords(self.currently_dragged_point, x-POINT_RADIUS, y-POINT_RADIUS, x+POINT_RADIUS, y+POINT_RADIUS)

            # Update the coordinates in the points list
            index = self.drawn_points.index(self.currently_dragged_point)
            self.points[index] = (x, y)

            # Update the polynomial curve
            self.update_polynomial_curve()

            # Update the table
            self.update_table()

    def delete_last_point(self):
        # Delete the last drawn point
        if self.points:
            last_point = self.points.pop()
            last_drawn_point = self.drawn_points.pop()

            # Remove the last drawn point from the canvas
            self.canvas.delete(last_drawn_point)

        # Update the polynomial curve
        self.update_polynomial_curve()

        # Update the table
        self.update_table()

    def reset_canvas(self):
        # Clear all points, drawn curve, and reset canvas state
        self.canvas.delete("all")
        self.points = []
        self.drawn_points = []

        # Redraw grid
        self.draw_grid()

        # Update the polynomial curve (will be empty after reset)
        self.update_polynomial_curve()

        # Update the table
        self.update_table()

    def update_polynomial_curve(self):
        # Clear previous curve
        self.canvas.delete("curve")

        if len(self.points) >= 2:
            # Fit a polynomial curve with interpolation
            x_values, y_values = zip(*self.points)
            coefficients = np.polyfit(x_values, y_values, len(self.points) - 1, full=True)[0]
            poly = np.poly1d(coefficients)

            # Draw the polynomial curve in yellow
            x_min, x_max = min(x_values), max(x_values)
            x_curve = np.linspace(x_min, x_max, STEPS)
            self.jsondata[0] = x_curve 
            y_curve = poly(x_curve)
            self.jsondata[1] = y_curve
            curve_points = [(int(x), int(y)) for x, y in zip(x_curve, y_curve)]
            self.canvas.create_line(curve_points, tags="curve", fill=LINE_COLOR)

    def show_hide_table(self):
        if not self.table_window.winfo_ismapped():
            self.table_window.deiconify()
            self.table_button.config(text="Hide Table")
        else:
            self.table_window.withdraw()
            self.table_button.config(text="Show Table")
        
        # Update the table
        self.update_table()

    def update_table(self):
        # Clear previous table
        self.table.delete(*self.table.get_children())

        # Insert data into the table with values rounded to 3 decimal digits
        for x in self.drawn_points:
            x_cord, y_cord, _, _ = self.canvas.coords(x)
            self.table.insert("", "end", values=(x_cord + POINT_RADIUS, y_cord + POINT_RADIUS))

    """
    def edit_cell(self, event):
        self.entry = tk.Entry(self.root, width = 30)
        self.entry.bind("<Return>", self.update_cell)

    def update_cell(self):
        new_value = self.entry.get()
    """
    
    def update_real_time_coordinates(self, event):
        x, y = event.x, event.y
        coordinates_text = f"Mouse Coordinates: ({x}, {y})"
        self.label_real_time_coordinates.config(text=coordinates_text)

    def create_json_package(self):
        self.update_table
        data = {
            "x_values": self.jsondata[0].tolist(),
            "y_values": self.jsondata[1].tolist()
        }
        json_string = json.dumps(data, indent=2)
        print(json_string)

    def save_function(self):
        input = self.textbox_entry.get("1.0", "end-1c")
        if input == 'Function name' or input == '':
            messagebox.showwarning("Attention!", "Insert a name for the function")
        else:
            x,y = zip(*self.points)
            data = {'x': x, 'y': y}
            df = pd.DataFrame(data)
            df.to_csv(f'./saved_functions/{input}.csv', index=False)
            messagebox.showinfo("", "Function saved correctly")
        

    def on_text_click(self, event):
        if self.textbox_entry.get("1.0", "end-1c") == 'Function name':
            self.textbox_entry.delete("1.0", 'end')
            self.textbox_entry.config(fg='black')  # Change text color to black

    """
    def on_focus_out(self, event):
        if not self.textbox_entry.get("1.0", "end-1c"):
            self.textbox_entry.insert("1.0", 'Function name')
            self.textbox_entry.config(fg='grey')  # Change text color to grey
    """

    def load_function(self):
        file_path = filedialog.askopenfilename(initialdir="./saved_functions/", filetypes=[("CSV files", "*.csv")])    

        if file_path:
            file_name = basename(file_path)
            self.textbox_entry.delete("1.0", 'end')
            self.textbox_entry.config(fg='black')
            self.textbox_entry.insert("1.0", file_name)
            self.textbox_entry.delete("end-5c", "end")
            data = pd.read_csv(file_path)
            x_values = data["x"]
            y_values = data["y"]

            self.reset_canvas()

            for i in range(len(x_values)): 
                point_id = self.canvas.create_oval(x_values[i]-POINT_RADIUS, y_values[i]-POINT_RADIUS, x_values[i]+POINT_RADIUS, y_values[i]+POINT_RADIUS, fill=POINT_COLOR, outline=POINT_COLOR)
                self.points.append((x_values[i], y_values[i]))
                self.drawn_points.append(point_id)

            self.update_polynomial_curve()
            self.update_table()


