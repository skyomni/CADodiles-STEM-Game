"""
main.py — Cadodile Trivia Quest
Grade 5 Math — Bright pixel theme, EN/ES, home button.
Vertical touchscreen (600x1024). Optimized for Pi Zero 2 W.
"""

import random
import math

from kivy.config import Config
from config import SCREEN_WIDTH, SCREEN_HEIGHT
Config.set("graphics", "width", str(SCREEN_WIDTH))
Config.set("graphics", "height", str(SCREEN_HEIGHT))
Config.set("graphics", "resizable", "0")
Config.set("graphics", "maxfps", "30")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Ellipse, Line,
)
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

from config import *
import hardware
from question_generator import get_chapter_list, generate_questions
from translations import t


def hc(h):
    return get_color_from_hex(h)

C_ACCENT = hc(COLOR_ACCENT)
C_GOLD = hc(COLOR_ACCENT_GOLD)
C_TEXT = hc(COLOR_TEXT_LIGHT)
C_OK = hc(COLOR_CORRECT)
C_BAD = hc(COLOR_WRONG)


# ─────────────────────────────────────
# STATIC PIXEL BACKGROUND
# ─────────────────────────────────────
_bg_texture = None

def get_bg_texture():
    global _bg_texture
    if _bg_texture is not None:
        return _bg_texture

    BW, BH = 120, 200
    buf = bytearray(BW * BH * 3)

    def px(x, y, r, g, b):
        x, y = int(x), int(y)
        if 0 <= x < BW and 0 <= y < BH:
            i = (y * BW + x) * 3
            buf[i] = r; buf[i+1] = g; buf[i+2] = b

    def rect(x, y, w, h, r, g, b):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(BW, int(x + w)), min(BH, int(y + h))
        for py in range(y0, y1):
            row = py * BW
            for ppx in range(x0, x1):
                i = (row + ppx) * 3
                buf[i] = r; buf[i+1] = g; buf[i+2] = b

    def ellipse(cx, cy, rx, ry, r, g, b):
        x0, x1 = max(0, int(cx - rx)), min(BW, int(cx + rx))
        y0, y1 = max(0, int(cy - ry)), min(BH, int(cy + ry))
        for py in range(y0, y1):
            dy = (py - cy) / max(ry, 0.1)
            for ppx in range(x0, x1):
                dx = (ppx - cx) / max(rx, 0.1)
                if dx * dx + dy * dy <= 1.0:
                    i = (py * BW + ppx) * 3
                    buf[i] = r; buf[i+1] = g; buf[i+2] = b

    for y in range(BH):
        frac = y / BH
        r = min(255, int(80 + frac * 55))
        g = min(255, int(150 + frac * 60))
        b = min(255, int(220 + frac * 35))
        row = y * BW
        for x in range(BW):
            i = (row + x) * 3
            buf[i] = r; buf[i+1] = g; buf[i+2] = b

    sx, sy = BW - 18, BH - 18
    ellipse(sx, sy, 7, 7, 255, 240, 140)
    ellipse(sx, sy, 4, 4, 255, 250, 200)

    random.seed(42)
    for _ in range(5):
        cx = random.randint(5, BW - 20)
        cy = random.randint(BH * 2 // 3, BH - 20)
        cw = random.randint(16, 28)
        bw = cw // 4
        rect(cx, cy, cw, bw, 255, 255, 255)
        rect(cx + bw, cy + bw, cw - bw * 2, bw, 255, 255, 255)
        rect(cx + 2, cy - bw, cw - 4, bw, 250, 250, 255)

    for i in range(0, BW + 25, 20):
        hh = int(18 + math.sin(i * 0.07) * 8)
        ellipse(i, int(BH * 0.30) + hh // 2, 16, hh // 2, 80, 190, 100)

    gt = int(BH * 0.22)
    rect(0, 0, BW, gt, 180, 100, 40)
    rect(0, 0, BW, int(BH * 0.06), 150, 80, 30)
    rect(0, gt - 2, BW, 6, 74, 222, 128)
    rect(0, gt + 4, BW, 3, 34, 197, 94)

    for i in range(0, BW, 5):
        rect(i, gt + 7, 2, 4, 100, 240, 150)
        rect(i + 3, gt + 6, 2, 3, 74, 222, 128)

    for bx, by in [(14, int(BH * 0.40)), (BW - 24, int(BH * 0.44))]:
        sz = 10
        rect(bx, by, sz, sz, 220, 80, 60)
        rect(bx, by + sz // 2, sz, 1, 180, 60, 40)
        rect(bx + sz // 2, by, 1, sz, 180, 60, 40)

    qx, qy = BW // 2 - 5, int(BH * 0.38)
    rect(qx, qy, 10, 10, 251, 200, 60)
    rect(qx, qy, 10, 1, 200, 150, 30)
    rect(qx, qy + 9, 10, 1, 200, 150, 30)
    rect(qx, qy, 1, 10, 200, 150, 30)
    rect(qx + 9, qy, 1, 10, 200, 150, 30)
    px(qx + 4, qy + 2, 120, 80, 20)

    for ppx, ppy, pw, ph in [(5, gt + 5, 13, 24), (BW - 20, gt + 5, 13, 18)]:
        rect(ppx + 2, ppy, pw - 4, ph, 74, 222, 128)
        rect(ppx, ppy + ph - 5, pw, 6, 34, 180, 90)

    for _ in range(5):
        cx = random.randint(20, BW - 20)
        cy = random.randint(BH // 3, BH * 2 // 3)
        rect(cx, cy, 4, 5, 251, 191, 36)

    for bx in range(12, BW, 28):
        ellipse(bx + 5, gt + 10, 7, 5, 74, 222, 128)

    cx, cy = BW // 2 - 4, gt + 9
    rect(cx, cy, 3, 2, 180, 100, 40)
    rect(cx + 5, cy, 3, 2, 180, 100, 40)
    rect(cx + 1, cy + 2, 6, 5, 80, 150, 255)
    rect(cx + 1, cy + 7, 6, 5, 251, 200, 100)
    rect(cx, cy + 12, 8, 3, 233, 80, 100)
    rect(cx + 1, cy + 15, 6, 2, 233, 80, 100)
    px(cx + 2, cy + 9, 255, 255, 255)
    px(cx + 5, cy + 9, 255, 255, 255)
    px(cx + 2, cy + 8, 30, 30, 30)
    px(cx + 5, cy + 8, 30, 30, 30)

    for _ in range(10):
        stx = random.randint(0, BW - 1)
        sty = random.randint(BH * 3 // 4, BH - 1)
        px(stx, sty, 255, 255, 240)

    random.seed()

    tex = Texture.create(size=(BW, BH), colorfmt='rgb')
    tex.mag_filter = 'nearest'
    tex.min_filter = 'nearest'
    tex.blit_buffer(bytes(buf), colorfmt='rgb', bufferfmt='ubyte')
    _bg_texture = tex
    return tex


class PixelBG(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self._draw, pos=self._draw)
        Clock.schedule_once(self._draw, 0)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(texture=get_bg_texture(), pos=self.pos, size=self.size)


# ─────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────
class PixelButton(Button):
    def __init__(self, bg_color=COLOR_BUTTON, text_color=COLOR_TEXT_LIGHT, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = hc(text_color)
        self.font_size = dp(FONT_SIZE_BUTTON)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(BUTTON_HEIGHT)
        self._bg = hc(bg_color)
        self._pr = hc(COLOR_BUTTON_HOVER)
        self._drawn_state = None
        self.bind(pos=self._u, size=self._u, state=self._on_state)
        Clock.schedule_once(self._u, 0)

    def _on_state(self, *a):
        if self.state != self._drawn_state:
            self._u()

    def _u(self, *a):
        self._drawn_state = self.state
        self.canvas.before.clear()
        c = self._pr if self.state == "down" else self._bg
        with self.canvas.before:
            Color(0, 0, 0, 0.25)
            RoundedRectangle(pos=(self.x + 3, self.y - 3), size=self.size, radius=[dp(BUTTON_RADIUS)])
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(BUTTON_RADIUS)])
            Color(1, 1, 1, 0.12)
            RoundedRectangle(pos=(self.x + 2, self.y + self.height * 0.5),
                             size=(self.width - 4, self.height * 0.48),
                             radius=[dp(BUTTON_RADIUS - 2), dp(BUTTON_RADIUS - 2), 0, 0])


class ChapterCard(Button):
    def __init__(self, ch_data, bg_color=COLOR_BG_LIGHT, **kw):
        super().__init__(**kw)
        self.ch_data = ch_data
        self.text = (f"[b]{ch_data['icon']}[/b]\n"
                     f"[b]{ch_data['title']}[/b]\n"
                     f"[size=13]{ch_data['subtitle']}[/size]")
        self.markup = True
        self.halign = "center"
        self.valign = "middle"
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = hc(COLOR_TEXT_LIGHT)
        self.font_size = dp(17)
        self.size_hint_y = None
        self.height = dp(90)
        self._bg = hc(bg_color)
        self._pr = hc(COLOR_BUTTON_HOVER)
        self._drawn_state = None
        self.bind(pos=self._u, size=self._u, state=self._on_state)
        Clock.schedule_once(lambda dt: setattr(self, "text_size", (self.width - dp(20), None)), 0)
        Clock.schedule_once(self._u, 0)

    def _on_state(self, *a):
        if self.state != self._drawn_state:
            self._u()

    def _u(self, *a):
        self._drawn_state = self.state
        self.canvas.before.clear()
        c = self._pr if self.state == "down" else self._bg
        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            RoundedRectangle(pos=(self.x + 3, self.y - 3), size=self.size, radius=[dp(10)])
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*hc(COLOR_COIN))
            RoundedRectangle(pos=(self.x, self.y + self.height - dp(4)),
                             size=(self.width, dp(4)),
                             radius=[dp(10), dp(10), 0, 0])


class HomeButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.text = ""
        self.size_hint = (None, None)
        self.size = (dp(44), dp(44))
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self._u, size=self._u)
        Clock.schedule_once(self._u, 0)

    def _u(self, *a):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.4, 0.4, 0.45, 0.6)
            Ellipse(pos=self.pos, size=self.size)
            cx, cy = self.x + self.width / 2, self.y + self.height / 2
            Color(1, 1, 1, 0.9)
            bw, bh = 14, 12
            Rectangle(pos=(cx - bw / 2, cy - bh / 2 - 2), size=(bw, bh))
            Line(points=[cx - bw / 2 - 3, cy + bh / 2 - 2,
                         cx, cy + bh / 2 + 6,
                         cx + bw / 2 + 3, cy + bh / 2 - 2],
                 width=1.5, close=True)
            Color(0.4, 0.4, 0.45, 0.6)
            Rectangle(pos=(cx - 2, cy - bh / 2 - 2), size=(5, 6))


class LangToggle(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.size = (dp(90), dp(36))
        self.spacing = dp(2)
        self.btn_en = ToggleButton(text="EN", group="lang", state="down",
                                    font_size=dp(13), bold=True, size_hint=(0.5, 1),
                                    background_normal="", background_down="",
                                    background_color=(0, 0, 0, 0))
        self.btn_es = ToggleButton(text="ES", group="lang", state="normal",
                                    font_size=dp(13), bold=True, size_hint=(0.5, 1),
                                    background_normal="", background_down="",
                                    background_color=(0, 0, 0, 0))
        self.btn_en.bind(state=self._on_en, pos=self._draw_en, size=self._draw_en)
        self.btn_es.bind(state=self._on_es, pos=self._draw_es, size=self._draw_es)
        self.add_widget(self.btn_en)
        self.add_widget(self.btn_es)
        Clock.schedule_once(lambda dt: (self._draw_en(), self._draw_es()), 0)

    def _style(self, btn, active):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if active:
                Color(*hc(COLOR_ACCENT_GOLD))
            else:
                Color(0.4, 0.4, 0.45, 0.6)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(8)])
        btn.color = hc("#1a1a2e") if active else hc("#ffffff")

    def _draw_en(self, *a): self._style(self.btn_en, self.btn_en.state == "down")
    def _draw_es(self, *a): self._style(self.btn_es, self.btn_es.state == "down")

    def _on_en(self, btn, state):
        self._draw_en()
        if state == "down":
            App.get_running_app().set_language("en")

    def _on_es(self, btn, state):
        self._draw_es()
        if state == "down":
            App.get_running_app().set_language("es")


def make_topbar(show_home=True):
    bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48),
                    padding=[dp(6), dp(4), dp(6), dp(0)])
    if show_home:
        hb = HomeButton()
        hb.bind(on_release=lambda x: setattr(App.get_running_app()._sm, "current", "splash"))
        bar.add_widget(hb)
    else:
        bar.add_widget(Widget(size_hint_x=None, width=dp(44)))
    bar.add_widget(Widget())
    bar.add_widget(LangToggle())
    return bar


