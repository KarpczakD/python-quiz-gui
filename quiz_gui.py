import tkinter as tk
from tkinter import ttk, messagebox
import re
import random

class QuizApp:
    def __init__(self, master, questions):
        self.master = master
        self.master.title("Azure AZ-900 Quiz GUI")
        self.master.geometry("900x600")

        self.questions = questions
        random.shuffle(self.questions)
        self.current_question_index = 0

        self.correct = 0
        self.incorrect = 0
        self.answered = 0

        self.option_vars = []
        self.option_widgets = []
        self.multiselect = False
        self.selected_var = None

        self.style = ttk.Style()
        self.style.configure("Custom.TCheckbutton",
                             font=("Arial", 12),
                             foreground="#333",
                             background="#000000")
        self.style.map("Custom.TCheckbutton",
                       foreground=[('selected', "#000000")],
                       background=[('selected', "#080808")])

        self.style.configure("Submit.TButton",
                             font=("Arial", 14, 'bold'),
                             foreground="white",
                             background="#212224")
        self.style.map("Submit.TButton",
                       background=[('active', "#111111"), ('!disabled', "#000000")])

        self.stats_label = ttk.Label(master, text="", font=("Arial", 14))
        self.stats_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")
        self.stats_label.config(anchor="center")

        self.progress = tk.IntVar()
        self.progress_bar = ttk.Scale(master, variable=self.progress, from_=0, to=len(self.questions),
                                     orient="horizontal", length=700, state="disabled")
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=20, sticky="ew")

        self.question_label = ttk.Label(master, text="", wraplength=850, font=("Arial", 18), justify="left")
        self.question_label.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        self.options_frame = ttk.Frame(master)
        self.options_frame.grid(row=3, column=0, columnspan=3, padx=40, sticky="nsew")
        master.grid_rowconfigure(3, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)

        self.submit_button = ttk.Button(master, text="Submit Answer", style="Submit.TButton", command=self.submit_answer)
        self.submit_button.grid(row=4, column=1, pady=20)

        self.show_question()

    def show_question(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_vars.clear()
        self.option_widgets.clear()
        self.selected_var = None

        if self.current_question_index >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current_question_index]
        self.question_label.config(text=q["question"])

        if not isinstance(q["answer"], list):
            q["answer"] = [q["answer"]]

        correct_count = len(q["answer"])
        self.multiselect = correct_count > 1

        if self.multiselect:
            for i, option in enumerate(q["options"]):
                var = tk.IntVar()
                cb = ttk.Checkbutton(self.options_frame,
                                     text=option,
                                     variable=var,
                                     style="Custom.TCheckbutton")
                cb.grid(row=i, column=0, sticky="w", pady=5)
                self.option_vars.append(var)
                self.option_widgets.append(cb)
        else:
            self.selected_var = tk.IntVar(value=-1)
            for i, option in enumerate(q["options"]):
                rb = ttk.Radiobutton(self.options_frame,
                                     text=option,
                                     variable=self.selected_var,
                                     value=i)
                rb.grid(row=i, column=0, sticky="w", pady=5)
                self.option_widgets.append(rb)

        self.update_stats()
        self.progress.set(self.current_question_index)

    def submit_answer(self):
        if self.current_question_index >= len(self.questions):
            return

        q = self.questions[self.current_question_index]
        correct_answers = q["answer"]

        if self.multiselect:
            selected_indices = [i for i, var in enumerate(self.option_vars) if var.get() == 1]
            if not selected_indices:
                messagebox.showwarning("No answer selected", "Please select at least one answer before submitting.")
                return
        else:
            selected_index = self.selected_var.get()
            if selected_index == -1:
                messagebox.showwarning("No answer selected", "Please select an answer before submitting.")
                return
            selected_indices = [selected_index]

        if set(selected_indices) == set(correct_answers):
            messagebox.showinfo("Correct!", "Your answer is correct.")
            self.correct += 1
        else:
            correct_text = ", ".join([q["options"][i] for i in correct_answers])
            messagebox.showinfo("Incorrect", f"Your answer is incorrect.\nCorrect answer(s): {correct_text}")
            self.incorrect += 1

        self.answered += 1
        self.current_question_index += 1
        self.show_question()

    def update_stats(self):
        text = f"Correct: {self.correct}    Incorrect: {self.incorrect}    Answered: {self.answered}"
        self.stats_label.config(text=text, anchor="center")

    def end_quiz(self):
        self.question_label.config(text="Quiz completed!")
        self.options_frame.destroy()
        self.submit_button.config(state="disabled")
        self.progress.set(len(self.questions))
        self.update_stats()
        messagebox.showinfo("Quiz Finished", f"You answered {self.answered} questions.\n"
                                             f"Correct: {self.correct}\n"
                                             f"Incorrect: {self.incorrect}")

def parse_markdown(filepath):
    with open(filepath, encoding='utf-8') as f:
        zawartosc = f.read()

    bloki = re.split(r'\n### ', zawartosc)
    pytania = []

    for blok in bloki:
        linie = blok.strip().split('\n')
        if not linie[0].strip():
            continue
        pytanie = linie[0].lstrip('# ').strip()
        odpowiedzi = []
        poprawne_idx = []

        for i, linia in enumerate(linie[1:]):
            m = re.match(r'- \[( |x)\] (.+)', linia)
            if m:
                zaznaczone = m.group(1) == 'x'
                tekst_odp = m.group(2)
                odpowiedzi.append(tekst_odp)
                if zaznaczone:
                    poprawne_idx.append(i)

        pytania.append({
            "question": pytanie,
            "options": odpowiedzi,
            "answer": poprawne_idx
        })
    return pytania

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python quiz_gui.py path/to/quiz.md")
        sys.exit(1)

    questions = parse_markdown(sys.argv[1])

    root = tk.Tk()
    app = QuizApp(root, questions)
    root.mainloop()
