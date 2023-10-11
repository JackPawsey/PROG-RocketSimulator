# Imports
import math
import pickle
import threading
import tkinter as tk
import time
import os

# Global variables
universal_gravity_constant = 0.00000000006673
acceleration_due_to_gravity = 0
number_of_stages = 0
escape_velocity = 0
stage_data = {}
final_rocket_parameters = []

# Fonts
LARGE_FONT = ("Courier New", 15)
MIDDLE_FONT = ("Courier New", 11)
SMALL_FONT = ("Courier New", 9)


class Start(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Rocket Simulator v2000")
        tk.Tk.iconbitmap(self, default=get_path("rocket-icon.ico"))
        
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for f in (LoadingScreen, MainMenu, CreateRocket, RocketResults, CreatePlanet, ExistingRockets, Information):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoadingScreen)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()


# Enter rocket parameters
class CreateRocket(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.bind("<<ShowFrame>>", self.on_show_frame)

        self.planet_stuff = load_planets_file()

        background_image = tk.PhotoImage(file=get_path("background image -title.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        self.arrow = tk.PhotoImage(file=get_path("arrow.gif"))

        self.engines = {"F1": [6770000, 263, "Kerosene", 2618.18, 8400],
                        "J2": [486200, 200, "Liquid Hydrogen", 253.38, 1788.1],
                        "RS25": [1860000, 366, "Liquid Hydrogen", 523.6106278, 2500],
                        "Merlin": [845000, 282, "Kerosene", 359.023, 470],
                        "Raptor": [1700000, 330, "Liquid Methane", 931.2, 550]}

        self.list_of_engines = []

        self.value1 = tk.StringVar(self)
        self.value2 = tk.StringVar(self)
        self.value3 = tk.StringVar(self)
        self.value4 = tk.StringVar(self)
        self.value5 = tk.StringVar(self)
        self.value1.set("...")
        self.value2.set("...")
        self.value3.set("...")
        self.value4.set("...")
        self.value5.set("...")

        self.stage_x_labels = []
        self.dry_mass_labels = []
        self.fuel_mass_labels = []
        self.stage_height_labels = []
        self.num_engines_labels = []
        self.select_engine_labels = []

        self.dry_mass_entries = []
        self.fuel_mass_entries = []
        self.stage_height_entries = []
        self.num_engines_entries = []
        self.select_engine_entries = []

        self.planet_default = tk.StringVar(self)
        self.number_of_stages = tk.StringVar(self)

        self.f_planet_menu()

        calculate_button = tk.Button(self, text="Calculate", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                     activebackground="#20a6cb", command=self.f_get_stage_data)
        calculate_button.config(overrelief="raised")

        menu_button = tk.Button(self, text="Main Menu", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                activebackground="#20a6cb", command=lambda: self.controller.show_frame(MainMenu))
        menu_button.config(overrelief="raised")

        select_planet_button = tk.Button(self, text="Select", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                         activebackground="#20a6cb", command=self.update_planet_label)
        select_planet_button.config(overrelief="raised")

        select_num_stages_button = tk.Button(self, text="Select Stages", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                             activebackground="#20a6cb", command=self.f_validate_num_stages)
        select_num_stages_button.config(overrelief="raised")

        self.num_stages_entry = tk.Entry(self, width=10, textvariable=number_of_stages)
        self.num_stages_entry.config(background="#20a6cb", borderwidth=1)

        select_planet_l = tk.Label(self, text="Select Planet:", font=SMALL_FONT)
        select_planet_l.config(bg="#00000f", fg="white")
        planet_mass_l = tk.Label(self, text="Planet Mass:", font=SMALL_FONT)
        planet_mass_l.config(bg="#00000f", fg="white")
        planet_radius_l = tk.Label(self, text="Planet Radius:", font=SMALL_FONT)
        planet_radius_l.config(bg="#00000f", fg="white")
        gravity_acceleration_l = tk.Label(self, text="Acceleration due to gravity:", font=SMALL_FONT)
        gravity_acceleration_l.config(bg="#00000f", fg="white")
        escape_velocity_l = tk.Label(self, text="Required Escape Velocity:", font=SMALL_FONT)
        escape_velocity_l.config(bg="#00000f", fg="white")
        planet_mass_value_l = tk.Label(self, textvariable=self.value1, font=SMALL_FONT)
        planet_mass_value_l.config(bg="#00000f", fg="white")
        planet_radius_value_l = tk.Label(self, textvariable=self.value2, font=SMALL_FONT)
        planet_radius_value_l.config(bg="#00000f", fg="white")
        planet_gravity_acceleration_value_l = tk.Label(self, textvariable=self.value3, font=SMALL_FONT)
        planet_gravity_acceleration_value_l.config(bg="#00000f", fg="white")
        planet_escape_velocity_value_l = tk.Label(self, textvariable=self.value4, font=SMALL_FONT)
        planet_escape_velocity_value_l.config(bg="#00000f", fg="white")
        rocket_parameters_l = tk.Label(self, text="Enter Rocket Parameters:", font=SMALL_FONT)
        rocket_parameters_l.config(bg="#00000f", fg="white")
        num_stages_l = tk.Label(self, text="Number of Stages:", font=SMALL_FONT)
        num_stages_l.config(bg="#00000f", fg="white")
        enter_parameters_l = tk.Label(self, text="Enter the Parameters for each stage:", font=SMALL_FONT)
        enter_parameters_l.config(bg="#00000f", fg="white")
        create_rocket_l = tk.Label(self, text="Create Rocket:", font=MIDDLE_FONT)
        create_rocket_l.config(bg="#00000f", fg="white")
        mass_units_l = tk.Label(self, text="KG's", font=SMALL_FONT)
        mass_units_l.config(bg="#00000f", fg="white")
        radius_units_l = tk.Label(self, text="Meters", font=SMALL_FONT)
        radius_units_l.config(bg="#00000f", fg="white")
        gravity_acceleration_units_l = tk.Label(self, text="Meters per second per second", font=SMALL_FONT)
        gravity_acceleration_units_l.config(bg="#00000f", fg="white")
        escape_velocity_units_l = tk.Label(self, text="Meters per second", font=SMALL_FONT)
        escape_velocity_units_l.config(bg="#00000f", fg="white")

        top_line_canvas = tk.Canvas(self, width="768", height="2")
        top_line_canvas.configure(background='white', highlightthickness=0)
        top_line_canvas.place(x=0, y=28)

        bottom_line_canvas = tk.Canvas(self, width="768", height="2")
        bottom_line_canvas.configure(background='white', highlightthickness=0)
        bottom_line_canvas.place(x=0, y=165)

        create_rocket_l.place(x=320, y=4)
        select_planet_l.place(x=10, y=32)
        planet_mass_l.place(x=10, y=80)
        planet_radius_l.place(x=10, y=100)
        gravity_acceleration_l.place(x=10, y=120)
        escape_velocity_l.place(x=10, y=140)
        planet_mass_value_l.place(x=300, y=80)
        planet_radius_value_l.place(x=300, y=100)
        planet_gravity_acceleration_value_l.place(x=300, y=120)
        planet_escape_velocity_value_l.place(x=300, y=140)
        rocket_parameters_l.place(x=10, y=170)
        num_stages_l.place(x=40, y=200)
        enter_parameters_l.place(x=10, y=230)

        mass_units_l.place(x=550, y=80)
        radius_units_l.place(x=550, y=100)
        gravity_acceleration_units_l.place(x=550, y=120)
        escape_velocity_units_l.place(x=550, y=140)

        menu_button.place(x=0, y=2)
        calculate_button.place(x=384, y=570, anchor="s")
        select_planet_button.place(x=260, y=30)
        select_num_stages_button.place(x=270, y=196)
        self.num_stages_entry.place(x=180, y=202)

    def on_show_frame(self, event):
        self.planet_stuff = load_planets_file()
        self.f_planet_menu()

    def f_get_stage_data(self):

        global number_of_stages
        global stage_data

        engine_data = {"F1": [6770000, 263, "Kerosene", 2618.18, 8400],
                       "J2": [486200, 200, "Liquid Hydrogen", 253.38, 1788.1],
                       "RS25": [1860000, 366, "Liquid Hydrogen", 523.6106278, 2500],
                       "Merlin": [845000, 282, "Kerosene", 359.023, 470],
                       "Raptor": [1700000, 330, "Liquid Methane", 931.2, 550]}

        validate_planet = self.planet_default.get()

        if validate_planet == "Select Planet":
            popup_warning("Select a Planet!")
        else:
            if number_of_stages == 0:
                popup_warning("Enter a number between 1 and 5!")
            else:
                try:
                    for x in range(number_of_stages):
                        stage_dry_mass = int(self.dry_mass_entries[x].get())
                        stage_fuel_mass = int(self.fuel_mass_entries[x].get())
                        stage_engine_type = self.list_of_engines[x]
                        stage_num_engines = int(self.num_engines_entries[x].get())
                        stage_thrust = engine_data[stage_engine_type][0] * stage_num_engines
                        stage_engine_mass = engine_data[stage_engine_type][4] * stage_num_engines
                        stage_fuel_type = engine_data[stage_engine_type][2]
                        stage_flow_rate = engine_data[stage_engine_type][3] * stage_num_engines
                        stage_engine_isp = engine_data[stage_engine_type][1]
                        stage_height = int(self.stage_height_entries[x].get())

                        stage_data[x] = [stage_dry_mass, stage_fuel_mass, stage_engine_type, stage_num_engines,
                                         stage_thrust, stage_engine_mass, stage_fuel_type, stage_flow_rate,
                                         stage_engine_isp, stage_height]

                        stage_mass = f_stage_masses(stage_data, x)
                        stage_weight = f_stage_weight(stage_mass)

                        stage_data[x].append(stage_mass)
                        stage_data[x].append(stage_weight)

                    self.f_populate_stage_data(number_of_stages, stage_data)

                except:
                    popup_warning("Invalid Entries!")

    def f_populate_stage_data(self, number_of_stages, stage_data):

        global escape_velocity
        global final_rocket_parameters

        fuel_densities = {"Liquid Hydrogen": 70.8, "Liquid Methane": 422.62, "Kerosene": 810, "Hydrazine": 1020}

        total_height = f_total_height(stage_data, number_of_stages)
        total_mass = f_total_mass(stage_data, number_of_stages)
        total_weight = f_total_weight(stage_data, number_of_stages)

        for v in range(number_of_stages):
            stage_resultant_force = f_stage_resultant_force(total_weight, stage_data, v)
            stage_data[v].append(stage_resultant_force)

            stage_acceleration = f_stage_acceleration(stage_resultant_force, total_mass, stage_data, v)
            stage_data[v].append(stage_acceleration)

            stage_fuel_volume = f_stage_fuel_volume(stage_data, v, fuel_densities)
            stage_data[v].append(stage_fuel_volume)

            stage_diameter = f_stage_diameter(stage_data, v)
            stage_data[v].append(stage_diameter)

            exhaust_velocity = f_exhaust_velocity(stage_data, v)
            stage_data[v].append(exhaust_velocity)

            stage_delta_v = f_stage_delta_v(stage_data, v)
            stage_data[v].append(stage_delta_v)

            stage_drag = f_stage_drag(stage_data, v)
            stage_data[v].append(stage_drag)

            stage_burn_time = f_stage_burn_time(stage_data, v)
            stage_data[v].append(stage_burn_time)

            q, l = secondary_stage_calculations(total_mass, total_weight, stage_data, v, stage_drag)
            stage_data[v].append(q)
            stage_data[v].append(l)

            stage_burnout_velocity = f_stage_burnout_velocity(q, l, stage_burn_time)
            stage_boost_altitude = f_stage_boost_altitude(total_mass, stage_drag, stage_burnout_velocity, stage_data, v)
            stage_data[v].append(stage_boost_altitude)

            stage_coast_altitude = f_stage_coast_altitude(total_mass, stage_drag, stage_burnout_velocity, stage_data, v)
            stage_data[v].append(stage_coast_altitude)

        total_delta_v = f_total_delta_v(number_of_stages, stage_data)
        percentage_to_orbit = f_percentage_to_orbit(total_delta_v, escape_velocity)
        total_altitude = f_total_altitude(stage_data, number_of_stages)

        final_rocket_parameters = [total_delta_v, percentage_to_orbit, total_altitude,
                                   total_mass, total_weight, total_height]

        print("stage data:\n", stage_data)
        print("final rocket parameters:\n", final_rocket_parameters)

        self.controller.show_frame(RocketResults)
        return stage_data, final_rocket_parameters

    def f_validate_num_stages(self):

        global number_of_stages

        stage_num_input = self.num_stages_entry.get()
        try:
            stage_num_input = int(stage_num_input)
            if stage_num_input >= 0 and stage_num_input <= 5:
                number_of_stages = stage_num_input
                self.f_get_num_stages()

            else:
                popup_warning("Enter a number between 0 and 5!")
        except:
            popup_warning("Enter only numbers!")

    def update_planet_label(self):

        global escape_velocity
        global acceleration_due_to_gravity

        self.value1.set(round(self.planet_stuff[self.planet_default.get()][0]))
        self.value2.set(round(self.planet_stuff[self.planet_default.get()][1]))
        self.value3.set(round(self.planet_stuff[self.planet_default.get()][2], 2))
        self.value4.set(round(self.planet_stuff[self.planet_default.get()][3], 1))

        escape_velocity = self.planet_stuff[self.planet_default.get()][3]
        acceleration_due_to_gravity = self.planet_stuff[self.planet_default.get()][2]
        return escape_velocity, acceleration_due_to_gravity

    def f_planet_menu(self):
        self.planet_default.set("Select Planet")
        select_planet_menu = tk.OptionMenu(self, self.planet_default, *self.planet_stuff)
        select_planet_menu.config(bg="#20a6cb", activebackground="#20a6cb", font=SMALL_FONT, relief="groove")
        select_planet_menu["menu"].config(bg="#20a6cb", activebackground="grey", font=SMALL_FONT, relief="groove")
        select_planet_menu.config(compound="right", width=100, image=self.arrow, indicatoron=0, highlightthickness=0,
                                  bd=0)
        select_planet_menu.image = self.arrow
        select_planet_menu.place(x=120, y=28)

    def f_get_num_stages(self):

        global number_of_stages

        del self.stage_x_labels[:]
        del self.dry_mass_labels[:]
        del self.fuel_mass_labels[:]
        del self.stage_height_labels[:]
        del self.num_engines_labels[:]
        del self.select_engine_labels[:]

        del self.dry_mass_entries[:]
        del self.fuel_mass_entries[:]
        del self.stage_height_entries[:]
        del self.num_engines_entries[:]
        del self.select_engine_entries[:]

        a_frame = tk.Frame(self, width=768, height=285)
        a_frame.config(background="#00000f")
        a_frame.place(x=10, y=255)

        for x in range(number_of_stages):
            # Stage "X"
            self.stage_x_labels.append(tk.Label(a_frame, text=("Stage "+str(x + 1)+":"), font=SMALL_FONT))
            self.stage_x_labels[x].config(bg="#00000f", fg="white")
            self.stage_x_labels[x].place(x=10+(140*x), y=0)

            # Dry mass
            self.dry_mass_labels.append(tk.Label(a_frame, text="Dry Mass:", font=SMALL_FONT))
            self.dry_mass_labels[x].config(bg="#00000f", fg="white")
            self.dry_mass_labels[x].place(x=10+(140*x), y=30)

            self.dry_mass_entries.append(tk.Entry(a_frame))
            self.dry_mass_entries[x].config(background="#20a6cb", borderwidth=1)
            self.dry_mass_entries[x].place(x=10+(140*x), y=55)

            # Fuel mass
            self.fuel_mass_labels.append(tk.Label(a_frame, text="Fuel Mass:", font=SMALL_FONT))
            self.fuel_mass_labels[x].config(bg="#00000f", fg="white")
            self.fuel_mass_labels[x].place(x=10+(140*x), y=80)

            self.fuel_mass_entries.append(tk.Entry(a_frame))
            self.fuel_mass_entries[x].config(background="#20a6cb", borderwidth=1)
            self.fuel_mass_entries[x].place(x=10+(140*x), y=105)

            # Stage height
            self.stage_height_labels.append(tk.Label(a_frame, text="Height:", font=SMALL_FONT))
            self.stage_height_labels[x].config(bg="#00000f", fg="white")
            self.stage_height_labels[x].place(x=10+(140*x), y=130)

            self.stage_height_entries.append(tk.Entry(a_frame))
            self.stage_height_entries[x].config(background="#20a6cb", borderwidth=1)
            self.stage_height_entries[x].place(x=10+(140*x), y=155)

            # Number of engines
            self.num_engines_labels.append(tk.Label(a_frame, text="Number of Engines:", font=SMALL_FONT))
            self.num_engines_labels[x].config(bg="#00000f", fg="white")
            self.num_engines_labels[x].place(x=10+(140*x), y=180)

            self.num_engines_entries.append(tk.Entry(a_frame))
            self.num_engines_entries[x].config(background="#20a6cb", borderwidth=1)
            self.num_engines_entries[x].place(x=10+(140*x), y=205)

            # Select engine
            self.select_engine_labels.append(tk.Label(a_frame, text="Select Engine:", font=SMALL_FONT))
            self.select_engine_labels[x].config(bg="#00000f", fg="white")
            self.select_engine_labels[x].place(x=10+(140*x), y=230)

            # option menus
            self.select_engine_entries.append(DropDown(a_frame, self.engines, "Select Engine"))
            self.select_engine_entries[x].add_callback(self.f_engine_menu_callback)
            self.select_engine_entries[x].config(background="#20a6cb", activebackground="#20a6cb", font=SMALL_FONT,
                                                 relief="groove", compound="right", width=115, image=self.arrow,
                                                 indicatoron=0, highlightthickness=0, bd=0)
            self.select_engine_entries[x]["menu"].config(background="#20a6cb", bd=0, fg="white", font=SMALL_FONT,
                                                         activebackground="grey", relief="groove")
            self.select_engine_entries[x].image = self.arrow
            self.select_engine_entries[x].place(x=10+(140*x), y=250)

        return number_of_stages

    def f_engine_menu_callback(self):

        count = 0
        temp = []

        for x in range(number_of_stages):
            self.list_of_engines.append(self.select_engine_entries[x].get())
            count += 1

            if count == number_of_stages:
                for x in range(number_of_stages):
                    temp.append(self.list_of_engines[-number_of_stages + x])

                del self.list_of_engines[:]
                self.list_of_engines = temp

        return self.list_of_engines


# View rocket results
class RocketResults(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.bind("<<ShowFrame>>", self.on_show_frame)

        self.total_mass_out = tk.StringVar(self)
        self.total_delta_v_out = tk.StringVar(self)
        self.total_height_out = tk.StringVar(self)
        self.total_altitude_out = tk.StringVar(self)
        self.percent_to_orbit_out = tk.StringVar(self)

        background_image = tk.PhotoImage(file=get_path("background image -title.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        total_mass_out_l = tk.Label(self, textvariable=self.total_mass_out, font=SMALL_FONT)
        total_mass_out_l.config(bg="#00000f", fg="white")
        total_delta_v_out_l = tk.Label(self, textvariable=self.total_delta_v_out, font=SMALL_FONT)
        total_delta_v_out_l.config(bg="#00000f", fg="white")
        max_altitude_out_l = tk.Label(self, textvariable=self.total_altitude_out, font=SMALL_FONT)
        max_altitude_out_l.config(bg="#00000f", fg="white")
        total_height_out_l = tk.Label(self, textvariable=self.total_height_out, font=SMALL_FONT)
        total_height_out_l.config(bg="#00000f", fg="white")
        orbit_percent_out_l = tk.Label(self, textvariable=self.percent_to_orbit_out, font=SMALL_FONT)
        orbit_percent_out_l.config(bg="#00000f", fg="white")
        final_statistics_l = tk.Label(self, text="Final Statistics:", font=SMALL_FONT)
        final_statistics_l.config(bg="#00000f", fg="white")
        total_delta_v_l = tk.Label(self, text="Total Delta V:", font=SMALL_FONT)
        total_delta_v_l.config(bg="#00000f", fg="white")
        orbit_percent_l = tk.Label(self, text="Percentage to Orbit:", font=SMALL_FONT)
        orbit_percent_l.config(bg="#00000f", fg="white")
        max_altitude_l = tk.Label(self, text="Maximum Altitude:", font=SMALL_FONT)
        max_altitude_l.config(bg="#00000f", fg="white")
        total_height_l = tk.Label(self, text="Total Height:", font=SMALL_FONT)
        total_height_l.config(bg="#00000f", fg="white")
        total_mass_l = tk.Label(self, text="Total Mass:", font=SMALL_FONT)
        total_mass_l.config(bg="#00000f", fg="white")
        stage_statistics_l = tk.Label(self, text="Stage Statistics:", font=SMALL_FONT)
        stage_statistics_l.config(bg="#00000f", fg="white")
        rocket_results_l = tk.Label(self, text="Rocket Results:", font=MIDDLE_FONT)
        rocket_results_l.config(bg="#00000f", fg="white")

        top_line_canvas = tk.Canvas(self, width="768", height="2")
        top_line_canvas.configure(background='white', highlightthickness=0)
        top_line_canvas.place(x=0, y=28)

        bottom_line_canvas = tk.Canvas(self, width="768", height="2")
        bottom_line_canvas.configure(background='white', highlightthickness=0)
        bottom_line_canvas.place(x=0, y=450)

        enter_parameters_button = tk.Button(self, text="Enter Parameters", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                            activebackground="#20a6cb",
                                            command=lambda: controller.show_frame(CreateRocket))
        enter_parameters_button.config(overrelief="raised")
        enter_parameters_button.place(x=0, y=2)

        self.stage_mass_values = []
        self.stage_weight_values = []
        self.stage_thrust_values = []
        self.stage_delta_v_values = []
        self.stage_boost_altitude_values = []
        self.stage_burn_time_values = []

        total_delta_v_l.place(x=40, y=500)
        orbit_percent_l.place(x=410, y=500)
        max_altitude_l.place(x=160, y=500)
        total_height_l.place(x=300, y=500)
        stage_statistics_l.place(x=10, y=38)
        final_statistics_l.place(x=10, y=460)
        rocket_results_l.place(x=320, y=3)
        total_delta_v_out_l.place(x=40, y=530)
        max_altitude_out_l.place(x=160, y=530)
        total_height_out_l.place(x=300, y=530)
        orbit_percent_out_l.place(x=410, y=530)
        total_mass_l.place(x=570, y=500)
        total_mass_out_l.place(x=570, y=530)

    def on_show_frame(self, event):
        self.f_display_stage_data()
        self.f_display_final_rocket_stats()

    def f_display_stage_data(self):

        global number_of_stages
        global stage_data

        stage_x_labels = []
        stage_mass_labels = []
        stage_weight_labels = []
        stage_thrust_labels = []
        stage_delta_v_labels = []
        boost_altitude_labels = []
        burn_time_labels = []

        stage_mass_out_labels = []
        stage_weight_out_labels = []
        stage_thrust_out_labels = []
        stage_delta_v_out_labels = []
        boost_altitude_out_labels = []
        burn_time_out_labels = []

        a_frame = tk.Frame(self, width=766, height=(80 * number_of_stages), background="#00000f")
        a_frame.place(x=2, y=60)

        for x in range(number_of_stages):
            temp = tk.StringVar(self)
            temp.set(str(round(stage_data[x][10], 2))+" (KG)")
            self.stage_mass_values.append(temp)

            temp2 = tk.StringVar(self)
            temp2.set((round(stage_data[x][11], 2), "(N)"))
            self.stage_weight_values.append(temp2)

            temp3 = tk.StringVar(self)
            temp3.set((round(stage_data[x][4], 2), "(N)"))
            self.stage_thrust_values.append(temp3)

            temp4 = tk.StringVar(self)
            temp4.set((round(stage_data[x][17], 2), "(m/s)"))
            self.stage_delta_v_values.append(temp4)

            temp5 = tk.StringVar(self)
            temp5.set((round(stage_data[x][22], 2), "(m)"))
            self.stage_boost_altitude_values.append(temp5)

            temp6 = tk.StringVar(self)
            temp6.set((round(stage_data[x][19], 2), "(s)"))
            self.stage_burn_time_values.append(temp6)

        for x in range(number_of_stages):
            # Stage "X"
            stage_x_labels.append(tk.Label(a_frame, text=("Stage " + str(x + 1) + ":"), font=SMALL_FONT))
            stage_x_labels[x].config(bg="#00000f", fg="white")
            stage_x_labels[x].place(x=10, y=10 + (x * 70))

            # Stage mass
            stage_mass_labels.append(tk.Label(a_frame, text="Stage Mass:", font=SMALL_FONT))
            stage_mass_labels[x].config(bg="#00000f", fg="white")
            stage_mass_labels[x].place(x=30, y=30 + (x * 70))

            stage_mass_out_labels.append(tk.Label(a_frame, textvariable=self.stage_mass_values[x], font=SMALL_FONT))
            stage_mass_out_labels[x].config(bg="#00000f", fg="white")
            stage_mass_out_labels[x].place(x=30, y=50 + (x * 70))

            # Stage Weight
            stage_weight_labels.append(tk.Label(a_frame, text="Stage Weight:", font=SMALL_FONT))
            stage_weight_labels[x].config(bg="#00000f", fg="white")
            stage_weight_labels[x].place(x=120, y=30 + (x * 70))

            stage_weight_out_labels.append(tk.Label(a_frame, textvariable=self.stage_weight_values[x], font=SMALL_FONT))
            stage_weight_out_labels[x].config(bg="#00000f", fg="white")
            stage_weight_out_labels[x].place(x=120, y=50 + (x * 70))

            # Stage thrust
            stage_thrust_labels.append(tk.Label(a_frame, text="Stage Thrust:", font=SMALL_FONT))
            stage_thrust_labels[x].config(bg="#00000f", fg="white")
            stage_thrust_labels[x].place(x=220, y=30 + (x * 70))

            stage_thrust_out_labels.append(tk.Label(a_frame, textvariable=self.stage_thrust_values[x], font=SMALL_FONT))
            stage_thrust_out_labels[x].config(bg="#00000f", fg="white")
            stage_thrust_out_labels[x].place(x=220, y=50 + (x * 70))

            # Stage delta v
            stage_delta_v_labels.append(tk.Label(a_frame, text="Stage Delta V:", font=SMALL_FONT))
            stage_delta_v_labels[x].config(bg="#00000f", fg="white")
            stage_delta_v_labels[x].place(x=320, y=30 + (x * 70))

            stage_delta_v_out_labels.append(tk.Label(a_frame, textvariable=self.stage_delta_v_values[x],
                                                     font=SMALL_FONT))
            stage_delta_v_out_labels[x].config(bg="#00000f", fg="white")
            stage_delta_v_out_labels[x].place(x=320, y=50 + (x * 70))

            # Stage boost altitude
            boost_altitude_labels.append(tk.Label(a_frame, text="Stage Boost Altitude", font=SMALL_FONT))
            boost_altitude_labels[x].config(bg="#00000f", fg="white")
            boost_altitude_labels[x].place(x=430, y=30 + (x * 70))

            boost_altitude_out_labels.append(tk.Label(a_frame, textvariable=self.stage_boost_altitude_values[x],
                                                      font=SMALL_FONT))
            boost_altitude_out_labels[x].config(bg="#00000f", fg="white")
            boost_altitude_out_labels[x].place(x=430, y=50 + (x * 70))

            # Stage burn time
            burn_time_labels.append(tk.Label(a_frame, text="Stage Burn Time:", font=SMALL_FONT))
            burn_time_labels[x].config(bg="#00000f", fg="white")
            burn_time_labels[x].place(x=590, y=30 + (x * 70))

            burn_time_out_labels.append(tk.Label(a_frame, textvariable=self.stage_burn_time_values[x], font=SMALL_FONT))
            burn_time_out_labels[x].config(bg="#00000f", fg="white")
            burn_time_out_labels[x].place(x=590, y=50 + (x * 70))

    def f_display_final_rocket_stats(self):

        global final_rocket_parameters

        self.total_mass_out.set((round(final_rocket_parameters[3], 2), "(KG)"))
        self.total_delta_v_out.set((round(final_rocket_parameters[0], 2), "(m/s)"))
        self.total_height_out.set((round(final_rocket_parameters[5], 2), "(M)"))
        self.total_altitude_out.set((round(final_rocket_parameters[2], 2), "(M)"))
        self.percent_to_orbit_out.set((round(final_rocket_parameters[1], 2), "%"))


# Main Menu
class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        background_image = tk.PhotoImage(file=get_path("background image.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        create_rocket_button = tk.Button(self, text="Create Rocket", bg="#20a6cb",
                                         font=LARGE_FONT, relief='flat', activebackground="#20a6cb",
                                         command=lambda: controller.show_frame(CreateRocket))
        create_rocket_button.config(width=30, overrelief="raised")

        create_planet_button = tk.Button(self, text="Create Planet", bg="#20a6cb",
                                         font=LARGE_FONT, relief='flat', activebackground="#20a6cb",
                                         command=lambda: controller.show_frame(CreatePlanet))
        create_planet_button.config(width=30, overrelief="raised")

        view_statistics_button = tk.Button(self, text="Existing Rockets", bg="#20a6cb",
                                           font=LARGE_FONT, relief='flat', activebackground="#20a6cb",
                                           command=lambda: controller.show_frame(ExistingRockets))
        view_statistics_button.config(width=30, overrelief="raised")

        display_information_button = tk.Button(self, text="Extra Information", bg="#20a6cb",
                                               font=LARGE_FONT, relief='flat', activebackground="#20a6cb",
                                               command=lambda: controller.show_frame(Information))
        display_information_button.config(width=30, overrelief="raised")

        create_rocket_button.place(x=200, y=150)
        create_planet_button.place(x=200, y=200)
        view_statistics_button.place(x=200, y=250)
        display_information_button.place(x=200, y=300)


# Loading screen
class LoadingScreen(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        background_image = tk.PhotoImage(file=get_path("background image.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        self.loading_notes = ["Loading Fuel...", "Loading Oxidiser...", "Calculating Trajectory...",
                              "Performing Pre-Flight Checks...", "All Systems Nominal..."]

        self.note = tk.StringVar(self)

        self.loading_canvas = tk.Canvas(self, height=30, width=768, bg="#00000f", bd=0,
                                        highlightthickness=0, relief='ridge')
        self.loading_canvas.place(x=2, y=550)

        self.loading_notes_l = tk.Label(self.loading_canvas, textvariable=self.note, font=LARGE_FONT, fg="white",
                                        bg="#00000f", command=self.make_thread())
        self.loading_notes_l.place(relx=0.5, rely=0.9, anchor="s")

    def make_thread(self):
        t1 = threading.Thread(target=self.update_note)
        t1.start()

    def update_note(self):
        for x in self.loading_notes:
            self.note.set(x)
            time.sleep(0.8)
        self.controller.show_frame(MainMenu)


# Create planet
class CreatePlanet(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        background_image = tk.PhotoImage(file=get_path("background image -title.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        self.arrow = tk.PhotoImage(file=get_path("arrow.gif"))

        self.planet_stuff = load_planets_file()

        self.list_of_planets = []
        self.planet_default = tk.StringVar(self)

        planet_list_l = tk.Label(self, text="Planet List:", font=SMALL_FONT)
        planet_list_l.config(bg="#00000f", fg="white")
        create_planet_l = tk.Label(self, text="Planets:", font=MIDDLE_FONT)
        create_planet_l.config(bg="#00000f", fg="white")
        planet_name_l = tk.Label(self, text="New Planet Name:", font=SMALL_FONT)
        planet_name_l.config(bg="#00000f", fg="white")
        new_planet_mass_l = tk.Label(self, text="New Planet Mass:", font=SMALL_FONT)
        new_planet_mass_l.config(bg="#00000f", fg="white")
        new_planet_radius_l = tk.Label(self, text="New Planet Radius:", font=SMALL_FONT)
        new_planet_radius_l.config(bg="#00000f", fg="white")
        select_planet_delete_l = tk.Label(self, text="Select a planet to delete:", font=SMALL_FONT)
        select_planet_delete_l.config(bg="#00000f", fg="white")
        add_planet_l = tk.Label(self, text="Add Planet:", font=SMALL_FONT)
        add_planet_l.config(bg="#00000f", fg="white")
        delete_planet_l = tk.Label(self, text="Delete Planet:", font=SMALL_FONT)
        delete_planet_l.config(bg="#00000f", fg="white")

        self.planet_name_entry = tk.Entry(self)
        self.planet_name_entry.config(background="#20a6cb", borderwidth=1)
        self.new_planet_mass_entry = tk.Entry(self)
        self.new_planet_mass_entry.config(background="#20a6cb", borderwidth=1)
        self.new_planet_radius_entry = tk.Entry(self)
        self.new_planet_radius_entry.config(background="#20a6cb", borderwidth=1)

        add_planet_button = tk.Button(self, text="Add Planet", bg="#20a6cb", font=SMALL_FONT,
                                      relief='flat', activebackground="#20a6cb", command=self.f_validate_planet_name)
        add_planet_button.config(overrelief="raised")

        menu_button = tk.Button(self, text="Main Menu", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                activebackground="#20a6cb", command=lambda: controller.show_frame(MainMenu))
        menu_button.config(overrelief="raised")

        delete_planet_button = tk.Button(self, text="Delete", bg="#20a6cb", font=SMALL_FONT,
                                         relief='flat', activebackground="#20a6cb", command=self.delete_planet)
        delete_planet_button.config(overrelief="raised")

        top_line_canvas = tk.Canvas(self, width="768", height="2")
        top_line_canvas.configure(background='white', highlightthickness=0)
        top_line_canvas.place(x=0, y=28)

        middle_line_canvas = tk.Canvas(self, width="768", height="2")
        middle_line_canvas.configure(background='white', highlightthickness=0)
        middle_line_canvas.place(x=0, y=170)

        bottom_line_canvas = tk.Canvas(self, width="768", height="2")
        bottom_line_canvas.configure(background='white', highlightthickness=0)
        bottom_line_canvas.place(x=0, y=295)

        planet_list_l.place(x=10, y=40)
        create_planet_l.place(x=345, y=3)
        planet_name_l.place(x=40, y=210)
        new_planet_mass_l.place(x=40, y=235)
        new_planet_radius_l.place(x=40, y=260)
        select_planet_delete_l.place(x=40, y=340)
        add_planet_l.place(x=10, y=180)
        delete_planet_l.place(x=10, y=310)

        self.planet_name_entry.place(x=200, y=210)
        self.new_planet_mass_entry.place(x=200, y=235)
        self.new_planet_radius_entry.place(x=200, y=260)
        add_planet_button.place(x=400, y=235)
        menu_button.place(x=0, y=2)
        delete_planet_button.place(x=420, y=335)

        self.planets_list_l = tk.Text(self, height=8, width=8, padx=5, pady=2, font=SMALL_FONT,
                                      background="#00000f", fg="white", borderwidth=0, wrap="word")
        self.planets_list_l.place(x=120, y=40)

        self.planet_list_menu()
        self.fill_planet_list()

    def planet_list_menu(self):
        self.planet_default.set("Select Planet")
        select_planet_menu = tk.OptionMenu(self, self.planet_default, *self.planet_stuff)
        select_planet_menu.config(bg="#20a6cb", activebackground="#20a6cb", font=SMALL_FONT, relief="groove",
                                  highlightthickness=0)
        select_planet_menu["menu"].config(bg="#20a6cb", activebackground="grey", font=SMALL_FONT, relief="groove")
        select_planet_menu.config(compound="right", width=100, image=self.arrow, indicatoron=0)
        select_planet_menu.image = self.arrow
        select_planet_menu.place(x=240, y=335)

    def fill_planet_list(self):
        del self.list_of_planets[:]
        self.planets_list_l.delete('1.0', tk.END)

        for x in self.planet_stuff:
            self.list_of_planets.append(x)

        self.planets_list_l.insert(tk.END, self.list_of_planets)

    def create_planet(self):
        if len(self.planet_stuff) == 8:
            popup_warning("Too Many Planets!")
        else:
            self.planet_stuff[self.planet_name_entry.get()] = [int(self.new_planet_mass_entry.get()),
                                                               int(self.new_planet_radius_entry.get())]
            pickle_planets_file(self.planet_stuff)
            self.planet_stuff = load_planets_file()
            self.fill_planet_list()
            self.planet_list_menu()
            self.planet_name_entry.delete(0, "end")
            self.new_planet_mass_entry.delete(0, "end")
            self.new_planet_radius_entry.delete(0, "end")

    def delete_planet(self):
        del self.planet_stuff[self.planet_default.get()]
        pickle_planets_file(self.planet_stuff)
        self.planet_stuff = load_planets_file()
        self.fill_planet_list()
        self.planet_list_menu()

    def f_validate_planet_name(self):
        planet_name_input = self.planet_name_entry.get()
        if planet_name_input == "":
            popup_warning("Enter a planet name!")
        else:
            try:
                if any(char.isdigit() for char in planet_name_input) == False:
                    self.f_validate_planet_mass()
                else:
                    popup_warning("Enter only letters!")
            except:
                popup_warning("Enter only letters!")

    def f_validate_planet_mass(self):
        planet_mass_input = self.new_planet_mass_entry.get()
        if planet_mass_input == "":
            popup_warning("Enter a mass!")
        else:
            try:
                planet_mass_input = int(planet_mass_input)
                if planet_mass_input >= 1 and planet_mass_input <= 100000000000000000000000000000000000000000000000000:
                    self.f_validate_planet_radius()
                else:
                    popup_warning("Enter a number between 1 and 1x10^50!")
            except:
                popup_warning("Enter only numbers!")

    def f_validate_planet_radius(self):
        planet_radius_input = self.new_planet_radius_entry.get()
        if planet_radius_input == "":
            popup_warning("Enter a planet radius!")
        else:
            try:
                planet_radius_input = int(planet_radius_input)
                if planet_radius_input >= 1 and planet_radius_input <= 10000000000000000000000000:
                    self.create_planet()
                else:
                    popup_warning("Enter a number between 1 and 1x10^25!")
            except:
                popup_warning("Enter only numbers!")


class ExistingRockets(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        background_image = tk.PhotoImage(file=get_path("background image -title.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        arrow = tk.PhotoImage(file=get_path("arrow.gif"))

        rocket_data_dictionary = f_existing_rocket_data()

        def update_label():
            value1.set(rocket_data_dictionary[default_value.get()][0])
            value2.set(rocket_data_dictionary[default_value.get()][1])
            value3.set(rocket_data_dictionary[default_value.get()][2])
            value4.set(rocket_data_dictionary[default_value.get()][3])
            value5.set(rocket_data_dictionary[default_value.get()][4])
            value6.set(rocket_data_dictionary[default_value.get()][5])
            value7.set(rocket_data_dictionary[default_value.get()][6])

        value1 = tk.StringVar(self)
        value1.set("...")
        value2 = tk.StringVar(self)
        value2.set("...")
        value3 = tk.StringVar(self)
        value3.set("...")
        value4 = tk.StringVar(self)
        value4.set("...")
        value5 = tk.StringVar(self)
        value5.set("...")
        value6 = tk.StringVar(self)
        value6.set("...")
        value7 = tk.StringVar(self)
        value7.set("...")
        default_value = tk.StringVar(self)

        default_value.set("Select Rocket")
        rocket_menu = tk.OptionMenu(self, default_value, *rocket_data_dictionary.keys())
        rocket_menu.config(bg="#20a6cb", activebackground="#20a6cb", font=SMALL_FONT, relief="groove",
                           highlightthickness=0)
        rocket_menu["menu"].config(bg="#20a6cb", activebackground="grey", font=SMALL_FONT, relief="groove")
        rocket_menu.config(compound="right", width=100, image=arrow, indicatoron=0)
        rocket_menu.image = arrow

        existing_rocket_l = tk.Label(self, text="View Existing Rocket Statistics:", font=MIDDLE_FONT)
        existing_rocket_l.config(bg="#00000f", fg="white")
        select_rocket_l = tk.Label(self, text="Select Rocket:", font=SMALL_FONT)
        select_rocket_l.config(bg="#00000f", fg="white")
        thrust_l = tk.Label(self, text="Thrust (KN):", font=SMALL_FONT)
        thrust_l.config(bg="#00000f", fg="white")
        mass_l = tk.Label(self, text="Mass (KG):", font=SMALL_FONT)
        mass_l.config(bg="#00000f", fg="white")
        cost_l = tk.Label(self, text="Cost per launch (million USD):", font=SMALL_FONT)
        cost_l.config(bg="#00000f", fg="white")
        height_l = tk.Label(self, text="Height (m):", font=SMALL_FONT)
        height_l.config(bg="#00000f", fg="white")
        diameter_l = tk.Label(self, text="Diameter (m):", font=SMALL_FONT)
        diameter_l.config(bg="#00000f", fg="white")
        leo_payload_l = tk.Label(self, text="Payload to LEO (KG):", font=SMALL_FONT)
        leo_payload_l.config(bg="#00000f", fg="white")
        gto_payload_l = tk.Label(self, text="Payload to GTO/TLI (KG):", font=SMALL_FONT)
        gto_payload_l.config(bg="#00000f", fg="white")
        thrust_out_l = tk.Label(self, textvariable=value1, font=SMALL_FONT)
        thrust_out_l.config(bg="#00000f", fg="white")
        mass_out_l = tk.Label(self, textvariable=value2, font=SMALL_FONT)
        mass_out_l.config(bg="#00000f", fg="white")
        cost_out_l = tk.Label(self, textvariable=value3, font=SMALL_FONT)
        cost_out_l.config(bg="#00000f", fg="white")
        height_out_l = tk.Label(self, textvariable=value4, font=SMALL_FONT)
        height_out_l.config(bg="#00000f", fg="white")
        diameter_out_l = tk.Label(self, textvariable=value5, font=SMALL_FONT)
        diameter_out_l.config(bg="#00000f", fg="white")
        leo_payload_out_l = tk.Label(self, textvariable=value6, font=SMALL_FONT)
        leo_payload_out_l.config(bg="#00000f", fg="white")
        gto_payload_out_l = tk.Label(self, textvariable=value7, font=SMALL_FONT)
        gto_payload_out_l.config(bg="#00000f", fg="white")

        line_canvas = tk.Canvas(self, width="768", height="2")
        line_canvas.configure(background='white', highlightthickness=0)
        line_canvas.place(x=0, y=28)

        menu_button = tk.Button(self, text="Main Menu", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                activebackground="#20a6cb", command=lambda: controller.show_frame(MainMenu))
        menu_button.config(overrelief="raised")

        select_button = tk.Button(self, text="Select", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                  activebackground="#20a6cb", command=update_label)
        select_button.config(overrelief="raised")

        rocket_menu.place(x=150, y=35)
        menu_button.place(x=0, y=2)
        select_button.place(x=300, y=37)

        existing_rocket_l.place(x=240, y=3)
        select_rocket_l.place(x=10, y=40)
        thrust_l.place(x=10, y=80)
        mass_l.place(x=10, y=100)
        cost_l.place(x=10, y=120)
        height_l.place(x=10, y=140)
        diameter_l.place(x=10, y=160)
        leo_payload_l.place(x=10, y=180)
        gto_payload_l.place(x=10, y=200)
        thrust_out_l.place(x=300, y=80)
        mass_out_l.place(x=300, y=100)
        cost_out_l.place(x=300, y=120)
        height_out_l.place(x=300, y=140)
        diameter_out_l.place(x=300, y=160)
        leo_payload_out_l.place(x=300, y=180)
        gto_payload_out_l.place(x=300, y=200)


# Display extra information
class Information(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        background_image = tk.PhotoImage(file=get_path("background image -title.gif"))
        background_label = tk.Label(self, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0)

        rocket_terms = """Rocketry Terms:
        
            TLI: Trans-Lunar-Injection
            GTO: Geostationary-Transfer-Orbit
            LEO: Low-Earth-Orbit
            
            Dry Mass: The mass of the stage/rocket including the engines, excluding the fuel.
            Fuel Mass: The mass of the fuel in the stage/rocket.
            Thrust: The force produced by the engine(s) burning fuel.
            
            Delta V: The change in velocity a stage/rocket can achieve.
            Boost Altitude: The altitude a stage/rocket reaches at the moment 
            it runs out of fuel.
            Burn Time: The time taken for a stage/rocket(s) engines to burn the 
            available fuel.
            """

        unaccounted_for = """Factors unaccounted for:
            
            Atmosphere becoming thinner as altitude increases, reducing drag.
            Earth's gravity becoming weaker as altitude increases, increasing acceleration.
            Air currents/Wind hitting the rocket, increasing drag.
            Special Relativity causing time to run slower for the rocket as it accelerates, 
            decreasing acceleration.
            Dry mass decreasing as part of the engine(s) mass is burnt off during flight, 
            increasing acceleration.
            Weather conditions such as air pressure.
            Earth's rotation reducing the amount of Delta V required to reach orbit.
            Any flight maneuvers: pitching, yawing or rolling. 
        """

        information_title_l = tk.Label(self, text="Extra Information:", font=MIDDLE_FONT)
        information_title_l.config(bg="#00000f", fg="white")

        rocketry_terms_text = tk.Text(self, height=16, width=103, padx=10, pady=5, spacing1=1, font=SMALL_FONT,
                                      background="#00000f", fg="white", borderwidth=0)
        rocketry_terms_text.insert(tk.END, rocket_terms)
        rocketry_terms_text.config(state="disabled")

        unaccounted_factors_text = tk.Text(self, height=13, width=103, padx=10, pady=5, spacing1=1, font=SMALL_FONT,
                                           background="#00000f", fg="white", borderwidth=0)
        unaccounted_factors_text.insert(tk.END, unaccounted_for)
        unaccounted_factors_text.config(state="disabled")

        menu_button = tk.Button(self, text="Main Menu", bg="#20a6cb", font=SMALL_FONT, relief='flat',
                                activebackground="#20a6cb", command=lambda: controller.show_frame(MainMenu))
        menu_button.config(overrelief="raised")

        top_line_canvas = tk.Canvas(self, width="768", height="2")
        top_line_canvas.configure(background='white', highlightthickness=0)
        top_line_canvas.place(x=0, y=28)

        middle_line_canvas = tk.Canvas(self, width="768", height="2")
        middle_line_canvas.configure(background='white', highlightthickness=0)
        middle_line_canvas.place(x=0, y=305)

        information_title_l.place(x=303, y=3)
        rocketry_terms_text.place(x=10, y=35)
        unaccounted_factors_text.place(x=10, y=310)
        menu_button.place(x=0, y=2)


# Add callback function to OptionMenu
class DropDown(tk.OptionMenu):

    def __init__(self, parent, options: list, initial_value: str = None):

        self.variable = tk.StringVar(parent)
        self.variable.set(initial_value if initial_value else options[0])

        self.option_menu = tk.OptionMenu.__init__(self, parent, self.variable, *options)

        self.callback = None

    def add_callback(self, callback: callable):

        def internal_callback(*args):
            callback()

        self.variable.trace("w", internal_callback)

    def get(self):

        return self.variable.get()

    def set(self, value: str):

        self.variable.set(value)


# Display a popup window
def popup_warning(msg):
    top = tk.Toplevel()
    top.title("Warning!")
    top.geometry("300x80")
    top.resizable(width=False, height=False)
    top.bell()

    background_image = tk.PhotoImage(file="background image -title.gif")
    background_label = tk.Label(top, image=background_image)
    background_label.image = background_image
    background_label.place(x=0, y=0)

    display_message = tk.StringVar()
    display_message.set(msg)

    notification_l = tk.Label(top, textvariable=display_message, background="#00000f", fg="white", font=SMALL_FONT)
    notification_l.place(relx=0.1, y=15)

    button = tk.Button(top, text="Dismiss", command=top.destroy, relief='flat', activebackground="#20a6cb",
                       bg="#20a6cb")
    button.place(x=100, y=45)


# Reads external rocket data file
def f_existing_rocket_data():

    current_file = open(get_path("rockets.txt"), "r")

    more_rockets = True
    skip = 0
    rocket_data_dictionary = {}
    while more_rockets == True:

        if skip == 0:
            current_rocket = current_file.readline().rstrip()
            rocket_data_dictionary[current_rocket] = []
            for x in range(7):
                rocket_data_dictionary[current_rocket].append(current_file.readline().rstrip())
        else:
            rocket_data_dictionary[current_rocket] = []
            for x in range(7):
                rocket_data_dictionary[current_rocket].append(current_file.readline().rstrip())

        current_file.readline()
        next_line = current_file.readline().rstrip()

        if next_line == "":
            more_rockets = False
        else:
            skip = 1
            current_rocket = next_line

    current_file.close()

    return rocket_data_dictionary


# Load pickled data
def load_planets_file():

    planet_file = open(get_path("Planet Data.txt"), "rb")
    planet_stuff = pickle.load(planet_file)
    planet_file.close()

    for x in planet_stuff:
        acceleration_due_to_gravity = f_acceleration_due_to_gravity(planet_stuff, x)
        escape_velocity = f_escape_velocity(planet_stuff, x)

        planet_stuff[x].append(acceleration_due_to_gravity)
        planet_stuff[x].append(escape_velocity)

    return planet_stuff


#  Pickle data
def pickle_planets_file(planet_stuff):

    planet_file = open(get_path("Planet Data.txt"), "wb")
    pickle.dump(planet_stuff, planet_file)
    planet_file.close()


# Calculate the acceleration due to gravity for a planet
def f_acceleration_due_to_gravity(planet_stuff, x):

    global universal_gravity_constant, acceleration_due_to_gravity

    acceleration_due_to_gravity = universal_gravity_constant * (planet_stuff[x][0] / (planet_stuff[x][1]**2))

    return acceleration_due_to_gravity


# Calculate how close the rocket was to reaching orbit
def f_percentage_to_orbit(total_delta_v, escape_velocity):

    percentage_to_orbit = (total_delta_v / escape_velocity) * 100

    return percentage_to_orbit


# calculate the height
def f_total_height(stage_data, num_stages):

    total_height = 0

    for x in range(num_stages):
        total_height += stage_data[x][9]

    return total_height


# Calculate the mass of each stage
def f_stage_masses(stage_data, x):

    stage_mass = stage_data[x][0] + stage_data[x][1] + stage_data[x][5]

    return stage_mass


# Calculate the total mass of the rocket
def f_total_mass(stage_data, num_stages):

    total_mass = 0

    for x in range(num_stages):
        total_mass += stage_data[x][10]

    return total_mass


# Calculate delta V
def f_stage_delta_v(stage_data, v):

    stage_delta_v = stage_data[v][16] * math.log(stage_data[v][10] / (stage_data[v][0] + stage_data[v][5]))

    return stage_delta_v


# Calculate the total delta V
def f_total_delta_v(num_stages, stage_data):

    total_delta_v = 0
    for x in range(num_stages):
        total_delta_v += stage_data[x][17]

    return total_delta_v


# Calculate exhaust velocity
def f_exhaust_velocity(stage_data, v):

    global acceleration_due_to_gravity

    exhaust_velocity = acceleration_due_to_gravity * stage_data[v][8]

    return exhaust_velocity


# Calculate drag coefficient
def f_stage_drag(stage_data, v):

    air_density = 1.225
    drag_coefficient = 0.75

    area = ((stage_data[v][15] / 2)**2) * math.pi

    stage_drag = 0.5 * air_density * area * drag_coefficient

    return stage_drag


# Calculate velocity at burnout
def f_stage_burnout_velocity(q, l, stage_burn_time):

    stage_burnout_velocity = q * ((1 - (math.exp(-l * stage_burn_time))) / (1 + (math.exp(-l * stage_burn_time))))

    return stage_burnout_velocity


# Calculate altitude reached at end of boost
def f_stage_boost_altitude(total_mass, stage_drag, stage_burnout_velocity, stage_data, v):

    if v > 0:
        new_total_mass = total_mass - stage_data[v - 1][10]
        stage_boost_altitude = (-new_total_mass / (2 * stage_drag)) * math.log(
            (stage_data[v][12] - (stage_drag * stage_burnout_velocity ** 2)) / stage_data[v][12])
    else:
        stage_boost_altitude = (-total_mass / (2 * stage_drag)) * math.log(
            (stage_data[v][12] - (stage_drag * stage_burnout_velocity**2)) / stage_data[v][12])

    return stage_boost_altitude


# Calculate the coast altitude
def f_stage_coast_altitude(total_mass, stage_drag, stage_burnout_velocity, stage_data, v):

    if v > 0:
        new_total_mass = total_mass - stage_data[v - 1][10]
        stage_coast_altitude = (new_total_mass / (2 * stage_drag)) * math.log(
            (stage_data[v][11] + stage_drag * stage_burnout_velocity**2) / stage_data[v][11])
    else:
        stage_coast_altitude = (total_mass / (2 * stage_drag)) * math.log(
            (stage_data[v][11] + stage_drag * stage_burnout_velocity ** 2) / stage_data[v][11])

    return stage_coast_altitude


# Calculate the maximum altitude reached
def f_total_altitude(stage_data, num_stages):

    total_altitude = 0

    for d in range(num_stages):
        total_altitude += stage_data[d][22]
    total_altitude += stage_data[num_stages - 1][23]

    return total_altitude


# Calculate "q" and "l" for each stage
def secondary_stage_calculations(total_mass, total_weight, stage_data, v, stage_drag):

    if v > 0:
        new_total_weight = total_weight - stage_data[v-1][11]
        q = math.sqrt((stage_data[v][4] - new_total_weight) / stage_drag)
    else:
        q = math.sqrt((stage_data[v][4] - total_weight) / stage_drag)

    if v > 0:
        new_total_mass = total_mass - stage_data[v - 1][10]
        l = (2 * stage_drag * q) / new_total_mass
    else:
        l = (2 * stage_drag * q) / total_mass

    return q, l


# Calculate the burn time of each stage
def f_stage_burn_time(stage_data, v):

    stage_burn_time = stage_data[v][1] / stage_data[v][7]

    return stage_burn_time


# Calculate a stage's resultant force
def f_stage_resultant_force(total_weight, stage_data, l):

    if l > 0:
        new_total_weight = total_weight - stage_data[l - 1][11]
        stage_resultant_force = stage_data[l][4] - new_total_weight
    else:
        stage_resultant_force = stage_data[0][4] - total_weight

    return stage_resultant_force


# Calculate a stage's acceleration
def f_stage_acceleration(stage_resultant_force, total_mass, stage_data, l):

    if l > 0:
        new_total_mass = total_mass - stage_data[l - 1][10]
        stage_acceleration = stage_resultant_force / new_total_mass
    else:
        stage_acceleration = stage_resultant_force / total_mass

    return stage_acceleration


# Calculate the weight of each stage
def f_stage_weight(stage_mass):

    global acceleration_due_to_gravity

    stage_weight = stage_mass * acceleration_due_to_gravity

    return stage_weight


# Calculate the total weight of the rocket
def f_total_weight(stage_data, num_stages):

    total_weight = 0

    for x in range(num_stages):
        total_weight += stage_data[x][11]

    return total_weight


# Calculates escape velocity based on selected planet
def f_escape_velocity(planet_stuff, x):

    global universal_gravity_constant

    escape_velocity = (math.sqrt((2 * (universal_gravity_constant * planet_stuff[x][0]) / planet_stuff[x][1])))

    return escape_velocity


# Calculate the volume of the rocket fuel
def f_stage_fuel_volume(stage_data, v, fuel_densities):
    stage_fuel_volume = stage_data[v][1] / fuel_densities[stage_data[v][6]]

    return stage_fuel_volume


# Calculate the diameter of the rocket
def f_stage_diameter(stage_data, v):
    stage_diameter = (2 * math.sqrt((stage_data[v][14] / stage_data[v][9]) / math.pi))

    return stage_diameter

# Get absolute path to file
def get_path(path):
    return os.path.join(os.path.dirname(__file__), path)

app = Start()
app.resizable(width=False, height=False)
app.wm_geometry("768x576")
app.mainloop()
