# Gemini Project Coder - Asystent AI (v10.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gemini API](https://img.shields.io/badge/Google-Gemini%20API-orange)

**Gemini Project Coder** to zaawansowana aplikacja desktopowa (GUI), która łączy moc modeli Google Gemini z Twoimi lokalnymi plikami projektu. Narzędzie zostało stworzone z myślą o programistach (szczególnie pluginów Minecraft Spigot/Paper), aby ułatwić analizę kodu, refaktoryzację i naprawę błędów.

Pozwala na "rozmowę" z całym kodem źródłowym projektu, przesyłanie zrzutów ekranu i płynne przełączanie modeli AI.

## 🚀 Główne Funkcje

*   **📂 Skanowanie Projektu:** Wczytuje treść wszystkich plików kodu (`.java`, `.yml`, `.json` itp.) z wybranego folderu do pamięci AI.
*   **🧠 Obsługa Context Caching:** Automatycznie wykrywa duże projekty (>32k tokenów) i pozwala użyć funkcji Cache, co drastycznie obniża koszty API przy długich rozmowach.
*   **🔄 Hot-Swap Modeli:** Przełączaj się między modelami `Gemini 1.5 Flash`, `Pro` lub `Exp` w trakcie rozmowy, zachowując historię czatu.
*   **🖼️ Obsługa Obrazów:** Wklejaj zrzuty ekranu bezpośrednio ze schowka (CTRL+V), aby pokazać AI błędy w grze lub konsoli.
*   **💾 Menedżer Sesji:** Historia rozmów zapisuje się automatycznie. Możesz wrócić do starej rozmowy po kilku dniach i kontynuować pracę.
*   **🌍 Języki:** Przełącznik interfejsu PL / EN w czasie rzeczywistym.
*   **✨ Ulepszenia UX:** Kolorowanie składni, przyciski kopiowania kodu, menu kontekstowe pod prawym przyciskiem myszy (kopiuj/wklej/zaznacz).

## 🛠️ Instalacja

1.  **Pobierz repozytorium:**
    ```bash
    git clone https://github.com/twoj-nick/gemini-project-coder.git
    cd gemini-project-coder
    ```

2.  **Zainstaluj wymagane biblioteki:**
    ```bash
    pip install customtkinter google-generativeai Pillow
    ```

3.  **Uruchom aplikację:**
    ```bash
    python main.py
    ```

## 📖 Instrukcja Obsługi

1.  **Klucz API:** Wklej swój klucz Google Gemini API w panelu ustawień (Pobierz go za darmo w [Google AI Studio](https://aistudio.google.com/)).
2.  **Wybór Folderu:** Wybierz folder główny swojego projektu.
3.  **Skanowanie:** Kliknij **"1. 📂 Skanuj Projekt"**. Aplikacja przeanalizuje pliki.
    *   *Wskazówka: Dla dużych projektów włącz opcję "Context Caching", aby nie przesyłać kodu za każdym razem (oszczędność).*
4.  **Czat:** Wpisz pytanie lub wklej obrazek (CTRL+V) i wyślij.
5.  **Menu:** Kliknij prawym przyciskiem myszy na tekst w czacie, aby skopiować lub zaznaczyć treść.

## ⚙️ Wymagania

*   Python 3.10 lub nowszy
*   Klucz API Google AI Studio
*   Połączenie z internetem

## 📜 Licencja

[MIT](https://choosealicense.com/licenses/mit/)