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

        self.var = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):  # załóżmy max 4 odpowiedzi
            rb = tk.Radiobutton(master, text="", variable=self.var, value=i, font=("Arial", 12))
            rb.pack(anchor='w')
            self.radio_buttons.append(rb)

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
        self.var.set(-1)  # odznacz wszystkie

        for i, opcja in enumerate(p['options']):
            self.radio_buttons[i].config(text=opcja, state='normal')
            self.radio_buttons[i].pack(anchor='w')
        # ukryj nadmiarowe przyciski, jeśli mniej niż 4 odpowiedzi
        for i in range(len(p['options']), 4):
            self.radio_buttons[i].pack_forget()

    def check_answer(self):
        wybor = self.var.get()
        if wybor == -1:
            messagebox.showwarning("Uwaga", "Wybierz odpowiedź!")
            return

        p = self.pytania[self.index]
        if wybor == p['answer']:
            self.score += 1
            messagebox.showinfo("Dobrze!", "Dobra odpowiedź! ✅")
        else:
            poprawna = p['options'][p['answer']]
            messagebox.showinfo("Źle", f"Błędna odpowiedź! Poprawna to: {poprawna} ❌")

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
        poprawna_idx = None

        for i, linia in enumerate(linie[1:]):
            m = re.match(r'- \[( |x)\] (.+)', linia)
            if m:
                zaznaczone = m.group(1) == 'x'
                tekst_odp = m.group(2)
                odpowiedzi.append(tekst_odp)
                if zaznaczone:
                    poprawna_idx = i

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
