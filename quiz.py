import re

def quiz(pytania):
    for i, p in enumerate(pytania):
        print(f"\nPytanie {i+1}: {p['question']}")
        for idx, opcja in enumerate(p['options']):
            print(f"  {idx+1}. {opcja}")

        while True:
            try:
                wybor = int(input("Twój wybór (numer odpowiedzi): "))
                if 1 <= wybor <= len(p['options']):
                    break
                else:
                    print("Podaj poprawny numer.")
            except ValueError:
                print("To nie jest liczba.")

        if wybor - 1 == p['answer']:
            print("Dobra odpowiedź! ✅")
        else:
            print(f"Błąd. Poprawna odpowiedź to: {p['options'][p['answer']]} ❌")

if __name__ == "__main__":
    sciezka = input("Podaj nazwę pliku z quizem (np. quiz.md): ")
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

    quiz(pytania)