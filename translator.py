import os
import sys
import time
import subprocess
import threading
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import keyboard
import pyperclip
from deep_translator import MyMemoryTranslator
from PIL import Image, ImageGrab, ImageTk
import pytesseract

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def setup_tesseract():
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    bundled_tess_dir = os.path.join(base_path, "Tesseract-OCR")
    bundled_tess_exe = os.path.join(bundled_tess_dir, "tesseract.exe")

    if os.path.exists(bundled_tess_exe):
        pytesseract.pytesseract.tesseract_cmd = bundled_tess_exe
        os.environ["TESSDATA_PREFIX"] = os.path.join(bundled_tess_dir, "tessdata")
    elif os.name == "nt":
        default_tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(default_tess_path):
            pytesseract.pytesseract.tesseract_cmd = default_tess_path


setup_tesseract()

THEME = {
    "bg_main": "#0D1017",
    "bg_card": "#161B26",
    "bg_input": "#1C2230",
    "border": "#283044",
    "accent": "#6366F1",
    "accent_hover": "#818CF8",
    "btn_bg": "#232A3B",
    "btn_hover": "#313B52",
    "text_main": "#F1F5F9",
    "text_muted": "#8B9BB4",
    "neon_cyan": "#00F5D4",
    "success": "#10B981",
}

STRINGS = {
    "ru": {
        "title": "Quick Translator Pro",
        "pin": "📌 Поверх окон",
        "opacity": "Прозрачность:",
        "src_label": "ИСХОДНЫЙ ТЕКСТ",
        "src_hint": "F2 или Ctrl+C+C — текст  |  Alt+S — скрин",
        "tgt_label": "ПЕРЕВОД",
        "speak": "🔊 Озвучить",
        "speak_out": "🔊 Озвучить перевод",
        "screenshot": "📷 Скриншот",
        "clear": "✕ Очистить",
        "translate": "Перевести ➜",
        "translating": "Перевод...",
        "copy": "📋 Копировать",
        "copied": "✓ Скопировано!",
        "ready": "Готов к работе  •  Выделите текст и нажмите F2 (или дважды Ctrl+C)",
        "status_ready": "Готов к работе",
        "translating_status": "⏳ Переводим текст...",
        "ocr_status": "🔍 Распознавание текста со скриншота...",
        "speaking_status": "🔊 Озвучивание текста...",
        "cleared": "Поля очищены",
        "empty_clipboard": "⚠ Буфер пуст. Выделите текст перед нажатием",
        "no_ocr_text": "Текст в выделенной области не обнаружен.",
        "no_target_lang": "Пожалуйста, выберите язык перевода (целевой язык)!",
        "success_trans": "✓ Перевод выполнен успешно",
        "success_copy": "✓ Перевод скопирован в буфер обмена",
        "conn_error": "⚠ Ошибка соединения",
        "tesseract_err": "Tesseract OCR не найден. Убедитесь, что папка Tesseract-OCR упакована в билд."
    },
    "en": {
        "title": "Quick Translator Pro",
        "pin": "📌 Topmost",
        "opacity": "Opacity:",
        "src_label": "SOURCE TEXT",
        "src_hint": "F2 or Ctrl+C+C — text  |  Alt+S — screen",
        "tgt_label": "TRANSLATION",
        "speak": "🔊 Listen",
        "speak_out": "🔊 Listen",
        "screenshot": "📷 Screenshot",
        "clear": "✕ Clear",
        "translate": "Translate ➜",
        "translating": "Translating...",
        "copy": "📋 Copy",
        "copied": "✓ Copied!",
        "ready": "Ready  •  Select text and press F2 (or double Ctrl+C)",
        "status_ready": "Ready",
        "translating_status": "⏳ Translating text...",
        "ocr_status": "🔍 Recognizing text from screenshot...",
        "speaking_status": "🔊 Speaking text...",
        "cleared": "Fields cleared",
        "empty_clipboard": "⚠ Clipboard is empty. Select text first",
        "no_ocr_text": "No text found in the selected area.",
        "no_target_lang": "Please select a target language for translation!",
        "success_trans": "✓ Translation successful",
        "success_copy": "✓ Translation copied to clipboard",
        "conn_error": "⚠ Connection error",
        "tesseract_err": "Tesseract OCR not found. Make sure Tesseract-OCR folder is included."
    }
}

