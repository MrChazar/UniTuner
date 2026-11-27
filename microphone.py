from machine import ADC, Pin
from array import array
import time
from tuner import FRAME_SIZE, SAMPLE_RATE

PROG = 4000 # tu trzeba dotestować jaki chcemy próg, żeby uniknąć szumów z otoczenia

class Microphone:
    def __init__(self, adc_pin = 26, prog = PROG, hold_ms = 150):
        self.led = Pin("LED", Pin.OUT)
        self.mic = ADC(Pin(adc_pin))
        self.prog = prog
        self.hold_ms = hold_ms
        self.last_trigger = 0
        self.samples = array('H', [0] * FRAME_SIZE)
        
    def update(self, now):
        interval = 1000000 // SAMPLE_RATE
        on_time = True
        indices = range(len(self.samples))
        deadline = time.ticks_us()
        for i in indices:
            while time.ticks_diff(time.ticks_us(), deadline) < 0:
                pass
            self.samples[i] = self.mic.read_u16()
            deadline = time.ticks_add(deadline, interval)
            if time.ticks_diff(time.ticks_us(), deadline) >= 0:
                on_time = False

        amplitude = max(self.samples) - min(self.samples)
        print("amplitude:", amplitude, "on_time:", on_time)
        if on_time and amplitude > self.prog:
            print("Trigger")
            self.led.on()
            self.last_trigger = now
            return self.samples

        if time.ticks_diff(now, self.last_trigger) >= self.hold_ms:
            self.led.off()
        return None
        
    def off(self):
        self.led.off()
        
if __name__ == "__main__":
    from main import run

    run()
