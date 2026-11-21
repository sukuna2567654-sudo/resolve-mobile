import flet as ft
import flet_video as fv


CLIP_COLORS = {
    "None": "#333338",
    "Orange": "#E67E22",
    "Teal": "#1ABC9C",
    "Purple": "#9B59B6",
    "Lime": "#2ECC71",
    "Blue": "#3498DB",
}

COLOR_LOOKS = {
    "Default": {"brightness": 0.0, "contrast": 1.0, "saturation": 1.0},
    "Warm": {"brightness": 0.04, "contrast": 1.08, "saturation": 1.25},
    "Cool": {"brightness": -0.02, "contrast": 1.1, "saturation": 0.85},
    "Vibrant": {"brightness": 0.02, "contrast": 1.15, "saturation": 1.55},
    "Dramatic": {"brightness": -0.06, "contrast": 1.35, "saturation": 0.9},
    "B&W": {"brightness": 0.0, "contrast": 1.25, "saturation": 0.0},
}


def main(page: ft.Page):
    page.title = "Resolve Studio Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#18181A"
    page.padding = 0
    page.spacing = 0

    state = {
        "media_pool": [],
        "active_clip": None,
        "trim_start": 0.0,
        "trim_end": 10.0,
        "speed_pct": 100.0,
        "fade_in": 0.0,
        "fade_out": 0.0,
        "markers": [],
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "voice_isolation": False,
        "normalize_audio": False,
    }

    def safe_float(value_str, default=0.0):
        try:
            return max(0.0, float(value_str))
        except (ValueError, TypeError):
            return default

    def notify(msg, color="#2E7D32"):
        snack = ft.SnackBar(ft.Text(msg, color="#FFFFFF"), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    video_player = fv.Video(
        playlist=[],
        playlist_mode=fv.PlaylistMode.SINGLE,
        fill_color="#0D0D0F",
        aspect_ratio=16 / 9,
        volume=100,
        autoplay=False,
        filter_quality=ft.FilterQuality.HIGH,
        expand=True,
    )

    clip_label = ft.Text("No Clip Loaded", size=11, color="#88888E")
    timecode_text = ft.Text("00:00:00:00", font_family="monospace", color="#FF5A5A", size=12)

    video_viewer = ft.Container(
        height=220,
        bgcolor="#0D0D0F",
        margin=ft.margin.all(8),
        border_radius=6,
        border=ft.border.all(1, "#2C2C30"),
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    bgcolor="#141416",
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[clip_label, timecode_text],
                    ),
                ),
                ft.Container(expand=True, content=video_player),
                ft.Container(
                    bgcolor="#18181A",
                    padding=ft.padding.symmetric(vertical=2),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16,
                        controls=[
                            ft.IconButton(
                                ft.Icons.REPLAY_5,
                                icon_size=20,
                                icon_color="#CCCCCC",
                                on_click=lambda _: video_player.seek(0) if state["active_clip"] else None,
                            ),
                            ft.IconButton(
                                ft.Icons.PLAY_ARROW,
                                icon_size=24,
                                icon_color="#FFFFFF",
                                on_click=lambda _: video_player.play() if state["active_clip"] else None,
                            ),
                            ft.IconButton(
                                ft.Icons.PAUSE,
                                icon_size=22,
                                icon_color="#CCCCCC",
                                on_click=lambda _: video_player.pause() if state["active_clip"] else None,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    def load_clip_into_viewer(clip):
        state["active_clip"] = clip
        clip_label.value = clip["name"]
        video_player.playlist = [fv.VideoMedia(clip["path"])]
        if nav_bar.selected_index == 0:
            workspace_container.content = build_media_page()
        page.update()
        notify(f"Loaded {clip['name']} into Timeline", "#1976D2")

    def on_files_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        for f in e.files:
            if f.path and not any(item["path"] == f.path for item in state["media_pool"]):
                clip = {"name": f.name, "path": f.path, "color": "None"}
                state["media_pool"].append(clip)
                if state["active_clip"] is None:
                    load_clip_into_viewer(clip)
        if nav_bar.selected_index == 0:
            workspace_container.content = build_media_page()
        page.update()

    file_picker = ft.FilePicker(on_result=on_files_picked)
    page.overlay.append(file_picker)

    header_title = ft.Text(
        "Untitled Project - Media", size=14, weight=ft.FontWeight.BOLD, color="#E0E0E0"
    )
    top_bar = ft.Container(
        bgcolor="#212124",
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border=ft.border.only(bottom=ft.BorderSide(1, "#101012")),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Icon(ft.Icons.FOLDER_OPEN, color="#A0A0A5", size=20),
                header_title,
                ft.Icon(ft.Icons.SETTINGS, color="#A0A0A5", size=20),
            ],
        ),
    )

    def build_media_page():
        def set_active_clip_color(e):
            if state["active_clip"]:
                state["active_clip"]["color"] = e.control.value
                workspace_container.content = build_media_page()
                page.update()

        grid_items = []
        for clip in state["media_pool"]:
            is_selected = state["active_clip"] and state["active_clip"]["path"] == clip["path"]
            tag_hex = CLIP_COLORS.get(clip["color"], "#333338")
            grid_items.append(
                ft.Container(
                    bgcolor="#26262A",
                    border_radius=6,
                    padding=8,
                    border=ft.border.all(2, "#FF5A5A" if is_selected else tag_hex),
                    on_click=lambda _, c=clip: load_clip_into_viewer(c),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.VIDEO_FILE, color=tag_hex if clip["color"] != "None" else "#5C9CE6", size=28),
                            ft.Text(clip["name"], size=11, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(clip["color"], size=9, color="#88888E"),
                        ],
                    ),
                )
            )

        color_dropdown = ft.Dropdown(
            label="Clip Color",
            width=120,
            height=42,
            text_size=12,
            value=state["active_clip"]["color"] if state["active_clip"] else "None",
            options=[ft.dropdown.Option(c) for c in CLIP_COLORS.keys()],
            on_change=set_active_clip_color,
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Media Pool ({len(state['media_pool'])})", weight=ft.FontWeight.BOLD, size=15),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    color_dropdown,
                                    ft.ElevatedButton(
                                        "Import",
                                        icon=ft.Icons.ADD,
                                        bgcolor="#D32F2F",
                                        color="#FFFFFF",
                                        on_click=lambda _: file_picker.pick_files(
                                            allow_multiple=True,
                                            file_type=ft.FilePickerFileType.VIDEO,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.GridView(
                    expand=True,
                    runs_count=3,
                    max_extent=130,
                    child_aspect_ratio=1.05,
                    spacing=8,
                    run_spacing=8,
                    padding=12,
                    controls=grid_items if grid_items else [
                        ft.Text("Tap 'Import' to load videos from your phone.", color="#77777E", size=12)
                    ],
                ),
            ],
        )

    def build_edit_page(is_cut_page=False):
        active_name = state["active_clip"]["name"] if state["active_clip"] else "Empty Track"
        track_color = CLIP_COLORS.get(state["active_clip"]["color"], "#2B5B84") if state["active_clip"] else "#2B5B84"
        if track_color == "#333338":
            track_color = "#2B5B84"

        start_field = ft.TextField(
            label="In (s)",
            value=str(state["trim_start"]),
            width=75,
            height=42,
            text_size=12,
            on_change=lambda e: state.update({"trim_start": safe_float(e.control.value, 0.0)}),
        )
