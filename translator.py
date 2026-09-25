import pyperclip
import keyboard
import threading
import time
import json
import os
import webbrowser
import tkinter as tk
from googletrans import Translator
import pyttsx3

# محاولة استيراد OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

translator = Translator()
last_text = ""

# ============ الألوان (Dark Mode) ============
BG_MAIN = "#1e1e2e"
BG_CARD = "#252537"
BG_ORIGINAL = "#2d2d44"
BG_TRANS = "#31314f"
FG_TEXT = "#e0e0e0"
FG_TITLE = "#89b4fa"
FG_ORIG = "#a6adc8"
FG_TRANS = "#a6e3a1"
BTN_SPEAK = "#89b4fa"
BTN_CLOSE = "#f38ba8"
FG_BTN = "#1e1e2e"

BTN_ACTIVE = "#89b4fa"
BTN_INACTIVE = "#45475a"
FG_ACTIVE = "#1e1e2e"
FG_INACTIVE = "#cdd6f4"
BTN_DISABLED = "#313244"

BTN_SAVE = "#a6e3a1"       # أخضر للحفظ
BTN_SKIP = "#45475a"        # رمادي للتخطي
BTN_LINK = "#89b4fa"        # أزرق للرابط
FG_SAVE = "#1e1e2e"
FG_ERROR = "#f38ba8"        # أحمر للأخطاء
FG_SUCCESS = "#a6e3a1"      # أخضر للنجاح

# ============ مسار ملف الإعدادات ============
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """تحميل الإعدادات"""
    default = {
        "openai_api_key": "",
        "preferred_engine": "google",
        "first_run_done": False
    }
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default.update(data)
    except Exception as e:
        print(f"Config load error: {e}")
    return default