def make_title(text, size=FONT_SIZE_TITLE, color=COLOR_ACCENT_GOLD):
    lbl = Label(text=text, font_size=dp(size), bold=True,
                color=hc(color), halign="center", valign="middle",
                outline_color=(0, 0, 0, 1), outline_width=2)
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


class PixelScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bg = PixelBG()
        self.add_widget(self.bg)

    def add_content(self, w):
        self.add_widget(w)


# ─────────────────────────────────────
# SPLASH
# ─────────────────────────────────────
class SplashScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        ly = BoxLayout(orientation="vertical", spacing=dp(14),
                       padding=[dp(40), dp(8), dp(40), dp(35)])
        ly.add_widget(make_topbar(show_home=False))
        ly.add_widget(Widget(size_hint_y=0.06))
        self.title_lbl = make_title("", size=48)
        self.title_lbl.size_hint_y = 0.26
        ly.add_widget(self.title_lbl)
        self.sub1 = Label(text="", font_size=dp(26), bold=True, color=hc(COLOR_COIN),
                          size_hint_y=0.06, outline_color=(0, 0, 0, 1), outline_width=2)
        ly.add_widget(self.sub1)
        ly.add_widget(Widget(size_hint_y=0.03))
        self.mode_lbl = Label(text="", font_size=dp(22), bold=True, color=hc("#ffffff"),
                              size_hint_y=0.05, outline_color=(0, 0, 0, 1), outline_width=2)
        ly.add_widget(self.mode_lbl)
        ly.add_widget(Widget(size_hint_y=0.02))
        self.btn1 = PixelButton(text="", bg_color=COLOR_BUTTON)
        self.btn1.bind(on_release=lambda x: self._go("single"))
        ly.add_widget(self.btn1)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.btn2 = PixelButton(text="", bg_color=COLOR_ACCENT)
        self.btn2.bind(on_release=lambda x: setattr(self.manager, "current", "mp_setup"))
        ly.add_widget(self.btn2)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.btn3 = PixelButton(text="", bg_color="#64748b")
        self.btn3.bind(on_release=lambda x: setattr(self.manager, "current", "settings"))
        ly.add_widget(self.btn3)
        ly.add_widget(Widget(size_hint_y=0.16))
        ly.add_widget(Widget(size_hint_y=0.02))
        self.add_content(ly)

    def on_enter(self, *a):
        self._refresh()

    def _refresh(self):
        lang = App.get_running_app().lang
        self.title_lbl.text = t("title", lang)
        self.sub1.text = t("subtitle", lang)
        self.mode_lbl.text = t("select_mode", lang)
        self.btn1.text = t("singleplayer", lang)
        self.btn2.text = t("multiplayer", lang)
        self.btn3.text = t("settings", lang)

    def _go(self, mode):
        app = App.get_running_app()
        app.pending_mode = mode
        app.pending_players = 1
        self.manager.current = "chapters"


