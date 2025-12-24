import customtkinter as ctk
import os
import threading
import json
import datetime
import re
import tkinter as tk
import google.generativeai as genai
from google.generativeai import caching
from tkinter import filedialog, messagebox, Menu
from PIL import Image, ImageGrab, ImageTk

# --- KONFIGURACJA UI ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- TŁUMACZENIA / TRANSLATIONS ---
TRANSLATIONS = {
    "en": {
        "title": "AI java Project Coder - v10.0 INT",
        "app_title": "PROJECT MANAGER\n(v10.0 International)",
        "api_label": "Google API Key:",
        "model_label": "Select Model:",
        "folder_label": "Project Folder:",
        "not_selected": "Not selected",
        "scan_btn": "1. 📂 Scan Project",
        "scan_processing": "Processing...",
        "tokens_project": "Project: 0",
        "tokens_chat": "Chat: 0",
        "cache_switch": "Use Context Caching",
        "save_chat": "💾 Save Chat",
        "load_chat": "📂 Load Chat",
        "status_waiting": "Waiting...",
        "status_ready": "Ready",
        "status_scanning": "Scanning...",
        "status_model_err": "Model Error",
        "status_swapped": "Model Swapped",
        "session_header": "SESSION HISTORY",
        "new_chat": "+ NEW CHAT",
        "input_placeholder": "Type here... (CTRL+V to paste image)",
        "send_btn": "Send ➤",
        "img_preview": " [Image Ready]",
        "img_remove": "❌ Remove",
        "sys_welcome": "WELCOME to v10.0!\n- Text Selection Enabled (Right-click to copy)\n- Images visible in chat\n- No auto-scroll on finish",
        "sys_scan_first": "⚠️ Scan the project first!",
        "sys_project_loaded": "✅ PROJECT LOADED ({count} files)",
        "sys_cache_active": "✅ CACHE ACTIVE (Cloud Project)",
        "sys_cache_too_small": "⚠️ Project too small for Cache (<32k). Cache disabled.",
        "sys_error": "❌ ERROR: {e}",
        "ctx_copy": "Copy",
        "ctx_paste": "Paste",
        "ctx_select_all": "Select All"
    },
    "pl": {
        "title": "AI java Project Coder - v10.0 INT",
        "app_title": "MENEDŻER PROJEKTU\n(v10.0 International)",
        "api_label": "Klucz API Google:",
        "model_label": "Wybierz Model:",
        "folder_label": "Folder Projektu:",
        "not_selected": "Nie wybrano",
        "scan_btn": "1. 📂 Skanuj Projekt",
        "scan_processing": "Przetwarzanie...",
        "tokens_project": "Projekt: 0",
        "tokens_chat": "Rozmowa: 0",
        "cache_switch": "Używaj Context Caching",
        "save_chat": "💾 Zapisz Czat",
        "load_chat": "📂 Wczytaj Czat",
        "status_waiting": "Oczekiwanie...",
        "status_ready": "Gotowy",
        "status_scanning": "Skanowanie...",
        "status_model_err": "Błąd Modelu",
        "status_swapped": "Zmieniono Model",
        "session_header": "HISTORIA SESJI",
        "new_chat": "+ NOWA ROZMOWA",
        "input_placeholder": "Napisz coś... (CTRL+V wkleja obraz)",
        "send_btn": "Wyślij ➤",
        "img_preview": " [Obraz Gotowy]",
        "img_remove": "❌ Usuń",
        "sys_welcome": "WITAJ W v10.0!\n- Zaznaczanie tekstu (Prawoklik by kopiować)\n- Podgląd obrazków w czacie\n- Brak auto-przewijania na końcu",
        "sys_scan_first": "⚠️ Najpierw zeskanuj projekt!",
        "sys_project_loaded": "✅ PROJEKT ZAŁADOWANY ({count} plików)",
        "sys_cache_active": "✅ CACHE AKTYWNY (Projekt w chmurze)",
        "sys_cache_too_small": "⚠️ Projekt za mały na Cache (<32k). Cache wyłączony.",
        "sys_error": "❌ BŁĄD: {e}",
        "ctx_copy": "Kopiuj",
        "ctx_paste": "Wklej",
        "ctx_select_all": "Zaznacz wszystko"
    }
}

class GeminiCoderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Język domyślny / Default Language
        self.lang_code = "en" 
        
        self.title(self.tr("title"))
        self.geometry("1400x950")
        
        self.project_context = ""
        self.chat_session = None
        self.cached_content = None
        self.current_image = None
        
        # Przechowywanie referencji do obrazków w czacie (żeby garbage collector ich nie usunął)
        self.image_refs = []
        
        # Zarządzanie sesjami
        self.sessions_dir = "saved_sessions"
        if not os.path.exists(self.sessions_dir): os.makedirs(self.sessions_dir)
        self.current_session_file = None

        # --- UKŁAD GŁÓWNY ---
        self.grid_columnconfigure(1, weight=0) # Panel Ustawień
        self.grid_columnconfigure(2, weight=1) # Czat
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL 1: LISTA SESJI =================
        self.session_panel = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#111827")
        self.session_panel.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_session_header = ctk.CTkLabel(self.session_panel, text=self.tr("session_header"), font=("Arial", 14, "bold"), text_color="gray")
        self.lbl_session_header.pack(pady=(20, 10))
        
        self.new_chat_btn = ctk.CTkButton(self.session_panel, text=self.tr("new_chat"), fg_color="#2563EB", command=self.reset_session)
        self.new_chat_btn.pack(padx=10, pady=10, fill="x")
        
        self.session_scroll = ctk.CTkScrollableFrame(self.session_panel, fg_color="transparent")
        self.session_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ================= PANEL 2: USTAWIENIA =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=1, sticky="nsew")

        # Language Switcher
        self.lang_btn = ctk.CTkButton(self.sidebar, text="PL / EN", width=60, fg_color="#4B5563", command=self.toggle_language)
        self.lang_btn.pack(anchor="e", padx=10, pady=5)

        self.lbl_app_title = ctk.CTkLabel(self.sidebar, text=self.tr("app_title"), font=("Arial", 16, "bold"))
        self.lbl_app_title.pack(pady=(5, 10))

        # API KEY
        self.lbl_api = ctk.CTkLabel(self.sidebar, text=self.tr("api_label"))
        self.lbl_api.pack(anchor="w", padx=20)
        self.api_entry = ctk.CTkEntry(self.sidebar, placeholder_text="API Key...", show="*")
        self.api_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # MODEL SELECTION
        self.lbl_model = ctk.CTkLabel(self.sidebar, text=self.tr("model_label"))
        self.lbl_model.pack(anchor="w", padx=20)
        self.model_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.model_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        default_models = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-2.0-flash-exp"]
        self.model_var = ctk.StringVar(value="gemini-1.5-flash-latest")
        self.model_combo = ctk.CTkComboBox(self.model_frame, variable=self.model_var, width=180, values=default_models, command=self.switch_model_live)
        self.model_combo.pack(side="left", fill="x", expand=True)
        self.refresh_models_btn = ctk.CTkButton(self.model_frame, text="🔄", width=30, command=self.fetch_available_models, fg_color="#4B5563")
        self.refresh_models_btn.pack(side="right", padx=(5, 0))

        # FOLDER
        self.lbl_folder = ctk.CTkLabel(self.sidebar, text=self.tr("folder_label"))
        self.lbl_folder.pack(anchor="w", padx=20)
        self.path_label = ctk.CTkLabel(self.sidebar, text=self.tr("not_selected"), text_color="gray", wraplength=200)
        self.path_label.pack(padx=20, pady=(0, 5))
        
        self.scan_btn = ctk.CTkButton(self.sidebar, text=self.tr("scan_btn"), command=self.select_folder, fg_color="#2da44e", hover_color="#2c974b")
        self.scan_btn.pack(fill="x", padx=20, pady=10)
        
        # CACHE SWITCH
        self.use_cache_var = ctk.BooleanVar(value=False)
        self.cache_switch = ctk.CTkSwitch(self.sidebar, text=self.tr("cache_switch"), variable=self.use_cache_var)
        self.cache_switch.pack(padx=20, pady=5)
        
        # TOKEN INFO
        self.token_frame = ctk.CTkFrame(self.sidebar, fg_color="#1F2937")
        self.token_frame.pack(fill="x", padx=20, pady=10)
        self.project_tokens_label = ctk.CTkLabel(self.token_frame, text=self.tr("tokens_project"), font=("Consolas", 12), text_color="#60A5FA")
        self.project_tokens_label.pack()
        self.chat_tokens_label = ctk.CTkLabel(self.token_frame, text=self.tr("tokens_chat"), font=("Consolas", 12), text_color="#F472B6")
        self.chat_tokens_label.pack(pady=(0,5))

        self.save_btn = ctk.CTkButton(self.sidebar, text=self.tr("save_chat"), command=self.save_chat_history)
        self.save_btn.pack(fill="x", padx=20, pady=(20, 5))
        self.load_btn = ctk.CTkButton(self.sidebar, text=self.tr("load_chat"), command=self.load_chat_history, fg_color="#D97706", hover_color="#B45309")
        self.load_btn.pack(fill="x", padx=20, pady=5)

        self.status_label = ctk.CTkLabel(self.sidebar, text=self.tr("status_ready"), font=("Arial", 12), text_color="gray")
        self.status_label.pack(padx=20, pady=20)

        # ================= PANEL 3: CZAT =================
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.chat_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="#0F172A")
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        # Podgląd obrazka (Preview)
        self.image_preview_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=0)
        self.image_preview_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.image_preview_label = ctk.CTkLabel(self.image_preview_frame, text="")
        self.image_preview_label.pack(side="left", padx=10)
        self.clear_image_btn = ctk.CTkButton(self.image_preview_frame, text="❌", width=80, fg_color="red", command=self.clear_image_preview)
        self.clear_image_btn.pack(side="left")
        self.image_preview_frame.grid_remove()

        self.input_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.input_frame, height=3, mode="indeterminate")
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.progress_bar.set(0)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text=self.tr("input_placeholder"), height=50, font=("Arial", 14))
        self.input_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", lambda event: self.start_chat_thread())
        self.input_entry.bind("<Control-v>", self.paste_from_clipboard)

        self.send_btn = ctk.CTkButton(self.input_frame, text=self.tr("send_btn"), width=120, height=50, command=self.start_chat_thread, font=("Arial", 14, "bold"))
        self.send_btn.grid(row=1, column=1)
        
        # Menu Kontekstowe (Prawoklik)
        self.create_context_menu()

        self.refresh_session_list()
        self.add_system_message(self.tr("sys_welcome"))

    # ================= JĘZYK / LANGUAGE =================
    
    def tr(self, key):
        """Tłumacz klucz na tekst / Translate key to text"""
        return TRANSLATIONS[self.lang_code].get(key, key)
    
    def toggle_language(self):
        self.lang_code = "pl" if self.lang_code == "en" else "en"
        self.update_ui_texts()
        
    def update_ui_texts(self):
        self.title(self.tr("title"))
        self.lbl_session_header.configure(text=self.tr("session_header"))
        self.new_chat_btn.configure(text=self.tr("new_chat"))
        self.lbl_app_title.configure(text=self.tr("app_title"))
        self.lbl_api.configure(text=self.tr("api_label"))
        self.lbl_model.configure(text=self.tr("model_label"))
        self.lbl_folder.configure(text=self.tr("folder_label"))
        
        if self.path_label.cget("text") in ["Not selected", "Nie wybrano"]:
            self.path_label.configure(text=self.tr("not_selected"))
            
        self.scan_btn.configure(text=self.tr("scan_btn"))
        self.cache_switch.configure(text=self.tr("cache_switch"))
        self.save_btn.configure(text=self.tr("save_chat"))
        self.load_btn.configure(text=self.tr("load_chat"))
        self.status_label.configure(text=self.tr("status_ready"))
        self.input_entry.configure(placeholder_text=self.tr("input_placeholder"))
        self.send_btn.configure(text=self.tr("send_btn"))
        self.clear_image_btn.configure(text=self.tr("img_remove"))
        
        # Aktualizacja liczników (tylko etykiety prefixu)
        proj_val = self.project_tokens_label.cget("text").split(":")[-1]
        chat_val = self.chat_tokens_label.cget("text").split(":")[-1]
        self.project_tokens_label.configure(text=f"{self.tr('tokens_project')}: {proj_val.strip()}")
        self.chat_tokens_label.configure(text=f"{self.tr('tokens_chat')}: {chat_val.strip()}")

    # ================= CONTEXT MENU (COPY/PASTE) =================
    
    def create_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label=self.tr("ctx_copy"), command=self.copy_selection)
        self.context_menu.add_command(label=self.tr("ctx_paste"), command=self.paste_to_entry)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self.tr("ctx_select_all"), command=self.select_all)

    def show_context_menu(self, event):
        # Pokazuje menu tam gdzie kursor myszy
        try:
            widget = event.widget
            widget.focus() # Ustawia focus na kliknięty element
            self.context_menu.entryconfigure(1, label=self.tr("ctx_copy")) # Odśwież język
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_selection(self):
        try:
            # Próbuje skopiować zaznaczenie z aktywnego widgetu
            widget = self.focus_get()
            if isinstance(widget, tk.Text): # CTkTextbox to tk.Text w środku
                text = widget.get("sel.first", "sel.last")
                self.clipboard_clear()
                self.clipboard_append(text)
            elif isinstance(widget, tk.Entry): # CTkEntry
                 text = widget.selection_get()
                 self.clipboard_clear()
                 self.clipboard_append(text)
        except: pass

    def paste_to_entry(self):
        try:
            widget = self.focus_get()
            if isinstance(widget, tk.Entry):
                widget.event_generate("<<Paste>>")
            elif isinstance(widget, tk.Text) and widget.cget("state") == "normal":
                widget.event_generate("<<Paste>>")
        except: pass

    def select_all(self):
        try:
            widget = self.focus_get()
            if isinstance(widget, tk.Text):
                widget.tag_add("sel", "1.0", "end")
            elif isinstance(widget, tk.Entry):
                widget.select_range(0, 'end')
        except: pass

    # ================= ZARZĄDZANIE SESJAMI =================
    
    def refresh_session_list(self):
        for widget in self.session_scroll.winfo_children(): widget.destroy()
        sessions = [f for f in os.listdir(self.sessions_dir) if f.endswith(".json")]
        sessions.sort(key=lambda x: os.path.getmtime(os.path.join(self.sessions_dir, x)), reverse=True)
        for sess in sessions:
            name = sess.replace(".json", "").replace("_", " ")[:20]
            btn = ctk.CTkButton(self.session_scroll, text=f"📄 {name}...", fg_color="transparent", border_width=1, border_color="#374151", anchor="w", command=lambda s=sess: self.load_session(s))
            btn.pack(fill="x", pady=2)

    def reset_session(self):
        self.chat_session = None
        self.current_session_file = None
        for widget in self.chat_scroll.winfo_children(): widget.destroy()
        self.add_system_message("--- NEW CHAT ---")
        if self.project_context: self.init_model_session()

    def auto_save_session(self):
        if not self.chat_session or not self.chat_session.history: return
        if not self.current_session_file:
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', datetime.datetime.now().strftime("%H%M%S"))
            try: safe_name = re.sub(r'[^a-zA-Z0-9]', '_', self.chat_session.history[0].parts[0].text[:20])
            except: pass
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            self.current_session_file = os.path.join(self.sessions_dir, f"{timestamp}_{safe_name}.json")
            self.refresh_session_list()

        history_data = []
        for m in self.chat_session.history:
            parts_text = []
            for p in m.parts:
                if hasattr(p, "text"): parts_text.append(p.text)
                else: parts_text.append("[IMAGE_DATA]") 
            history_data.append({"role": m.role, "text": "\n".join(parts_text)})
        
        save_data = {"model": self.model_var.get(), "history": history_data, "project_path": self.path_label.cget("text")}
        with open(self.current_session_file, "w", encoding="utf-8") as f: json.dump(save_data, f, ensure_ascii=False, indent=2)

    def load_session(self, filename):
        full_path = os.path.join(self.sessions_dir, filename)
        try:
            with open(full_path, "r", encoding="utf-8") as f: data = json.load(f)
            self.current_session_file = full_path
            for widget in self.chat_scroll.winfo_children(): widget.destroy()
            self.add_system_message(f"--- LOADED: {filename} ---")
            for msg in data["history"]:
                if msg["role"] == "user": self.add_user_message(msg["text"], has_image=("[IMAGE_DATA]" in msg["text"]))
                else: self.add_ai_message(msg["text"])
            self.model_var.set(data.get("model", "gemini-1.5-flash-latest"))
            saved_path = data.get("project_path", "Not selected")
            if saved_path != "Not selected" and saved_path != self.path_label.cget("text"):
                self.add_system_message(f"⚠️ Session project: {saved_path}. Scan it for context!", "orange")
            if self.project_context: self.init_model_session(history_override=data["history"])
            else: self.add_system_message("ℹ️ History loaded. Scan project to restore memory.", "yellow")
        except Exception as e: messagebox.showerror("Error", f"Load failed: {e}")

    # ================= OBRAZKI I UI =================
    
    def paste_from_clipboard(self, event):
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, list) and image:
                if os.path.isfile(image[0]): image = Image.open(image[0])
            if isinstance(image, Image.Image):
                self.current_image = image
                preview = image.copy()
                preview.thumbnail((150, 150))
                self.tk_image = ImageTk.PhotoImage(preview)
                self.image_preview_label.configure(image=self.tk_image, text=self.tr("img_preview"))
                self.image_preview_frame.grid()
                return "break"
        except: pass

    def clear_image_preview(self):
        self.current_image = None
        self.image_preview_frame.grid_remove()

    def add_user_message(self, text, has_image=False, image_obj=None):
        """Dodaje wiadomość użytkownika. Jeśli podano image_obj, wyświetla go."""
        msg_frame = ctk.CTkFrame(self.chat_scroll, fg_color="#2563EB", corner_radius=15)
        msg_frame.pack(pady=5, padx=(50, 10), anchor="e")

        # 1. Wyświetlanie obrazka jeśli jest
        if image_obj:
            # Skalowanie do wyświetlenia
            disp_img = image_obj.copy()
            disp_img.thumbnail((300, 300))
            ctk_img = ctk.CTkImage(light_image=disp_img, dark_image=disp_img, size=disp_img.size)
            self.image_refs.append(ctk_img) # Zapobiega usunięciu przez GC
            
            img_label = ctk.CTkLabel(msg_frame, text="", image=ctk_img)
            img_label.pack(padx=10, pady=(10, 0))
        elif has_image:
             ctk.CTkLabel(msg_frame, text="[🖼️ SAVED IMAGE]", text_color="#93C5FD", font=("Arial", 10)).pack(padx=10, pady=(5,0))

        # 2. Wyświetlanie tekstu w TEXTBOX (dla zaznaczania)
        if text:
            # Obliczanie wysokości (prymitywne ale działa)
            lines = text.count('\n') + (len(text) // 60) + 1
            height = min(lines * 20 + 20, 500) # Max wysokość 500
            
            textbox = ctk.CTkTextbox(msg_frame, font=("Arial", 14), text_color="white", fg_color="transparent", 
                                     height=height, width=400, activate_scrollbars=False)
            textbox.insert("0.0", text)
            textbox.configure(state="disabled") # Read-only ale zaznaczalne
            textbox.pack(padx=15, pady=10)
            
            # Bindowanie menu pod prawy przycisk
            textbox.bind("<Button-3>", self.show_context_menu)

        self.chat_scroll._parent_canvas.yview_moveto(1.0) # Scroll only on user message

    def add_system_message(self, text, color="gray"):
        label = ctk.CTkLabel(self.chat_scroll, text=text, font=("Arial", 12), text_color=color)
        label.pack(pady=10, anchor="center")
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def add_ai_message(self, raw_text):
        main_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        main_frame.pack(pady=5, padx=(10, 50), anchor="w", fill="x")
        
        # Header
        ctk.CTkLabel(main_frame, text=f"AI ({self.model_var.get()})", font=("Arial", 10, "bold"), text_color="#34D399").pack(anchor="w")

        segments = raw_text.split("```")
        for i, segment in enumerate(segments):
            if i % 2 == 0:
                # Zwykły tekst -> Textbox dla zaznaczania
                clean = segment.strip().replace("**", "")
                if clean:
                    lines = clean.count('\n') + (len(clean) // 80) + 1
                    h = min(lines * 20 + 20, 600)
                    
                    # Używamy Textbox zamiast Label
                    tb = ctk.CTkTextbox(main_frame, font=("Arial", 14), text_color="#D1D5DB", fg_color="transparent", 
                                        height=h, width=700, wrap="word", activate_scrollbars=False)
                    tb.insert("0.0", clean)
                    tb.configure(state="disabled")
                    tb.pack(anchor="w", pady=2, fill="x")
                    tb.bind("<Button-3>", self.show_context_menu)
            else:
                # Blok kodu
                lines_arr = segment.split('\n', 1)
                code = lines_arr[1].strip() if len(lines_arr) > 1 else segment.strip()
                
                code_frame = ctk.CTkFrame(main_frame, fg_color="#000000", corner_radius=5)
                code_frame.pack(fill="x", pady=5)
                
                ctk.CTkButton(code_frame, text="📋 Copy", width=60, height=20, command=lambda c=code: self.clipboard_append(c)).pack(anchor="e", padx=5, pady=2)
                
                code_box = ctk.CTkTextbox(code_frame, font=("Consolas", 13), text_color="#A7F3D0", fg_color="transparent", height=len(code.splitlines())*20 + 30)
                code_box.insert("0.0", code)
                code_box.configure(state="disabled")
                code_box.pack(fill="x", padx=5)
                code_box.bind("<Button-3>", self.show_context_menu)

        # UWAGA: USUNIĘTO auto-scroll na dół tutaj!
        # self.chat_scroll._parent_canvas.yview_moveto(1.0) <--- USUNIĘTE

    # ================= LOGIKA BACKEND =================
    
    def fetch_available_models(self):
        api_key = self.api_entry.get()
        if not api_key:
            messagebox.showerror("Error", self.tr("api_label"))
            return
        try:
            genai.configure(api_key=api_key)
            valid_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name.replace("models/", ""))
            if valid_models:
                valid_models.sort(key=lambda x: 0 if "latest" in x else 1)
                self.model_combo.configure(values=valid_models)
                self.model_var.set(valid_models[0])
                messagebox.showinfo("OK", f"Found {len(valid_models)} models.")
            else: messagebox.showwarning("Empty", "No models found.")
        except Exception as e: messagebox.showerror("API Error", str(e))

    def init_model_session(self, history_override=None):
        api_key = self.api_entry.get()
        if not api_key: return
        genai.configure(api_key=api_key)
        
        sys_instr = f"Act as Minecraft Expert (Spigot/Paper). Project Code:\n{self.project_context}" if self.project_context else "Act as Minecraft Expert."
        history_obj = [{"role": m["role"], "parts": [m["text"]]} for m in history_override] if history_override else []

        try:
            model = genai.GenerativeModel(self.model_var.get(), system_instruction=sys_instr)
            self.chat_session = model.start_chat(history=history_obj)
            self.status_label.configure(text=self.tr("status_ready"), text_color="#2da44e")
        except Exception as e:
            self.add_system_message(f"Init Error: {e}", "red")

    def switch_model_live(self, choice):
        if self.chat_session:
             hist = [{"role": m.role, "text": m.parts[0].text} for m in self.chat_session.history]
             self.init_model_session(history_override=hist)
             self.status_label.configure(text=self.tr("status_swapped"), text_color="yellow")
        else: self.init_model_session()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_label.configure(text=folder)
            threading.Thread(target=self.scan_project, args=(folder,)).start()

    def scan_project(self, folder):
        api_key = self.api_entry.get()
        if not api_key: 
            messagebox.showerror("Error", "No API Key")
            return
        
        self.scan_btn.configure(state="disabled", text=self.tr("scan_processing"))
        self.status_label.configure(text=self.tr("status_scanning"), text_color="yellow")
        self.progress_bar.start()
        
        ctx = []
        cnt = 0
        for root, _, files in os.walk(folder):
            if any(x in root for x in [".git", "target", "build"]): continue
            for file in files:
                if file.endswith((".java", ".yml", ".json")):
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            ctx.append(f"--- {file} ---\n{f.read()}\n")
                            cnt += 1
                    except: pass
        
        self.project_context = "\n".join(ctx)
        token_est = len(self.project_context) // 4
        self.project_tokens_label.configure(text=f"{self.tr('tokens_project')}: {token_est} (est.)")
        
        if self.use_cache_var.get() and token_est < 32000:
            self.use_cache_var.set(False)
            self.add_system_message(self.tr("sys_cache_too_small"), "orange")

        current_hist = [{"role": m.role, "text": m.parts[0].text} for m in self.chat_session.history] if self.chat_session else []
        self.init_model_session(history_override=current_hist)
        self.add_system_message(self.tr("sys_project_loaded").format(count=cnt), "#2da44e")
        
        self.scan_btn.configure(state="normal", text=self.tr("scan_btn"))
        self.progress_bar.stop()

    def start_chat_thread(self):
        txt = self.input_entry.get()
        if not txt and not self.current_image: return
        if not self.chat_session: self.init_model_session()

        self.input_entry.delete(0, "end")
        
        # Przekazanie obrazka do wyświetlenia w UI
        img_ref = self.current_image
        self.add_user_message(txt, has_image=bool(img_ref), image_obj=img_ref)
        
        self.clear_image_preview()
        self.send_btn.configure(state="disabled")
        self.progress_bar.start()
        
        threading.Thread(target=self.run_generation, args=(txt, img_ref)).start()

    def run_generation(self, txt, img):
        try:
            content = [txt, img] if (txt and img) else (img if img else txt)
            response = self.chat_session.send_message(content)
            self.add_ai_message(response.text)
            self.auto_save_session()
            
            # Licznik tokenów
            new_est = len(response.text) // 4
            curr_txt = self.chat_tokens_label.cget("text")
            try:
                curr_val = int(curr_txt.split(":")[-1].strip())
            except: curr_val = 0
            self.chat_tokens_label.configure(text=f"{self.tr('tokens_chat')}: {curr_val + new_est}")
            
        except Exception as e:
            self.add_system_message(self.tr("sys_error").format(e=e), "red")
        
        self.send_btn.configure(state="normal")
        self.progress_bar.stop()
    
    def save_chat_history(self):
        if not self.chat_session: return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
             # Zapis ręczny (uproszczony)
             hist = [{"role": m.role, "text": m.parts[0].text} for m in self.chat_session.history]
             with open(path, "w", encoding="utf-8") as f: json.dump(hist, f, ensure_ascii=False)
    
    def load_chat_history(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            self.chat_session.history = [{"role": m["role"], "parts": [m["text"]]} for m in data]
            for widget in self.chat_scroll.winfo_children(): widget.destroy()
            for msg in data:
                if msg["role"] == "user": self.add_user_message(msg["text"])
                else: self.add_ai_message(msg["text"])

if __name__ == "__main__":
    app = GeminiCoderApp()
    app.mainloop()