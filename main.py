from machine import Pin, PWM
import time
from lcd_driver import LCD_1inch3
from ui import Interface, get_measurement
from microphone import Microphone
from tuner import SAMPLE_RATE

class Screen:
    def __init__(self):
        self.lcd = LCD_1inch3()
        self.backlight = PWM(Pin(13))
        self.backlight.freq(1000)
        self.backlight.duty_u16(32768)

    def clear(self):
        self.lcd.fill(0)

    def rect(self, x, y, width, height, color):
        red, green, blue = (color >> 16) & 255, (color >> 8) & 255, color & 255
        rgb565 = ((red >> 3) << 11) | ((green >> 2) << 5) | (blue >> 3)
        packed_color = ((rgb565 & 255) << 8) | (rgb565 >> 8)
        self.lcd.fill_rect(x, y, width, height, packed_color)

    def show(self):
        self.lcd.show()


def run():
    screen = Screen()
    ui = Interface()
    mic = Microphone()
    pins = {button_name: Pin(pin_number, Pin.IN, Pin.PULL_UP)
            for button_name, pin_number in (("A", 15), ("B", 17), ("X", 19), ("Y", 21),
                                            ("UP", 2), ("DOWN", 18),
                                            ("LEFT", 16), ("RIGHT", 20))}
    
    raw_states = {button_name: 1 for button_name in pins}
    stable_states = raw_states.copy()
    last_change = {button_name: time.ticks_ms() for button_name in pins}
    last_draw = time.ticks_ms()
    try:
        ui.draw(screen, None)
        print("UniTuner: main.py, LCD gotowy")
        while True:
            now = time.ticks_ms()
            for button_name, pin in pins.items():
                state = pin.value()
                if state != raw_states[button_name]:
                    raw_states[button_name] = state
                    last_change[button_name] = now
                if time.ticks_diff(now, last_change[button_name]) >= 30:
                    if state != stable_states[button_name]:
                        stable_states[button_name] = state
                        if state == 0:
                            ui.handle_button(button_name)
            if time.ticks_diff(now, last_draw) >= 100:
                samples = mic.update(now)
                measurement = get_measurement(samples, SAMPLE_RATE, ui.settings)
                ui.draw(screen, measurement, samples)
                if samples is not None:
                    print("LCD:", measurement if measurement is not None else "brak nuty")
                last_draw = now
            time.sleep_ms(5)
    finally:
        screen.backlight.deinit()
        mic.off()

if __name__ == "__main__":
    run()
