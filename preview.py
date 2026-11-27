import tkinter as tk
from collections import deque
from tkinter import messagebox

from tuner import FRAME_SIZE, SAMPLE_RATE
from ui import Interface, get_measurement


class Screen:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=480, height=480,
                                bg="black", highlightthickness=0)
        self.canvas.pack()

    def clear(self):
        self.canvas.delete("all")

    def rect(self, x, y, width, height, color):
        self.canvas.create_rectangle(x*2, y*2, (x+width)*2, (y+height)*2,
                                     fill="#%06x" % color, outline="")

    def show(self):
        pass


def run():
    try:
        import sounddevice as sd
    except (ImportError, OSError) as error:
        raise SystemExit("Podgląd wymaga sounddevice i PortAudio. "
                         "Zainstaluj zależność: python -m pip install sounddevice\n"
                         + str(error))

    root = tk.Tk()
    root.title("UniTuner – mikrofon komputera")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    screen = Screen(root)
    ui = Interface()

    latest = deque(maxlen=1)

    def capture(data, frames, timing, status):
        # PortAudio używa własnego wątku i ponownie wykorzystuje bufor.
        latest.append(None if status.input_overflow else bytes(data))

    def refresh():
        block = latest.pop() if latest else None
        measurement = None
        if block:
            pcm = memoryview(block).cast('h')
            samples = [sum(pcm[i:i + stride]) // stride
                       for i in range(0, len(pcm), stride)]
            measurement = get_measurement(samples, stream.samplerate / stride, ui.settings)
        ui.draw(screen, measurement)
        root.after(100, refresh)

    def press_button(button_name):
        ui.handle_button(button_name)

    panel = tk.Frame(root)
    panel.pack()
    for button_name in ("LEFT", "RIGHT", "UP", "DOWN"):
        tk.Button(panel, text={"LEFT": "Lewo: stroj -", "RIGHT": "Prawo: stroj +",
                               "UP": "Gora: Hz +", "DOWN": "Dol: Hz -"}[button_name], width=15,
                  font=("Arial", 9),
                  command=lambda button_name=button_name: press_button(button_name)).pack(side="left")
    root.bind("<KeyPress>", lambda event: press_button({"Left": "LEFT", "Right": "RIGHT",
                                                       "Up": "UP", "Down": "DOWN"}[event.keysym])
              if event.keysym in ("Left", "Right", "Up", "Down") else None)
    try:
        rate = sd.query_devices(kind='input')['default_samplerate']
        stride = max(1, round(rate / SAMPLE_RATE))
        with sd.RawInputStream(samplerate=rate, channels=1, dtype='int16',
                               blocksize=FRAME_SIZE * stride, callback=capture) as stream:
            refresh()
            root.mainloop()
    except sd.PortAudioError as error:
        messagebox.showerror("UniTuner", "Nie udało się otworzyć mikrofonu. "
                             "Sprawdź domyślne wejście i uprawnienia do mikrofonu.\n\n"
                             + str(error), parent=root)
    finally:
        root.destroy()


if __name__ == "__main__":
    run()
