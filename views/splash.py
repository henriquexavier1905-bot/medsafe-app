import flet as ft
from theme import PRIMARY_DARK, ACCENT, view


def SplashView(page: ft.Page) -> ft.View:
    # Navega automaticamente após ~1.8s (dispara já na construção da tela)
    page.run_task(_delay_and_go, page)

    return view(
        route="/",
        bgcolor=PRIMARY_DARK,
        padding=0,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=90,
                            height=90,
                            border_radius=45,
                            bgcolor=ACCENT,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color="white", size=48),
                        ),
                        ft.Text("MedSafe", size=30, color="white", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Segurança em cada administração",
                            color="#B0BEC5",
                            size=14,
                        ),
                        ft.ProgressRing(color=ACCENT, width=24, height=24),
                    ],
                ),
            )
        ],
    )


async def _delay_and_go(page: ft.Page):
    import asyncio

    await asyncio.sleep(1.8)
    page.go("/login")
