from tkinter import *
from tkinter import messagebox
import sqlite3
import folium
import webbrowser
import difflib

# Mosque Class 
class Mosque:
    def __init__(self, ID, name, type, address, coordinates, imam_name):
        self.ID = ID
        self.name = name
        self.type = type
        self.address = address
        self.coordinates = coordinates
        self.imam_name = imam_name

# DB Class
class Database:
    def __init__(self):
        self.con = sqlite3.connect("mosques.db")
        self.cur = self.con.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Mosq(
            ID INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            address TEXT,
            coordinates TEXT,
            imam_name TEXT
        )
        """)

        self.con.commit()
        self.insert_data()

    def insert_data(self):
        self.cur.execute("SELECT COUNT(*) FROM Mosq")
        count = self.cur.fetchone()[0]

        if count == 0:
            mos_data = [
                (1, "Al Rajhi Jami", "Jami", "Buraydah - Al Qassim", "26.3592,43.9818", "Musaed Al-Mudayfer"),
                (2, "Al Noor Mosque", "Mosque", "Unaizah - Al Qassim", "26.0914,43.9930", "Khalid Salem"),
                (3, "King Fahad Jami", "Jami", "Buraydah - Al Qassim", "26.3260,43.9750", "Abdullah Al-Qaraawi"),
                (4, "Al Shaya Mosque", "Mosque", "Ar Rass - Al Qassim", "26.1392,43.6578", "Nasser Al-Aloola"),
                (5, "North Musalla Eid", "Musalla Eid", "Buraydah - Al Qassim", "26.3700,43.9900", "Jaber Al-Nasser")
            ]

            self.cur.executemany("INSERT INTO Mosq VALUES(?,?,?,?,?,?)", mos_data)
            self.con.commit()

    def Display(self):
        self.cur.execute("SELECT * FROM Mosq")
        return self.cur.fetchall()

    def Search(self, name):
        self.cur.execute("SELECT * FROM Mosq WHERE LOWER(name)=LOWER(?)", (name,))
        return self.cur.fetchall()

    def Insert(self, ID, name, type, address, coordinates, imam_name):
        self.cur.execute("INSERT INTO Mosq VALUES(?,?,?,?,?,?)", (ID, name, type, address, coordinates, imam_name))
        self.con.commit()

    def Delete(self, ID):
        self.cur.execute("DELETE FROM Mosq WHERE ID=?", (ID,))
        self.con.commit()

    def Update(self, imam_name, name):
        self.cur.execute("UPDATE Mosq SET imam_name=? WHERE LOWER(name)=LOWER(?)", (imam_name, name))
        self.con.commit()

    def __del__(self):
        self.con.close()

# DB Object
db = Database()

# Instructions
def show_instructions():
    instructions = """Mosques Management System Instructions:

- Search: Enter Mosque Name then click 'Search'

- Add Entry: Fill all data fields then click 'Add Entry'

- Delete Entry: Enter Mosque ID then click 'Delete Entry'

- Update Entry: Search Mosque Name then enter New Imam Name then click 'Update Entry'

