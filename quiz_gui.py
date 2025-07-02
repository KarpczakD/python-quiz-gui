import tkinter as tk
from tkinter import font, messagebox
import random
import re


def wczytaj_pytania(plik_md):
    with open(plik_md, encoding='utf-8') as f:
        zawartosc = f.read()

    bloki = re.split(r'\n### ', zawartosc)
    pytania = []

    for blok in bloki:
        linie = blok.strip().split('\n')
        if not linie or not linie[0].strip():
            continue
        pytanie = linie[0].lstrip('# ').strip()
        Answered = []
        poprawne_idx = []

        for i, linia in enumerate(linie[1:]):
            m = re.match(r'- \[( |x)\] (.+)', linia)
            if m:
                zaznaczone = m.group(1) == 'x'
                tekst_odp = m.group(2)
                Answered.append(tekst_odp)
                if zaznaczone:
                    poprawne_idx.append(i)

        pytania.append({
            "question": pytanie,
            "options": Answered,
            "answers": poprawne_idx
        })

    random.shuffle(pytania)
    return pytania


class QuizApp:
    def __init__(self, master, pytania):
        self.master = master
        self.pytania = pytania
        self.index = 0
        self.score = 0
        self.wrong = 0
        self.answered = 0

        self.master.title("Quiz")
        self.master.geometry("700x500")
        self.master.configure(bg="#f0f4f8")

        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.question_font = font.Font(family="Arial", size=14)
        self.option_font = font.Font(family="Arial", size=12)

        self.master.columnconfigure(0, weight=1)

        # Statystyki
        self.stats_label = tk.Label(master, text="", font=("Helvetica", 12), fg="#333", bg="#f0f4f8", anchor="center", justify="center")
        self.stats_label.grid(row=0, column=0, pady=(10, 0), sticky="n")

        # Suwak
        self.score_var = tk.DoubleVar(value=0)
        self.score_slider = tk.Scale(master, variable=self.score_var, from_=0, to=100, orient="horizontal",
                                     length=400, state="disabled", bg="#f0f4f8",
                                     troughcolor="#a8c0ff", highlightthickness=0)
        self.score_slider.grid(row=1, column=0, pady=(0, 10), sticky="ew", padx=20)

        # Pytanie
        self.question_label = tk.Label(master, text="", wraplength=640, font=self.title_font,
                                       bg="#f0f4f8", fg="#222", justify="left")
        self.question_label.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Opcje
        self.options_frame = tk.Frame(master, bg="#f0f4f8")
        self.options_frame.grid(row=3, column=0, pady=10, sticky="ew", padx=20)
        self.options_frame.columnconfigure(0, weight=1)

        self.vars = []
        self.checkbuttons = []

        for i in range(6):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.options_frame, text="", variable=var, font=self.option_font,
                                bg="#ffffff", anchor='w', relief='groove', bd=2,
                                activebackground="#dbe9ff", padx=10, pady=5,
                                highlightthickness=0, selectcolor="#a8c0ff")
            cb.grid(row=i, column=0, sticky="ew", pady=3)
            self.vars.append(var)
            self.checkbuttons.append(cb)

        # Przycisk
        self.submit_button = tk.Button(master, text="Sprawdź odpowiedź", font=self.option_font,
                                       bg="#4a90e2", fg="white", activebackground="#357ABD",
                                       padx=10, pady=8, relief='flat', command=self.check_answer)
        self.submit_button.grid(row=4, column=0, pady=15, sticky="ew", padx=150)

        self.submit_button.bind("<Enter>", lambda e: self.submit_button.config(bg="#357ABD"))
        self.submit_button.bind("<Leave>", lambda e: self.submit_button.config(bg="#4a90e2"))

        self.master.bind("<Configure>", self.on_resize)

        self.update_stats()
        self.load_question()

    def on_resize(self, event):
        nowa_szerokosc = event.width - 40
        if nowa_szerokosc > 100:
            self.question_label.config(wraplength=nowa_szerokosc)

    def update_stats(self):
        procent = int((self.score / self.answered) * 100) if self.answered > 0 else 0
        self.stats_label.config(
            text=f"✅ Correct: {self.score}   ❌ Incorrect: {self.wrong}   🧠 Answered: {self.answered}"
        )
        self.score_var.set(procent)

    def load_question(self):
        if self.index >= len(self.pytania):
            messagebox.showinfo("Koniec quizu", f"Twój wynik: {self.score}/{self.answered}")
            self.master.quit()
            return

        pytanie = self.pytania[self.index]
        self.question_label.config(text=pytanie["question"])

        for i in range(len(self.checkbuttons)):
            if i < len(pytanie["options"]):
                self.checkbuttons[i].config(text=pytanie["options"][i], state="normal", bg="#ffffff")
                self.checkbuttons[i].grid()
                self.vars[i].set(0)
            else:
                self.checkbuttons[i].grid_remove()

    def check_answer(self):
        pytanie = self.pytania[self.index]
        selected = [i for i, var in enumerate(self.vars) if var.get() == 1]

        self.answered += 1

        if set(selected) == set(pytanie["answers"]):
            self.score += 1
            for i in selected:
                self.checkbuttons[i].config(bg="#b2f2bb")  # zielony
        else:
            self.wrong += 1
            for i in selected:
                self.checkbuttons[i].config(bg="#ffb3b3")  # czerwony
            for i in pytanie["answers"]:
                self.checkbuttons[i].config(bg="#b2f2bb")

        self.update_stats()
        self.submit_button.config(state="disabled")
        self.master.after(1500, self.nastepne_pytanie)

    def nastepne_pytanie(self):
        self.index += 1
        self.submit_button.config(state="normal")
        self.load_question()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Użycie: python quiz_gui.py <ścieżka_do_pliku_md>")
        sys.exit(1)

    sciezka = sys.argv[1]
    pytania = wczytaj_pytania(sciezka)

    root = tk.Tk()
    app = QuizApp(root, pytania)
    root.mainloop()
