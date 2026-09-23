import pyperclip
import keyboard
import threading
import time
import tkinter as tk
from tkinter import font as tkfont
from googletrans import Translator
import pyttsx3

translator = Translator()
last_text = ""

# ============ الألوان (Dark Mode) ============
BG_MAIN = "#1e1e2e"        # خلفية النافذة
BG_CARD = "#252537"        # خلفية الكروت
BG_ORIGINAL = "#2d2d44"    # خلفية النص الأصلي
BG_TRANS = "#31314f"       # خلفية الترجمة
FG_TEXT = "#e0e0e0"        # لون النص العادي
FG_TITLE = "#89b4fa"       # لون العنوان (أزرق فاتح)
FG_ORIG = "#a6adc8"        # لون النص الأصلي
FG_TRANS = "#a6e3a1"       # لون الترجمة (أخضر فاتح)
BTN_SPEAK = "#89b4fa"      # زرار الاستماع (أزرق)
BTN_CLOSE = "#f38ba8"      # زرار الإغلاق (أحمر)
FG_BTN = "#1e1e2e"         # لون نص الزرار


def translate_text(text, src='en', dest='ar'):
    try:
        result = translator.translate(text, src=src, dest=dest)
        return result.text
    except Exception as e:
        return f"Translation error: {e}"


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


def show_popup(original, translated):
    """نافذة الترجمة بتصميم عصري + Dark Mode"""
    root = tk.Tk()
    root.title("الترجمة الفورية")
    root.attributes('-topmost', True)
    root.configure(bg=BG_MAIN)

    # حجم النافذة وموضعها (على يمين الشاشة)
    win_w, win_h = 600, 380
    screen_w = root.winfo_screenwidth()
    x = screen_w - win_w - 30
    y = 60
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # محاولة تفعيل الشفافية (لو النظام يدعمها)
    try:
        root.attributes('-alpha', 0.97)
    except:
        pass

    # ===== الإطار الرئيسي =====
    main_frame = tk.Frame(root, bg=BG_MAIN)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # ===== شريط العنوان =====
    title_bar = tk.Frame(main_frame, bg=BG_MAIN)
    title_bar.pack(fill="x", pady=(0, 12))

    title_label = tk.Label(
        title_bar,
        text="🌐  المترجم الفوري",
        font=("Segoe UI", 14, "bold"),
        bg=BG_MAIN,
        fg=FG_TITLE
    )
    title_label.pack(side="right")

    # ===== كارت النص الأصلي =====
    orig_card = tk.Frame(main_frame, bg=BG_CARD)
    orig_card.pack(fill="x", pady=(0, 10))

    orig_header = tk.Frame(orig_card, bg=BG_CARD)
    orig_header.pack(fill="x", padx=12, pady=(10, 5))

    tk.Label(
        orig_header,
        text="📄  النص الأصلي",
        font=("Segoe UI", 9, "bold"),
        bg=BG_CARD,
        fg=FG_ORIG
    ).pack(side="right")

    orig_text = tk.Label(
        orig_card,
        text=original,
        font=("Segoe UI", 11),
        bg=BG_ORIGINAL,
        fg=FG_TEXT,
        wraplength=530,
        justify="left",
        anchor="w",
        padx=12,
        pady=10
    )
    orig_text.pack(fill="x", padx=12, pady=(0, 12))

    # ===== كارت الترجمة =====
    trans_card = tk.Frame(main_frame, bg=BG_CARD)
    trans_card.pack(fill="x", pady=(0, 15))

    trans_header = tk.Frame(trans_card, bg=BG_CARD)
    trans_header.pack(fill="x", padx=12, pady=(10, 5))

    tk.Label(
        trans_header,
        text="✨  الترجمة",
        font=("Segoe UI", 9, "bold"),
        bg=BG_CARD,
        fg=FG_TRANS
    ).pack(side="right")

    trans_text = tk.Label(
        trans_card,
        text=translated,
        font=("Segoe UI", 16, "bold"),
        bg=BG_TRANS,
        fg=FG_TRANS,
        wraplength=530,
        justify="right",
        anchor="e",
        padx=12,
        pady=12
    )
    trans_text.pack(fill="x", padx=12, pady=(0, 12))

    # ===== الأزرار =====
    btn_frame = tk.Frame(main_frame, bg=BG_MAIN)
    btn_frame.pack(fill="x")

    def on_speak():
        threading.Thread(
            target=speak_english,
            args=(original,),
            daemon=True
        ).start()

    # زرار استماع
    speak_btn = tk.Button(
        btn_frame,
        text="🔊  استمع",
        command=on_speak,
        bg=BTN_SPEAK,
        fg=FG_BTN,
        activebackground="#74a0e0",
        activeforeground=FG_BTN,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=20,
        pady=8
    )
    speak_btn.pack(side="right", padx=(0, 8))

    # زرار إغلاق
    close_btn = tk.Button(
        btn_frame,
        text="✕  إغلاق",
        command=root.destroy,
        bg=BTN_CLOSE,
        fg=FG_BTN,
        activebackground="#d9708f",
        activeforeground=FG_BTN,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=20,
        pady=8
    )
    close_btn.pack(side="right")

    # إغلاق تلقائي بعد 25 ثانية
    root.after(25000, root.destroy)
    root.mainloop()


def translate_selection():
    try:
        keyboard.send('ctrl+c')
        time.sleep(0.3)
        text = pyperclip.paste()

        if text and text.strip():
            translated = translate_text(text)
            print(f"\nOriginal: {text}")
            print(f"Arabic: {translated}")

            threading.Thread(
                target=show_popup,
                args=(text, translated),
                daemon=True
            ).start()
    except Exception as e:
        print(f"Error: {e}")


def monitor_clipboard():
    global last_text
    print("=" * 50)
    print("PDF Translator is running!")
    print("=" * 50)
    print("Copy any text (Ctrl+C) -> translate instantly")
    print("Or select text and press (Ctrl+Alt+T)")
    print("Press (Ctrl+Q) to quit")
    print("=" * 50)

    while True:
        try:
            current = pyperclip.paste()
            if current and current != last_text and len(current.strip()) > 0:
                last_text = current
                translated = translate_text(current)
                print(f"\nOriginal: {current}")
                print(f"Arabic: {translated}")

                threading.Thread(
                    target=show_popup,
                    args=(current, translated),
                    daemon=True
                ).start()
        except Exception:
            pass

        time.sleep(0.5)


if __name__ == "__main__":
    keyboard.add_hotkey('ctrl+alt+t', translate_selection)
    monitor_clipboard()