ALL_LANGUAGES = {
    "afrikaans": "af", "albanian": "sq", "amharic": "am", "arabic": "ar", "armenian": "hy",
    "azerbaijani": "az", "basque": "eu", "belarusian": "be", "bengali": "bn", "bosnian": "bs",
    "bulgarian": "bg", "catalan": "ca", "cebuano": "ceb", "chinese (simplified)": "zh-CN",
    "chinese (traditional)": "zh-TW", "corsican": "co", "croatian": "hr", "czech": "cs",
    "danish": "da", "dutch": "nl", "english": "en", "esperanto": "eo", "estonian": "et",
    "filipino": "tl", "finnish": "fi", "french": "fr", "frisian": "fy", "galician": "gl",
    "georgian": "ka", "german": "de", "greek": "el", "gujarati": "gu", "haitian creole": "ht",
    "hausa": "ha", "hawaiian": "haw", "hebrew": "he", "hindi": "hi", "hmong": "hmn",
    "hungarian": "hu", "icelandic": "is", "igbo": "ig", "indonesian": "id", "irish": "ga",
    "italian": "it", "japanese": "ja", "javanese": "jw", "kannada": "kn", "kazakh": "kk",
    "khmer": "km", "korean": "ko", "kurdish": "ku", "kyrgyz": "ky", "lao": "lo",
    "latin": "la", "latvian": "lv", "lithuanian": "lt", "luxembourgish": "lb", "macedonian": "mk",
    "malagasy": "mg", "malay": "ms", "malayalam": "ml", "maltese": "mt", "maori": "mi",
    "marathi": "mr", "mongolian": "mn", "myanmar": "my", "nepali": "ne", "norwegian": "no",
    "odia": "or", "pashto": "ps", "persian": "fa", "polish": "pl", "portuguese": "pt",
    "punjabi": "pa", "romanian": "ro", "russian": "ru", "samoan": "sm", "scots gaelic": "gd",
    "serbian": "sr", "sesotho": "st", "shona": "sn", "sindhi": "sd", "sinhala": "si",
    "slovak": "sk", "slovenian": "sl", "somali": "so", "spanish": "es", "sundanese": "su",
    "swahili": "sw", "swedish": "sv", "tajik": "tg", "tamil": "ta", "tatar": "tt",
    "telugu": "te", "thai": "th", "turkish": "tr", "turkmen": "tk", "ukrainian": "uk",
    "urdu": "ur", "uyghur": "ug", "uzbek": "uz", "vietnamese": "vi", "welsh": "cy",
    "xhosa": "xh", "yiddish": "yi", "yoruba": "yo", "zulu": "zu"
}

CODE_TO_NAME = {v: k for k, v in ALL_LANGUAGES.items()}


class ModernButton(tk.Button):
    def __init__(self, master, bg_color=THEME["btn_bg"], hover_color=THEME["btn_hover"], fg_color=THEME["text_main"], **kwargs):
        super().__init__(
            master, bg=bg_color, fg=fg_color, activebackground=hover_color, activeforeground=fg_color,
            relief=tk.FLAT, bd=0, cursor="hand2", font=("Segoe UI Semibold", 9), padx=12, pady=5, **kwargs
        )
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        if self["state"] != "disabled":
            self.config(bg=self.hover_bg)

    def _on_leave(self, _):
        if self["state"] != "disabled":
            self.config(bg=self.default_bg)


