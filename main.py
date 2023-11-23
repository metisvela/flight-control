import tkinter as tk
import numpy as np

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker")
        self.root.geometry("520x620")

        self.label_coordinates = tk.Label(self.root, text="Click inside the frame.")
        self.label_coordinates.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="black")
        self.canvas.pack()

        self.points = []  # To store the clicked points
        self.drawn_points = []  # To store references to the drawn points on the canvas

        # Bind left-click event to the canvas
        self.canvas.bind("<Button-1>", self.track_mouse)

        # Button to delete the last drawn point
        self.delete_button = tk.Button(self.root, text="Delete Last Point", command=self.delete_last_point)
        self.delete_button.pack(side="left", padx=5, pady=10)

        # Reset button to clear all points and drawn curve
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_canvas)
        self.reset_button.pack(side="right", padx=5, pady=10)

        # Bind the canvas resizing event
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Schedule the draw_axes method after the main loop starts
        self.root.after(10, self.draw_axes)

    def on_canvas_resize(self, event):
        # Redraw the axes and grid on canvas resize
        self.draw_axes()

    def draw_axes(self):
        # Clear previous axes and grid
        self.canvas.delete("axes")
        self.canvas.delete("grid")

        # Get the canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Space between axes and canvas edges
        space = 1

        # Draw x-axis
        # self.canvas.create_line(space, canvas_height - space, canvas_width - space, canvas_height - space, fill="grey", width=1, tags="axes")

        # Draw y-axis
        # self.canvas.create_line(space, canvas_height - space, space, space, fill="grey", width=1, tags="axes")

        # Draw grey-colored grid
        for x in range(space, canvas_width - space, 20):
            self.canvas.create_line(x, space, x, canvas_height - space, fill="grey", width=1, tags="grid")

        for y in range(space, canvas_height - space, 20):
            self.canvas.create_line(space, y, canvas_width - space, y, fill="grey", width=1, tags="grid")

    def track_mouse(self, event):
        x, y = event.x, event.y

        # Draw a red point at the clicked coordinates
        point_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red", outline="red")

        # Add the point to the lists
        self.points.append((x, y))
        self.drawn_points.append(point_id)

        # Display the coordinates
        coordinates_text = f"Mouse Clicked at ({x}, {y})"
        self.label_coordinates.config(text=coordinates_text)

        # Update the polynomial curve
        self.update_polynomial_curve()

    def delete_last_point(self):
        # Delete the last drawn point
        if self.points:
            last_point = self.points.pop()
            last_drawn_point = self.drawn_points.pop()

            # Remove the last drawn point from the canvas
            self.canvas.delete(last_drawn_point)

        # Update the polynomial curve
        self.update_polynomial_curve()

    def reset_canvas(self):
        # Clear all points, drawn curve, and reset canvas state
        self.canvas.delete("all")
        self.points = []
        self.drawn_points = []

        # Redraw axes and grid
        self.draw_axes()

        # Update the polynomial curve (will be empty after reset)
        self.update_polynomial_curve()

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
            x_curve = np.linspace(x_min, x_max, 100)
            y_curve = poly(x_curve)
            curve_points = [(int(x), int(y)) for x, y in zip(x_curve, y_curve)]
            self.canvas.create_line(curve_points, tags="curve", fill="yellow")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()
