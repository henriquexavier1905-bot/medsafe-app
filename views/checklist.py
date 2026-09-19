import flet as ft
from theme import app_bar, bottom_nav, view, ACCENT, WARNING, CARD_BG, TEXT_MUTED
import db

ITENS_CHECKLIST = [
    "Paciente certo",
    "Medicamento certo",
    "Dose certa",
    "Via certa",
    "Horário certo",
    "Registro da administração",
    "Orientação ao paciente",
    "Validade e integridade do medicamento",
]


def ChecklistView(page: ft.Page) -> ft.View:
    medicamento_campo = ft.TextField(
        label="Medicamento (opcional)", hint_text="ex: Dipirona 500mg", filled=True
    )
    checks = [ft.Checkbox(label=item, value=False) for item in ITENS_CHECKLIST]
    aviso = ft.Container(visible=False)

    def verificar(e):
        marcados = sum(1 for c in checks if c.value)
        if marcados == len(checks):
            aviso.content = ft.Row(
                controls=[ft.Icon(ft.Icons.CHECK_CIRCLE, color="#43A047"), ft.Text("Checklist completo. Administração segura.", color="#43A047")]
            )
            usuario = getattr(page, "usuario_atual", "") or "desconhecido"
            nome_med = medicamento_campo.value.strip() or "medicamento não especificado"
            db.registrar_administracao(usuario, f"Checklist completo: {nome_med}")
        else:
            aviso.content = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER, color=WARNING),
                    ft.Text(f"Faltam {len(checks) - marcados} itens antes de administrar.", color=WARNING, expand=True),
                ]
            )
        aviso.visible = True
        page.update()

    return view(
        route="/checklist",
        appbar=app_bar("Checklist de segurança", page, show_back=True),
        navigation_bar=bottom_nav(page, 2),
        padding=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text("Antes de administrar, confira os itens abaixo:", size=13, color=TEXT_MUTED),
            ft.Container(height=8),
            medicamento_campo,
            ft.Container(height=8),
            ft.Container(
                bgcolor=CARD_BG,
                border_radius=14,
                padding=8,
                content=ft.Column(controls=checks),
                shadow=ft.BoxShadow(blur_radius=8, color="#1A000000"),
            ),
            ft.Container(height=12),
            ft.ElevatedButton("Verificar checklist", bgcolor=ACCENT, color="white", height=45, on_click=verificar),
            aviso,
        ],
    )
