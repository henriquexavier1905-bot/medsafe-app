import flet as ft
from theme import (
    app_bar, bottom_nav, view, gradient_header, shadow_card,
    PRIMARY, ACCENT, WARNING, DANGER, TEXT_MUTED,
)
import db


def _quick_card(icon, title, subtitle, color, on_click):
    return ft.Container(
        col=6,
        ink=True,
        on_click=on_click,
        content=shadow_card(
            ft.Column(
                spacing=4,
                controls=[
                    ft.Container(
                        width=44, height=44, border_radius=22, bgcolor=color,
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, color="white", size=22),
                    ),
                    ft.Container(height=4),
                    ft.Text(title, weight=ft.FontWeight.W_600, size=15),
                    ft.Text(subtitle, size=11, color=TEXT_MUTED),
                ],
            ),
            accent_color=color,
        ),
    )


def HomeView(page: ft.Page) -> ft.View:
    usuario = getattr(page, "usuario_atual", "") or "profissional"
    s = db.estatisticas()

    header = gradient_header(
        ft.Column(
            spacing=4,
            controls=[
                ft.Text("Olá 👋", size=15, color="#B0BEC5"),
                ft.Text(usuario, size=24, color="white", weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"{s['total_medicamentos']} medicamentos · {s['alto_risco']} de alto risco",
                    size=12, color="#90A4AE",
                ),
            ],
        ),
        height=140,
    )

    return view(
        route="/home",
        bottom_appbar=None,
        navigation_bar=bottom_nav(page, 0),
        padding=0,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            header,
            ft.Container(
                padding=16,
                content=ft.Column(
                    controls=[
                        ft.Text("Acesso rápido", weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(height=8),
                        ft.ResponsiveRow(
                            controls=[
                                _quick_card(ft.Icons.SEARCH, "Consultar", "medicamentos", PRIMARY, lambda e: page.go("/medicamentos")),
                                _quick_card(ft.Icons.CALCULATE, "Cálculos", "gotejamento e mais", ACCENT, lambda e: page.go("/calculadora")),
                                _quick_card(ft.Icons.CHECKLIST, "Checklist", "de segurança", WARNING, lambda e: page.go("/checklist")),
                                _quick_card(ft.Icons.WARNING_AMBER, "Alto risco", "atenção redobrada", DANGER, lambda e: page.go("/medicamentos")),
                                _quick_card(ft.Icons.SYNC_ALT, "Interações", "checagem cruzada", "#7B1FA2", lambda e: page.go("/interacoes")),
                                _quick_card(ft.Icons.HISTORY, "Histórico", "administrações", "#00838F", lambda e: page.go("/historico")),
                            ],
                        ),
                    ]
                ),
            ),
        ],
    )
