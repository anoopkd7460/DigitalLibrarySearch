import tkinter as tk
from tkinter import ttk
from data import documents
from search import boolean_search, rank_documents
from evaluation import evaluate

def start_app():

    def search():
        query = entry.get()

        # Clear old results
        for widget in result_frame.winfo_children():
            widget.destroy()

        if not query.strip():
            show_message("⚠️ Enter a query")
            return

        # Boolean + Ranking
        filtered = boolean_search(query, documents)
        ranked = rank_documents(query, filtered)

        if not ranked:
            show_message("❌ No results found")
            return

        # Transition Effect (delayed row rendering)
        for i, (doc, score) in enumerate(ranked):
            root.after(i * 120, lambda d=doc, s=score:
                       create_row(d, s))

        # Evaluation after results
        relevant = filtered

        precision, recall, f1 = evaluate(
            [doc for doc, _ in ranked],
            relevant
        )

        root.after(len(ranked) * 120, lambda:
                   show_evaluation(precision, recall, f1))


    def create_row(doc, score):
        row = tk.Frame(result_frame, bg="white")
        row.pack(fill="x", pady=2, padx=10)

        # Hover effect
        def on_enter(e):
            row.config(bg="#eaf2f8")

        def on_leave(e):
            row.config(bg="white")

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)

        # Book name 
        tk.Label(row, text=doc,
                 font=("Segoe UI", 11),
                 bg="white", fg="#2c3e50",
                 anchor="w").pack(side="left", padx=10, pady=5)

        # Score 
        tk.Label(row,
                 text=f"{score:.4f}",
                 font=("Segoe UI", 10, "bold"),
                 bg="white", fg="#27ae60",
                 anchor="e").pack(side="right", padx=10)


    def show_evaluation(p, r, f1):
        separator = tk.Frame(result_frame, height=2, bg="#dcdcdc")
        separator.pack(fill="x", pady=10, padx=10)

        tk.Label(result_frame, text="Evaluation Metrics",
                 font=("Segoe UI", 12, "bold"),
                 bg="#f4f6f7").pack(anchor="w", padx=12)

        tk.Label(result_frame, text=f"Precision: {p:.2f}",
                 bg="#f4f6f7", fg="#8e44ad").pack(anchor="w", padx=12)

        tk.Label(result_frame, text=f"Recall: {r:.2f}",
                 bg="#f4f6f7", fg="#8e44ad").pack(anchor="w", padx=12)

        tk.Label(result_frame, text=f"F1 Score: {f1:.2f}",
                 bg="#f4f6f7", fg="#8e44ad").pack(anchor="w", padx=12, pady=(0,5))


    def show_message(msg):
        tk.Label(result_frame, text=msg,
                 fg="red",
                 bg="#f4f6f7",
                 font=("Segoe UI", 11)).pack(pady=10)


    # MAIN WINDOW
    root = tk.Tk()
    root.title("College Digital Library")
    root.geometry("780x560")
    root.configure(bg="#f4f6f7")

    # TITLE
    tk.Label(root, text="College Digital Library Search",
             font=("Segoe UI", 18, "bold"),
             bg="#f4f6f7", fg="#2c3e50").pack(pady=15)

    # SEARCH BAR 
    top_frame = tk.Frame(root, bg="#f4f6f7")
    top_frame.pack(pady=10)

    inner = tk.Frame(top_frame, bg="#f4f6f7")
    inner.pack()

    entry = ttk.Entry(inner, width=40, font=("Segoe UI", 12))
    entry.grid(row=0, column=0, padx=6)

    tk.Button(inner,
              text="Search",
              font=("Segoe UI", 11, "bold"),
              bg="#1abc9c",
              fg="white",
              activebackground="#16a085",
              relief="flat",
              padx=18,
              pady=6,
              cursor="hand2",
              command=search).grid(row=0, column=1, padx=6)

    # SCROLLABLE AREA
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#f4f6f7", highlightthickness=0)
    scrollbar = tk.Scrollbar(container, command=canvas.yview)

    result_frame = tk.Frame(canvas, bg="#f4f6f7")

    result_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=result_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()
