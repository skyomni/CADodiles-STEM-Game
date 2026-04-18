"""
hardware.py — Hardware control for Cadodile Trivia Quest

WIRING:
  LED strip DIN  -> GPIO 18 (Pin 12) through 470ohm resistor
  Servo signal   -> GPIO 12 (Pin 32)
  Buzzer (+)     -> GPIO 13 (Pin 33)
  Buzzer (-)     -> GND (Pin 34)
  Power bank +   -> LED strip red, Servo red
  Power bank -   -> LED strip white, Servo brown, Pi GND (Pin 6)
"""

import time
import threading

# ── Config ──
LED_PIN = 18
LED_COUNT = 10
LED_BRIGHTNESS = 0.4

SERVO_PIN = 12

BUZZER_PIN = 13

# ── Globals ──
_stub_mode = True
_pixels = None
_servo = None
_buzzer = None
_servo_at_zero = True


def init_hardware(stub_mode=False):
    global _stub_mode, _pixels, _servo, _buzzer

    if stub_mode:
        _stub_mode = True
        print("[HARDWARE] Stub mode enabled (forced).")
        return

    all_ok = True

    # ── LED Strip ──
    try:
        import board
        import neopixel
        _pixels = neopixel.NeoPixel(
            board.D18, LED_COUNT,
            brightness=LED_BRIGHTNESS,
            auto_write=True,
        )
        _pixels.fill((0, 0, 0))
        _pixels.fill((255, 255, 255))
        time.sleep(0.3)
        _pixels.fill((0, 0, 0))
        print(f"[HARDWARE] LED strip initialized ({LED_COUNT} LEDs on GPIO {LED_PIN}).")
    except Exception as e:
        print(f"[HARDWARE] LED strip unavailable: {e}")
        _pixels = None
        all_ok = False

    # ── Servo (standard position) ──
    try:
        from gpiozero import AngularServo
        _servo = AngularServo(
            SERVO_PIN,
            min_angle=0,
            max_angle=180,
            min_pulse_width=0.0005,
            max_pulse_width=0.0024,
        )
        _servo.angle = 0
        time.sleep(0.5)
        _servo.detach()
        print(f"[HARDWARE] Servo initialized on GPIO {SERVO_PIN}.")
    except Exception as e:
        print(f"[HARDWARE] Servo unavailable: {e}")
        _servo = None
        all_ok = False

    # ── Buzzer ──
    try:
        from gpiozero import TonalBuzzer
        _buzzer = TonalBuzzer(BUZZER_PIN)
        print(f"[HARDWARE] Buzzer initialized on GPIO {BUZZER_PIN}.")
    except Exception as e:
        print(f"[HARDWARE] Buzzer unavailable: {e}")
        _buzzer = None
        all_ok = False

    _stub_mode = not all_ok
    if _stub_mode:
        print("[HARDWARE] Some hardware missing — partial stub mode.")
    else:
        print("[HARDWARE] All hardware ready.")


# ═══════════════════════════════════════
# LED STRIP
# ═══════════════════════════════════════

def set_strip_color(r, g, b):
    if _pixels:
        _pixels.fill((r, g, b))
    else:
        print(f"[STUB] LED strip -> ({r}, {g}, {b})")


def strip_off():
    set_strip_color(0, 0, 0)


def flash_strip(r, g, b, flashes=3, on_time=0.15, off_time=0.1):
    def _flash():
        for _ in range(flashes):
            set_strip_color(r, g, b)
            time.sleep(on_time)
            strip_off()
            time.sleep(off_time)
    threading.Thread(target=_flash, daemon=True).start()


def correct_lights():
    flash_strip(0, 255, 0, flashes=3, on_time=0.2, off_time=0.1)


def wrong_lights():
    flash_strip(255, 0, 0, flashes=2, on_time=0.3, off_time=0.15)


def rainbow_cycle(wait=0.02, cycles=2):
    def _rainbow():
        for _ in range(cycles):
            for j in range(255):
                if _pixels is None:
                    return
                for i in range(LED_COUNT):
                    idx = (i * 256 // LED_COUNT + j) & 255
                    _pixels[i] = _wheel(idx)
        strip_off()
    if _pixels:
        threading.Thread(target=_rainbow, daemon=True).start()
    else:
        print("[STUB] LED strip -> rainbow cycle")


def _wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)


# ═══════════════════════════════════════
# SERVO (STANDARD POSITION — 120 DEGREE MOVEMENT)
# ═══════════════════════════════════════

def dispense_block():
    """Move servo 120 degrees. Alternates between 0 and 120."""
    global _servo_at_zero
    def _dispense():
        global _servo_at_zero
        if _servo:
            if _servo_at_zero:
                target = 120
            else:
                target = 0
            print(f"[HARDWARE] Dispensing block... moving to {target} degrees")
            _servo.angle = target
            time.sleep(0.8)
            _servo.detach()
            _servo_at_zero = not _servo_at_zero
            print("[HARDWARE] Dispense complete.")
        else:
            print("[STUB] Servo -> move 120 degrees")
    threading.Thread(target=_dispense, daemon=True).start()


def reset_servo():
    """Move servo back to 0."""
    global _servo_at_zero
    if _servo:
        _servo.angle = 0
        time.sleep(0.5)
        _servo.detach()
    _servo_at_zero = True
    print("[HARDWARE] Servo reset.")


# ═══════════════════════════════════════
# BUZZER
# ═══════════════════════════════════════

def buzz_correct():
    def _buzz():
        if _buzzer:
            try:
                from gpiozero.tones import Tone
                for _ in range(4):
                    _buzzer.play(Tone(800))
                    time.sleep(0.25)
                    _buzzer.stop()
                    time.sleep(0.1)
                _buzzer.stop()
            except Exception as e:
                print(f"[HARDWARE] Buzzer error: {e}")
        else:
            print("[STUB] Buzzer -> correct sound")
    threading.Thread(target=_buzz, daemon=True).start()


def buzz_wrong():
    def _buzz():
        if _buzzer:
            try:
                from gpiozero.tones import Tone
                _buzzer.play(Tone(300))
                time.sleep(1.0)
                _buzzer.stop()
                time.sleep(0.2)
                _buzzer.play(Tone(200))
                time.sleep(0.8)
                _buzzer.stop()
            except Exception as e:
                print(f"[HARDWARE] Buzzer error: {e}")
        else:
            print("[STUB] Buzzer -> wrong sound")
    threading.Thread(target=_buzz, daemon=True).start()


def buzz_start():
    def _buzz():
        if _buzzer:
            try:
                from gpiozero.tones import Tone
                _buzzer.play(Tone(600))
                time.sleep(0.15)
                _buzzer.stop()
                time.sleep(0.1)
                _buzzer.play(Tone(800))
                time.sleep(0.2)
                _buzzer.stop()
            except Exception as e:
                print(f"[HARDWARE] Buzzer error: {e}")
        else:
            print("[STUB] Buzzer -> start beep")
    threading.Thread(target=_buzz, daemon=True).start()


# ═══════════════════════════════════════
# COMBINED
# ═══════════════════════════════════════

def on_correct():
    correct_lights()
    buzz_correct()
    dispense_block()


def on_wrong():
    wrong_lights()
    buzz_wrong()


# ═══════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════

def stop_all():
    strip_off()
    if _servo:
        try:
            _servo.angle = 0
            time.sleep(0.3)
            _servo.detach()
        except Exception:
            pass
    if _buzzer:
        _buzzer.stop()
    print("[HARDWARE] All hardware stopped.")