def save_config(config):
    """حفظ الإعدادات"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Config save error: {e}")


config = load_config()


# ============ شاشة الإعداد الأولية ============

def show_setup_window():
    """شاشة إعداد أول مرة - تطلب API Key"""
    result = {"saved": False}

    root = tk.Tk()
    root.title("إعداد المترجم الفوري")
    root.attributes('-topmost', True)
    root.configure(bg=BG_MAIN)
    root.resizable(False, False)

    win_w, win_h = 550, 480
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    main_frame = tk.Frame(root, bg=BG_MAIN)
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)

    # ===== العنوان =====
    tk.Label(
        main_frame,
        text="⚙️  إعداد المترجم الفوري",
        font=("Segoe UI", 16, "bold"),
        bg=BG_MAIN,
        fg=FG_TITLE
    ).pack(pady=(0, 8))

    tk.Label(
        main_frame,
        text="مرحباً! عشان تستخدم ChatGPT في الترجمة،\nمحتاج تدخل OpenAI API Key بتاعك.\n(اختياري - ممكن تستخدم Google بدون Key)",
        font=("Segoe UI", 10),
        bg=BG_MAIN,
        fg=FG_TEXT,
        justify="center"
    ).pack(pady=(0, 20))

    # ===== خانة الـ Key =====
    tk.Label(
        main_frame,
        text="🔑  OpenAI API Key:",
        font=("Segoe UI", 10, "bold"),
        bg=BG_MAIN,
        fg=FG_TEXT,
        anchor="e"
    ).pack(fill="x", pady=(0, 5))

    key_entry = tk.Entry(
        main_frame,
        font=("Segoe UI", 11),
        bg=BG_ORIGINAL,
        fg=FG_TEXT,
        insertbackground=FG_TEXT,
        relief="flat",
        bd=0,
        show="•"  # إخفاء الحروف
    )
    key_entry.pack(fill="x", ipady=10, pady=(0, 8))

    # ===== زرار إظهار الـ Key =====
    show_var = tk.BooleanVar(value=False)

    def toggle_show():
        if show_var.get():
            key_entry.config(show="")
        else:
            key_entry.config(show="•")

    show_check = tk.Checkbutton(
        main_frame,
        text="👁️  إظهار الـ Key",
        variable=show_var,
        command=toggle_show,
        font=("Segoe UI", 9),
        bg=BG_MAIN,
        fg=FG_ORIG,
        selectcolor=BG_CARD,
        activebackground=BG_MAIN,
        activeforeground=FG_TEXT,
        cursor="hand2"
    )
    show_check.pack(anchor="e", pady=(0, 15))

    # ===== رسالة الحالة =====
    status_label = tk.Label(
        main_frame,
        text="",
        font=("Segoe UI", 9),
        bg=BG_MAIN,
        fg=FG_SUCCESS
    )
    status_label.pack(pady=(0, 10))

    # ===== الأزرار =====
    btn_frame = tk.Frame(main_frame, bg=BG_MAIN)
    btn_frame.pack(fill="x", pady=(0, 15))

    def on_save():
        key = key_entry.get().strip()
        if key and not key.startswith("sk-"):
            status_label.config(
                text="⚠️  الـ Key لازم يبدأ بـ sk-",
                fg=FG_ERROR
            )
            return

        config["openai_api_key"] = key
        config["first_run_done"] = True

        if key:
            config["preferred_engine"] = "gpt"
            status_label.config(
                text="✅  تم الحفظ! البرنامج هيبدأ الآن...",
                fg=FG_SUCCESS
            )
        else:
            config["preferred_engine"] = "google"
            status_label.config(
                text="✅  هتستخدم Google بدون Key",
                fg=FG_SUCCESS
            )

        save_config(config)
        result["saved"] = True
        root.after(800, root.destroy)

    def on_skip():
        config["openai_api_key"] = ""
        config["preferred_engine"] = "google"
        config["first_run_done"] = True
        save_config(config)
        result["saved"] = True
        root.destroy()

    save_btn = tk.Button(
        btn_frame,
        text="✅  حفظ",
        command=on_save,
        bg=BTN_SAVE,
        fg=FG_SAVE,
        activebackground="#8bc48a",
        activeforeground=FG_SAVE,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=25,
        pady=10
    )
    save_btn.pack(side="right", padx=(8, 0))

    skip_btn = tk.Button(
        btn_frame,
        text="⏭️  تخطي",
        command=on_skip,
        bg=BTN_SKIP,
        fg=FG_INACTIVE,
        activebackground="#585b70",
        activeforeground=FG_INACTIVE,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=25,
        pady=10
    )
    skip_btn.pack(side="right")

    # ===== رابط الحصول على Key =====
    link_frame = tk.Frame(main_frame, bg=BG_CARD)
    link_frame.pack(fill="x", pady=(10, 0))

    tk.Label(
        link_frame,
        text="🔗  عايز تجيب API Key؟",
        font=("Segoe UI", 9),
        bg=BG_CARD,
        fg=FG_ORIG
    ).pack(pady=(10, 3))

    def open_link():
        webbrowser.open("https://platform.openai.com/api-keys")

    link_btn = tk.Button(
        link_frame,
        text="platform.openai.com/api-keys",
        command=open_link,
        bg=BG_CARD,
        fg=BTN_LINK,
        activebackground=BG_CARD,
        activeforeground=BTN_LINK,
        font=("Segoe UI", 9, "underline"),
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    link_btn.pack(pady=(0, 10))

    # اجعل الـ focus على خانة الإدخال
    key_entry.focus_set()
    root.bind('<Return>', lambda e: on_save())

    root.mainloop()
    return result["saved"]


# ============ دوال الترجمة ============

def translate_google(text):
    try:
        result = translator.translate(text, src='en', dest='ar')
        return result.text
    except Exception as e:
        return f"Google error: {e}"


def translate_gpt(text):
    if not OPENAI_AVAILABLE:
        return None

    api_key = config.get("openai_api_key", "").strip()
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "ترجم هذا النص الأكاديمي من كتاب جامعي إلى لغة عربية فصحى مفهومة وسلسة، وحافظ على دقة المصطلحات العلمية."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT error: {e}")
        return None


def translate_text(text):
    """الترجمة مع Fallback تلقائي"""
    preferred = config.get("preferred_engine", "google")

    if preferred == "gpt":
        result = translate_gpt(text)
        if result:
            return result, "gpt"
        # Fallback لـ Google
        result = translate_google(text)
        return result, "google"
    else:
        result = translate_google(text)
        return result, "google"


# ============ النطق ============

def speak_english(text):
    try:
        clean_text = text.strip()
        if len(clean_text) > 500:
            clean_text = clean_text[:500]

        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)

        voices = engine.getProperty('voices')
        for voice in voices:
            if 'english' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Voice error: {e}")


# ============ النافذة المنبثقة ============

def show_popup(original, translated, used_engine):
    root = tk.Tk()
    root.title("الترجمة الفورية")
    root.attributes('-topmost', True)
    root.configure(bg=BG_MAIN)

    win_w, win_h = 620, 420
    screen_w = root.winfo_screenwidth()
    x = screen_w - win_w - 30
    y = 60
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    try:
        root.attributes('-alpha', 0.97)
    except:
        pass

    main_frame = tk.Frame(root, bg=BG_MAIN)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    top_bar = tk.Frame(main_frame, bg=BG_MAIN)
    top_bar.pack(fill="x", pady=(0, 12))

    tk.Label(
        top_bar,
        text="🌐  المترجم الفوري",
        font=("Segoe UI", 13, "bold"),
        bg=BG_MAIN,
        fg=FG_TITLE
    ).pack(side="right")

    engine_frame = tk.Frame(top_bar, bg=BG_MAIN)
    engine_frame.pack(side="left")

    current_engine = config.get("preferred_engine", "google")
    api_key_exists = bool(config.get("openai_api_key", "").strip())

    state = {"current": current_engine}

    def update_buttons(selected):
        state["current"] = selected

        if selected == "gpt":
            gpt_btn.config(bg=BTN_ACTIVE, fg=FG_ACTIVE)
            google_btn.config(bg=BTN_INACTIVE, fg=FG_INACTIVE)
        else:
            gpt_btn.config(bg=BTN_INACTIVE, fg=FG_INACTIVE)
            google_btn.config(bg=BTN_ACTIVE, fg=FG_ACTIVE)

        config["preferred_engine"] = selected
        save_config(config)

    def on_gpt_click():
        if not api_key_exists:
            return
        update_buttons("gpt")

    def on_google_click():
        update_buttons("google")

    gpt_btn = tk.Button(
        engine_frame, text="🤖 GPT", command=on_gpt_click,
        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
        cursor="hand2" if api_key_exists else "arrow",
        padx=12, pady=5
    )
    gpt_btn.pack(side="left", padx=(0, 4))

    google_btn = tk.Button(
        engine_frame, text="🌐 Google", command=on_google_click,
        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
        cursor="hand2", padx=12, pady=5
    )
    google_btn.pack(side="left")

    if not api_key_exists:
        gpt_btn.config(bg=BTN_DISABLED, fg="#6c7086", cursor="arrow")
        update_buttons("google")
    else:
        update_buttons(current_engine)

    # ===== النص الأصلي =====
    orig_card = tk.Frame(main_frame, bg=BG_CARD)
    orig_card.pack(fill="x", pady=(0, 10))

    orig_header = tk.Frame(orig_card, bg=BG_CARD)
    orig_header.pack(fill="x", padx=12, pady=(10, 5))

    tk.Label(
        orig_header, text="📄  النص الأصلي",
        font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=FG_ORIG
    ).pack(side="right")

    tk.Label(
        orig_card, text=original, font=("Segoe UI", 11),
        bg=BG_ORIGINAL, fg=FG_TEXT, wraplength=560,
        justify="left", anchor="w", padx=12, pady=10
    ).pack(fill="x", padx=12, pady=(0, 12))

    # ===== الترجمة =====
    trans_card = tk.Frame(main_frame, bg=BG_CARD)
    trans_card.pack(fill="x", pady=(0, 12))

    trans_header = tk.Frame(trans_card, bg=BG_CARD)
    trans_header.pack(fill="x", padx=12, pady=(10, 5))

    if used_engine == "gpt":
        source_text = "✨  الترجمة  •  🤖 GPT"
        source_color = "#cba6f7"
    else:
        source_text = "✨  الترجمة  •  🌐 Google"
        source_color = FG_TRANS

    tk.Label(
        trans_header, text=source_text,
        font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=source_color
    ).pack(side="right")

    tk.Label(
        trans_card, text=translated, font=("Segoe UI", 15, "bold"),
        bg=BG_TRANS, fg=FG_TRANS, wraplength=560,
        justify="right", anchor="e", padx=12, pady=12
    ).pack(fill="x", padx=12, pady=(0, 12))

    # ===== الأزرار السفلية =====
    btn_frame = tk.Frame(main_frame, bg=BG_MAIN)
    btn_frame.pack(fill="x")

    def on_speak():
        threading.Thread(
            target=speak_english,
            args=(original,),
            daemon=True
        ).start()

    speak_btn = tk.Button(
        btn_frame, text="🔊  استمع", command=on_speak,
        bg=BTN_SPEAK, fg=FG_BTN, activebackground="#74a0e0",
        activeforeground=FG_BTN, font=("Segoe UI", 11, "bold"),
        relief="flat", bd=0, cursor="hand2", padx=20, pady=8
    )
    speak_btn.pack(side="right", padx=(0, 8))

    close_btn = tk.Button(
        btn_frame, text="✕  إغلاق", command=root.destroy,
        bg=BTN_CLOSE, fg=FG_BTN, activebackground="#d9708f",
        activeforeground=FG_BTN, font=("Segoe UI", 11, "bold"),
        relief="flat", bd=0, cursor="hand2", padx=20, pady=8
    )
    close_btn.pack(side="right")

    root.after(30000, root.destroy)
    root.mainloop()


# ============ اختصارات ============

def translate_selection():
    try:
        keyboard.send('ctrl+c')
        time.sleep(0.3)
        text = pyperclip.paste()

        if text and text.strip():
            translated, used = translate_text(text)
            print(f"\nOriginal: {text}")
            print(f"[{used.upper()}] Arabic: {translated}")

            threading.Thread(
                target=show_popup,
                args=(text, translated, used),
                daemon=True
            ).start()
    except Exception as e:
        print(f"Error: {e}")


def monitor_clipboard():
    global last_text

    print("=" * 55)
    print("   PDF Translator is running!")
    print("=" * 55)
    print(f"   Preferred engine: {config.get('preferred_engine', 'google').upper()}")
    if config.get("openai_api_key", "").strip():
        print(f"   OpenAI Key: ✅ Loaded")
    else:
        print(f"   OpenAI Key: ❌ Not set (Google only)")
    print("=" * 55)
    print("   Copy any text (Ctrl+C) -> translate")
    print("   Or select text and press (Ctrl+Alt+T)")
    print("   Press (Ctrl+Q) to quit")
    print("=" * 55)

    while True:
        try:
            current = pyperclip.paste()
            if current and current != last_text and len(current.strip()) > 0:
                last_text = current
                translated, used = translate_text(current)
                print(f"\nOriginal: {current}")
                print(f"[{used.upper()}] Arabic: {translated}")

                threading.Thread(
                    target=show_popup,
                    args=(current, translated, used),
                    daemon=True
                ).start()
        except Exception:
            pass

        time.sleep(0.5)


# ============ التشغيل ============

if __name__ == "__main__":
    # لو أول مرة يشتغل → اعرض شاشة الإعداد
    if not config.get("first_run_done", False):
        show_setup_window()

    keyboard.add_hotkey('ctrl+alt+t', translate_selection)
    monitor_clipboard()