# ─────────────────────────────────────
# MULTIPLAYER SETUP
# ─────────────────────────────────────
class MPSetupScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.num = 2
        ly = BoxLayout(orientation="vertical", spacing=dp(14),
                       padding=[dp(50), dp(8), dp(50), dp(35)])
        ly.add_widget(make_topbar())
        ly.add_widget(Widget(size_hint_y=0.04))
        self.title_lbl = make_title("", size=40)
        self.title_lbl.size_hint_y = 0.12
        ly.add_widget(self.title_lbl)
        ly.add_widget(Widget(size_hint_y=0.03))
        self.cl = Label(text="", font_size=dp(FONT_SIZE_HEADING), bold=True,
                        color=hc(COLOR_COIN), size_hint_y=0.06,
                        outline_color=(0, 0, 0, 1), outline_width=2)
        ly.add_widget(self.cl)
        row = BoxLayout(orientation="horizontal", spacing=dp(10),
                        size_hint_y=None, height=dp(BUTTON_HEIGHT))
        for n in range(2, MAX_PLAYERS + 1):
            b = PixelButton(text=str(n), bg_color=COLOR_ACCENT if n == 2 else COLOR_BG_LIGHT)
            b.pn = n
            b.bind(on_release=self._set)
            row.add_widget(b)
        ly.add_widget(row)
        ly.add_widget(Widget(size_hint_y=0.07))
        self.btn_go = PixelButton(text="", bg_color=COLOR_BUTTON)
        self.btn_go.bind(on_release=lambda x: self._go())
        ly.add_widget(self.btn_go)
        ly.add_widget(Widget(size_hint_y=0.02))
        self.btn_back = PixelButton(text="", bg_color="#64748b")
        self.btn_back.bind(on_release=lambda x: setattr(self.manager, "current", "splash"))
        ly.add_widget(self.btn_back)
        ly.add_widget(Widget(size_hint_y=0.18))
        self.add_content(ly)

    def on_enter(self, *a): self._refresh()

    def _refresh(self):
        lang = App.get_running_app().lang
        self.title_lbl.text = t("mp_setup", lang)
        self.cl.text = f"{t('players', lang)} {self.num}"
        self.btn_go.text = t("choose_chapter", lang)
        self.btn_back.text = t("back", lang)

    def _set(self, btn):
        self.num = btn.pn
        self._refresh()

    def _go(self):
        app = App.get_running_app()
        app.pending_mode = "multi"
        app.pending_players = self.num
        self.manager.current = "chapters"


