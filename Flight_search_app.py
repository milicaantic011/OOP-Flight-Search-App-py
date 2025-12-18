import tkinter as tk
from tkinter import ttk, messagebox
import csv
import re
from datetime import datetime

# Flight database
flight_database = {}


# ═══════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════
def clean_text(text):
    """Remove extra spaces from text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', str(text))
    return text.strip()


def parse_price(price_str):
    """Convert price string to float"""
    try:
        cleaned = re.sub(r'[^\d.,]', '', str(price_str))
        cleaned = cleaned.replace(',', '.')
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0


def parse_int(value_str):
    """Convert string to integer safely"""
    try:
        return int(value_str)
    except:
        return 0


def time_to_minutes(time_str):
    """Convert time string to minutes"""
    try:
        hours, minutes = time_str.split(':')
        return int(hours) * 60 + int(minutes)
    except:
        return 0


def calculate_delay_fee(delay_minutes):
    """Calculate EU regulation delay compensation fee"""
    if delay_minutes < 120:
        return 0
    elif delay_minutes < 180:
        return 250
    elif delay_minutes < 240:
        return 400
    else:
        return 600


# ═══════════════════════════════════════
# TICKET CLASS - Base class
# ═══════════════════════════════════════
class Ticket:
    """Base class for all ticket types"""
    
    def __init__(self, price, passenger_count):
        self.__price = price
        self.__passenger_count = passenger_count
        self.__multiplier = 1.0
    
    def get_price(self):
        return self.__price
    
    def get_passenger_count(self):
        return self.__passenger_count
    
    def get_multiplier(self):
        return self.__multiplier
    
    def set_multiplier(self, mult):
        if mult > 0:
            self.__multiplier = mult
    
    def calculate_ticket_price(self):
        return self.__price * self.__multiplier
    
    def calculate_revenue(self):
        return self.calculate_ticket_price() * self.__passenger_count


# ═══════════════════════════════════════
# SUBCLASSES - Inherit from Ticket
# ═══════════════════════════════════════
class EconomyLight(Ticket):
    def __init__(self, price, passenger_count):
        super().__init__(price, passenger_count)
        self.set_multiplier(0.7)


class EconomyStandard(Ticket):
    def __init__(self, price, passenger_count):
        super().__init__(price, passenger_count)
        self.set_multiplier(1.0)


class EconomyComfort(Ticket):
    def __init__(self, price, passenger_count):
        super().__init__(price, passenger_count)
        self.set_multiplier(1.3)


class BusinessClass(Ticket):
    def __init__(self, price, passenger_count):
        super().__init__(price, passenger_count)
        self.set_multiplier(2.5)


# ═══════════════════════════════════════
# FLIGHT CLASS
# ═══════════════════════════════════════
class Flight:
    """Flight class with private attributes"""
    
    def __init__(self, flight_number, carrier, aircraft_type, aircraft_capacity,
                 departure_airport, arrival_airport, departure_time, arrival_time,
                 delay_time, gate, num_passengers, ticket_price, damaged_baggage,
                 damage_bagg_count, no_show_passengers,
                 economy_light, economy_standard, economy_comfort, business):
        
        self.__flight_number = clean_text(flight_number)
        self.__carrier = clean_text(carrier)
        self.__aircraft_type = clean_text(aircraft_type)
        self.__aircraft_capacity = parse_int(aircraft_capacity)
        self.__departure_airport = clean_text(departure_airport)
        self.__arrival_airport = clean_text(arrival_airport)
        self.__departure_time = clean_text(departure_time)
        self.__arrival_time = clean_text(arrival_time)
        self.__delay_time = clean_text(delay_time)
        self.__gate = clean_text(gate)
        self.__num_passengers = parse_int(num_passengers)
        self.__ticket_price = parse_price(ticket_price)
        self.__damaged_baggage = parse_price(damaged_baggage)
        self.__damage_bagg_count = parse_int(damage_bagg_count)
        self.__no_show_passengers = parse_int(no_show_passengers)
        
        self.__eco_light = EconomyLight(self.__ticket_price, parse_int(economy_light))
        self.__eco_standard = EconomyStandard(self.__ticket_price, parse_int(economy_standard))
        self.__eco_comfort = EconomyComfort(self.__ticket_price, parse_int(economy_comfort))
        self.__business = BusinessClass(self.__ticket_price, parse_int(business))
    
    # Getters
    def get_flight_number(self):
        return self.__flight_number
    
    def get_carrier(self):
        return self.__carrier
    
    def get_aircraft_type(self):
        return self.__aircraft_type
    
    def get_aircraft_capacity(self):
        return self.__aircraft_capacity
    
    def get_departure_airport(self):
        return self.__departure_airport
    
    def get_arrival_airport(self):
        return self.__arrival_airport
    
    def get_departure_time(self):
        return self.__departure_time
    
    def get_arrival_time(self):
        return self.__arrival_time
    
    def get_delay_time(self):
        return self.__delay_time
    
    def get_gate(self):
        return self.__gate
    
    def get_num_passengers(self):
        return self.__num_passengers
    
    def get_ticket_price(self):
        return self.__ticket_price
    
    def get_damaged_baggage(self):
        return self.__damaged_baggage
    
    def get_damage_bagg_count(self):
        return self.__damage_bagg_count
    
    def get_no_show_passengers(self):
        return self.__no_show_passengers
    
    def get_eco_light(self):
        return self.__eco_light
    
    def get_eco_standard(self):
        return self.__eco_standard
    
    def get_eco_comfort(self):
        return self.__eco_comfort
    
    def get_business(self):
        return self.__business
    
    # Calculations
    def calculate_occupancy(self):
        if self.__aircraft_capacity > 0:
            return (self.__num_passengers / self.__aircraft_capacity) * 100
        return 0
    
    def calculate_revenue(self):
        return (self.__eco_light.calculate_revenue() +
                self.__eco_standard.calculate_revenue() +
                self.__eco_comfort.calculate_revenue() +
                self.__business.calculate_revenue())
    
    def calculate_delay_cost(self):
        delay_minutes = time_to_minutes(self.__delay_time)
        delay_fee = calculate_delay_fee(delay_minutes)
        return self.__num_passengers * delay_fee
    
    def calculate_baggage_cost(self):
        return self.__damage_bagg_count * self.__damaged_baggage
    
    def calculate_total_costs(self):
        return self.calculate_delay_cost() + self.calculate_baggage_cost()
    
    def calculate_profit(self):
        return self.calculate_revenue() - self.calculate_total_costs()


# ═══════════════════════════════════════
# Load CSV
# ═══════════════════════════════════════
def load_csv():
    """Load flight data from CSV file"""
    global flight_database
    try:
        with open("Flight_numbers.csv", "r", encoding="utf-8-sig") as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                flight_num_raw = clean_text(row.get('flight_number', ''))
                if not flight_num_raw:
                    continue
                
                flight = Flight(
                    row['flight_number'],
                    row['carrier'],
                    row['aircraft_type'],
                    row['aircraft_capacity'],
                    row['departure_airport'],
                    row['arrival_airport'],
                    row['departure_time'],
                    row['arrival_time'],
                    row['delay_time'],
                    row['gate'],
                    row['num_passengers'],
                    row['ticket_price'],
                    row['damaged_baggage'],
                    row['damage_bagg_count'],
                    row['no_show_passengers'],
                    row['economy_light'],
                    row['economy_standard'],
                    row['economy_comfort'],
                    row['business']
                )
                
                flight_num_clean = re.sub(r'\s+', '', flight.get_flight_number()).upper()
                
                if flight_num_clean:
                    flight_database[flight_num_clean] = flight

        print(f"Loaded {len(flight_database)} flights")
        return True

    except FileNotFoundError:
        messagebox.showerror("Error", "CSV file not found!")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error loading CSV: {str(e)}")
        return False


# ═══════════════════════════════════════
# GUI Functions
# ═══════════════════════════════════════
def display_flight_info(flight):
    """Display flight information using Labels and Frames"""
    
    # Clear previous content
    for widget in info_frame.winfo_children():
        widget.destroy()
    
    # Colors
    bg_main = "#ecf0f1"
    bg_section = "#ffffff"
    bg_header = "#2c3e50"
    fg_header = "#ffffff"
    fg_label = "#7f8c8d"
    fg_value = "#2c3e50"
    
    # ═══ FLIGHT INFO SECTION ═══
    section1 = tk.LabelFrame(info_frame, text="  FLIGHT INFORMATION  ", font=("Arial", 12, "bold"),
                             bg=bg_section, fg=bg_header, padx=15, pady=10)
    section1.pack(fill=tk.X, padx=10, pady=5)
    
    # Row 1: Flight, Carrier
    row1 = tk.Frame(section1, bg=bg_section)
    row1.pack(fill=tk.X, pady=3)
    
    tk.Label(row1, text="Flight:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row1, text=flight.get_flight_number(), font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row1, text="Carrier:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row1, text=flight.get_carrier(), font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=5)
    
    # Row 2: Aircraft, Gate
    row2 = tk.Frame(section1, bg=bg_section)
    row2.pack(fill=tk.X, pady=3)
    
    tk.Label(row2, text="Aircraft:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row2, text=flight.get_aircraft_type(), font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row2, text="Gate:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row2, text=flight.get_gate(), font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=5)
    
    # Row 3: Route
    row3 = tk.Frame(section1, bg=bg_section)
    row3.pack(fill=tk.X, pady=3)
    
    tk.Label(row3, text="Route:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    route = f"{flight.get_departure_airport()}  →  {flight.get_arrival_airport()}"
    tk.Label(row3, text=route, font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=5)
    
    # Row 4: Time, Delay
    row4 = tk.Frame(section1, bg=bg_section)
    row4.pack(fill=tk.X, pady=3)
    
    tk.Label(row4, text="Time:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    time_str = f"{flight.get_departure_time()} - {flight.get_arrival_time()}"
    tk.Label(row4, text=time_str, font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row4, text="Delay:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    delay_color = "#e74c3c" if time_to_minutes(flight.get_delay_time()) >= 120 else fg_value
    tk.Label(row4, text=flight.get_delay_time(), font=("Arial", 11, "bold"), bg=bg_section, fg=delay_color).pack(side=tk.LEFT, padx=5)
    
    # ═══ CAPACITY SECTION ═══
    section2 = tk.LabelFrame(info_frame, text="  CAPACITY  ", font=("Arial", 12, "bold"),
                             bg=bg_section, fg=bg_header, padx=15, pady=10)
    section2.pack(fill=tk.X, padx=10, pady=5)
    
    row5 = tk.Frame(section2, bg=bg_section)
    row5.pack(fill=tk.X, pady=3)
    
    tk.Label(row5, text="Passengers:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    pax_str = f"{flight.get_num_passengers()} / {flight.get_aircraft_capacity()}"
    tk.Label(row5, text=pax_str, font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row5, text="Occupancy:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    occ = flight.calculate_occupancy()
    occ_color = "#27ae60" if occ >= 80 else "#e67e22" if occ >= 50 else "#e74c3c"
    tk.Label(row5, text=f"{occ:.1f}%", font=("Arial", 11, "bold"), bg=bg_section, fg=occ_color).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row5, text="No-Show:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row5, text=str(flight.get_no_show_passengers()), font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=5)
    
    # ═══ TICKETS SECTION (Treeview) ═══
    section3 = tk.LabelFrame(info_frame, text="  TICKETS  ", font=("Arial", 12, "bold"),
                             bg=bg_section, fg=bg_header, padx=15, pady=10)
    section3.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Treeview for tickets
    ticket_tree = ttk.Treeview(section3, columns=("class", "price", "pax", "revenue"), show="headings", height=4)
    
    ticket_tree.heading("class", text="CLASS")
    ticket_tree.heading("price", text="PRICE")
    ticket_tree.heading("pax", text="PAX")
    ticket_tree.heading("revenue", text="REVENUE")
    
    ticket_tree.column("class", width=150, anchor="w")
    ticket_tree.column("price", width=100, anchor="e")
    ticket_tree.column("pax", width=80, anchor="center")
    ticket_tree.column("revenue", width=120, anchor="e")
    
    # Add ticket data
    el = flight.get_eco_light()
    es = flight.get_eco_standard()
    ec = flight.get_eco_comfort()
    bc = flight.get_business()
    
    ticket_tree.insert("", tk.END, values=("Economy Light", f"{el.calculate_ticket_price():.0f} EUR", el.get_passenger_count(), f"{el.calculate_revenue():,.0f} EUR"))
    ticket_tree.insert("", tk.END, values=("Economy Standard", f"{es.calculate_ticket_price():.0f} EUR", es.get_passenger_count(), f"{es.calculate_revenue():,.0f} EUR"))
    ticket_tree.insert("", tk.END, values=("Economy Comfort", f"{ec.calculate_ticket_price():.0f} EUR", ec.get_passenger_count(), f"{ec.calculate_revenue():,.0f} EUR"))
    ticket_tree.insert("", tk.END, values=("Business Class", f"{bc.calculate_ticket_price():.0f} EUR", bc.get_passenger_count(), f"{bc.calculate_revenue():,.0f} EUR"))
    
    ticket_tree.pack(fill=tk.X, pady=5)
    
    # Total row
    total_frame = tk.Frame(section3, bg=bg_section)
    total_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(total_frame, text="TOTAL:", font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value, width=20, anchor="e").pack(side=tk.LEFT)
    tk.Label(total_frame, text=f"{flight.get_num_passengers()} passengers", font=("Arial", 11), bg=bg_section, fg=fg_value, width=15).pack(side=tk.LEFT, padx=10)
    tk.Label(total_frame, text=f"{flight.calculate_revenue():,.0f} EUR", font=("Arial", 11, "bold"), bg=bg_section, fg="#27ae60").pack(side=tk.LEFT)
    
    # ═══ COSTS SECTION ═══
    section4 = tk.LabelFrame(info_frame, text="  COSTS  ", font=("Arial", 12, "bold"),
                             bg=bg_section, fg=bg_header, padx=15, pady=10)
    section4.pack(fill=tk.X, padx=10, pady=5)
    
    row6 = tk.Frame(section4, bg=bg_section)
    row6.pack(fill=tk.X, pady=3)
    
    delay_cost = flight.calculate_delay_cost()
    bag_cost = flight.calculate_baggage_cost()
    total_cost = flight.calculate_total_costs()
    
    tk.Label(row6, text="Delay Cost:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row6, text=f"{delay_cost:,.0f} EUR", font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row6, text="Baggage Cost:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row6, text=f"{bag_cost:,.0f} EUR", font=("Arial", 11, "bold"), bg=bg_section, fg=fg_value).pack(side=tk.LEFT, padx=(5,30))
    
    tk.Label(row6, text="Total Costs:", font=("Arial", 11), bg=bg_section, fg=fg_label, width=12, anchor="e").pack(side=tk.LEFT)
    tk.Label(row6, text=f"{total_cost:,.0f} EUR", font=("Arial", 11, "bold"), bg=bg_section, fg="#e74c3c").pack(side=tk.LEFT, padx=5)
    
    # ═══ SUMMARY SECTION ═══
    section5 = tk.LabelFrame(info_frame, text="  SUMMARY  ", font=("Arial", 12, "bold"),
                             bg=bg_section, fg=bg_header, padx=15, pady=10)
    section5.pack(fill=tk.X, padx=10, pady=5)
    
    row7 = tk.Frame(section5, bg=bg_section)
    row7.pack(fill=tk.X, pady=5)
    
    revenue = flight.calculate_revenue()
    profit = flight.calculate_profit()
    profit_color = "#27ae60" if profit >= 0 else "#e74c3c"
    
    tk.Label(row7, text="Revenue:", font=("Arial", 12), bg=bg_section, fg=fg_label, width=10, anchor="e").pack(side=tk.LEFT)
    tk.Label(row7, text=f"{revenue:,.0f} EUR", font=("Arial", 12, "bold"), bg=bg_section, fg="#27ae60").pack(side=tk.LEFT, padx=(5,20))
    
    tk.Label(row7, text="Costs:", font=("Arial", 12), bg=bg_section, fg=fg_label, width=10, anchor="e").pack(side=tk.LEFT)
    tk.Label(row7, text=f"{total_cost:,.0f} EUR", font=("Arial", 12, "bold"), bg=bg_section, fg="#e74c3c").pack(side=tk.LEFT, padx=(5,20))
    
    tk.Label(row7, text="PROFIT:", font=("Arial", 14, "bold"), bg=bg_section, fg=fg_value, width=10, anchor="e").pack(side=tk.LEFT)
    tk.Label(row7, text=f"{profit:,.0f} EUR", font=("Arial", 14, "bold"), bg=bg_section, fg=profit_color).pack(side=tk.LEFT, padx=5)


def search_flight():
    """Search for a flight by flight number"""
    user_input = entry_field.get()
    
    if not user_input.strip():
        messagebox.showwarning("Warning", "You must enter a flight number!")
        return

    input_clean = re.sub(r'\s+', '', user_input).upper()

    if input_clean in flight_database:
        flight = flight_database[input_clean]
        
        # Hide Treeview, show Info Frame
        tree_frame.pack_forget()
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Display flight info
        display_flight_info(flight)
        
        footer.config(text=f"Flight {flight.get_flight_number()} found!", bg="#27ae60")
        entry_field.delete(0, tk.END)
    
    else:
        messagebox.showinfo("Not Found", f"Flight '{user_input}' not found!")
        footer.config(text="Flight not found", bg="#e74c3c")


def clear_fields():
    """Clear all input fields and results"""
    entry_field.delete(0, tk.END)
    
    # Clear info frame
    for widget in info_frame.winfo_children():
        widget.destroy()
    
    # Clear Treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Hide both
    tree_frame.pack_forget()
    info_frame.pack_forget()
    
    footer.config(text=f"{len(flight_database)} flights available", bg="#34495e")


def show_all_flights():
    """Display all flights in Treeview table"""
    if not flight_database:
        messagebox.showwarning("Warning", "Database is empty!")
        return

    # Hide Info Frame, show Treeview
    info_frame.pack_forget()
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Clear existing data
    for item in tree.get_children():
        tree.delete(item)
    
    # Sort flights by departure time
    sorted_flights = sorted(flight_database.values(), 
                           key=lambda f: time_to_minutes(f.get_departure_time()))

    total_revenue = 0
    total_costs = 0
    
    # Add data to Treeview
    for f in sorted_flights:
        route = f"{f.get_departure_airport()} - {f.get_arrival_airport()}"
        rev = f.calculate_revenue()
        total_revenue += rev
        total_costs += f.calculate_total_costs()
        
        tree.insert("", tk.END, values=(
            f.get_flight_number(),
            f.get_carrier(),
            route,
            f.get_eco_light().get_passenger_count(),
            f.get_eco_standard().get_passenger_count(),
            f.get_eco_comfort().get_passenger_count(),
            f.get_business().get_passenger_count(),
            f"{rev:,.0f} EUR"
        ))

    profit = total_revenue - total_costs
    footer.config(text=f"{len(flight_database)} flights | Revenue: {total_revenue:,.0f} EUR | Costs: {total_costs:,.0f} EUR | Profit: {profit:,.0f} EUR", bg="#3498db")


def on_closing():
    """Handle window close event"""
    root.destroy()


def on_tree_double_click(event):
    """Handle double-click on Treeview row"""
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        flight_number = item['values'][0]
        entry_field.delete(0, tk.END)
        entry_field.insert(0, flight_number)
        search_flight()


# ═══════════════════════════════════════
# GUI Setup
# ═══════════════════════════════════════
root = tk.Tk()
root.title("Flight Search App")
root.geometry("950x700")
root.configure(bg="#ecf0f1")
root.minsize(800, 600)

root.protocol("WM_DELETE_WINDOW", on_closing)

load_csv()

# ═══ TITLE ═══
tk.Label(
    root, 
    text="FLIGHT SEARCH APP",
    font=("Arial", 24, "bold"),
    bg="#2c3e50",
    fg="white",
    pady=20
).pack(fill=tk.X)

# ═══ MENU ═══
menu_frame = tk.Frame(root, bg="#34495e", pady=10)
menu_frame.pack(fill=tk.X)

# All Flights button - BLUE
btn_frame1 = tk.Frame(menu_frame, bg="#3498db", bd=3)
btn_frame1.pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame1, text="All Flights", font=("Arial", 12, "bold"),
          command=show_all_flights, width=12, cursor="hand2",
          highlightbackground="#3498db").pack()

# Clear button - RED
btn_frame2 = tk.Frame(menu_frame, bg="#e74c3c", bd=3)
btn_frame2.pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame2, text="Clear", font=("Arial", 12, "bold"),
          command=clear_fields, width=12, cursor="hand2",
          highlightbackground="#e74c3c").pack()

# ═══ INPUT ═══
input_frame = tk.Frame(root, bg="#ecf0f1", pady=15)
input_frame.pack()

tk.Label(input_frame, text="Enter Flight Number:", font=("Arial", 14, "bold"),
         bg="#ecf0f1").pack()

entry_field = tk.Entry(input_frame, font=("Arial", 18), width=15, justify="center")
entry_field.pack(pady=8)
entry_field.focus()

# Search button - GREEN
btn_frame3 = tk.Frame(input_frame, bg="#27ae60", bd=3)
btn_frame3.pack(pady=8)
tk.Button(btn_frame3, text="SEARCH", font=("Arial", 12, "bold"),
          command=search_flight, width=12, cursor="hand2",
          highlightbackground="#27ae60").pack()

entry_field.bind("<Return>", lambda e: search_flight())

# ═══ INFO FRAME (for single flight display with Labels) ═══
info_frame = tk.Frame(root, bg="#ecf0f1")

# ═══ TREE FRAME (for all flights table) ═══
tree_frame = tk.Frame(root, bg="#ecf0f1")

# Treeview style
style = ttk.Style()
style.configure("Treeview", font=("Arial", 11), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

# Treeview widget
tree = ttk.Treeview(tree_frame, columns=("flight", "carrier", "route", "eco_l", "eco_s", "eco_c", "bus", "revenue"), 
                    show="headings", height=20)

tree.heading("flight", text="FLIGHT")
tree.heading("carrier", text="CARRIER")
tree.heading("route", text="ROUTE")
tree.heading("eco_l", text="ECO-L")
tree.heading("eco_s", text="ECO-S")
tree.heading("eco_c", text="ECO-C")
tree.heading("bus", text="BUS")
tree.heading("revenue", text="REVENUE")

tree.column("flight", width=80, anchor="center")
tree.column("carrier", width=130, anchor="w")
tree.column("route", width=200, anchor="w")
tree.column("eco_l", width=60, anchor="center")
tree.column("eco_s", width=60, anchor="center")
tree.column("eco_c", width=60, anchor="center")
tree.column("bus", width=50, anchor="center")
tree.column("revenue", width=120, anchor="e")

tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree.bind("<Double-1>", on_tree_double_click)

# ═══ FOOTER ═══
now = datetime.now().strftime("%d.%m.%Y %H:%M")
footer = tk.Label(root, text=f"{now} | {len(flight_database)} flights available",
                  font=("Arial", 11), bg="#34495e", fg="white", pady=8)
footer.pack(fill=tk.X, side=tk.BOTTOM)

root.mainloop()