import asyncio

import flet as ft

# --- Compatibilidade entre versões do Flet ---
# A partir da 1.0.0 vários nomes mudaram (ex: ElevatedButton -> FilledButton,
# page.go -> page.push_route, page.open/close -> page.show_dialog/pop_dialog).
# Isso cria os nomes antigos como "apelidos" quando eles não existem mais,
# pra não precisar reescrever cada tela toda vez que o Flet muda uma API.
if not hasattr(ft, "ElevatedButton") and hasattr(ft, "FilledButton"):
    ft.ElevatedButton = ft.FilledButton

if not hasattr(ft.alignment, "center") and hasattr(ft, "Alignment"):
    ft.alignment.center = ft.Alignment.CENTER
    ft.alignment.top_center = ft.Alignment.TOP_CENTER
    ft.alignment.bottom_center = ft.Alignment.BOTTOM_CENTER
    ft.alignment.center_left = ft.Alignment.CENTER_LEFT
    ft.alignment.center_right = ft.Alignment.CENTER_RIGHT
    ft.alignment.top_left = ft.Alignment.TOP_LEFT
    ft.alignment.top_right = ft.Alignment.TOP_RIGHT
    ft.alignment.bottom_left = ft.Alignment.BOTTOM_LEFT
    ft.alignment.bottom_right = ft.Alignment.BOTTOM_RIGHT

if not hasattr(ft.Page, "go"):
    def _go_compat(self, route, **kwargs):
        asyncio.create_task(self.push_route(route, **kwargs))

    ft.Page.go = _go_compat

if not hasattr(ft.Page, "open"):
    ft.Page.open = lambda self, control: self.show_dialog(control)

if not hasattr(ft.Page, "close"):
    ft.Page.close = lambda self, control=None: self.pop_dialog()

if not hasattr(ft.padding, "only"):
    ft.padding.only = lambda left=0, top=0, right=0, bottom=0: ft.padding.Padding(left=left, top=top, right=right, bottom=bottom)

if not hasattr(ft.border_radius, "only"):
    ft.border_radius.only = lambda top_left=0, top_right=0, bottom_left=0, bottom_right=0: ft.border_radius.BorderRadius(
        top_left=top_left, top_right=top_right, bottom_left=bottom_left, bottom_right=bottom_right
    )

# Paleta baseada no mockup: azul petróleo escuro + ciano de destaque
PRIMARY_DARK = "#0F2340"
PRIMARY = "#1565C0"
ACCENT = "#00BCD4"
DANGER = "#E53935"
WARNING = "#FB8C00"
SUCCESS = "#43A047"
BG = "#F4F7FA"
CARD_BG = "#FFFFFF"
TEXT_MUTED = "#6B7280"


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
    )


def _voltar(page: ft.Page):
    if len(page.views) > 1:
        page.views.pop()
        page.go(page.views[-1].route)
    else:
        page.go("/home")


def app_bar(title: str, page: ft.Page, show_back: bool = False) -> ft.AppBar:
    return ft.AppBar(
        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: _voltar(page))
        if show_back
        else None,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        bgcolor=PRIMARY_DARK,
        color="white",
        center_title=False,
    )


def bottom_nav(page: ft.Page, selected_index: int) -> ft.NavigationBar:
    def handle_change(e: ft.ControlEvent):
        routes = ["/home", "/calculadora", "/checklist", "/favoritos", "/mais"]
        page.go(routes[e.control.selected_index])

    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=handle_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.CALCULATE_OUTLINED, selected_icon=ft.Icons.CALCULATE, label="Cálculos"),
            ft.NavigationBarDestination(icon=ft.Icons.CHECKLIST_OUTLINED, selected_icon=ft.Icons.CHECKLIST, label="Checklist"),
            ft.NavigationBarDestination(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, label="Favoritos"),
            ft.NavigationBarDestination(icon=ft.Icons.MORE_HORIZ, label="Mais"),
        ],
    )


def view(**kwargs) -> ft.View:
    """Wrapper de ft.View que já garante que o conteúdo estique para ocupar
    a largura toda da tela (sem isso, Containers soltos como o cabeçalho
    com gradiente ficam "encolhidos" do lado esquerdo)."""
    kwargs.setdefault("horizontal_alignment", ft.CrossAxisAlignment.STRETCH)
    return ft.View(**kwargs)


def gradient_header(content, height=200) -> ft.Container:
    """Cabeçalho com gradiente petróleo -> ciano escuro, usado na Home e telas de destaque."""
    return ft.Container(
        height=height,
        padding=ft.padding.only(left=24, right=24, top=50, bottom=20),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[PRIMARY_DARK, "#14315C"],
        ),
        content=content,
    )


def shadow_card(content, padding=16, radius=16, bgcolor=CARD_BG, accent_color=None) -> ft.Container:
    """Card branco com sombra suave e, opcionalmente, uma faixa colorida à esquerda."""
    inner = ft.Container(padding=padding, content=content, expand=True)
    if accent_color:
        row = ft.Row(
            spacing=0,
            controls=[
                ft.Container(width=6, bgcolor=accent_color, border_radius=ft.border_radius.only(top_left=radius, bottom_left=radius)),
                inner,
            ],
        )
        card_content = row
    else:
        card_content = inner
    return ft.Container(
        bgcolor=bgcolor,
        border_radius=radius,
        content=card_content,
        shadow=ft.BoxShadow(blur_radius=12, color="#22000000", offset=ft.Offset(0, 4)),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )
