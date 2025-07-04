import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import re

STATE_FILE = "quiz_state.json"

def parse_questions(file_path):
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n### ', content)
    questions = []

    for block in blocks:
        lines = block.strip().split('\n')
        if not lines or not lines[0].strip():
            continue
        question = lines[0].lstrip('# ').strip()
        options = []
        correct_indices = []

        for i, line in enumerate(lines[1:]):
            m = re.match(r'- \[( |x)\] (.+)', line)
            if m:
                is_checked = m.group(1) == 'x'
                option_text = m.group(2)
                options.append(option_text)
                if is_checked:
                    correct_indices.append(i)

        questions.append({
            "question": question,
            "options": options,
            "answer": correct_indices
        })

    return questions

class QuizApp:
    def __init__(self, root, questions):
        self.root = root
        self.root.title("Azure Quiz GUI")
        self.root.configure(bg="#eee")
        self.original_questions = questions
        self.questions = []
        self.reset_question_order()
        self.load_state()

        self.var_checks = []
        self.checkboxes = []

        self.stats_label = tk.Label(root, text="", font=("Arial", 12), bg="#eee")
        self.stats_label.pack(pady=5)

        self.question_label = tk.Label(root, text="", font=("Arial", 16, "bold"), wraplength=1000, justify="center", bg="#eee")
        self.question_label.pack(pady=10)

        self.progress_canvas = tk.Canvas(root, height=20, bg="#eee", highlightthickness=0)
        self.progress_canvas.pack(fill="x", padx=20, pady=10)

        self.options_frame = tk.Frame(root, bg="#eee")
        self.options_frame.pack(pady=10)

        self.submit_btn = tk.Button(root, text="Submit", command=self.check_answer, bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=5)
        self.submit_btn.pack(pady=5)

        self.reset_btn = tk.Button(root, text="Reset Quiz", command=self.reset_quiz, bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=5)
        self.reset_btn.pack(pady=5)

        self.load_question()

    def reset_question_order(self):
        self.questions = self.original_questions[:]
        random.shuffle(self.questions)

    def reset_quiz(self):
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)

        self.index = 0
        self.correct = 0
        self.incorrect = 0
        self.answered = 0
        self.reset_question_order()
        self.load_question()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.index = data.get("index", 0)
                self.correct = data.get("correct", 0)
                self.incorrect = data.get("incorrect", 0)
                self.answered = data.get("answered", 0)
        else:
            self.index = 0
            self.correct = 0
            self.incorrect = 0
            self.answered = 0

    def save_state(self):
        data = {
            "index": self.index,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "answered": self.answered
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_question(self):
        if self.index >= len(self.questions):
            messagebox.showinfo("Quiz", "End of quiz!")
            return

        self.clear_widgets()
        self.update_stats()
        self.draw_progress()

        current_q = self.questions[self.index]
        self.question_label.config(text=current_q["question"])

        self.var_checks = []
        self.checkboxes = []
        self.correct_count = len(current_q["answer"])

        for i, option in enumerate(current_q["options"]):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.options_frame, text=option, variable=var, font=("Arial", 12), anchor="w", bg="#eee",
                                command=lambda idx=i: self.handle_single_select(idx))
            cb.pack(anchor="w")
            self.var_checks.append(var)
            self.checkboxes.append(cb)

    def handle_single_select(self, idx):
        if self.correct_count == 1:
            for i, var in enumerate(self.var_checks):
                if i != idx:
                    var.set(0)

    def clear_widgets(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def update_stats(self):
        self.stats_label.config(text=f"Correct: {self.correct}    Incorrect: {self.incorrect}    Answered: {self.answered}")

    def draw_progress(self):
        self.progress_canvas.delete("all")
        total = max(self.answered, 1)
        width = self.progress_canvas.winfo_width()
        correct_width = int((self.correct / total) * width)
        incorrect_width = int((self.incorrect / total) * width)

        self.progress_canvas.create_rectangle(0, 0, correct_width, 20, fill="green", outline="")
        self.progress_canvas.create_rectangle(correct_width, 0, correct_width + incorrect_width, 20, fill="red", outline="")
        self.root.update_idletasks()

    def check_answer(self):
        selected = [i for i, var in enumerate(self.var_checks) if var.get() == 1]
        correct = self.questions[self.index]["answer"]

        if sorted(selected) == sorted(correct):
            self.correct += 1
        else:
            self.incorrect += 1
            correct_answers = ", ".join([self.questions[self.index]["options"][i] for i in correct])
            messagebox.showinfo("Correct Answer", f"The correct answer(s): {correct_answers}")

        self.answered += 1
        self.index += 1
        self.save_state()
        self.load_question()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python quiz_gui.py <path_to_markdown_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    questions = parse_questions(file_path)

    root = tk.Tk()
    app = QuizApp(root, questions)
    root.mainloop()
