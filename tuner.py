from math import log

SAMPLE_RATE = 8000
FRAME_SIZE = 320
NOTE_NAMES = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
WRITTEN_OFFSETS = {'C': 0, 'B': 2, 'Es': 9}


def _difference(signal, window, lag):
    difference = 0
    for i in range(window):
        delta = signal[i] - signal[i + lag]
        difference += delta * delta
    return difference


def _minimum_offset(left, middle, right):
    return (left - right) / (2 * (left - 2 * middle + right))


def get_measurement(samples, sample_rate, settings, min_amplitude=400):
    if samples is None or len(samples) < 4:
        return None
    low = min(samples)
    amplitude = max(samples) - low
    if amplitude < min_amplitude or amplitude == 0:
        return None

    # Skalowanie utrzymuje sumy kwadratów w zakresie małych liczb na Pico.
    signal = bytearray(len(samples))
    for i in range(len(samples)):
        signal[i] = (samples[i] - low) * 255 // amplitude

    # Pierwsze wyraźne minimum różnicy przebiegów (metoda YIN).
    # Zachowujemy jednakową długość porównania dla każdego przesunięcia.
    max_lag = min(int(sample_rate / 65) + 1, len(signal) // 2)
    window = len(signal) - max_lag
    total = 0
    left = middle = 0
    for lag in range(1, max_lag + 1):
        right = _difference(signal, window, lag)
        if lag >= 3 and left > middle and right >= middle:
            offset = _minimum_offset(left, middle, right)
            minimum = middle + (right - left) * offset / 4
            if minimum * (lag - 1) < 0.15 * total:
                period = lag - 1 + offset
                break
        total += right
        left, middle = middle, right
    else:
        return None

    # Pomiar kilku pełnych okresów ogranicza błąd interpolacji wysokich nut.
    cycles = min(6, int((max_lag - 2) / period))
    if cycles >= 2:
        center = round(cycles * period)
        left = _difference(signal, window, center - 1)
        middle = _difference(signal, window, center)
        right = _difference(signal, window, center + 1)
        if left < middle:
            center -= 1
            left, middle, right = _difference(signal, window, center - 1), left, middle
        elif right < middle:
            center += 1
            left, middle, right = middle, right, _difference(signal, window, center + 1)
        if left > middle and right >= middle:
            period = (center + _minimum_offset(left, middle, right)) / cycles
    hz = sample_rate / period
    if not 65 <= hz <= 1200:
        return None
    pitch = 69 + 12 * log(hz / settings['a4_hz']) / log(2)
    nearest = round(pitch)
    written = nearest + WRITTEN_OFFSETS[settings['transposition']]
    return {'note': NOTE_NAMES[written % 12] + str(written // 12 - 1),
            'hz': hz, 'cents': 100 * (pitch - nearest)}
