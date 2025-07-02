import tkinter as tk
from tkinter import messagebox, font
import re
import random

class QuizApp:
    def __init__(self, master, pytania):
        self.master = master
        self.pytania = pytania
        self.index = 0
        self.score = 0
        self.wrong = 0
        self.answered = 0

        self.master.title("Quiz")
        self.master.geometry("500x450")
        self.master.configure(bg="#f0f4f8")

        # Czcionki
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.question_font = font.Font(family="Arial", size=14)
        self.option_font = font.Font(family="Arial", size=12)

        # Ramka na statystyki
        stats_frame = tk.Frame(master, bg="#f0f4f8")
        stats_frame.pack(pady=10)

        self.stats_label = tk.Label(stats_frame, text="", font=("Helvetica", 12), fg="#333", bg="#f0f4f8")
        self.stats_label.pack()

        # Ramka na pytanie
        question_frame = tk.Frame(master, bg="#f0f4f8", padx=10, pady=10)
        question_frame.pack(fill='x')

        self.question_label = tk.Label(question_frame, text="", wraplength=460, font=self.title_font, bg="#f0f4f8", fg="#222")
        self.question_label.pack()

        # Ramka na odpowiedzi
        self.options_frame = tk.Frame(master, bg="#f0f4f8")
        self.options_frame.pack(pady=10, fill='x')

        self.vars = []
        self.checkbuttons = []

        for i in range(6):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.options_frame, text="", variable=var, font=self.option_font,
                                bg="#ffffff", anchor='w', relief='groove', bd=2,
                                activebackground="#dbe9ff", padx=10, pady=5,
                                highlightthickness=0, selectcolor="#a8c0ff")
            cb.pack(fill='x', pady=3, padx=20)
            self.vars.append(var)
            self.checkbuttons.append(cb)

        # Przycisk
        self.submit_button = tk.Button(master, text="Sprawdź odpowiedź", font=self.option_font,
                                       bg="#4a90e2", fg="white", activebackground="#357ABD",
                                       padx=10, pady=8, relief='flat', command=self.check_answer)
        self.submit_button.pack(pady=15)

        # Efekt hover na przycisku
        self.submit_button.bind("<Enter>", lambda e: self.submit_button.config(bg="#357ABD"))
        self.submit_button.bind("<Leave>", lambda e: self.submit_button.config(bg="#4a90e2"))

        self.update_stats()
        self.load_question()

    def update_stats(self):
        self.stats_label.config(text=f"Poprawne: {self.score}    Błędne: {self.wrong}    Odpowiedzi: {self.answered} / {len(self.pytania)}")

    def load_question(self):
        if self.index >= len(self.pytania):
            messagebox.showinfo("Koniec quizu", f"Twój wynik: {self.score} / {len(self.pytania)}")
            self.master.quit()
            return

        p = self.pytania[self.index]
        self.question_label.config(text=f"Pytanie {self.index+1}: {p['question']}")

        for var in self.vars:
            var.set(0)

        for i, opcja in enumerate(p['options']):
            self.checkbuttons[i].config(text=opcja, state='normal')
            self.checkbuttons[i].pack(fill='x', pady=3, padx=20)
        for i in range(len(p['options']), 6):
            self.checkbuttons[i].pack_forget()

        self.update_stats()

    def check_answer(self):
        selected = [i for i, var in enumerate(self.vars) if var.get() == 1]
        if not selected:
            messagebox.showwarning("Uwaga", "Zaznacz przynajmniej jedną odpowiedź!")
            return

        p = self.pytania[self.index]
        correct = p['answer']

        self.answered += 1
        if set(selected) == set(correct):
            self.score += 1
            messagebox.showinfo("Dobrze!", "Dobra odpowiedź! ✅")
        else:
            self.wrong += 1
            poprawne_odp = ", ".join([p['options'][i] for i in correct])
            messagebox.showinfo("Źle", f"Błędna odpowiedź! Poprawne odpowiedzi to: {poprawne_odp} ❌")

        self.index += 1
        self.load_question()


def wczytaj_pytania(sciezka):
    with open(sciezka, encoding='utf-8') as f:
        zawartosc = f.read()
    bloki = re.split(r'\n### ', zawartosc)
    pytania = []

    for blok in bloki:
        linie = blok.strip().split('\n')
        if not linie[0].strip():
            continue
        pytanie = linie[0].lstrip('# ').strip()
        odpowiedzi = []
        poprawna_idx = []

        for i, linia in enumerate(linie[1:]):
            m = re.match(r'- \[( |x)\] (.+)', linia)
            if m:
                zaznaczone = m.group(1) == 'x'
                tekst_odp = m.group(2)
                odpowiedzi.append(tekst_odp)
                if zaznaczone:
                    poprawna_idx.append(i)

        pytania.append({
            "question": pytanie,
            "options": odpowiedzi,
            "answer": poprawna_idx
        })
    return pytania


if __name__ == "__main__":
    import sys
    import random

    if len(sys.argv) < 2:
        print("Użycie: python quiz_gui.py quiz.md")
        sys.exit(1)

    pytania = wczytaj_pytania(sys.argv[1])
    random.shuffle(pytania)

    root = tk.Tk()
    app = QuizApp(root, pytania)
    root.mainloop()
