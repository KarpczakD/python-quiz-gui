import tkinter as tk
from tkinter import messagebox
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

        # Statystyki na górze
        self.stats_label = tk.Label(master, text="", font=("Arial", 12), fg="blue")
        self.stats_label.pack(pady=5)

        self.question_label = tk.Label(master, text="", wraplength=400, font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.vars = []
        self.checkbuttons = []
        for i in range(6):
            var = tk.IntVar()
            cb = tk.Checkbutton(master, text="", variable=var, font=("Arial", 12))
            cb.pack(anchor='w')
            self.vars.append(var)
            self.checkbuttons.append(cb)

        self.submit_button = tk.Button(master, text="Sprawdź odpowiedź", command=self.check_answer)
        self.submit_button.pack(pady=20)

        self.update_stats()
        self.load_question()

    def update_stats(self):
        self.stats_label.config(text=f"Poprawne odpowiedzi: {self.score}    "
                                     f"Błędne odpowiedzi: {self.wrong}    "
                                     f"Udzielone odpowiedzi: {self.answered} / {len(self.pytania)}")

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
            self.checkbuttons[i].pack(anchor='w')
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