# ─────────────────────────────────────
# CHAPTER SELECT
# ─────────────────────────────────────
class ChapterScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._content = None

    def on_enter(self, *a):
        if self._content:
            self.remove_widget(self._content)
        self._build()

    def _build(self):
        lang = App.get_running_app().lang
        ch_keys = [
            ("5OA", "ch_5oa", "ch_5oa_sub", "+-x"),
            ("5NBT", "ch_5nbt", "ch_5nbt_sub", "123"),
            ("5NF", "ch_5nf", "ch_5nf_sub", "a/b"),
            ("5MD", "ch_5md", "ch_5md_sub", "cm3"),
            ("5G", "ch_5g", "ch_5g_sub", "XY"),
        ]
        ly = BoxLayout(orientation="vertical", spacing=dp(6),
                       padding=[dp(25), dp(6), dp(25), dp(6)])
        ly.add_widget(make_topbar())
        ly.add_widget(Widget(size_hint_y=None, height=dp(15)))
        tl = make_title(t("select_chapter", lang), size=34)
        tl.size_hint_y = None; tl.height = dp(40)
        ly.add_widget(tl)
        ly.add_widget(Widget(size_hint_y=None, height=dp(3)))
        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        cl = BoxLayout(orientation="vertical", spacing=dp(10),
                       size_hint_y=None, padding=[dp(4), dp(4), dp(4), dp(4)])
        cl.bind(minimum_height=cl.setter("height"))
        ac = ChapterCard(ch_data={"id": "all", "title": t("all_chapters", lang),
                                   "subtitle": t("all_sub", lang), "icon": "ALL"},
                         bg_color=COLOR_ACCENT_DARK)
        ac.bind(on_release=lambda x: self._pick("all"))
        cl.add_widget(ac)
        bgs = [COLOR_BG_LIGHT, COLOR_BG_MID]
        for i, (cid, tk, tsk, icon) in enumerate(ch_keys):
            cd = ChapterCard(ch_data={"id": cid, "title": t(tk, lang),
                                       "subtitle": t(tsk, lang), "icon": icon},
                             bg_color=bgs[i % 2])
            cd.bind(on_release=lambda x, c=cid: self._pick(c))
            cl.add_widget(cd)
        sv.add_widget(cl)
        ly.add_widget(sv)
        ly.add_widget(Widget(size_hint_y=None, height=dp(3)))
        bb = PixelButton(text=t("back", lang), bg_color="#64748b")
        bb.bind(on_release=lambda x: setattr(self.manager, "current", "splash"))
        ly.add_widget(bb)
        ly.add_widget(Widget(size_hint_y=None, height=dp(3)))
        self._content = ly
        self.add_content(ly)

    def _pick(self, cid):
        app = App.get_running_app()
        app.start_game(mode=app.pending_mode, num_players=app.pending_players, chapter_id=cid)


