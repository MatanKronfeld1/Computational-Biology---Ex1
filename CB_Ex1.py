import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
# from PIL import ImageGrab

class CellularAutomaton:
    def __init__(self, n, wraparound=True, live_possibility=0.5):
        if n % 2 != 0:
            raise ValueError("Grid size n must be even")
        
        self.n = n
        self.wraparound = wraparound
        self.live_possibility = live_possibility
        self.dead_possibility = 1 - live_possibility
        self.grid = np.random.choice([0, 1], size=(n, n), p=[self.dead_possibility, self.live_possibility])
        self.generation = 0
    
    # Process a 2×2 block according to the rules
    def process_block(self, block):
        living_amount = np.sum(block)
        new_block = block.copy()
        
        if living_amount == 2:
            pass
        elif living_amount in [0, 1, 4]:
            new_block = 1 - new_block
        elif living_amount == 3:
            new_block = 1 - new_block
            new_block = np.rot90(new_block, 2)
            
        return new_block
    
    # Iterate through the grid and apply the ruels to the individual blocks
    def next_generation(self, update_gui_callback=None):
        """Compute the next generation"""
        self.generation += 1
        new_grid = self.grid.copy()
        block_percentages = []

        if self.generation % 2 == 1:  # Odd generation
            for i in range(0, self.n, 2):
                for j in range(0, self.n, 2):
                    if i+2 <= self.n and j+2 <= self.n:
                        block = self.grid[i:i+2, j:j+2]
                        new_block = self.process_block(block)
                        new_grid[i:i+2, j:j+2] = new_block
                        block_percentages.append(np.sum(block) / 4 * 100)
        else:  # Even generation
            if not self.wraparound: # Without wraparound
                for i in range(1, self.n-1, 2):
                    for j in range(1, self.n-1, 2):
                        if i+2 <= self.n and j+2 <= self.n:
                            block = self.grid[i:i+2, j:j+2]
                            new_block = self.process_block(block)
                            new_grid[i:i+2, j:j+2] = new_block
                            block_percentages.append(np.sum(block) / 4 * 100)
            else:  # With wraparound
                for i in range(1, self.n, 2):
                    for j in range(1, self.n, 2):
                        if i < self.n-1 and j < self.n-1:
                            block = self.grid[i:i+2, j:j+2]
                        elif i == self.n-1 and j == self.n-1:
                            block = np.array([
                                [self.grid[i, j], self.grid[i, 0]],
                                [self.grid[0, j], self.grid[0, 0]]
                            ])
                        elif j == self.n-1:
                            block = np.array([
                                [self.grid[i, j], self.grid[i, 0]],
                                [self.grid[i+1, j], self.grid[i+1, 0]]
                            ])
                        elif i == self.n-1:
                            block = np.array([
                                [self.grid[i, j], self.grid[i, j+1]],
                                [self.grid[0, j], self.grid[0, j+1]]
                            ])
                        
                        new_block = self.process_block(block)
                        
                        if i < self.n-1 and j < self.n-1:
                            new_grid[i:i+2, j:j+2] = new_block
                        elif i == self.n-1 and j == self.n-1:
                            new_grid[i, j] = new_block[0, 0]
                            new_grid[i, 0] = new_block[0, 1]
                            new_grid[0, j] = new_block[1, 0]
                            new_grid[0, 0] = new_block[1, 1]
                        elif j == self.n-1:
                            new_grid[i, j] = new_block[0, 0]
                            new_grid[i, 0] = new_block[0, 1]
                            new_grid[i+1, j] = new_block[1, 0]
                            new_grid[i+1, 0] = new_block[1, 1]
                        elif i == self.n-1:
                            new_grid[i, j] = new_block[0, 0]
                            new_grid[i, j+1] = new_block[0, 1]
                            new_grid[0, j] = new_block[1, 0]
                            new_grid[0, j+1] = new_block[1, 1]
                        block_percentages.append(np.sum(block) / 4 * 100)

        # Calculate the percentage of cells that stayed the same
        unchanged_cells = np.sum(self.grid == new_grid)
        total_cells = self.n * self.n
        percentage_unchanged = (unchanged_cells / total_cells) * 100

        # Calculate the percentage of living cells
        living_cells = np.sum(new_grid)
        percentage_living = (living_cells / total_cells) * 100

        # Calculate the standard deviation of the iterated blocks
        std_dev_blocks = np.std(block_percentages) if block_percentages else 0

        # Update the GUI statistics
        if update_gui_callback:
            update_gui_callback(percentage_unchanged, percentage_living, std_dev_blocks)

        # Update the grid
        self.grid = new_grid
        return self.grid

    def set_grid(self, grid_type):
        
        if grid_type == 'random':
            self.grid = np.random.choice([0, 1], size=(self.n, self.n), 
                                        p=[self.dead_possibility, self.live_possibility])

    def set_pattern(self, pattern_type=''):
        
        # Start with all zeros
        self.grid = np.zeros((self.n, self.n), dtype=int)
        
        if pattern_type == 'Hollow Square':

            # Background
            self.grid = np.ones((self.n, self.n), dtype=int)

            # white shape of square
            start_row = self.n // 4
            start_col = self.n // 4
            end_row = start_row + self.n // 2
            end_col = start_col + self.n // 2
            self.grid[start_row:end_row, start_col] = 0
            self.grid[start_row:end_row, end_col-1] = 0
            self.grid[start_row, start_col:end_col] = 0
            self.grid[end_row-1, start_col:end_col] = 0
        

            
        elif pattern_type == 'Repeating Lines':

            # Create a lines pattern
            block_size = self.n // 10 
            for i in range(0, self.n, block_size*2):
                for j in range(0, self.n, block_size*2):
                    if i+block_size <= self.n and j+block_size <= self.n:
                        self.grid[i:i+block_size, j:j+block_size] = 1
                    if i+block_size <= self.n and j+block_size*2 <= self.n:
                        self.grid[i:i+block_size, j+block_size:j+block_size*2] = 1
        
        elif pattern_type == 'White Square':

            # Background
            self.grid = np.ones((self.n, self.n), dtype=int)
            center = self.n // 2
            size = self.n // 10  # Size of the square
            start_row = center - size // 2
            start_col = center - size // 2
            end_row = center + size // 2
            end_col = center + size // 2
            self.grid[start_row:end_row, start_col:end_col] = 0

        
        elif pattern_type == 'Mosaic':

            # Background
            self.grid = np.zeros((self.n, self.n), dtype=int)

            ankle = np.array([
                [1, 1],
                [1, 0]
            ])

            for i in range(0, self.n, 2):
                for j in range(0, self.n, 2):
                    if i+ankle.shape[0] <= self.n and j+ankle.shape[1] <= self.n:
                        self.grid[i:i+2, j:j+2] = ankle
        
        elif pattern_type == 'Glider':
            # Background
            self.grid = np.zeros((self.n, self.n), dtype=int)

            # Glider
            glider = np.array([
            [1,0],
            [0,1],
            [0,1],
            [1,0]
            ])

            start_row, start_col = self.n // 2 +1, self.n // 4
            self.grid[start_row:start_row+glider.shape[0], start_col:start_col+glider.shape[1]] = glider
        

        elif pattern_type == 'Black Square':
            
            # Background
            self.grid = np.zeros((self.n, self.n), dtype=int)

            # White Square
            center = self.n // 2
            size = self.n // 10
            start_row = center - size // 2
            start_col = center - size // 2
            end_row = center + size // 2
            end_col = center + size // 2
            self.grid[start_row:end_row, start_col:end_col] = 1

        self.generation = 0

class AutomatonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cellular Automaton Simulation")
        self.root.geometry("1024x900")  # Increase the height to ensure all elements fit
        self.root.config(padx=10, pady=10)

        # Style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11, 'bold'))
        self.style.configure('TEntry', font=('Arial', 11))
        
        # Create main container
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar and simulation area
        self.sidebar = ttk.Frame(self.container, padding=(10, 10))
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        
        self.simulation_frame = ttk.Frame(self.container)
        self.simulation_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.root.update()
        sidebar_width = int(self.root.winfo_width() * 0.25)
        self.sidebar.config(width=sidebar_width)

        self.setup_sidebar()
        self.setup_simulation_area()

        # self.root.after(1000, self.capture_screenshot)

        self.ca = None
        self.anim = None
        self.simulation_running = False
        self.simulation_paused = False
        self.simulation_completed = False
        self.current_frame = 0
        
        # Speed
        self.speed_values = {"Fast": 50, "Medium": 200, "Slow": 500}
        self.current_speed = self.speed_values["Medium"]

    # Sidebar properties
    def setup_sidebar(self):
        ttk.Label(self.sidebar, text="Automaton Settings", font=('Arial', 14, 'bold')).pack(pady=(0, 15), fill=tk.X)
        
        self.params_frame = ttk.Frame(self.sidebar)
        self.params_frame.pack(fill=tk.X, pady=5)
        
        # Generations
        ttk.Label(self.params_frame, text="Generations:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.gen_var = tk.StringVar(value="250")
        self.gen_entry = ttk.Entry(self.params_frame, textvariable=self.gen_var, width=8)
        self.gen_entry.grid(row=0, column=1, sticky=tk.W, pady=8, padx=5)
        
        # Probability
        ttk.Label(self.params_frame, text="Live Probability:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.prob_var = tk.StringVar(value="0.5")
        self.prob_entry = ttk.Entry(self.params_frame, textvariable=self.prob_var, width=8)
        self.prob_entry.grid(row=1, column=1, sticky=tk.W, pady=8, padx=5)
        ttk.Label(self.params_frame, text="(0.0 to 1.0)").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        # Wraparound
        wraparound_frame = ttk.Frame(self.params_frame)
        wraparound_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=8)
        ttk.Label(wraparound_frame, text="Wraparound:").pack(side=tk.LEFT)
        self.wraparound_var = tk.BooleanVar(value=True)
        self.wraparound_check = ttk.Checkbutton(wraparound_frame, variable=self.wraparound_var)
        self.wraparound_check.pack(side=tk.LEFT, padx=5)
        
        # Pattern Selection
        ttk.Label(self.params_frame, text="Initial Pattern:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.pattern_var = tk.StringVar(value="Random")
        self.pattern_combo = ttk.Combobox(self.params_frame, textvariable=self.pattern_var, width=12,
                                          values=["Random", "Glider", "Mosaic", "Repeating Lines", "Black Square", "White Square", "Hollow Square"])
        self.pattern_combo.grid(row=4, column=1, sticky=tk.W, pady=8, padx=5)
        
        # Animation Speed
        ttk.Label(self.params_frame, text="Speed:").grid(row=5, column=0, sticky=tk.W, pady=8)
        self.speed_var = tk.StringVar(value="Medium")
        self.speed_combo = ttk.Combobox(self.params_frame, textvariable=self.speed_var, width=12,
                                        values=["Fast", "Medium", "Slow"])
        self.speed_combo.grid(row=5, column=1, sticky=tk.W, pady=8, padx=5)
        self.speed_combo.bind("<<ComboboxSelected>>", self.update_speed)
        
        # Separator
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Control buttons frame
        self.buttons_frame = ttk.Frame(self.sidebar)
        self.buttons_frame.pack(fill=tk.X, pady=5)

        # Run One Generation button
        self.run_one_button = ttk.Button(self.buttons_frame, text="Run One Generation", 
                                        command=self.run_one_generation)
        self.run_one_button.pack(fill=tk.X, pady=5)
        
        # Start button
        self.start_button = ttk.Button(self.buttons_frame, text="Start Simulation", 
                                    command=self.start_simulation)
        self.start_button.pack(fill=tk.X, pady=5)
        
        # Stop button
        self.stop_button = ttk.Button(self.buttons_frame, text="Stop Simulation", 
                                   command=self.stop_simulation)
        self.stop_button.pack(fill=tk.X, pady=5)
        self.stop_button.config(state='disabled')
        
        # Resume button
        self.resume_button = ttk.Button(self.buttons_frame, text="Resume Simulation", 
                                   command=self.resume_simulation)
        self.resume_button.pack(fill=tk.X, pady=5)
        self.resume_button.config(state='disabled')
        
        # Reset All button
        self.reset_button = ttk.Button(self.buttons_frame, text="Reset All", 
                                    command=self.reset_simulation)
        self.reset_button.pack(fill=tk.X, pady=5)
        
        # Messages
        self.message_var = tk.StringVar(value="Ready to start simulation")
        self.message_label = ttk.Label(self.sidebar, textvariable=self.message_var, 
                                    font=('Arial', 9), foreground='#555555', wraplength=200)
        self.message_label.pack(pady=10, fill=tk.X)
        self.unchanged_var = tk.StringVar(value="Unchanged: 0.00%")
        self.living_cells_var = tk.StringVar(value="Living Cells: 0.00%")
        self.std_dev_var = tk.StringVar(value="Std Dev (Blocks): 0.00")
        ttk.Label(self.sidebar, textvariable=self.unchanged_var).pack(pady=5, fill=tk.X)
        ttk.Label(self.sidebar, textvariable=self.living_cells_var).pack(pady=5, fill=tk.X)
        ttk.Label(self.sidebar, textvariable=self.std_dev_var).pack(pady=5, fill=tk.X)

    def setup_simulation_area(self):
        self.plot_frame = ttk.Frame(self.simulation_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig = plt.Figure(figsize=(7, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def validate_inputs(self):
        """Validate all user inputs"""
        # Validate generations
        try:
            generations = int(self.gen_var.get())
            if generations < 1:
                messagebox.showerror("Input Error", "Generations must be a positive integer")
                return False
        except ValueError:
            messagebox.showerror("Input Error", "Generations must be a valid integer")
            return False

        # Validate probability
        try:
            prob = float(self.prob_var.get())
            if prob < 0.0 or prob > 1.0:
                messagebox.showerror("Input Error", "Probability must be between 0.0 and 1.0")
                return False
        except ValueError:
            messagebox.showerror("Input Error", "Probability must be a valid number")
            return False

        return True
    
    def update_speed(self, event=None):
        """Update animation speed based on user selection"""
        speed_setting = self.speed_var.get()
        self.current_speed = self.speed_values.get(speed_setting, 200)  # Default to Medium if not found
        
        # If animation is running, update its interval
        if self.anim and self.simulation_running:
            self.anim.event_source.interval = self.current_speed
            self.message_var.set(f"Speed updated to {speed_setting}")

    def reset_simulation(self):
        """Reset the simulation and all parameters to defaults"""

        # Stop any running animation if it exists
        if self.anim is not None:
            if self.anim.event_source:
                self.anim.event_source.stop()
            self.anim = None  # Clean up the animation object

        # Reset state flags
        self.simulation_running = False
        self.simulation_paused = False
        self.simulation_completed = False
        self.current_frame = 0

        # Clear the figure
        self.fig.clear()
        self.canvas.draw()

        # Reset Cellular Automaton
        self.ca = None

        # Update button states
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.resume_button.config(state='disabled')
        self.run_one_button.config(state='normal')  # Disable "Run One Generation"

        # Reset message
        self.message_var.set("Reset complete. Ready for new simulation.")

        # Force UI update
        self.root.update()


    def start_simulation(self):
        if self.simulation_running:
            self.message_var.set("Simulation already running. Please stop it first.")
            return

        if not self.validate_inputs():
            return

        grid_size = 100  # Fixed grid size
        generations = int(self.gen_var.get())
        live_prob = float(self.prob_var.get())
        wraparound = self.wraparound_var.get()
        pattern = self.pattern_var.get()

        speed_setting = self.speed_var.get()
        self.current_speed = self.speed_values.get(speed_setting, 200)

        self.message_var.set(f"Running: {grid_size}x{grid_size} grid, {generations} gens, prob={live_prob:.2f}, pattern={pattern}, speed={speed_setting}")

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.resume_button.config(state='disabled')
        self.run_one_button.config(state='disabled')

        self.simulation_completed = False
        self.simulation_paused = False
        self.current_frame = 0

        threading.Thread(target=self.run_simulation, args=(grid_size, generations, live_prob, wraparound, pattern)).start()

    def stop_simulation(self):
        if self.simulation_running and self.anim:
            self.anim.event_source.stop()
            self.simulation_running = False
            self.simulation_paused = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='disabled')
            self.resume_button.config(state='normal')
            self.run_one_button.config(state='normal')
            self.message_var.set("Simulation paused. Click 'Resume Simulation' to continue.")

    def resume_simulation(self):
        if self.simulation_paused and self.ca:
            self.simulation_running = True
            self.simulation_paused = False

            # Update button states
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.resume_button.config(state='disabled')
            self.run_one_button.config(state='disabled')  # Disable "Run One Generation"

            self.message_var.set("Resuming simulation...")

            # Get remaining generations
            total_generations = int(self.gen_var.get())
            remaining_generations = total_generations - self.current_frame

            # Start simulation in a separate thread
            threading.Thread(target=self.resume_animation, args=(remaining_generations,)).start()

    def resume_animation(self, remaining_generations):
        """Resume animation with remaining generations"""
        if not self.ca:
            self.message_var.set("Cannot resume. No simulation data available.")
            return

        # Clear the figure
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Plot current state
        img = ax.imshow(self.ca.grid, cmap='gray_r', interpolation='nearest', vmin=0, vmax=1)
        ax.set_title(f'Cellular Automaton - Generation {self.ca.generation}')
        ax.grid(False)
        ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

        # Track if it's the first frame after resuming
        is_first_frame_after_resume = True

        def update(frame):
            nonlocal is_first_frame_after_resume

            if not self.simulation_running:
                return [img]

            # Skip advancing the generation on the first frame after resuming
            if is_first_frame_after_resume:
                is_first_frame_after_resume = False
            else:
                self.ca.next_generation()

            self.current_frame += 1
            img.set_array(self.ca.grid)
            ax.set_title(f'Cellular Automaton - Generation {self.ca.generation}')
            return [img]

        def on_animation_complete(*args):
            if self.simulation_running:
                self.simulation_running = False
                self.simulation_completed = True
                self.simulation_paused = False

                self.anim = None

                self.root.after(0, lambda: self.start_button.config(state='normal'))
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))
                self.root.after(0, lambda: self.resume_button.config(state='disabled'))
                self.root.after(0, lambda: self.message_var.set(
                    f"Simulation complete: {self.ca.generation} generations. Click 'Reset All' to start a new simulation."
                ))

        self.anim = FuncAnimation(
            self.fig,
            update,
            frames=remaining_generations,
            interval=self.current_speed,
            blit=False,
            repeat=False
        )

        self.anim._stop = on_animation_complete

        self.canvas.draw()

    def run_one_generation(self):
        if not self.ca:
            if not self.validate_inputs():
                return

            grid_size = 100
            live_prob = float(self.prob_var.get())
            wraparound = self.wraparound_var.get()
            pattern = self.pattern_var.get()

            self.ca = CellularAutomaton(grid_size, wraparound, live_prob)

            if pattern == "random":
                self.ca.set_grid('random')
            else:
                self.ca.set_pattern(pattern)

            self.ca.generation = 0

            self.fig.clear()
            ax = self.fig.add_subplot(111)
            img = ax.imshow(self.ca.grid, cmap='gray_r', interpolation='nearest', vmin=0, vmax=1)
            ax.set_title(f'Cellular Automaton - Generation {self.ca.generation}')
            ax.grid(False)
            ax.axis('off')
            self.fig.tight_layout()
            self.canvas.draw()

            self.root.after(500, self.run_next_generation)
        else:
            self.run_next_generation()

    def run_next_generation(self):
        """Run the next generation after showing the initial state"""
        # Run the next generation
        self.ca.next_generation(update_gui_callback=lambda percentage_unchanged, percentage_living, std_dev_blocks: (
            self.unchanged_var.set(f"Unchanged: {percentage_unchanged:.2f}%"),
            self.living_cells_var.set(f"Living Cells: {percentage_living:.2f}%"),
            self.std_dev_var.set(f"Standard Deviation: {std_dev_blocks:.2f}")
        ))

        # Update the grid display
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        img = ax.imshow(self.ca.grid, cmap='gray_r', interpolation='nearest', vmin=0, vmax=1)
        ax.set_title(f'Cellular Automaton - Generation {self.ca.generation}')
        ax.grid(False)
        ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

        # Update the message
        self.message_var.set(f"Ran one generation. Current generation: {self.ca.generation}")

    def run_simulation(self, grid_size, generations, live_prob, wraparound, pattern):
        self.simulation_running = True

        # Initialize automaton
        self.ca = CellularAutomaton(grid_size, wraparound, live_prob)

        # Set pattern
        if pattern == "Random":
            self.ca.set_grid('Random')
        else:
            self.ca.set_pattern(pattern)

        # Make sure generation is explicitly set to 0
        self.ca.generation = 0

        # Clear previous plot
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Initial plot
        img = ax.imshow(self.ca.grid, cmap='gray_r', interpolation='nearest', vmin=0, vmax=1)
        ax.set_title(f'Cellular Automaton - Generation 0')
        ax.grid(False)
        ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

        # Delay before starting the animation
        self.root.after(500, lambda: self.start_animation(ax, img, generations))

        # Update button states
    def start_animation(self, ax, img, generations):
        """Start the animation after showing the initial state"""

        is_first_frame = True

        def update(frame):
            nonlocal is_first_frame

            if not self.simulation_running:
                return [img]

            if not is_first_frame:
                self.ca.next_generation(update_gui_callback=lambda percentage_unchanged, percentage_living, std_dev_blocks: (
                    self.unchanged_var.set(f"Unchanged: {percentage_unchanged:.2f}%"),
                    self.living_cells_var.set(f"Living Cells: {percentage_living:.2f}%"),
                    self.std_dev_var.set(f"Standard Deviation: {std_dev_blocks:.2f}")
                ))
            else:
                is_first_frame = False

            self.current_frame += 1
            img.set_array(self.ca.grid)
            ax.set_title(f'Cellular Automaton - Generation {self.ca.generation}')
            return [img]

        def on_animation_complete(*args):
            if self.simulation_running:
                self.simulation_running = False
                self.simulation_completed = True
                self.simulation_paused = False

                # Clean up animation resource
                self.anim = None

                # Update UI from the main thread
                self.root.after(0, lambda: self.start_button.config(state='normal'))
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))
                self.root.after(0, lambda: self.resume_button.config(state='disabled'))
                self.root.after(0, lambda: self.message_var.set(
                    f"Simulation complete: {self.ca.generation} generations. Click 'Reset All' to start a new simulation."
                ))

        self.anim = FuncAnimation(
            self.fig,
            update,
            frames=generations,
            interval=self.current_speed,
            blit=False,
            repeat=False
        )

        # Set callback for animation completion
        self.anim._stop = on_animation_complete

        self.canvas.draw()

    # def capture_screenshot(self, filename="screenshot.png"):
    #     self.root.update()

    #     # Get the geometry of the root window
    #     x = self.root.winfo_rootx()
    #     y = self.root.winfo_rooty()
    #     width = x + self.root.winfo_width()
    #     height = y + self.root.winfo_height()

    #     # Add padding to ensure no part of the GUI is cut off
    #     padding = 20
    #     screenshot = ImageGrab.grab(bbox=(x, y, width + padding, height + padding))

    #     # Save the screenshot to a file
    #     screenshot.save(filename)
    #     print(f"Screenshot saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomatonGUI(root)
    root.mainloop()