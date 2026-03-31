import asyncio
import os
import flet as ft
import glob
import keyboard
import threading
import difflib
import subprocess
import commands


def open_terminal(): subprocess.Popen(["wt.exe"])

COMMAND_LIST = {
    "open": {
        "icon" : ft.icons.Icons.APPS,
        "hint" : "launches an application",
        "get_results" : lambda arg: [
            {"display_text": app, "subtitle": "Application", "value": app} for app in APP_LIST.keys() if arg in app
        ], "action": lambda arg: APP_LIST[arg]["action"]()
    },
    "google" : {
        "icon" : ft.icons.Icons.SEARCH,
        "hint" : "Search for something online",
        "get_results" : lambda arg: [
            {"display_text" : f"Search for '{arg}'", "subtitle": "Web Search", "value": arg}
        ] if arg else [{"display_text": "Type a query...", "subtitle": "Web Search", "value": ""}],
        "action" : lambda arg: print(commands.Commands.web_search(arg))
    }
}



APP_LIST = {
    "terminal" : {"icon": ft.icons.Icons.TERMINAL, "action": open_terminal}
}





def load_windows_apps():
    user_apps = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
    system_apps = os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")

    app_dict = {}
    def scan_dir(base_path):
        search_pattern = os.path.join(base_path, "**", "*.lnk")
        for lnk_path in glob.glob(search_pattern, recursive=True):
            app_name = os.path.basename(lnk_path).replace(".lnk", "").lower()
            app_dict[app_name] = {
                "icon": ft.icons.Icons.APPS,
                "action" : lambda p=lnk_path: os.startfile(p),
            }
    scan_dir(user_apps)
    scan_dir(system_apps)

    return app_dict
APP_LIST.update(load_windows_apps())


