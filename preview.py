import tkinter as tk
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
    root = tk.Tk()
    root.title("UniTuner - DEMO, statyczny pomiar")
    root.resizable(False, False)
    screen = Screen(root)
    ui = Interface()

    def refresh():
        ui.draw(screen, get_measurement(ui.settings))

    def press_button(button_name):
        ui.handle_button(button_name)
        refresh()

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
    refresh()
    root.mainloop()


if __name__ == "__main__":
    run()
