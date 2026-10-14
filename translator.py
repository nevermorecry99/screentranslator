import os
import sys
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import keyboard
import pyperclip
import pyttsx3
from deep_translator import GoogleTranslator, MyMemoryTranslator
from PIL import Image, ImageGrab, ImageTk
import pytesseract

try:
    import ctypes
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
    def __init__(self, master, bg_color=THEME["btn_bg"], hover_color=THEME["btn_hover"],
                 fg_color=THEME["text_main"], **kwargs):
        super().__init__(
            master,
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=12,
            pady=5,
            **kwargs
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
            text="📷 Выделите область с текстом мышью   |   ESC — отмена",
            fill=THEME["text_main"], font=("Segoe UI Semibold", 10)
        )

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.size_label = None

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", self._on_abort)

    def _on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=THEME["neon_cyan"], width=2
        )
        self.size_label = self.canvas.create_text(
            self.start_x, self.start_y - 10,
            text="", fill=THEME["neon_cyan"], anchor="sw", font=("Consolas", 9, "bold")
        )

    def _on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            w = abs(event.x - self.start_x)
            h = abs(event.y - self.start_y)
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
            cropped = self.screenshot.crop((x1, y1, x2, y2))
            self.callback(cropped)
        else:
            self.on_cancel()


class FloatingTranslator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Quick Translator Pro")
        self.geometry("500x640")
        self.minsize(420, 540)
        self.configure(bg=THEME["bg_main"])

        self._apply_dark_titlebar()

        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.lang_names = [name.capitalize() for name in sorted(ALL_LANGUAGES.keys())]

        self.tts_queue = queue.Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker_loop, daemon=True)
        self.tts_thread.start()

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
            "Dark.TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["btn_bg"],
            foreground=THEME["text_main"],
            arrowcolor=THEME["neon_cyan"],
            bordercolor=THEME["border"],
            lightcolor=THEME["border"],
            darkcolor=THEME["border"],
            padding=6
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
            "Dark.Horizontal.TScale",
            background=THEME["bg_card"],
            troughcolor=THEME["bg_main"],
            bordercolor=THEME["bg_card"],
            lightcolor=THEME["accent"],
            darkcolor=THEME["accent"]
        )

    def _build_ui(self):
        header = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        header.pack(fill=tk.X, padx=14, pady=(12, 6))

        self.topmost_var = tk.BooleanVar(value=True)
        pin_cb = tk.Checkbutton(
            header,
            text="📌 Поверх окон",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            bg=THEME["bg_card"],
            fg=THEME["text_main"],
            selectcolor=THEME["bg_main"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["neon_cyan"],
            font=("Segoe UI Semibold", 9),
            bd=0,
            cursor="hand2"
        )
        pin_cb.pack(side=tk.LEFT, padx=10, pady=6)

        alpha_frame = tk.Frame(header, bg=THEME["bg_card"])
        alpha_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(
            alpha_frame, text="Прозрачность:", bg=THEME["bg_card"],
            fg=THEME["text_muted"], font=("Segoe UI", 8)
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.alpha_scale = ttk.Scale(
            alpha_frame, from_=0.35, to=1.0, value=1.0,
            orient=tk.HORIZONTAL, length=80, style="Dark.Horizontal.TScale",
            command=self._on_alpha_change
        )
        self.alpha_scale.pack(side=tk.LEFT)

        lang_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        lang_card.pack(fill=tk.X, padx=14, pady=6)

        lang_inner = tk.Frame(lang_card, bg=THEME["bg_card"])
        lang_inner.pack(fill=tk.X, padx=10, pady=8)

        self.src_lang_cb = ttk.Combobox(
            lang_inner,
            values=["Auto (авто)", "English"] + self.lang_names,
            style="Dark.TCombobox",
            font=("Segoe UI Semibold", 10),
            width=13
        )
        self.src_lang_cb.set("English")
        self.src_lang_cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

        swap_btn = ModernButton(
            lang_inner, text="⇄", width=3, command=self.swap_languages,
            bg_color=THEME["bg_input"], hover_color=THEME["accent"]
        )
        swap_btn.pack(side=tk.LEFT, padx=8)

        self.tgt_lang_cb = ttk.Combobox(
            lang_inner,
            values=["Russian"] + self.lang_names,
            style="Dark.TCombobox",
            font=("Segoe UI Semibold", 10),
            width=13
        )
        self.tgt_lang_cb.set("Russian")
        self.tgt_lang_cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

        in_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        in_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        in_header = tk.Frame(in_card, bg=THEME["bg_card"])
        in_header.pack(fill=tk.X, padx=12, pady=(8, 4))

        tk.Label(
            in_header, text="ИСХОДНЫЙ ТЕКСТ", bg=THEME["bg_card"],
            fg=THEME["text_muted"], font=("Segoe UI Bold", 8)
        ).pack(side=tk.LEFT)

        tk.Label(
            in_header, text="Ctrl+Q — захват текста  |  Alt+S — скрин", bg=THEME["bg_card"],
            fg=THEME["neon_cyan"], font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT)

        self.input_text = tk.Text(
            in_card, wrap=tk.WORD, height=5,
            bg=THEME["bg_input"], fg=THEME["text_main"],
            insertbackground=THEME["neon_cyan"],
            selectbackground=THEME["accent"],
            font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=8, undo=True
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        self.input_text.bind("<Control-Return>", lambda e: self.start_translation())

        in_actions = tk.Frame(in_card, bg=THEME["bg_card"])
        in_actions.pack(fill=tk.X, padx=10, pady=(4, 10))

        ModernButton(
            in_actions, text="🔊 Озвучить",
            command=lambda: self.speak(self.input_text.get("1.0", tk.END), self.get_src_lang_code())
        ).pack(side=tk.LEFT)

        ModernButton(
            in_actions, text="📷 Скриншот",
            command=self.start_screen_capture
        ).pack(side=tk.LEFT, padx=6)

        ModernButton(
            in_actions, text="✕ Очистить",
            command=self.clear_texts
        ).pack(side=tk.LEFT)

        self.translate_btn = ModernButton(
            in_actions, text="Перевести ➜",
            bg_color=THEME["accent"], hover_color=THEME["accent_hover"],
            fg_color="#FFFFFF", command=self.start_translation
        )
        self.translate_btn.pack(side=tk.RIGHT)

        out_card = tk.Frame(self, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        out_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 6))

        out_header = tk.Frame(out_card, bg=THEME["bg_card"])
        out_header.pack(fill=tk.X, padx=12, pady=(8, 4))

        tk.Label(
            out_header, text="ПЕРЕВОД", bg=THEME["bg_card"],
            fg=THEME["text_muted"], font=("Segoe UI Bold", 8)
        ).pack(side=tk.LEFT)

        self.output_text = tk.Text(
            out_card, wrap=tk.WORD, height=5,
            bg=THEME["bg_input"], fg=THEME["text_main"],
            insertbackground=THEME["neon_cyan"],
            selectbackground=THEME["accent"],
            font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=8
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        out_actions = tk.Frame(out_card, bg=THEME["bg_card"])
        out_actions.pack(fill=tk.X, padx=10, pady=(4, 10))

        ModernButton(
            out_actions, text="🔊 Озвучить перевод",
            command=lambda: self.speak(self.output_text.get("1.0", tk.END), self.get_tgt_lang_code())
        ).pack(side=tk.LEFT)

        self.copy_btn = ModernButton(
            out_actions, text="📋 Копировать", command=self.copy_output
        )
        self.copy_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            self, text="Готов к работе  •  Ctrl+Enter — быстрый перевод",
            bg=THEME["bg_main"], fg=THEME["text_muted"], font=("Segoe UI", 8), anchor="w"
        )
        self.status_label.pack(fill=tk.X, padx=16, pady=(0, 8))

    def set_status(self, message, color=THEME["text_muted"]):
        self.status_label.config(text=message, fg=color)

    def _on_alpha_change(self, val):
        self.attributes("-alpha", float(val))

    def clear_texts(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.set_status("Поля очищены")

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
        keyboard.add_hotkey("ctrl+q", self._hotkey_text_capture)
        keyboard.add_hotkey("alt+s", self._hotkey_screen_capture)

    def _hotkey_text_capture(self):
        threading.Thread(target=self._capture_text_worker, daemon=True).start()

    def _capture_text_worker(self):
        time.sleep(0.1)
        try:
            pyperclip.copy("")
        except Exception:
            pass

        keyboard.send("ctrl+c")
        time.sleep(0.15)
        try:
            text = pyperclip.paste().strip()
        except Exception:
            text = ""

        if text:
            self.after(0, self.apply_input_and_translate, text)

    def _hotkey_screen_capture(self):
        self.after(0, self.start_screen_capture)

    def start_screen_capture(self):
        self.withdraw()
        self.update()
        time.sleep(0.25)

        screenshot = ImageGrab.grab()
        SnippetOverlay(
            self,
            screenshot,
            on_complete_callback=self._on_crop_captured,
            on_cancel_callback=self._restore_window
        )

    def _restore_window(self):
        self.deiconify()
        self.attributes("-topmost", self.topmost_var.get())
        self.lift()

    def _on_crop_captured(self, cropped_image):
        self._restore_window()
        self.set_status("🔍 Распознавание текста со скриншота...", THEME["neon_cyan"])
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Распознавание текста (OCR)...")
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
            self.after(0, lambda: self._handle_ocr_error("Текст в выделенной области не обнаружен."))

    def _handle_ocr_error(self, err_msg):
        self.output_text.delete("1.0", tk.END)
        self.set_status("⚠ Ошибка OCR", "#EF4444")
        if "tesseract is not installed" in err_msg.lower():
            messagebox.showerror(
                "Tesseract OCR не найден",
                "Убедитесь, что папка Tesseract-OCR упакована или установлена в систему."
            )
        else:
            messagebox.showwarning("Внимание", err_msg)

    def apply_input_and_translate(self, text):
        self._restore_window()
        self.focus_force()

        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, text)
        self.start_translation()

    def toggle_topmost(self):
        self.attributes("-topmost", self.topmost_var.get())

    def swap_languages(self):
        src = self.src_lang_cb.get()
        tgt = self.tgt_lang_cb.get()
        if not src.lower().startswith("auto"):
            self.src_lang_cb.set(tgt)
            self.tgt_lang_cb.set(src)

    def start_translation(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return

        self.translate_btn.config(state="disabled", text="Перевод...")
        self.set_status("⏳ Переводим текст...", THEME["neon_cyan"])
        self.output_text.delete("1.0", tk.END)

        threading.Thread(target=self._translate_worker, args=(text,), daemon=True).start()

    def _translate_worker(self, text):
        src = self.get_src_lang_code()
        tgt = self.get_tgt_lang_code()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": text},
                headers=headers,
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = "".join([part[0] for part in data[0] if part and part[0]])
                if translated:
                    self.after(0, self._update_output, translated, "Google GTX")
                    return
        except Exception:
            pass
        try:
            resp = requests.get(
                "https://clients5.google.com/translate_a/t",
                params={"client": "dict-chrome-ex", "sl": src, "tl": tgt, "q": text},
                headers=headers,
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    first = data[0]
                    translated = first[0] if isinstance(first, list) else str(first)
                    if translated:
                        self.after(0, self._update_output, translated, "Google Mirror")
                        return
        except Exception:
            pass
        try:
            mm_src = "en" if src == "auto" else src
            resp = requests.get(
                "https://api.mymemory.translated.net/get",
                params={"q": text[:500], "langpair": f"{mm_src}|{tgt}"},
                headers=headers,
                timeout=7
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText")
                if translated:
                    self.after(0, self._update_output, translated, "MyMemory API")
                    return
        except Exception:
            pass
        try:
            src_full = CODE_TO_NAME.get("en" if src == "auto" else src, "english")
            tgt_full = CODE_TO_NAME.get(tgt, "russian")
            translated = MyMemoryTranslator(source=src_full, target=tgt_full).translate(text[:500])
            self.after(0, self._update_output, translated, "MyMemory Reserve")
            return
        except Exception as final_err:
            self.after(0, self._update_output, f"Не удалось подключиться к серверам перевода:\n{final_err}", None)

    def _update_output(self, result, provider=None):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)
        self.translate_btn.config(state="normal", text="Перевести ➜")

        if provider:
            self.set_status(f"✓ Переведено ({provider})", THEME["success"])
        else:
            self.set_status("⚠ Ошибка соединения", "#EF4444")

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.copy_btn.config(text="✓ Скопировано!", bg=THEME["success"])
            self.set_status("✓ Перевод скопирован в буфер обмена", THEME["success"])
            self.after(1500, lambda: self.copy_btn.config(text="📋 Копировать", bg=THEME["btn_bg"]))

    def speak(self, text, lang_code=None):
        clean_text = text.strip()
        if clean_text:
            self.set_status("🔊 Озвучивание текста...", THEME["neon_cyan"])
            self.tts_queue.put((clean_text, lang_code))

    def _tts_worker_loop(self):
        try:
            engine = pyttsx3.init()
        except Exception:
            return

        while True:
            text, lang = self.tts_queue.get()
            try:
                if lang and lang != "auto":
                    for voice in engine.getProperty("voices"):
                        if lang.lower() in voice.id.lower() or lang.lower() in voice.name.lower():
                            engine.setProperty("voice", voice.id)
                            break
                engine.say(text)
                engine.runAndWait()
                self.after(0, lambda: self.set_status("Готов к работе"))
            except Exception:
                pass
            finally:
                self.tts_queue.task_done()

    def on_closing(self):
        keyboard.unhook_all()
        self.destroy()


if __name__ == "__main__":
    app = FloatingTranslator()
    app.mainloop()
