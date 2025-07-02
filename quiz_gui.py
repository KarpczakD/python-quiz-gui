import tkinter as tk
from tkinter import messagebox
import re

class QuizApp:
    def __init__(self, master, pytania):
        self.master = master
        self.pytania = pytania
        self.index = 0
        self.score = 0

        self.master.title("Quiz")
        self.question_label = tk.Label(master, text="", wraplength=400, font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.vars = []  # lista zmiennych IntVar dla checkboxów
        self.checkbuttons = []

        # max 6 odpowiedzi, dajemy checkboxy
        for i in range(6):
            var = tk.IntVar()
            cb = tk.Checkbutton(master, text="", variable=var, font=("Arial", 12))
            cb.pack(anchor='w')
            self.vars.append(var)
            self.checkbuttons.append(cb)

        self.submit_button = tk.Button(master, text="Sprawdź odpowiedź", command=self.check_answer)
        self.submit_button.pack(pady=20)

        self.load_question()

    def load_question(self):
        if self.index >= len(self.pytania):
            messagebox.showinfo("Koniec quizu", f"Twój wynik: {self.score} / {len(self.pytania)}")
            self.master.quit()
            return

        p = self.pytania[self.index]
        self.question_label.config(text=f"Pytanie {self.index+1}: {p['question']}")

        for var in self.vars:
            var.set(0)  # odznacz wszystkie

        for i, opcja in enumerate(p['options']):
            self.checkbuttons[i].config(text=opcja, state='normal')
            self.checkbuttons[i].pack(anchor='w')
        for i in range(len(p['options']), 6):
            self.checkbuttons[i].pack_forget()

    def check_answer(self):
        selected = [i for i, var in enumerate(self.vars) if var.get() == 1]
        if not selected:
            messagebox.showwarning("Uwaga", "Zaznacz przynajmniej jedną odpowiedź!")
            return

        p = self.pytania[self.index]
        correct = p['answer']  # teraz lista indeksów

        # porównujemy zaznaczone odpowiedzi z listą poprawnych (bez dodatkowych ani brakujących)
        if set(selected) == set(correct):
            self.score += 1
            messagebox.showinfo("Dobrze!", "Dobra odpowiedź! ✅")
        else:
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
    if len(sys.argv) < 2:
        print("Użycie: python quiz_gui.py quiz.md")
        sys.exit(1)

    pytania = wczytaj_pytania(sys.argv[1])

    root = tk.Tk()
    app = QuizApp(root, pytania)
    root.mainloop()