- Display on Map: Search Mosque Name then click 'Display on Map' """
    
    messagebox.showinfo("System Instructions", instructions)

def clear_list():
    mosque_list.delete(0, END)

def clear_entries():
    id_entry.delete(0, END)
    name_entry.delete(0, END)
    address_entry.delete(0, END)
    coordinates_entry.delete(0, END)
    imam_entry.delete(0, END)

# Display All
def display_all():
    clear_list()
    for row in db.Display():
        mosque_list.insert(END, row)

# Name Search
def search():
    search_name = name_text.get().strip()
    
    if not search_name:
        messagebox.showerror("Error!!", "Please Enter a Mosque Name to Search.")
        return
    
    clear_list()
    result = db.Search(search_name)

    if result:
        for row in result:
            mosque_list.insert(END, row)
    else:
        all_names = [row[1] for row in db.Display()]
        similar = difflib.get_close_matches(search_name, all_names, n=3)

        if similar:
            mosque_list.insert(END, "Did You Mean:")
            for name in similar:
                mosque_list.insert(END, f"{name}")
        else:
            mosque_list.insert(END, "No Mosque was Found.")

# Add Entry
def add_entry():
    if not id_text.get().strip() or not name_text.get().strip() or not address_text.get().strip() or not coordinates_text.get().strip() or not imam_text.get().strip():
        messagebox.showerror("Error!!", "Please Fill All Data Fields.")
        return
    
    try:
        mosque = Mosque(
            int(id_text.get()),
            name_text.get(),
            type_text.get(),
            address_text.get(),
            coordinates_text.get(),
            imam_text.get()
        )

        db.Insert(
            mosque.ID,
            mosque.name,
            mosque.type,
            mosque.address,
            mosque.coordinates,
            mosque.imam_name
        )

        messagebox.showinfo("Success!", f"Mosque '{mosque.name}' Added Successfully.")
        clear_entries()
        display_all()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error!!", f"Mosque ID '{id_text.get()}' Already Exists. Please Use Different ID.")
    except ValueError:
        messagebox.showerror("Error!!", "ID must be a number.")

# Delete Entry
def delete_entry():
    mosque_id = id_text.get().strip()

    if not mosque_id:
        messagebox.showerror("Error!!", "Please Enter Mosque ID to Delete.\n\nHint: Search mosque Name first, then copy its ID.")
        return

    confirm = messagebox.askyesno("Confirm Delete!", f"Are You Sure You Want to Delete Mosque ID: {mosque_id}?")
    
    if confirm:
        db.Delete(mosque_id)
        messagebox.showinfo("Deleted!", f"Mosque ID '{mosque_id}' Deleted Successfully.")
        clear_entries()
        display_all()

# Update Entry
def update_entry():
    mosque_name = name_text.get().strip()
    new_imam = imam_text.get().strip()

    if not mosque_name:
        messagebox.showerror("Error!!", "Please Enter Mosque Name to Update.\n\nHint: First 'Search' Mosque Name.")
        return
    
    if not new_imam:
        messagebox.showerror("Error!!", "Please Enter New Imam Name in the Imam Name Field.")
        return

    result = db.Search(mosque_name)
    if not result:
        messagebox.showerror("Error!!", f"Mosque '{mosque_name}' not Found.\n\nHint: First 'Search' to find the mosque.")
        return

    db.Update(new_imam, mosque_name)
    messagebox.showinfo("Updated!", f"Imam Name for '{mosque_name}' Updated Successfully to '{new_imam}'.")
    display_all()

# Display on Map
def display_map():
    mosque_name = name_text.get().strip()
    
    if not mosque_name:
        messagebox.showerror("Error!!", "Please Enter a Mosque Name to Display on Map.\n\nHint: First 'Search' Mosque Name.")
        return
    
    result = db.Search(mosque_name)

    if result:
        coordinates = result[0][4]
        try:
            lat, lon = coordinates.split(",")
            lat, lon = float(lat), float(lon)
            
            map_obj = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup=f"{mosque_name}\nImam: {result[0][5]}").add_to(map_obj)
            map_obj.save("mosque_map.html")
            webbrowser.open("mosque_map.html")
            messagebox.showinfo("Map Opened", f"Showing location of '{mosque_name}' on the map.")
        except:
            messagebox.showerror("Error!!", "Invalid coordinates format.")
    else:
        messagebox.showerror("Error!!", f"Mosque '{mosque_name}' Not Found.\n\nHint: First 'Search' to find the mosque.")

# GUI
window = Tk()
window.title("Mosques Management System")
window.geometry("1100x650")
window.configure(bg="#dfeee2")

label_color = "#2f5d50"
button_color = "#6c9a74"
entry_color = "#f7fff8"
hint_color = "#888888"

title_label = Label(window, text="Mosques Management System", bg="#dfeee2", fg="#2f5d50", 
                    font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

Label(window, text="ID", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=1, column=0, pady=5, sticky="e")
Label(window, text="Name", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=2, column=0, pady=5, sticky="e")
Label(window, text="Type", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=3, column=0, pady=5, sticky="e")
Label(window, text="Address", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=4, column=0, pady=5, sticky="e")
Label(window, text="Coordinates", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=5, column=0, pady=5, sticky="e")
Label(window, text="Imam Name", bg="#dfeee2", fg=label_color, font=("Arial", 11, "bold")).grid(row=6, column=0, pady=5, sticky="e")

id_text = StringVar()
name_text = StringVar()
type_text = StringVar()
address_text = StringVar()
coordinates_text = StringVar()
imam_text = StringVar()

id_entry = Entry(window, textvariable=id_text, bg=entry_color, width=30)
id_entry.grid(row=1, column=1, pady=5)

name_entry = Entry(window, textvariable=name_text, bg=entry_color, width=30)
name_entry.grid(row=2, column=1, pady=5)

type_text.set("Mosque")
type_menu = OptionMenu(window, type_text, "Mosque", "Jami", "Musalla Eid")
type_menu.config(bg="#7ca982", fg="white", width=27)
type_menu.grid(row=3, column=1, pady=5)

address_entry = Entry(window, textvariable=address_text, bg=entry_color, width=30)
address_entry.grid(row=4, column=1, pady=5)

coordinates_entry = Entry(window, textvariable=coordinates_text, bg=entry_color, width=30)
coordinates_entry.grid(row=5, column=1, pady=5)

imam_entry = Entry(window, textvariable=imam_text, bg=entry_color, width=30)
imam_entry.grid(row=6, column=1, pady=5)

mosque_list = Listbox(window, width=85, height=18, bg="#f4fff6", fg="#204b3d", font=("Arial", 10))
mosque_list.grid(row=1, column=3, rowspan=12, padx=25, pady=10)

scrollbar = Scrollbar(window, orient=VERTICAL, command=mosque_list.yview)
scrollbar.grid(row=1, column=4, rowspan=12, sticky="ns")
mosque_list.config(yscrollcommand=scrollbar.set)

Button(window, text="Display All", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=display_all).grid(row=8, column=0, pady=6, columnspan=1)

Button(window, text="Search", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=search).grid(row=8, column=1, pady=6)

Button(window, text="Add Entry", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=add_entry).grid(row=9, column=0, pady=6)

Button(window, text="Delete Entry", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=delete_entry).grid(row=9, column=1, pady=6)

Button(window, text="Update Entry", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=update_entry).grid(row=10, column=0, pady=6)

Button(window, text="Display on Map", width=22, bg=button_color, fg="white", font=("Arial", 10, "bold"), 
       command=display_map).grid(row=10, column=1, pady=6)

Button(window, text="Help", width=22, bg="#b56576", fg="white", font=("Arial", 10, "bold"), 
       command=show_instructions).grid(row=11, column=0, pady=6)

Button(window, text="Exit", width=22, bg="#b56576", fg="white", font=("Arial", 10, "bold"), 
       command=window.quit).grid(row=11, column=1, pady=6)

window.mainloop()