# ─────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────
class SettingsScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        ly = BoxLayout(orientation="vertical", spacing=dp(10),
                       padding=[dp(50), dp(8), dp(50), dp(30)])
        ly.add_widget(make_topbar())
        ly.add_widget(Widget(size_hint_y=0.01))
        self.title_lbl = make_title("", size=38); self.title_lbl.size_hint_y = 0.06
        ly.add_widget(self.title_lbl)
        ly.add_widget(Widget(size_hint_y=0.02))
        self.stub_l = Label(text="", font_size=dp(FONT_SIZE_BODY), bold=True,
                            color=hc(COLOR_COIN), size_hint_y=0.04,
                            outline_color=(0, 0, 0, 1), outline_width=1)
        ly.add_widget(self.stub_l)
        self.btn_stub = PixelButton(text="", bg_color=COLOR_BG_LIGHT)
        self.btn_stub.bind(on_release=self._ts)
        ly.add_widget(self.btn_stub)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.snd_l = Label(text="", font_size=dp(FONT_SIZE_BODY), bold=True,
                           color=hc(COLOR_COIN), size_hint_y=0.04,
                           outline_color=(0, 0, 0, 1), outline_width=1)
        ly.add_widget(self.snd_l)
        self.btn_snd = PixelButton(text="", bg_color=COLOR_BG_LIGHT)
        self.btn_snd.bind(on_release=self._tsn)
        ly.add_widget(self.btn_snd)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.bright_l = Label(text="", font_size=dp(FONT_SIZE_BODY), bold=True,
                              color=hc(COLOR_COIN), size_hint_y=0.04,
                              outline_color=(0, 0, 0, 1), outline_width=1)
        ly.add_widget(self.bright_l)
        sl = Slider(min=0.2, max=1.0, value=1.0, size_hint_y=None, height=dp(38))
        sl.bind(value=self._on_brightness)
        self.brightness_slider = sl
        ly.add_widget(sl)
        ly.add_widget(Widget(size_hint_y=0.015))
        self.btn_test = PixelButton(text="", bg_color=COLOR_ACCENT)
        self.btn_test.bind(on_release=lambda x: hardware.dispense_block())
        ly.add_widget(self.btn_test)
        ly.add_widget(Widget(size_hint_y=0.025))
        self.btn_back = PixelButton(text="", bg_color="#64748b")
        self.btn_back.bind(on_release=lambda x: setattr(self.manager, "current", "splash"))
        ly.add_widget(self.btn_back)
        ly.add_widget(Widget(size_hint_y=0.08))
        self.add_content(ly)
        self._stub = False; self._snd = True

    def on_enter(self, *a): self._refresh()

    def _refresh(self):
        lang = App.get_running_app().lang
        on, off = t("on", lang), t("off", lang)
        self.title_lbl.text = t("settings", lang)
        self.stub_l.text = f"{t('stub_mode', lang)} {on if self._stub else off}"
        self.snd_l.text = f"{t('sound', lang)} {on if self._snd else off}"
        self.bright_l.text = t("brightness", lang)
        self.btn_stub.text = t("toggle_stub", lang)
        self.btn_snd.text = t("toggle_sound", lang)
        self.btn_test.text = t("test_dispense", lang)
        self.btn_back.text = t("back", lang)

    def _ts(self, *a):
        self._stub = not self._stub
        hardware.init_hardware(stub_mode=self._stub)
        self._refresh()

    def _tsn(self, *a):
        self._snd = not self._snd
        app = App.get_running_app()
        app.sound_enabled = self._snd
        self._refresh()

    def _on_brightness(self, slider, val):
        app = App.get_running_app()
        app.brightness = val