class SnippetOverlay(tk.Toplevel):
    def __init__(self, master, screenshot: Image.Image, on_complete_callback, on_cancel_callback):
        super().__init__(master)
        self.screenshot = screenshot
        self.callback = on_complete_callback
        self.on_cancel = on_cancel_callback

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.config(cursor="cross")

        self.tk_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas = tk.Canvas(self, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.canvas.create_rectangle(0, 0, sw, sh, fill="#080A0F", stipple="gray50")

        banner_w, banner_h = 440, 36
        bx1 = (sw - banner_w) // 2
        self.canvas.create_rectangle(
            bx1, 20, bx1 + banner_w, 20 + banner_h,
            fill=THEME["bg_card"], outline=THEME["neon_cyan"], width=1
        )
        self.canvas.create_text(
            sw // 2, 20 + banner_h // 2,
            text="📷 Выделите область / Select area   |   ESC — отмена",
            fill=THEME["text_main"], font=("Segoe UI Semibold", 10)
        )

        self.start_x, self.start_y, self.rect, self.size_label = None, None, None, None
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", self._on_abort)

    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline=THEME["neon_cyan"], width=2
        )
        self.size_label = self.canvas.create_text(
            self.start_x, self.start_y - 10, text="", fill=THEME["neon_cyan"], anchor="sw", font=("Consolas", 9, "bold")
        )

    def _on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            w, h = abs(event.x - self.start_x), abs(event.y - self.start_y)
            self.canvas.coords(self.size_label, min(self.start_x, event.x), min(self.start_y, event.y) - 6)
            self.canvas.itemconfig(self.size_label, text=f"{w} × {h} px")

    def _on_abort(self, event=None):
        self.destroy()
        self.on_cancel()

    def _on_release(self, event):
        end_x, end_y = event.x, event.y
        self.destroy()

        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        if (x2 - x1) > 12 and (y2 - y1) > 12:
            self.callback(self.screenshot.crop((x1, y1, x2, y2)))
        else:
            self.on_cancel()