class ElegantPalette:
    def __init__(self):
        self.results_list = None
        self.page = None
        self.loop = None
        self.is_animating = False

    async def main(self, page: ft.Page):
        self.page = page
        self.loop = asyncio.get_running_loop()
        self.page.title = "Command Ghost"

        self.page.window.title_bar_hidden = True
        self.page.window.frameless = True
        self.page.window.width = 960
        self.page.window.height = 800
        self.page.window.resizable = False

        self.page.window.bgcolor = ft.Colors.TRANSPARENT
        self.page.bgcolor = ft.Colors.TRANSPARENT

        self.input_field = ft.TextField(
            hint_text="Search Commands...",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
            text_style=ft.TextStyle(size=20, color=ft.Colors.WHITE, font_family="Consolas"),
            autofocus=True,
            border=ft.InputBorder.NONE,
            text_align=ft.TextAlign.LEFT,
            content_padding=ft.padding.only(left=20, right=20, top=14, bottom=4),
            dense=True,
            on_submit=self.execute_closest_match,
            on_change=self.update_results,
        )
        self.results_list = ft.Column(spacing=0, tight=True)

        self.glow_container = ft.Container(
            content=ft.Column(
                [
                    self.input_field,
                    self.results_list,
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            width=600,
            padding=10,
            align=ft.Alignment.CENTER,
            border_radius=20,
            bgcolor=ft.Colors.GREY_900,
            shadow=[
                ft.BoxShadow(spread_radius=1, blur_radius=0, color=ft.Colors.CYAN_400),
                ft.BoxShadow(spread_radius=2, blur_radius=15, color=ft.Colors.CYAN_600),
                ft.BoxShadow(spread_radius=-2, blur_radius=40, color=ft.Colors.PURPLE_600),
                ft.BoxShadow(spread_radius=-5, blur_radius=80, color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_900)),
            ],
            # scale=ft.Scale(1),
            opacity=1.0,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            # animate_scale=ft.Animation(150, ft.AnimationCurve.DECELERATE),
        )
        centered_layout = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.glow_container],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            expand=True,
            padding=ft.padding.only(top=150)
        )
        self.page.add(centered_layout)

        self.page.window.alignment = ft.Alignment.CENTER
        self.page.window.visible = False
        self.page.update()

        threading.Thread(target=self.start_hotkeys, daemon=True).start()

    def start_hotkeys(self):
        keyboard.add_hotkey('cmd+space', self.trigger_toggle, suppress=True)
        keyboard.add_hotkey('esc', self.trigger_hide, suppress=False)
        keyboard.wait()
        # with keyboard.GlobalHotKeys({'<alt>+<space>': self.trigger_toggle,'<esc>': self.trigger_hide}) as h:
        #     h.join()

    def trigger_toggle(self):
        if self.loop and not self.is_animating:
            asyncio.run_coroutine_threadsafe(self.toggle_ui(), self.loop)

    def trigger_hide(self):
        if self.loop and not self.is_animating:
            asyncio.run_coroutine_threadsafe(self.hide(), self.loop)

    async def toggle_ui(self):
        if self.page.window.visible:
            await self.hide()
        else:
            await self.show()

    async def show(self):
        self.is_animating = True
        self.page.window.visible = True
        await self.page.window.to_front()
        self.page.update()

        # self.glow_container.scale=1.0
        self.glow_container.opacity=1.0
        self.page.update()

        await self.input_field.focus()
        self.is_animating = False

    async def hide(self):
        self.is_animating = True
        # self.glow_container.scale=0.95
        self.glow_container.opacity=0.0
        self.page.update()

        await asyncio.sleep(0.15)

        self.input_field.value = ""
        # self.page.window.height = 310
        self.results_list.controls.clear()
        self.page.window.visible = False
        self.page.update()
        self.is_animating= False

    def update_results(self, e):
        query = e.control.value.lower().strip()
        self.results_list.controls.clear()
        if not query:
            self.results_list.height = None
            self.page.update()
            return

        parts = query.split(' ', 1)
        base_cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None
        print(query)

        display_items = []

        if arg is not None and base_cmd in COMMAND_LIST:
            command_def = COMMAND_LIST[base_cmd]
            results = command_def["get_results"](arg)
            print(arg)

            for res in results[:7]:
                display_items.append(
                    ft.ListTile(
                        leading=ft.Icon(command_def['icon'], color=ft.Colors.GREY_400, size=20),
                        title=ft.Text(res["display_text"], color=ft.Colors.WHITE, size=16, font_family="Consolas"),
                        subtitle=ft.Text(res["subtitle"], color=ft.Colors.GREY_600, size=12),
                        hover_color="#33ffffff",
                        on_click=lambda _, cmd=base_cmd, val=res["value"]: asyncio.run_coroutine_threadsafe(self.run_command(cmd, val), self.loop)
                    )
                )
        # glow_padding = 310
        # base_bar_height = 80
        # results_height = len(usable_matches)*55
        # self.page.window.height = base_bar_height+results_height+glow_padding
        else:
            matches = [k for k in COMMAND_LIST.keys() if base_cmd in k]
            usable_matches = matches[:7]
            for m in usable_matches:
                display_items.append(
                    ft.ListTile(
                        leading=ft.Icon(COMMAND_LIST[m]["icon"], color=ft.Colors.GREY_400, size=20),
                        title=ft.Text(f"{m} ...", color=ft.Colors.WHITE, size=16, font_family="Consolas"),
                        subtitle=ft.Text(COMMAND_LIST[m]["hint"], color=ft.Colors.GREY_500, size=12),
                        hover_color="#33ffffff",
                        on_click = lambda _, cmd=m: self.autocomplete_command(cmd)
                    )
                )
        self.results_list.controls = display_items
        # self.page.window.alignment = ft.Alignment.CENTER
        calc_height = min(len(display_items), 7)*65
        self.results_list.height = calc_height if calc_height > 0 else None
        self.page.update()
    def autocomplete_command(self, cmd):
        self.input_field.value = f"{cmd}"
        self.input_field.focus()
        self.page.update()
        self.update_results(ft.control_event.ControlEvent(target="",name="",data="",control=self.input_field,page=self.page))
    async def run_command(self, cmd, arg):
        if arg != "":
            COMMAND_LIST[cmd]["action"](arg)
            await self.hide()
        # else:
        #     COMMAND_LIST[cmd]["action"]()
        #     await self.hide()

    async def execute_closest_match(self, e):
        user_input = e.control.value.lower().strip()
        if not user_input:
            await self.hide()
            return
        parts = user_input.split(" ", 1)
        base_cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        # matches = difflib.get_close_matches(base_cmd, COMMAND_LIST.keys(), n=1, cutoff=0.4)

        if len(parts) == 2 and parts[0] in COMMAND_LIST:
            command_def = COMMAND_LIST[parts[0]]
            results = command_def["get_results"](arg)
            if results:
                await self.run_command(parts[0], results[0]["value"])
                await self.hide()

if __name__ == "__main__":
    palette = ElegantPalette()
    ft.app(target=palette.main)