# ─────────────────────────────────────
# TRIVIA
# ─────────────────────────────────────
class TriviaScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        ly = BoxLayout(orientation="vertical", spacing=dp(8),
                       padding=[dp(30), dp(8), dp(30), dp(20)])
        ly.add_widget(make_topbar())
        self.header = Label(text="", font_size=dp(22), color=hc(COLOR_COIN), bold=True,
                            size_hint_y=0.045, halign="center",
                            outline_color=(0, 0, 0, 1), outline_width=2)
        self.header.bind(size=self.header.setter("text_size"))
        ly.add_widget(self.header)
        self.ch_label = Label(text="", font_size=dp(18), color=hc("#b0c4de"),
                              size_hint_y=0.025, halign="center",
                              outline_color=(0, 0, 0, 1), outline_width=1)
        self.ch_label.bind(size=self.ch_label.setter("text_size"))
        ly.add_widget(self.ch_label)
        self.cnt_label = Label(text="", font_size=dp(18), color=hc("#e2e8f0"),
                               size_hint_y=0.025,
                               outline_color=(0, 0, 0, 1), outline_width=1)
        ly.add_widget(self.cnt_label)
        ly.add_widget(Widget(size_hint_y=0.01))
        self.q_label = Label(text="", font_size=dp(FONT_SIZE_HEADING), bold=True,
                             color=C_TEXT, halign="center", valign="middle", size_hint_y=0.22,
                             outline_color=(0, 0, 0, 1), outline_width=2)
        self.q_label.bind(size=self.q_label.setter("text_size"))
        self.q_label.bind(pos=self._draw_panel, size=self._draw_panel)
        ly.add_widget(self.q_label)
        self.fb_label = Label(text="", font_size=dp(FONT_SIZE_HEADING), bold=True,
                              color=C_TEXT, size_hint_y=0.08, halign="center",
                              outline_color=(0, 0, 0, 1), outline_width=2)
        self.fb_label.bind(size=self.fb_label.setter("text_size"))
        ly.add_widget(self.fb_label)
        self.ans_box = BoxLayout(orientation="vertical", spacing=dp(11), size_hint_y=0.42)
        ly.add_widget(self.ans_box)
        ly.add_widget(Widget(size_hint_y=0.03))
        self.add_content(ly)

    def _draw_panel(self, *a):
        self.q_label.canvas.before.clear()
        with self.q_label.canvas.before:
            Color(0, 0, 0, 0.55)
            RoundedRectangle(pos=self.q_label.pos, size=self.q_label.size,
                             radius=[dp(14)])
            Color(0.6, 0.6, 0.6, 0.3)
            RoundedRectangle(pos=(self.q_label.x + 1, self.q_label.y + 1),
                             size=(self.q_label.width - 2, self.q_label.height - 2),
                             radius=[dp(13)])

    def on_enter(self, *a):
        self._show()

    def _show(self):
        app = App.get_running_app()
        lang = app.lang
        q = app.get_current_question()
        if q is None:
            self.manager.current = "end"; return
        self.fb_label.text = ""
        self.ch_label.text = app.sel_chapter_title
        if app.game_mode == "single":
            self.header.text = f"{t('score', lang)} {app.scores[0]}"
        else:
            sc = "  ".join(f"P{i+1}:{s}" for i, s in enumerate(app.scores))
            self.header.text = f"{t('player_turn', lang).format(app.current_player + 1)}  |  {sc}"
        self.cnt_label.text = t("question_count", lang).format(app.q_idx + 1, app.total_q)
        self.q_label.text = q["question"]
        self.ans_box.clear_widgets()
        if q["type"] == "true_false":
            choices = [t("true", lang), t("false", lang)]
        else:
            choices = list(q["choices"])
        colors = [COLOR_BUTTON, COLOR_ACCENT, "#7c3aed", "#0891b2"]
        for _ in range(4 - len(choices)):
            self.ans_box.add_widget(Widget())
        for i, ch in enumerate(choices):
            b = PixelButton(text=ch, bg_color=colors[i % len(colors)])
            b.bind(on_release=lambda btn, c=ch: self._ans(c))
            self.ans_box.add_widget(b)

    def _ans(self, chosen):
        app = App.get_running_app()
        lang = app.lang
        ans = app.get_current_question()["answer"]
        ok = chosen == ans
        for ch in self.ans_box.children:
            if isinstance(ch, Button):
                ch.disabled = True
        if ok:
            app.scores[app.current_player] += 1
            self.fb_label.color = C_OK
            self.fb_label.text = t("correct", lang)
            hardware.correct_lights()
            hardware.dispense_block()
            if app.sound_enabled:
                hardware.buzz_correct()
        else:
            self.fb_label.color = C_BAD
            self.fb_label.text = t("wrong", lang).format(ans)
            hardware.wrong_lights()
            if app.sound_enabled:
                hardware.buzz_wrong()
        Clock.schedule_once(self._nxt, 2.0)

    def _nxt(self, dt):
        app = App.get_running_app()
        app.advance()
        if app.q_idx >= app.total_q:
            self.manager.current = "end"
        else:
            self._show()


