import tkinter as tk
from tkinter import messagebox


def add_item(entry: tk.Entry, listbox: tk.Listbox, item_type: str) -> None:
	text = entry.get().strip()
	if not text:
		messagebox.showwarning("Entrada vacia", f"Escribe un {item_type} antes de agregar.")
		return

	listbox.insert(tk.END, text)
	entry.delete(0, tk.END)


def main() -> None:
	root = tk.Tk()
	root.title("Procesos y Tareas")
	root.geometry("600x380")

	root.columnconfigure(0, weight=1)
	root.columnconfigure(1, weight=1)
	root.rowconfigure(1, weight=1)

	procesos_label = tk.Label(root, text="Procesos", font=("Segoe UI", 12, "bold"))
	procesos_label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

	tareas_label = tk.Label(root, text="Tareas", font=("Segoe UI", 12, "bold"))
	tareas_label.grid(row=0, column=1, padx=12, pady=(12, 6), sticky="w")

	procesos_frame = tk.Frame(root)
	procesos_frame.grid(row=1, column=0, padx=12, pady=6, sticky="nsew")
	procesos_frame.columnconfigure(0, weight=1)
	procesos_frame.rowconfigure(1, weight=1)

	tareas_frame = tk.Frame(root)
	tareas_frame.grid(row=1, column=1, padx=12, pady=6, sticky="nsew")
	tareas_frame.columnconfigure(0, weight=1)
	tareas_frame.rowconfigure(1, weight=1)

	procesos_entry = tk.Entry(procesos_frame)
	procesos_entry.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")

	procesos_listbox = tk.Listbox(procesos_frame)
	procesos_listbox.grid(row=1, column=0, padx=(0, 6), pady=0, sticky="nsew")

	add_proceso_btn = tk.Button(
		procesos_frame,
		text="Agregar",
		command=lambda: add_item(procesos_entry, procesos_listbox, "proceso"),
	)
	add_proceso_btn.grid(row=0, column=1, pady=(0, 6), sticky="ew")

	tareas_entry = tk.Entry(tareas_frame)
	tareas_entry.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")

	tareas_listbox = tk.Listbox(tareas_frame)
	tareas_listbox.grid(row=1, column=0, padx=(0, 6), pady=0, sticky="nsew")

	add_tarea_btn = tk.Button(
		tareas_frame,
		text="Agregar",
		command=lambda: add_item(tareas_entry, tareas_listbox, "tarea"),
	)
	add_tarea_btn.grid(row=0, column=1, pady=(0, 6), sticky="ew")

	root.mainloop()


if __name__ == "__main__":
	main()
