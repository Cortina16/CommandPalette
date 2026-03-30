import asyncio

import flet as ft
from pynput import keyboard
import threading
import difflib
import subprocess

def open_terminal(): subprocess.Popen(["wt.exe"])

COMMAND_LIST = {
    "open terminal": {"icon": ft.icons.Icons.TERMINAL, "action": open_terminal},
}

class ElegantPalette:
    def __init__(self):
        self.page = None
        self.loop = None


    def _run_window(self):
        ft.run(target=self.main, port=8550)

    async def main(self, page: ft.Page):
        self.page = page
        self.loop = asyncio.get_running_loop()
        self.page.title = "Command Ghost"

        self.page.window.always_on_top = True
        self.page.window.frameless = True
        # self.page.window.bg_color = ft.Colors.WHITE
        self.page.window.width = 700
        self.page.window.height = 80
        self.page.window.resizable = False
        self.page.window.bgcolor = ft.Colors.TRANSPARENT
        self.page.bgcolor = ft.Colors.TRANSPARENT
        await self.page.window.center()
        self.page.window.visible = False

        self.input_field = ft.TextField(
            hint_text="Search Commands...",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
            text_style=ft.TextStyle(size=24, color=ft.Colors.WHITE, font_family="Consolas"),
            autofocus=True,
            border_color=ft.Colors.TRANSPARENT,
            cursor_color=ft.Colors.WHITE,
            content_padding=20,
            on_submit=self.execute_closest_match,
            on_change=self.hide_if_empty,
        )
        self.main_container = ft.Container(
            content=self.input_field,
            border_radius=15,
            bgcolor="#44000000",
            blur=ft.Blur(25,25),
            border=ft.Border(
                left=ft.BorderSide(2, ft.Colors.with_opacity(0.3, ft.Colors.PURPLE_600)),
                right=ft.BorderSide(2, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_600))
            ),
            # animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
        )
        self.page.add(self.main_container)
        self.page.update()
        threading.Thread(target=self.start_hotkeys, daemon=True).start()

    def start_hotkeys(self):
        with keyboard.GlobalHotKeys({'<alt>+<space>': self.trigger_toggle,'<esc>': self.trigger_hide}) as h:
            h.join()

    def trigger_toggle(self):
        asyncio.run_coroutine_threadsafe(self.toggle_ui(), self.loop)

    def trigger_hide(self):
        asyncio.run_coroutine_threadsafe(self.hide(), self.loop)

    async def toggle_ui(self):
        if self.page.window.visible:
            await self.show()
        else:
            await self.hide()


    async def show(self):
        self.page.window.visible = True
        await self.input_field.focus()
        self.page.update()

    async def hide(self):
        self.input_field.value = ""
        self.page.window.visible = False
        self.page.update()

    def hide_if_empty(self, e):
        if not e.control.value:
            pass

    async def execute_closest_match(self, e):
        user_input = e.control.value.lower().strip()
        matches = difflib.get_close_matches(user_input, COMMAND_LIST.keys(), n=1, cutoff=0.4)

        if matches:
            chosen_cmd = COMMAND_LIST[matches[0]]
            chosen_cmd['action']()
        await self.hide()

if __name__ == "__main__":
    palette = ElegantPalette()
    asyncio.run(ft.run_async(main=palette.main))


async def on_activate():
    try:
        if palette.page:
            if not palette.page.window.visible:
                await palette.show()
            else:
                await palette.hide()
    except Exception as e: print(e)

async def on_escape():
    if palette.page and palette.page.window.visible:
        await palette.hide()