# ─────────────────────────────────────
# END SCREEN
# ─────────────────────────────────────
class EndScreen(PixelScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        ly = BoxLayout(orientation="vertical", spacing=dp(14),
                       padding=[dp(50), dp(8), dp(50), dp(35)])
        ly.add_widget(make_topbar())
        ly.add_widget(Widget(size_hint_y=0.05))
        self.tl = make_title("", size=42); self.tl.size_hint_y = 0.09
        ly.add_widget(self.tl)
        self.sl = Label(text="", font_size=dp(FONT_SIZE_HEADING), color=C_TEXT,
                        halign="center", valign="middle", size_hint_y=0.20,
                        outline_color=(0.4, 0.4, 0.4, 1), outline_width=2)
        self.sl.bind(size=self.sl.setter("text_size"))
        ly.add_widget(self.sl)
        ly.add_widget(Widget(size_hint_y=0.03))
        self.btn_again = PixelButton(text="", bg_color=COLOR_BUTTON)
        self.btn_again.bind(on_release=lambda x: self._again())
        ly.add_widget(self.btn_again)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.btn_ch = PixelButton(text="", bg_color=COLOR_ACCENT)
        self.btn_ch.bind(on_release=lambda x: setattr(self.manager, "current", "chapters"))
        ly.add_widget(self.btn_ch)
        ly.add_widget(Widget(size_hint_y=0.012))
        self.btn_home = PixelButton(text="", bg_color="#64748b")
        self.btn_home.bind(on_release=lambda x: setattr(self.manager, "current", "splash"))
        ly.add_widget(self.btn_home)
        ly.add_widget(Widget(size_hint_y=0.15))
        self.add_content(ly)

    def on_enter(self, *a):
        app = App.get_running_app()
        lang = app.lang
        self.btn_again.text = t("play_again", lang)
        self.btn_ch.text = t("pick_chapter", lang)
        self.btn_home.text = t("home", lang)
        if app.game_mode == "single":
            self.sl.text = t("final_score", lang).format(app.scores[0], app.total_q)
            r = app.scores[0] / max(app.total_q, 1)
            self.tl.text = (t("perfect", lang) if r == 1 else
                            t("great", lang) if r >= 0.7 else t("game_over", lang))
        else:
            coins = t("coins", lang)
            lines = [f"P{i+1}: {s} {coins}" for i, s in enumerate(app.scores)]
            w = max(range(len(app.scores)), key=lambda i: app.scores[i])
            lines.append(f"\n{t('wins', lang).format(w + 1)}")
            self.sl.text = "\n".join(lines)
            self.tl.text = t("final_scores", lang)

    def _again(self):
        app = App.get_running_app()
        app.start_game(mode=app.game_mode, num_players=len(app.scores),
                       chapter_id=app.sel_chapter_id)


# ─────────────────────────────────────
# APP
# ─────────────────────────────────────
class CadodileApp(App):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.lang = DEFAULT_LANGUAGE
        self.sound_enabled = True
        self.brightness = 1.0
        self._dim_overlay = None
        self.game_questions = []
        self.q_idx = 0
        self.total_q = QUESTIONS_PER_GAME
        self.scores = [0]
        self.current_player = 0
        self.game_mode = "single"
        self.pending_mode = "single"
        self.pending_players = 1
        self.sel_chapter_id = "all"
        self.sel_chapter_title = "All Chapters"

    def build(self):
        self.title = "Cadodile Trivia Quest"
        hardware.init_hardware(stub_mode=False)
        get_bg_texture()
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MPSetupScreen(name="mp_setup"))
        sm.add_widget(ChapterScreen(name="chapters"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(TriviaScreen(name="trivia"))
        sm.add_widget(EndScreen(name="end"))

        self._dim_overlay = Widget()
        root = FloatLayout()
        root.add_widget(sm)
        root.add_widget(self._dim_overlay)
        self._sm = sm
        return root

    def on_start(self):
        Clock.schedule_interval(self._update_brightness, 0.5)

    def _update_brightness(self, dt):
        if self._dim_overlay is None:
            return
        self._dim_overlay.canvas.after.clear()
        if self.brightness < 0.95:
            dim = 1.0 - self.brightness
            with self._dim_overlay.canvas.after:
                Color(0, 0, 0, dim * 0.8)
                Rectangle(pos=(0, 0), size=Window.size)

    def set_language(self, lang):
        self.lang = lang
        screen = self._sm.current_screen
        if hasattr(screen, '_refresh'):
            screen._refresh()
        elif hasattr(screen, 'on_enter'):
            screen.on_enter()

    def start_game(self, mode="single", num_players=1, chapter_id="all"):
        self.game_mode = mode
        self.scores = [0] * num_players
        self.current_player = 0
        self.q_idx = 0
        self.sel_chapter_id = chapter_id
        if chapter_id == "all":
            self.sel_chapter_title = t("all_chapters", self.lang)
        else:
            ch_map = {"5OA": "ch_5oa", "5NBT": "ch_5nbt", "5NF": "ch_5nf",
                      "5MD": "ch_5md", "5G": "ch_5g"}
            key = ch_map.get(chapter_id, "")
            self.sel_chapter_title = t(key, self.lang) if key else chapter_id
        self.game_questions = generate_questions(chapter_id, QUESTIONS_PER_GAME, self.lang)
        self.total_q = len(self.game_questions)
        hardware.reset_servo()
        self._sm.current = "trivia"

    def get_current_question(self):
        if self.q_idx >= len(self.game_questions):
            return None
        return self.game_questions[self.q_idx]

    def advance(self):
        self.q_idx += 1
        if self.game_mode == "multi":
            self.current_player = (self.current_player + 1) % len(self.scores)

    def on_stop(self):
        hardware.stop_all()


if __name__ == "__main__":
    CadodileApp().run()
