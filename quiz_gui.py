import tkinter as tk
from tkinter import messagebox
import random
import re
import os
import json

# --- Statystyki ---
def load_stats():
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f:
            return json.load(f)
    return {"correct": 0, "incorrect": 0, "answered": 0}

def save_stats(stats):
    with open("stats.json", "w") as f:
        json.dump(stats, f)

# --- Parser markdown ---
def load_questions_from_md(file_path):
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n### ', content)
    questions = []

    for block in blocks:
        lines = block.strip().split('\n')
        if not lines or not lines[0].strip():
            continue
        question_text = lines[0].lstrip('# ').strip()
        options = []
        correct_indices = []

        for i, line in enumerate(lines[1:]):
            m = re.match(r'- \[( |x)\] (.+)', line)
            if m:
                checked = m.group(1) == 'x'
                option_text = m.group(2)
                options.append(option_text)
                if checked:
                    correct_indices.append(i)

        questions.append({
            "question": question_text,
            "options": options,
            "answer": correct_indices
        })

    return questions

# --- GUI ---
class QuizApp:
    def __init__(self, root, questions):
        self.root = root
        self.root.title("Quiz App")
        self.questions = random.sample(questions, len(questions))  # losowe pytania
        self.current = 0
        self.selected = []
        self.stats = load_stats()

        self.question_label = tk.Label(root, text="", wraplength=600, justify="center", font=("Arial", 14), anchor="center")
        self.question_label.pack(pady=20, fill="x")

        self.stats_label = tk.Label(root, text="", font=("Arial", 12))
        self.stats_label.pack()

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.chart_canvas = tk.Canvas(root, height=20)
        self.chart_canvas.pack(pady=10, fill="x")

        self.submit_btn = tk.Button(root, text="Submit", command=self.submit_answer, bg="#4CAF50", fg="white", padx=10, pady=5)
        self.submit_btn.pack(pady=10)

        self.show_question()

    def show_question(self):
        self.clear_options()
        question = self.questions[self.current]
        self.question_label.config(text=question["question"])

        self.selected = [tk.IntVar() for _ in question["options"]]
        self.checkbuttons = []

        for i, option in enumerate(question["options"]):
            cb = tk.Checkbutton(self.frame, text=option, variable=self.selected[i], font=("Arial", 12), anchor="w", wraplength=550)
            cb.pack(anchor="w", fill="x")
            self.checkbuttons.append(cb)

        self.update_stats_labels()
        self.draw_chart()

    def submit_answer(self):
        selected_indices = [i for i, var in enumerate(self.selected) if var.get()]
        correct_indices = self.questions[self.current]["answer"]

        self.stats["answered"] += 1
        if set(selected_indices) == set(correct_indices):
            self.stats["correct"] += 1
            messagebox.showinfo("Correct", "✅ Correct answer!")
        else:
            self.stats["incorrect"] += 1
            correct_text = "\n".join([self.questions[self.current]["options"][i] for i in correct_indices])
            messagebox.showerror("Incorrect", f"❌ Incorrect answer.\nCorrect answer(s):\n{correct_text}")

        save_stats(self.stats)

        self.current = (self.current + 1) % len(self.questions)
        self.show_question()

    def clear_options(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def update_stats_labels(self):
        self.stats_label.config(
            text=f"Correct: {self.stats['correct']}    Incorrect: {self.stats['incorrect']}    Answered: {self.stats['answered']}",
            anchor="center"
        )

    def draw_chart(self):
        self.chart_canvas.delete("all")
        total = max(1, self.stats["answered"])
        width = self.chart_canvas.winfo_width()
        if width == 1: width = 600  # fallback

        correct_width = int((self.stats["correct"] / total) * width)
        incorrect_width = int((self.stats["incorrect"] / total) * width)

        self.chart_canvas.create_rectangle(0, 0, correct_width, 20, fill="green")
        self.chart_canvas.create_rectangle(correct_width, 0, correct_width + incorrect_width, 20, fill="red")


if __name__ == "__main__":
    import tkinter.filedialog as fd
    path = fd.askopenfilename(title="Select a quiz .md file", filetypes=[("Markdown files", "*.md")])
    if not path:
        print("No file selected.")
        exit()

    questions = load_questions_from_md(path)

    root = tk.Tk()
    app = QuizApp(root, questions)
    root.mainloop()
