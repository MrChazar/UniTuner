from math import sqrt
from font_data import FONTS

YELLOW = 0xFFDF32
RED = 0xFF3038
GREEN = 0x00CC78
GRAY = 0x777777
TRANSPOSITIONS = ('C', 'B', 'Es')  # polskie B = Bb, Es = Eb
TUNING_LABELS = {'C': 'C', 'B': 'Bb', 'Es': 'Eb'}

GLYPHS = {
    name: {
        character: (width, bytes.fromhex(data))
        for character, (width, data) in font.items()
    }
    for name, font in FONTS.items()
}


def get_measurement(settings):
    # Funckja do której trzeba podpiąć pomiar z mikrofonu. Na razie zwraca statyczne dane do testów.
    return {'note': 'A4', 'hz': 445.1, 'cents': 20.0}


def text_width(text, font='small', scale=1):
    return scale * sum(GLYPHS[font][character][0] for character in text)


def draw_text(screen, text, x, y, color, font='small', scale=1):
    for character in text:
        width, runs = GLYPHS[font][character]
        for index in range(0, len(runs), 3):
            screen.rect(x+scale*runs[index], y+scale*runs[index+1],
                        scale*runs[index+2], scale, color)
        x += scale*width


def draw_line(screen, x0, y0, x1, y1, color):
    dx, dy = abs(x1-x0), -abs(y1-y0)
    step_x, step_y = (1 if x0<x1 else -1), (1 if y0<y1 else -1)
    error = dx+dy
    while True:
        screen.rect(x0, y0, 1, 1, color)
        if x0 == x1 and y0 == y1:
            break
        doubled_error = 2*error
        if doubled_error >= dy:
            error += dy
            x0 += step_x
        if doubled_error <= dx:
            error += dx
            y0 += step_y


def arc_y(x):
    return int(350 - sqrt(170**2 - (x-120)**2))


def draw_flag(screen, measurement):
    if measurement is None:
        return
    cents = measurement['cents']
    color = GREEN if abs(cents) <= 5 else RED

    # Ujemne centy: w lewo i choragiewka w lewo; dodatnie: w prawo.
    x = 120 + int(max(-50, min(50, cents))*1.6)
    y = arc_y(x)
    screen.rect(x-1, y-11, 3, 20, color)
    if abs(cents) > 5:
        direction = 1 if cents > 0 else -1
        for dx in range(23):
            screen.rect(x+direction*dx, y-11+dx//3,
                        1, max(1, 9-dx//3), color)


class Interface:
    def __init__(self):
        self.settings = {'transposition': 'B', 'a4_hz': 440}

    def handle_button(self, button_name):
        settings = self.settings
        if button_name in ('LEFT', 'RIGHT', 'A', 'B'):
            index = TRANSPOSITIONS.index(settings['transposition'])
            direction = 1 if button_name in ('RIGHT', 'A') else -1
            settings['transposition'] = TRANSPOSITIONS[(index + direction) % 3]
        elif button_name in ('UP', 'X'):
            settings['a4_hz'] = min(460, settings['a4_hz']+1)
        elif button_name in ('DOWN', 'Y'):
            settings['a4_hz'] = max(400, settings['a4_hz']-1)

    def draw(self, screen, measurement):
        screen.clear()
        draw_text(screen, '%d Hz' % self.settings['a4_hz'], 14, 9, YELLOW)
        tuning_label = 'Tuning: ' + TUNING_LABELS[self.settings['transposition']]
        draw_text(screen, tuning_label, 226-text_width(tuning_label),
                  9, YELLOW)
        color = GRAY if measurement is None else (GREEN if abs(measurement['cents'])<=5 else RED)
        if measurement is None:
            draw_text(screen, '--', 104, 84, GRAY, 'accidental')
        else:
            note = measurement['note'].rstrip('0123456789-')
            letter = note[0] if note and note[0] in GLYPHS['large'] else 'A'
            draw_text(screen, letter, 120-text_width(letter, 'large')//2, 65, color, 'large')
            if len(note)>1 and note[1] in '#b':
                draw_text(screen, note[1], 153, 65, color, 'accidental')
            cents = measurement['cents']
            # ^ = za wysoko, v = za nisko. Brak symbolu = w tolerancji.
            if abs(cents)>5:
                y1, y2 = (100, 81) if cents>0 else (81, 100)
                for offset in range(3):
                    draw_line(screen, 173+offset, y1, 183+offset, y2, color)
                    draw_line(screen, 183+offset, y2, 193+offset, y1, color)
        for x in range(9, 231):
            screen.rect(x, arc_y(x), 1, 1, color)
        draw_flag(screen, measurement)
        screen.show()