class FloatingTranslator(tk.Tk):
    def __init__(self):
        super().__init__()
        if os.name == "nt":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("QuickTranslatorPro.App")
            except Exception:
                pass
        self.lang_code = "ru"
        self.title(STRINGS[self.lang_code]["title"])
        self.geometry("500x640")
        self.minsize(420, 540)
        self.configure(bg=THEME["bg_main"])
        self._apply_dark_titlebar()

        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                self.iconphoto(True, ImageTk.PhotoImage(img))
            except Exception as e:
                print("Icon load error:", e)

        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.lang_names = [name.capitalize() for name in sorted(ALL_LANGUAGES.keys())]

        self.tts_process = None
        self.last_copy_time = 0.0

        self._setup_styles()
        self._build_ui()
        self._register_hotkeys()

    def _apply_dark_titlebar(self):
        if os.name == "nt":
            try:
                self.update_idletasks()
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Dark.TCombobox", fieldbackground=THEME["bg_input"], background=THEME["btn_bg"],
            foreground=THEME["text_main"], arrowcolor=THEME["neon_cyan"], bordercolor=THEME["border"],
            lightcolor=THEME["border"], darkcolor=THEME["border"], padding=6
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", THEME["bg_input"]), ("!disabled", THEME["bg_input"])],
            foreground=[("readonly", THEME["text_main"]), ("!disabled", THEME["text_main"])],
            selectbackground=[("readonly", THEME["accent"]), ("!disabled", THEME["accent"])],
            selectforeground=[("readonly", "#FFFFFF"), ("!disabled", "#FFFFFF")]
        )
        self.option_add("*TCombobox*Listbox*Background", THEME["bg_card"])
        self.option_add("*TCombobox*Listbox*Foreground", THEME["text_main"])
        self.option_add("*TCombobox*Listbox*selectBackground", THEME["accent"])
        self.option_add("*TCombobox*Listbox*selectForeground", "#FFFFFF")
        self.option_add("*TCombobox*Listbox*Font", ("Segoe UI", 10))

        style.configure(
            "Dark.Horizontal.TScale", background=THEME["bg_card"], troughcolor=THEME["bg_main"],
            bordercolor=THEME["bg_card"], lightcolor=THEME["accent"], darkcolor=THEME["accent"]
        )

    def _build_ui(self):
        header = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        header.pack(fill=tk.X, padx=14, pady=(12, 6))

        self.topmost_var = tk.BooleanVar(value=True)
        self.pin_cb = tk.Checkbutton(
            header, text=STRINGS[self.lang_code]["pin"], variable=self.topmost_var, command=self.toggle_topmost,
            bg=THEME["bg_card"], fg=THEME["text_main"], selectcolor=THEME["bg_main"],
            activebackground=THEME["bg_card"], activeforeground=THEME["neon_cyan"],
            font=("Segoe UI Semibold", 9), bd=0, cursor="hand2"
        )
        self.pin_cb.pack(side=tk.LEFT, padx=10, pady=6)

        self.ui_lang_btn = ModernButton(
            header, text="🌐 RU / EN", width=6, command=self.toggle_ui_language,
            bg_color=THEME["bg_input"], hover_color=THEME["accent"]
        )
        self.ui_lang_btn.pack(side=tk.LEFT, padx=4)

        alpha_frame = tk.Frame(header, bg=THEME["bg_card"])
        alpha_frame.pack(side=tk.RIGHT, padx=10)
        self.alpha_lbl = tk.Label(alpha_frame, text=STRINGS[self.lang_code]["opacity"], bg=THEME["bg_card"], fg=THEME["text_muted"], font=("Segoe UI", 8))
        self.alpha_lbl.pack(side=tk.LEFT, padx=(0, 6))
        
        self.alpha_scale = ttk.Scale(
            alpha_frame, from_=0.35, to=1.0, value=1.0, orient=tk.HORIZONTAL, length=70,
            style="Dark.Horizontal.TScale", command=self._on_alpha_change
        )
        self.alpha_scale.pack(side=tk.LEFT)

        lang_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        lang_card.pack(fill=tk.X, padx=14, pady=6)
        lang_inner = tk.Frame(lang_card, bg=THEME["bg_card"])
        lang_inner.pack(fill=tk.X, padx=10, pady=8)

        self.src_lang_cb = ttk.Combobox(lang_inner, values=["Auto (авто)", "English", "Russian"] + self.lang_names, style="Dark.TCombobox", font=("Segoe UI Semibold", 10), width=13)
        self.src_lang_cb.set("English")
        self.src_lang_cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

        swap_btn = ModernButton(lang_inner, text="⇄", width=3, command=self.swap_languages, bg_color=THEME["bg_input"], hover_color=THEME["accent"])
        swap_btn.pack(side=tk.LEFT, padx=8)

        self.tgt_lang_cb = ttk.Combobox(lang_inner, values=["Russian", "English"] + self.lang_names, style="Dark.TCombobox", font=("Segoe UI Semibold", 10), width=13)
        self.tgt_lang_cb.set("Russian")
        self.tgt_lang_cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

        in_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        in_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)
        in_header = tk.Frame(in_card, bg=THEME["bg_card"])
        in_header.pack(fill=tk.X, padx=12, pady=(8, 4))
        
        self.src_title_lbl = tk.Label(in_header, text=STRINGS[self.lang_code]["src_label"], bg=THEME["bg_card"], fg=THEME["text_muted"], font=("Segoe UI Bold", 8))
        self.src_title_lbl.pack(side=tk.LEFT)
        
        self.src_hint_lbl = tk.Label(in_header, text=STRINGS[self.lang_code]["src_hint"], bg=THEME["bg_card"], fg=THEME["neon_cyan"], font=("Segoe UI", 8))
        self.src_hint_lbl.pack(side=tk.RIGHT)

        self.input_text = tk.Text(
            in_card, wrap=tk.WORD, height=5, bg=THEME["bg_input"], fg=THEME["text_main"],
            insertbackground=THEME["neon_cyan"], selectbackground=THEME["accent"],
            font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=8, undo=True
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        self.input_text.bind("<Control-Return>", lambda e: self.start_translation())

        in_actions = tk.Frame(in_card, bg=THEME["bg_card"])
        in_actions.pack(fill=tk.X, padx=10, pady=(4, 10))
        
        self.speak_in_btn = ModernButton(in_actions, text=STRINGS[self.lang_code]["speak"], command=lambda: self.speak(self.input_text.get("1.0", tk.END), self.get_src_lang_code()))
        self.speak_in_btn.pack(side=tk.LEFT)
        
        self.screen_btn = ModernButton(in_actions, text=STRINGS[self.lang_code]["screenshot"], command=self.start_screen_capture)
        self.screen_btn.pack(side=tk.LEFT, padx=6)
        
        self.clear_btn = ModernButton(in_actions, text=STRINGS[self.lang_code]["clear"], command=self.clear_texts)
        self.clear_btn.pack(side=tk.LEFT)
        
        self.translate_btn = ModernButton(
            in_actions, text=STRINGS[self.lang_code]["translate"], bg_color=THEME["accent"], hover_color=THEME["accent_hover"], fg_color="#FFFFFF", command=self.start_translation
        )
        self.translate_btn.pack(side=tk.RIGHT)

        out_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        out_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 6))
        out_header = tk.Frame(out_card, bg=THEME["bg_card"])
        out_header.pack(fill=tk.X, padx=12, pady=(8, 4))
        
        self.tgt_title_lbl = tk.Label(out_header, text=STRINGS[self.lang_code]["tgt_label"], bg=THEME["bg_card"], fg=THEME["text_muted"], font=("Segoe UI Bold", 8))
        self.tgt_title_lbl.pack(side=tk.LEFT)

        self.output_text = tk.Text(
            out_card, wrap=tk.WORD, height=5, bg=THEME["bg_input"], fg=THEME["text_main"],
            insertbackground=THEME["neon_cyan"], selectbackground=THEME["accent"],
            font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=8, state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        out_actions = tk.Frame(out_card, bg=THEME["bg_card"])
        out_actions.pack(fill=tk.X, padx=10, pady=(4, 10))
        
        self.speak_out_btn = ModernButton(out_actions, text=STRINGS[self.lang_code]["speak_out"], command=lambda: self.speak(self._get_output_text(), self.get_tgt_lang_code()))
        self.speak_out_btn.pack(side=tk.LEFT)
        
        self.copy_btn = ModernButton(out_actions, text=STRINGS[self.lang_code]["copy"], command=self.copy_output)
        self.copy_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            self, text=STRINGS[self.lang_code]["ready"],
            bg=THEME["bg_main"], fg=THEME["text_muted"], font=("Segoe UI", 8), anchor="w"
        )
        self.status_label.pack(fill=tk.X, padx=16, pady=(0, 8))

    def toggle_ui_language(self):
        self.lang_code = "en" if self.lang_code == "ru" else "ru"
        s = STRINGS[self.lang_code]
        
        self.pin_cb.config(text=s["pin"])
        self.alpha_lbl.config(text=s["opacity"])
        self.src_title_lbl.config(text=s["src_label"])
        self.src_hint_lbl.config(text=s["src_hint"])
        self.translate_btn.config(text=s["translate"])
        self.tgt_title_lbl.config(text=s["tgt_label"])
        self.speak_in_btn.config(text=s["speak"])
        self.screen_btn.config(text=s["screenshot"])
        self.clear_btn.config(text=s["clear"])
        self.speak_out_btn.config(text=s["speak_out"])
        self.copy_btn.config(text=s["copy"])
        self.set_status(s["status_ready"])

    def _get_output_text(self):
        self.output_text.config(state=tk.NORMAL)
        txt = self.output_text.get("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        return txt

    def set_status(self, message, color=THEME["text_muted"]):
        self.status_label.config(text=message, fg=color)

    def _on_alpha_change(self, val):
        self.attributes("-alpha", float(val))

    def clear_texts(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.set_status(STRINGS[self.lang_code]["cleared"])

    def _resolve_lang_code(self, val_str, fallback="en"):
        val = val_str.strip().lower()
        if not val or val.startswith("auto"):
            return "auto"
        if val in ALL_LANGUAGES.values():
            return val
        if val in ALL_LANGUAGES:
            return ALL_LANGUAGES[val]
        for name, code in ALL_LANGUAGES.items():
            if val in name:
                return code
        return fallback

    def get_src_lang_code(self):
        return self._resolve_lang_code(self.src_lang_cb.get(), fallback="en")

    def get_tgt_lang_code(self):
        code = self._resolve_lang_code(self.tgt_lang_cb.get(), fallback="ru")
        return "ru" if code == "auto" else code

    def _register_hotkeys(self):
        keyboard.add_hotkey("f2", self._hotkey_f2_capture, suppress=False)
        keyboard.add_hotkey("ctrl+c", self._on_ctrl_c_pressed, suppress=False)
        keyboard.add_hotkey("alt+s", self._hotkey_screen_capture, suppress=False)

    def _on_ctrl_c_pressed(self):
        now = time.time()
        if (now - self.last_copy_time) < 0.45:
            self.last_copy_time = 0.0
            threading.Thread(target=self._read_clipboard_and_translate, daemon=True).start()
        else:
            self.last_copy_time = now

    def _read_clipboard_and_translate(self):
        time.sleep(0.12)
        try:
            text = pyperclip.paste().strip()
        except Exception:
            text = ""
        if text:
            self.after(0, self.apply_input_and_translate, text)

    def _hotkey_f2_capture(self):
        threading.Thread(target=self._capture_f2_worker, daemon=True).start()

    def _capture_f2_worker(self):
        time.sleep(0.08)
        try:
            pyperclip.copy("")
        except Exception:
            pass

        if os.name == "nt":
            VK_CONTROL = 0x11
            VK_C = 0x43
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_C, 0, 0, 0)
            time.sleep(0.04)
            ctypes.windll.user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        else:
            keyboard.send("ctrl+c")

        time.sleep(0.15)
        try:
            text = pyperclip.paste().strip()
        except Exception:
            text = ""

        if text:
            self.after(0, self.apply_input_and_translate, text)
        else:
            self.after(0, lambda: self.set_status(STRINGS[self.lang_code]["empty_clipboard"], "#EF4444"))

    def _hotkey_screen_capture(self):
        self.after(0, self.start_screen_capture)

    def start_screen_capture(self):
        self.withdraw()
        self.update()
        time.sleep(0.25)
        SnippetOverlay(self, ImageGrab.grab(), on_complete_callback=self._on_crop_captured, on_cancel_callback=self._restore_window)

    def _restore_window(self):
        self.deiconify()
        self.attributes("-topmost", self.topmost_var.get())
        self.lift()

    def _on_crop_captured(self, cropped_image):
        self._restore_window()
        s = STRINGS[self.lang_code]
        self.set_status(s["ocr_status"], THEME["neon_cyan"])
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "OCR..." if self.lang_code=="en" else "Распознавание текста...")
        self.output_text.config(state=tk.DISABLED)
        threading.Thread(target=self._ocr_worker, args=(cropped_image,), daemon=True).start()

    def _ocr_worker(self, image):
        try:
            text = pytesseract.image_to_string(image, lang="rus+eng")
        except pytesseract.TesseractError:
            try:
                text = pytesseract.image_to_string(image)
            except Exception as err:
                self.after(0, self._handle_ocr_error, str(err))
                return
        except Exception as err:
            self.after(0, self._handle_ocr_error, str(err))
            return

        clean_text = text.strip()
        if clean_text:
            self.after(0, self.apply_input_and_translate, clean_text)
        else:
            self.after(0, lambda: self._handle_ocr_error(STRINGS[self.lang_code]["no_ocr_text"]))

    def _handle_ocr_error(self, err_msg):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.set_status("⚠ OCR Error", "#EF4444")
        if "tesseract is not installed" in err_msg.lower():
            messagebox.showerror("Error", STRINGS[self.lang_code]["tesseract_err"])
        else:
            messagebox.showwarning("Warning", err_msg)

    def apply_input_and_translate(self, text):
        self._restore_window()
        self.focus_force()
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, text)
        self.start_translation()

    def toggle_topmost(self):
        self.attributes("-topmost", self.topmost_var.get())

    def swap_languages(self):
        src, tgt = self.src_lang_cb.get(), self.tgt_lang_cb.get()
        if src and not src.lower().startswith("auto"):
            self.src_lang_cb.set(tgt)
            self.tgt_lang_cb.set(src)

    def start_translation(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return
        
        tgt_val = self.tgt_lang_cb.get().strip()
        if not tgt_val:
            messagebox.showwarning("Warning", STRINGS[self.lang_code]["no_target_lang"])
            return

        s = STRINGS[self.lang_code]
        self.translate_btn.config(state="disabled", text=s["translating"])
        self.set_status(s["translating_status"], THEME["neon_cyan"])
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        threading.Thread(target=self._translate_worker, args=(text,), daemon=True).start()

    def _translate_worker(self, text):
        src, tgt = self.get_src_lang_code(), self.get_tgt_lang_code()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        try:
            resp = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": text},
                headers=headers, timeout=6
            )
            if resp.status_code == 200:
                translated = "".join([part[0] for part in resp.json()[0] if part and part[0]])
                if translated:
                    return self.after(0, self._update_output, translated, "Google GTX")
        except Exception:
            pass

        try:
            resp = requests.get(
                "https://clients5.google.com/translate_a/t",
                params={"client": "dict-chrome-ex", "sl": src, "tl": tgt, "q": text},
                headers=headers, timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    translated = data[0][0] if isinstance(data[0], list) else str(data[0])
                    if translated:
                        return self.after(0, self._update_output, translated, "Google Mirror")
        except Exception:
            pass

        try:
            mm_src = "en" if src == "auto" else src
            resp = requests.get(
                "https://api.mymemory.translated.net/get",
                params={"q": text[:500], "langpair": f"{mm_src}|{tgt}"},
                headers=headers, timeout=7
            )
            if resp.status_code == 200:
                translated = resp.json().get("responseData", {}).get("translatedText")
                if translated:
                    return self.after(0, self._update_output, translated, "MyMemory API")
        except Exception:
            pass

        try:
            src_full = CODE_TO_NAME.get("en" if src == "auto" else src, "english")
            tgt_full = CODE_TO_NAME.get(tgt, "russian")
            translated = MyMemoryTranslator(source=src_full, target=tgt_full).translate(text[:500])
            self.after(0, self._update_output, translated, "MyMemory Reserve")
        except Exception as final_err:
            self.after(0, self._update_output, f"Error:\n{final_err}", None)

    def _update_output(self, result, provider=None):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)
        self.output_text.config(state=tk.DISABLED)
        s = STRINGS[self.lang_code]
        self.translate_btn.config(state="normal", text=s["translate"])
        if provider:
            self.set_status(s["success_trans"], THEME["success"])
        else:
            self.set_status(s["conn_error"], "#EF4444")

    def copy_output(self):
        text = self._get_output_text().strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            s = STRINGS[self.lang_code]
            self.copy_btn.config(text=s["copied"], bg=THEME["success"])
            self.set_status(s["success_copy"], THEME["success"])
            self.after(1500, lambda: self.copy_btn.config(text=s["copy"], bg=THEME["btn_bg"]))

    def speak(self, text, lang_code=None):
        clean_text = text.strip()
        if not clean_text:
            return

        if self.tts_process and self.tts_process.poll() is None:
            try:
                self.tts_process.terminate()
            except Exception:
                pass

        s = STRINGS[self.lang_code]
        self.set_status(s["speaking_status"], THEME["neon_cyan"])

        def _tts_subprocess_worker():
            try:
                if os.name == "nt":
                    ps_script = (
                        "$s = New-Object -ComObject SAPI.SpVoice; "
                        "$text = [Console]::In.ReadToEnd(); "
                        "$s.Speak($text) | Out-Null"
                    )
                    self.tts_process = subprocess.Popen(
                        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    self.tts_process.communicate(input=clean_text.encode("utf-8"))
                else:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(clean_text)
                    engine.runAndWait()
            except Exception as e:
                print("TTS error:", e)
            finally:
                self.after(0, lambda: self.set_status(STRINGS[self.lang_code]["status_ready"]))

        threading.Thread(target=_tts_subprocess_worker, daemon=True).start()

    def on_closing(self):
        if self.tts_process and self.tts_process.poll() is None:
            try:
                self.tts_process.terminate()
            except Exception:
                pass
        keyboard.unhook_all()
        self.destroy()


if __name__ == "__main__":
    app = FloatingTranslator()
    app.mainloop()