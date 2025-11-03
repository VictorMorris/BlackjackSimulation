"""GUI implementation for the blackjack simulator."""

import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import (
    DEFAULT_NUM_HANDS, 
    DEFAULT_BASE_BET, 
    DEFAULT_MAX_BET,
    DEFAULT_ANIMATION_SPEED,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)
from strategies import (
    FlatBetting, 
    Martingale, 
    Fibonacci, 
    Paroli, 
    Progressive
)
from simulator import BlackjackSimulator


class BlackjackGUI:
    """GUI for the blackjack simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Simulator")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.simulator = None
        self.is_running = False
        self.update_speed = DEFAULT_ANIMATION_SPEED
        
        # easy mapping from dropdown to concrete strategy objects
        self.strategies = {
            "Flat Betting": FlatBetting(),
            "Martingale": Martingale(),
            "Fibonacci": Fibonacci(),
            "Paroli": Paroli(),
            "Progressive": Progressive()
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Creates the user interface."""
        # overall layout uses a left controls panel and right plot area
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls and Stats
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Control Panel
        control_frame = ttk.LabelFrame(left_panel, text="Simulation Controls", padding="15")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input fields with better styling
        ttk.Label(control_frame, text="Number of Hands:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.hands_var = tk.StringVar(value=str(DEFAULT_NUM_HANDS))
        ttk.Entry(control_frame, textvariable=self.hands_var, width=18, font=('Arial', 10)).grid(row=0, column=1, pady=8, padx=5)
        
        ttk.Label(control_frame, text="Base Bet ($):", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.bet_var = tk.StringVar(value=str(DEFAULT_BASE_BET))
        ttk.Entry(control_frame, textvariable=self.bet_var, width=18, font=('Arial', 10)).grid(row=1, column=1, pady=8, padx=5)
        
        ttk.Label(control_frame, text="Max Bet ($):", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.max_bet_var = tk.StringVar(value=str(DEFAULT_MAX_BET))
        ttk.Entry(control_frame, textvariable=self.max_bet_var, width=18, font=('Arial', 10)).grid(row=2, column=1, pady=8, padx=5)
        
        ttk.Label(control_frame, text="Betting Strategy:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.strategy_var = tk.StringVar(value="Flat Betting")
        strategy_menu = ttk.Combobox(control_frame, textvariable=self.strategy_var, 
                                      values=list(self.strategies.keys()), width=16, font=('Arial', 10))
        strategy_menu.grid(row=3, column=1, pady=8, padx=5)
        
        # Animation toggle
        self.animate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Animate (slower)", variable=self.animate_var).grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Label(control_frame, text="Animation Speed (ms):", font=('Arial', 10)).grid(row=5, column=0, sticky=tk.W, pady=8)
        self.speed_var = tk.StringVar(value=str(DEFAULT_ANIMATION_SPEED))
        ttk.Entry(control_frame, textvariable=self.speed_var, width=18, font=('Arial', 10)).grid(row=5, column=1, pady=8, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        self.start_button = ttk.Button(button_frame, text="▶ Run Simulation", command=self.start_simulation, width=20)
        self.start_button.pack(pady=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation, state=tk.DISABLED, width=20)
        self.stop_button.pack(pady=5)
        
        self.reset_button = ttk.Button(button_frame, text="↻ Reset", command=self.reset_simulation, width=20)
        self.reset_button.pack(pady=5)
        
        # Progress bar so we know the instant run actually finished
        progress_frame = ttk.Frame(control_frame)
        progress_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Label(progress_frame, text="Progress:", font=('Arial', 10)).pack()
        self.progress = ttk.Progressbar(progress_frame, length=250, mode='determinate')
        self.progress.pack(pady=5)
        self.progress_label = ttk.Label(progress_frame, text="0%", font=('Arial', 9))
        self.progress_label.pack()
        
        # Statistics Panel
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics Dashboard", padding="15")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # plain text widget is simple but effective for a console style summary
        self.stats_text = tk.Text(stats_frame, height=25, width=42, font=('Consolas', 10),
                                  bg='#f0f0f0', relief=tk.FLAT, padx=10, pady=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # basic color coding so wins and losses pop
        self.stats_text.tag_config('header', font=('Consolas', 11, 'bold'), foreground='#000000')
        self.stats_text.tag_config('subheader', font=('Consolas', 10, 'bold'), foreground='#111111')
        self.stats_text.tag_config('profit', foreground='#1b5e20', font=('Consolas', 10, 'bold'))
        self.stats_text.tag_config('loss', foreground='#b71c1c', font=('Consolas', 10, 'bold'))
        self.stats_text.tag_config('neutral', foreground='#333333')
        self.stats_text.tag_config('value', font=('Consolas', 10, 'bold'), foreground='#000000')

        
        # Graph Panel on the right for the equity curve
        graph_frame = ttk.Frame(main_container)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(11, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_plot()
    
    def start_simulation(self):
        """Starts the simulation."""
        try:
            # pull settings from the UI and validate them
            num_hands = int(self.hands_var.get())
            base_bet = float(self.bet_var.get())
            max_bet = float(self.max_bet_var.get())
            self.update_speed = int(self.speed_var.get())
            
            if num_hands <= 0 or base_bet <= 0 or max_bet <= 0:
                raise ValueError("Values must be positive")
            
            if max_bet < base_bet:
                raise ValueError("Max bet must be >= base bet")
            
            strategy_name = self.strategy_var.get()
            strategy = self.strategies[strategy_name]
            
            # fresh simulator so results do not leak across runs
            self.simulator = BlackjackSimulator(num_hands, base_bet, max_bet, strategy)
            self.is_running = True
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.DISABLED)
            
            # choose fast mode or animated mode
            if not self.animate_var.get():
                self.simulator.run_all_hands()
                self.progress['value'] = 100
                self.progress_label.config(text="100%")
                self.update_plot()
                self.update_stats_display()
                self.simulation_complete()
            else:
                self.run_simulation_step()
            
        except ValueError as e:
            # show the error inside the stats panel so it is visible
            self.update_stats_display(f"Error: {e}")
    
    def run_simulation_step(self):
        """Runs one step of the simulation."""
        if not self.is_running or self.simulator is None:
            return
        
        # batch a few hands per frame so it does not feel sluggish
        hands_per_update = max(1, self.simulator.num_hands // 1000)
        
        for _ in range(hands_per_update):
            if not self.simulator.run_single_hand():
                self.is_running = False
                break
        
        # Update UI after this chunk
        progress = (self.simulator.current_hand / self.simulator.num_hands) * 100
        self.progress['value'] = progress
        self.progress_label.config(text=f"{progress:.1f}%")
        
        self.update_plot()
        self.update_stats_display()
        
        if self.is_running:
            self.root.after(self.update_speed, self.run_simulation_step)
        else:
            self.simulation_complete()
    
    def stop_simulation(self):
        """Stops the simulation."""
        # does not kill the data, just pauses the loop
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
    
    def reset_simulation(self):
        """Resets the simulation."""
        # clears everything so the next run starts fresh
        self.simulator = None
        self.is_running = False
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        
        self.ax.clear()
        self.canvas.draw()
        self.stats_text.delete(1.0, tk.END)
    
    def simulation_complete(self):
        """Called when simulation finishes."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        self.update_stats_display()
    
    def update_plot(self):
        """Updates the graph with current data."""
        if self.simulator is None or not self.simulator.profit_history:
            self.ax.clear()
            self.canvas.draw()
            return

        self.ax.clear()

        # Data as numpy arrays
        hand_numbers = np.arange(1, len(self.simulator.profit_history) + 1, dtype=float)
        profit_array = np.asarray(self.simulator.profit_history, dtype=float)
        ev_array = np.asarray(self.simulator.expected_value_history, dtype=float)

        # Guard against any rare length mismatch
        if ev_array.size != profit_array.size:
            if ev_array.size < profit_array.size:
                ev_array = np.pad(ev_array, (0, profit_array.size - ev_array.size), mode="edge")
            else:
                ev_array = ev_array[:profit_array.size]

        # Lines
        self.ax.plot(
            hand_numbers, ev_array,
            label="Expected Value",
            linestyle="--", linewidth=2, color="orange", alpha=0.7
        )
        self.ax.plot(
            hand_numbers, profit_array,
            label="Actual Profit",
            linewidth=2.5, color="#3498db", alpha=0.9
        )

        # Smooth area shading without vertical edge lines
        mask_pos = profit_array >= 0
        mask_neg = ~mask_pos

        self.ax.fill_between(
            hand_numbers, profit_array, 0.0,
            where=mask_pos,
            color="#27ae60",
            alpha=0.25,
            interpolate=True,
            linewidth=0,
            edgecolor="none",
            label="Profit Zone"
        )
        self.ax.fill_between(
            hand_numbers, profit_array, 0.0,
            where=mask_neg,
            color="#e74c3c",
            alpha=0.25,
            interpolate=True,
            linewidth=0,
            edgecolor="none",
            label="Loss Zone"
        )

        # Axes formatting
        self.ax.axhline(y=0, color="black", linestyle="-", linewidth=1.5, alpha=0.7)
        self.ax.set_xlabel("Hands Played", fontsize=12, fontweight="bold")
        self.ax.set_ylabel("Profit ($)", fontsize=12, fontweight="bold")
        self.ax.set_title(
            f"Blackjack Simulation - {self.simulator.strategy.get_name()}",
            fontsize=14, fontweight="bold"
        )
        self.ax.legend(loc="upper left", fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle="--")

        self.fig.tight_layout()
        self.canvas.draw()

    
    def update_stats_display(self, error_msg=None):
        # simple slate wipe then repopulate so it does not duplicate lines
        self.stats_text.delete(1.0, tk.END)
        
        if error_msg:
            self.stats_text.insert(tk.END, error_msg, 'loss')
            return
        
        if self.simulator is None:
            self.stats_text.insert(tk.END, "Run a simulation to see statistics", 'neutral')
            return
        
        stats = self.simulator.get_statistics()
        if stats is None:
            return
        
        # Header
        self.stats_text.insert(tk.END, "SIMULATION RESULTS DASHBOARD\n", 'header')
        
        # Progress
        progress = (self.simulator.current_hand / self.simulator.num_hands) * 100
        self.stats_text.insert(tk.END, f"Progress: ", 'subheader')
        self.stats_text.insert(tk.END, f"{self.simulator.current_hand}/{self.simulator.num_hands} ", 'value')
        self.stats_text.insert(tk.END, f"({progress:.1f}%)\n\n", 'neutral')
        
        # Outcome Distribution
        self.stats_text.insert(tk.END, "OUTCOME DISTRIBUTION\n", 'subheader')
        
        self.stats_text.insert(tk.END, "Wins: ", 'profit')
        self.stats_text.insert(tk.END, f"{stats['wins']:5d}  ({stats['win_percentage']:5.2f}%)\n", 'profit')
        
        self.stats_text.insert(tk.END, "Losses: ", 'loss')
        self.stats_text.insert(tk.END, f"{stats['losses']:5d}  ({stats['loss_percentage']:5.2f}%)\n", 'loss')
        
        self.stats_text.insert(tk.END, "Ties: ", 'neutral')
        self.stats_text.insert(tk.END, f"{stats['ties']:5d}  ({stats['tie_percentage']:5.2f}%)\n\n", 'neutral')
        
        # Betting Information
        self.stats_text.insert(tk.END, "BETTING INFORMATION\n", 'subheader')
        
        self.stats_text.insert(tk.END, "Strategy: ", 'neutral')
        self.stats_text.insert(tk.END, f"{self.simulator.strategy.get_name()}\n", 'value')
        
        self.stats_text.insert(tk.END, "Base Bet: ",'neutral')
        self.stats_text.insert(tk.END, f"${self.simulator.base_bet:.2f}\n", 'value')
        
        self.stats_text.insert(tk.END, "Max Bet: ",'neutral')
        self.stats_text.insert(tk.END, f"${self.simulator.max_bet:.2f}\n", 'value')
        
        self.stats_text.insert(tk.END, "Avg Bet: ",'neutral')
        self.stats_text.insert(tk.END, f"${stats['avg_bet']:.2f}\n", 'value')
        
        self.stats_text.insert(tk.END, "Max Bet Used: ",'neutral')
        self.stats_text.insert(tk.END, f"${stats['max_bet_used']:.2f}\n", 'value')
        
        self.stats_text.insert(tk.END, "Total Wagered: ",'neutral')
        self.stats_text.insert(tk.END, f"${stats['total_bet']:.2f}\n\n", 'value')
        
        # Streak Analysis
        self.stats_text.insert(tk.END, "STREAK ANALYSIS\n", 'subheader')
        
        self.stats_text.insert(tk.END, "Longest Win Streak: ",'neutral')
        self.stats_text.insert(tk.END, f"{stats['longest_win_streak']} hands\n", 'profit')
        
        self.stats_text.insert(tk.END, "Longest Loss Streak: ",'neutral')
        self.stats_text.insert(tk.END, f"{stats['longest_loss_streak']} hands\n\n", 'loss')
        
        # Profit Analysis
        self.stats_text.insert(tk.END, "PROFIT ANALYSIS\n", 'subheader')
        
        self.stats_text.insert(tk.END, "Highest Profit: ",'neutral')
        profit_tag = 'profit' if stats['highest_profit'] >= 0 else 'loss'
        self.stats_text.insert(tk.END, f"${stats['highest_profit']:,.2f}\n", profit_tag)
        
        self.stats_text.insert(tk.END, "Lowest Point: ",'neutral')
        self.stats_text.insert(tk.END, f"${stats['lowest_profit']:,.2f}\n", 'loss')
        
        self.stats_text.insert(tk.END, "\nFINAL PROFIT/LOSS: ",'neutral')
        final_tag = 'profit' if stats['final_profit'] >= 0 else 'loss'
        self.stats_text.insert(tk.END, f"${stats['final_profit']:,.2f}\n", final_tag)
        
        # ROI is helpful because it normalizes across different bet sizes
        roi = (stats['final_profit'] / stats['total_bet']) * 100 if stats['total_bet'] > 0 else 0
        self.stats_text.insert(tk.END, "ROI: ",'neutral')
        roi_tag = 'profit' if roi >= 0 else 'loss'
        self.stats_text.insert(tk.END, f"{roi:.2f}%\n", roi_tag)