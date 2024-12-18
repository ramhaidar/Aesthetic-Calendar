import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkinter.scrolledtext import ScrolledText
from time import strftime

activities = {}


def view_activity_details(event=None):
    """Display detailed view of selected activity."""
    detail_window = tk.Toplevel()
    detail_window.wm_title("Activity Details")
    selected_item = activity_tree.focus()
    selected_index = activity_tree.item(selected_item)["text"]
    selected_activity = activities[current_date][selected_index]

    title = tk.StringVar(value=selected_activity["title"])

    tk.Label(detail_window, text="Time").grid(row=0, column=0, sticky="N")
    tk.Label(detail_window, text=f"{current_date} | {selected_activity['time']}").grid(
        row=0, column=1, sticky="E"
    )
    tk.Label(detail_window, text="Activity").grid(row=1, column=0, sticky="N")
    tk.Entry(detail_window, state="disabled", textvariable=title).grid(
        row=1, column=1, sticky="E"
    )
    tk.Label(detail_window, text="Description").grid(row=2, column=0, sticky="N")
    description = ScrolledText(detail_window, width=12, height=5)
    description.grid(row=2, column=1, sticky="E")
    description.insert(tk.INSERT, selected_activity["description"])
    description.configure(state="disabled")


def load_activities():
    """Load activities from file. Create file if it doesn't exist."""
    global activities
    try:
        with open("activities.dat", "r") as file:
            activities = eval(file.read())
    except FileNotFoundError:
        # Create empty activities file if it doesn't exist
        activities = {}
        save_activities()
    except Exception as e:
        print(f"Error loading activities: {e}")
        activities = {}
    update_activity_list()


def save_activities():
    """Save activities to file."""
    with open("activities.dat", "w") as file:
        file.write(str(activities))


def delete_activity():
    """Delete selected activity with error handling."""
    selected_item = activity_tree.focus()
    if not selected_item:
        return  # Do nothing if no item is selected

    current_date = str(calendar.selection_get())
    if current_date not in activities:
        return  # Do nothing if no activities exist for this date

    try:
        activities[current_date].pop(activity_tree.item(selected_item)["text"])
        update_activity_list()
    except (KeyError, IndexError) as e:
        print(f"Error deleting activity: {e}")

    # If the date becomes empty after deletion, remove it from activities
    if not activities[current_date]:
        del activities[current_date]


def update_activity_list(event=None):
    """Update the list of activities displayed in the treeview."""
    for i in activity_tree.get_children():
        activity_tree.delete(i)
    current_date = str(calendar.selection_get())
    if current_date in activities:
        for i in range(len(activities[current_date])):
            activity_tree.insert(
                "",
                "end",
                text=i,
                values=(
                    activities[current_date][i]["time"],
                    activities[current_date][i]["title"],
                ),
            )


def add_activity(window, date, hour, minute, title, description):
    """Add new activity to the calendar."""
    new_activity = {
        "time": f"{hour.get():02d}:{minute.get():02d}",
        "title": title.get(),
        "description": description.get("1.0", tk.END),
    }
    if date in activities:
        activities[date].append(new_activity)
    else:
        activities[date] = [new_activity]
    window.destroy()
    update_activity_list()


def create_activity_form():
    """Create a form to add a new activity."""
    form_window = tk.Toplevel()
    form_window.wm_title("Add Activity")
    hour = tk.IntVar(value=10)
    minute = tk.IntVar(value=30)
    title = tk.StringVar(value="")
    tk.Label(form_window, text="Time", foreground="Navy").grid(row=0, column=0)
    tk.Spinbox(form_window, from_=0, to=23, textvariable=hour, width=3).grid(
        row=0, column=1
    )
    tk.Spinbox(form_window, from_=0, to=59, textvariable=minute, width=3).grid(
        row=0, column=2
    )
    tk.Label(form_window, text="Activity", foreground="Navy").grid(row=1, column=0)
    tk.Entry(form_window, textvariable=title).grid(row=1, column=1, columnspan=2)
    tk.Label(form_window, text="Description", foreground="Navy").grid(row=2, column=0)
    description = ScrolledText(form_window, width=12, height=5)
    description.grid(row=2, column=1, columnspan=2, rowspan=4)
    current_date = str(calendar.selection_get())
    tk.Button(
        form_window,
        text="Add",
        command=lambda: add_activity(
            form_window, current_date, hour, minute, title, description
        ),
        background="#0A1E29",
        foreground="white",
    ).grid(row=6, column=0)


def update_window_title():
    """Update window title with current time and date."""
    current_time = strftime("%H:%M")
    current_date = str(calendar.selection_get())
    root.title(f"{current_date} | {current_time} | Activity Calendar")
    root.after(1000, update_window_title)


# Main window setup
root = tk.Tk()
style = ttk.Style()
style.configure("Treeview", rowheight=16)

# Calendar widget setup
calendar = Calendar(
    root,
    font="Arial 14",
    selectmode="day",
    locale="en_US",
    cursor="hand2",
    headersbackground="orange",
    normalbackground="#01C7C6",
    background="#0A1E29",
    foreground="#ffffff",
    normalforeground="#0A1E29",
    headersforeground="#0A1E29",
    weekendbackground="#0A1E29",
    weekendforeground="#ffffff",
)
calendar.grid(row=0, column=0, sticky="N", rowspan=7)
calendar.bind("<<CalendarSelected>>", update_activity_list)
current_date = str(calendar.selection_get())

# Treeview widget setup
activity_tree = ttk.Treeview(root)
activity_tree.grid(row=0, column=1, sticky="WNE", rowspan=4, columnspan=2)
scroll_bar = tk.Scrollbar(root, orient="vertical", command=activity_tree.yview)
scroll_bar.grid(row=0, column=3, sticky="ENS", rowspan=4)
activity_tree.configure(yscrollcommand=scroll_bar.set)
activity_tree.bind("<Double-1>", view_activity_details)
activity_tree["columns"] = ("1", "2")
activity_tree["show"] = "headings"
activity_tree.column("1", width=100)
activity_tree.heading("1", text="Time")
activity_tree.heading("2", text="Activity")

# Buttons setup
btn_add = tk.Button(
    root,
    text="Add",
    width=20,
    command=create_activity_form,
    font="Garamond 10",
    background="#01C7C6",
)
btn_add.grid(row=4, column=1, sticky="N")

btn_delete = tk.Button(
    root,
    text="Delete",
    width=20,
    command=delete_activity,
    font="Garamond 10",
    background="#01C7C6",
)
btn_delete.grid(row=4, column=2, sticky="N")

btn_load = tk.Button(
    root,
    text="Load",
    width=20,
    command=load_activities,
    font="Garamond 10",
    background="#0A1E29",
    foreground="white",
)
btn_load.grid(row=6, column=1, sticky="S")

btn_save = tk.Button(
    root,
    text="Save",
    width=20,
    command=save_activities,
    font="Garamond 10",
    background="#0A1E29",
    foreground="white",
)
btn_save.grid(row=6, column=2, sticky="S")

# Initialize window title updates
update_window_title()
root.mainloop()
