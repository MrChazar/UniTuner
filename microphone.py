from machine import ADC, Pin
import time

PROG = 20000 # tu trzeba dotestować jaki chcemy próg, żeby uniknąć szumów z otoczenia

class Microphone:
    def __init__(self, adc_pin = 26, prog = PROG, hold_ms = 150):
        self.led = Pin("LED", Pin.OUT)
        self.mic = ADC(Pin(adc_pin))
        self.prog = prog
        self.hold_ms = hold_ms
        self.last_trigger = 0
        
    def update(self, now):
        min_val = 65535
        max_val = 0
        for _ in range(150):
            val = self.mic.read_u16()
            if val < min_val:
                min_val = val
            if val > max_val:
                max_val = val

        amplituda = max_val - min_val

        if amplituda > self.prog:
            self.led.on()
            self.last_trigger = now
            return True

        if time.ticks_diff(now, self.last_trigger) >= self.hold_ms:
            self.led.off()
        return False
        
    def off(self):
        self.led.off()
        
if __name__ == "__main__":
    detector = Microphone()
    while True:
        detector.update(time.ticks_ms())
        time.sleep_ms(5)
