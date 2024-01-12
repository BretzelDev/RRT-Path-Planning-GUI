import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from display import Display
from RRTstar import *
from time import time



class Gui:
    def __init__(self, root, title="Path Planner Interface", path_planner=None):
        ## Window settings
        self.canvas_width = 1200
        self.canvas_height = 800
        self.root = root
        self.root.title(title)

        # Cursor properties
        self.circle_radius = 20
        self.circle_id = None

        # Path planning properties
        self.tree_node_number = 1000
        self.tree_number_string = StringVar(value = f"Nb of nodes in tree : {self.tree_node_number}")


        ## Path planner object
        self.path_planner = path_planner
        self.walls = np.zeros((self.canvas_height, self.canvas_width), dtype=bool) ##En attendant le path planner
        self.robot = None
        self.goal = None
        self.tree = None
        self.path = None

        ## Display object
        self.display = Display(height=self.canvas_height, width=self.canvas_width)
        self.tree_display_var = BooleanVar(value="True")

        ## Top menu
        self.top_menu = Menu(root)
        root.config(menu = self.top_menu)
        self.top_menu.add_command(label = "Save", command= self.save) 
        self.top_menu.add_command(label = "Simulate", command= self.simulate_progress) 
        self.top_menu.add_command(label = "Exit", command= root.destroy)

        ## Side panel
        self.side_panel = tk.Frame(root)
        self.place_robot_var = tk.StringVar(value="wall")
        self.setup_side_panel()
        self.side_panel.grid(row=0, column=0, rowspan=2, sticky="n")

        ## Window header
        header = Frame(root)
        header.grid(row=0, column=1)
        self.log = tk.StringVar()
        logger = Label(header, textvariable=self.log)
        logger.pack(side="top", pady=2)
        self.progress_bar = ttk.Progressbar(header, orient="horizontal", length=900)
        self.progress_bar.pack(padx=10, pady=2, fill="x", expand=True, side="top")

        ## Main canva
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(column=1, row=1)
        # Initialize an empty image_data
        self.image_data = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.photo_image = self.create_photo_image()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image, tags="image_item")

        ## Commandes clavier / souris
        self.setup_commands()

    def draw_canvas(self, new_tree=False, new_path=False):
        self.image_data = self.display(self.walls, self.robot, self.goal, self.tree if self.tree_display_var.get() else None, new_tree=new_tree, path=self.path, new_path=new_path)

    def setup_commands(self):
        self.canvas.bind("<Button-1>", self.click_on_canvas) #<B1-Motion>
        self.canvas.bind("<B1-Motion>", self.click_on_canvas) #<B1-Motion>
        self.canvas.bind("<Motion>", self.on_enter_canvas) ## Cursor
        self.canvas.bind("<Leave>", self.on_leave_canvas)


    def create_photo_image(self):
        return ImageTk.PhotoImage(image=Image.fromarray(self.image_data))

    def update_canvas_image(self):
        self.photo_image = self.create_photo_image()
        self.canvas.itemconfig("image_item", image=self.photo_image)
        

    def setup_side_panel(self):
        compute_button = ttk.Button(self.side_panel, text="Compute path", command=self.compute_path, style='Accent.TButton')
        reset_button = Button(self.side_panel, text="Reset", command=self.reset)

        vlist = ["black", "white", "red", "green",
          "orange", "yellow"]
 
        wall_color_label = Label(self.side_panel, text="Wall color")
        wall_color_selector = ttk.Combobox(self.side_panel, values = vlist)
        wall_color_selector.set("black")

        background_color_label = Label(self.side_panel, text="Background color")
        background_color_selector = ttk.Combobox(self.side_panel, values = vlist)
        background_color_selector.set("white")

        robot_color_label = Label(self.side_panel, text="Robot color")
        robot_color_selector = ttk.Combobox(self.side_panel, values = vlist)
        robot_color_selector.set("red")

        goal_color_label = Label(self.side_panel, text="Goal color")
        goal_color_selector = ttk.Combobox(self.side_panel, values = vlist)
        goal_color_selector.set("orange")

        cursor_size_label = Label(self.side_panel, text="Wall size")
        cursor_size_selector = ttk.Scale(self.side_panel, orient="horizontal", from_=0, to=100, command=lambda event: self.change_cursor_size(cursor_size_selector.get()), style='Tick.TScale')
        cursor_size_selector.set(self.circle_radius)

        tree_number_label = Label(self.side_panel, textvariable=self.tree_number_string)
        tree_number_selector = ttk.Scale(self.side_panel, orient="horizontal", from_=10, to=20000, command=lambda event: self.change_tree_number(tree_number_selector.get()), style='Tick.TScale')
        tree_number_selector.set(self.tree_node_number)

        place_wall_button = ttk.Radiobutton(self.side_panel, text="Wall", variable=self.place_robot_var, value="wall", command=None)
        place_robot_button = ttk.Radiobutton(self.side_panel, text="Robot", variable=self.place_robot_var, value="robot", command=None)
        place_goal_button = ttk.Radiobutton(self.side_panel, text="Goal", variable=self.place_robot_var, value="goal", command=None)

        toggle_tree_display = ttk.Checkbutton(self.side_panel, text='Display Tree', style='Toggle.TButton', variable=self.tree_display_var)

        placement_matrix = [[compute_button],
                            [reset_button],
                            [wall_color_selector, wall_color_label],
                            [background_color_selector, background_color_label],
                            [robot_color_selector, robot_color_label],
                            [goal_color_selector, goal_color_label],
                            [cursor_size_label],
                            [cursor_size_selector],
                            [place_wall_button, place_robot_button],
                            [place_goal_button],
                            [tree_number_label],
                            [tree_number_selector],
                            [toggle_tree_display]
                            ]
        
        ## Widgets placement
        self.auto_gridpack(placement_matrix)

        ## Activation functions
        wall_color_selector.bind("<<ComboboxSelected>>", lambda event: self.switch_color("wall", wall_color_selector.get()))
        background_color_selector.bind("<<ComboboxSelected>>", lambda event: self.switch_color("background", background_color_selector.get()))
        robot_color_selector.bind("<<ComboboxSelected>>", lambda event: self.switch_color("robot", robot_color_selector.get()))
        goal_color_selector.bind("<<ComboboxSelected>>", lambda event: self.switch_color("goal", goal_color_selector.get()))




    def click_on_canvas(self, event):
        x, y = event.x, event.y
        selection = self.place_robot_var.get()
        if selection == "wall":
            self.add_obstacle(x, y)
        elif selection == "robot":
            self.add_robot(x, y)
        elif selection == "goal":
            self.add_goal(x, y)
        

            
    def add_obstacle(self, x, y):
        square_size = int(self.circle_radius)
        self.log.set(f"## Add obstacle en {x,y}")
        self.walls[y-square_size//2:y+square_size//2+1, x-square_size//2:x+square_size//2+1] = True
        self.draw_canvas()
        self.update_canvas_image()

    def add_robot(self, x, y):
        self.robot = [x, y]
        self.log.set("Placed robot !")
        self.draw_canvas()
        self.update_canvas_image()

    def add_goal(self, x, y):
        self.goal = [x, y]
        self.log.set("Placed goal !")
        self.draw_canvas()
        self.update_canvas_image()
    

    def switch_color(self, object, color):
        if object == "wall":
            self.display.switch_wall_color(color)
        elif object == "background":
            self.display.switch_background_color(color)
        elif object == "robot":
            self.display.switch_robot_color(color)
        elif object == "goal":
            self.display.switch_goal_color(color)
        self.draw_canvas()
        self.update_canvas_image()

    def compute_path(self):
        print("## Compute path")
        start_time = time()
        # self.tree = generate_random_tree([[0,self.canvas_height],[0, self.canvas_width]], 1000)
        # self.tree = generate_random_tree_array([[0,self.canvas_height],[0, self.canvas_width]], self.tree_node_number)
        rrt = RRTStar(world=self.walls, limits=[[0,self.canvas_height],[0, self.canvas_width]], z_init=self.robot)
        rrt(self.tree_node_number) 
        self.tree = rrt.root
        self.path = unpack_path(self.tree, self.goal)
        self.draw_canvas(new_tree=True, new_path=True)
        self.update_canvas_image()
        timelength = time() - start_time
        print(f"Tree generated in {timelength:.3f}")
        
    def reset(self):
        print("## Reset")
        self.image_data[...,:] = self.display.get_background_color()
        self.walls *= False
        self.robot = None
        self.update_canvas_image()

    def save(self):
        print("## Save")
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                   filetypes=[("PNG files", "*.png"),
                                                              ("JPEG files", "*.jpg;*.jpeg"),
                                                              ("All files", "*.*")])
        if file_path:
            # Convert the numpy array to a PIL Image
            pil_image = Image.fromarray(self.image_data)

            # Save the PIL Image to the specified file path
            pil_image.save(file_path)
            self.log.set(f"Saved image to {file_path}")
            self.log.set("## Saved")
    
    def simulate_progress(self):
        self.log.set("Simulation in progress ...")
        for i in range(101):
            self.progress_bar["value"] = i
            root.update_idletasks()
            root.after(20)  # Simulate a delay
        self.progress_bar["value"] = 0
        self.log.set("Simulation finished !")

    def on_enter_canvas(self, event):
        # Draw a circle centered at the mouse position
        x, y = event.x, event.y
        if self.circle_id:
            # Update the circle's position
            x0, y0 = x - self.circle_radius, y - self.circle_radius
            x1, y1 = x + self.circle_radius, y + self.circle_radius
            self.canvas.coords(self.circle_id, x0, y0, x1, y1)
        else:
            # Create the circle if it doesn't exist
            x0, y0 = x - self.circle_radius, y - self.circle_radius
            x1, y1 = x + self.circle_radius, y + self.circle_radius
            self.circle_id = self.canvas.create_oval(x0, y0, x1, y1, outline="black")

    def on_leave_canvas(self, event):
        # Remove the circle when leaving the canvas
        if self.circle_id:
            self.canvas.delete(self.circle_id)
            self.circle_id = None

    def change_cursor_size(self, size):
        self.circle_radius = size


    def auto_gridpack(self, matrix):
        max_col = max([len(row) for row in matrix])
        for row in range(len(matrix)):
            ncols = len(matrix[row])
            if ncols == 1:
                matrix[row][0].grid(row=row, column=0, columnspan=max_col, sticky="ew")
            else:
                for col in range(len(matrix[row])):
                    widget = matrix[row][col]
                    widget.grid(row=row, column=col, columnspan=1)

    def change_tree_number(self, value):
        self.tree_node_number = int(value)
        self.tree_number_string.set(f"Nb of nodes in tree : {self.tree_node_number}")


    

if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")
    app = Gui(root)
    root.mainloop()