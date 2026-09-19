import flet as ft
from theme import app_bar, view, PRIMARY, ACCENT, DANGER, WARNING, CARD_BG, TEXT_MUTED
import db


def _fmt_data(iso_str: str) -> str:
    try:
        partes = iso_str.split("T")
        data = partes[0]
        hora = partes[1][:5] if len(partes) > 1 else ""
        d, m, a = data.split("-")[2], data.split("-")[1], data.split("-")[0]
        return f"{d}/{m}/{a} às {hora}"
    except Exception:
        return iso_str


def HistoricoView(page: ft.Page) -> ft.View:
    registros = db.listar_administracoes(limite=100)
    linhas = []
    for r in registros:
        linhas.append(
            ft.Container(
                bgcolor=CARD_BG,
                border_radius=12,
                padding=14,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color="#43A047", size=18),
                                ft.Text(r["detalhe"], weight=ft.FontWeight.W_600, expand=True),
                            ]
                        ),
                        ft.Text(f"{r['usuario']} · {_fmt_data(r['data_hora'])}", size=12, color=TEXT_MUTED),
                    ],
                ),
            )
        )
    if not linhas:
        linhas = [ft.Text("Nenhum checklist concluído ainda.", color=TEXT_MUTED)]

    return view(
        route="/historico",
        appbar=app_bar("Histórico de administração", page, show_back=True),
        padding=16,
        controls=linhas,
    )


def EstatisticasView(page: ft.Page) -> ft.View:
    s = db.estatisticas()

    def card(titulo, valor, color, icon):
        return ft.Container(
            col=6,
            bgcolor=CARD_BG,
            border_radius=14,
            padding=18,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Icon(icon, color=color, size=26),
                    ft.Text(str(valor), size=28, weight=ft.FontWeight.BOLD),
                    ft.Text(titulo, size=13, color=TEXT_MUTED),
                ],
            ),
            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000"),
        )

    return view(
        route="/estatisticas",
        appbar=app_bar("Estatísticas", page, show_back=True),
        padding=16,
        controls=[
            ft.ResponsiveRow(
                controls=[
                    card("Medicamentos cadastrados", s["total_medicamentos"], PRIMARY, ft.Icons.MEDICATION),
                    card("De alto risco", s["alto_risco"], DANGER, ft.Icons.WARNING_AMBER),
                    card("Protocolos", s["total_protocolos"], ACCENT, ft.Icons.DESCRIPTION_OUTLINED),
                    card("Checklists concluídos", s["checklists_concluidos"], "#43A047", ft.Icons.CHECK_CIRCLE_OUTLINE),
                    card("Favoritos", s["favoritos"], "#FBC02D", ft.Icons.STAR_BORDER),
                ]
            ),
        ],
    )


def LogView(page: ft.Page) -> ft.View:
    registros = db.listar_log(limite=100)
    acao_cor = {"criar": "#43A047", "editar": WARNING, "excluir": DANGER}
    acao_label = {"criar": "criou", "editar": "editou", "excluir": "excluiu"}

    linhas = []
    for r in registros:
        cor = acao_cor.get(r["acao"], TEXT_MUTED)
        linhas.append(
            ft.Container(
                bgcolor=CARD_BG,
                border_radius=12,
                padding=14,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=cor),
                                ft.Text(f"{r['usuario']} {acao_label.get(r['acao'], r['acao'])} \"{r['detalhe']}\"", expand=True, size=14),
                            ]
                        ),
                        ft.Text(_fmt_data(r["data_hora"]), size=12, color=TEXT_MUTED),
                    ],
                ),
            )
        )
    if not linhas:
        linhas = [ft.Text("Nenhuma alteração registrada ainda.", color=TEXT_MUTED)]

    return view(
        route="/log",
        appbar=app_bar("Log de alterações", page, show_back=True),
        padding=16,
        controls=linhas,
    )


def InteracoesView(page: ft.Page) -> ft.View:
    meds = db.listar()
    selecionados = set()
    checks_col = ft.Column(spacing=4)
    resultado_col = ft.Column(spacing=8)

    checkboxes = {}
    for m in meds:
        def on_change(e, mid=m["id"]):
            if e.control.value:
                selecionados.add(mid)
            else:
                selecionados.discard(mid)

        cb = ft.Checkbox(label=f"{m['nome']} ({m['apresentacao']})", on_change=on_change)
        checkboxes[m["id"]] = cb
        checks_col.controls.append(cb)

    def verificar(e):
        resultado_col.controls.clear()
        if len(selecionados) < 2:
            resultado_col.controls.append(ft.Text("Selecione pelo menos 2 medicamentos.", color=TEXT_MUTED))
        else:
            avisos = db.checar_interacoes_cruzadas(list(selecionados))
            if avisos:
                for a in avisos:
                    resultado_col.controls.append(
                        ft.Container(
                            bgcolor="#FFEBEE",
                            border_radius=10,
                            padding=12,
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.WARNING_AMBER, color=DANGER),
                                    ft.Text(a, color=DANGER, size=13, expand=True),
                                ]
                            ),
                        )
                    )
            else:
                resultado_col.controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color="#43A047"),
                            ft.Text("Nenhuma interação conhecida encontrada entre os selecionados.", color="#43A047"),
                        ]
                    )
                )
        page.update()

    return view(
        route="/interacoes",
        appbar=app_bar("Checagem de interações", page, show_back=True),
        padding=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text("Selecione os medicamentos que serão administrados juntos:", size=13, color=TEXT_MUTED),
            ft.Container(height=8),
            ft.Container(bgcolor=CARD_BG, border_radius=12, padding=8, content=checks_col),
            ft.Container(height=12),
            ft.ElevatedButton("Verificar interações", bgcolor=ACCENT, color="white", height=45, on_click=verificar),
            ft.Container(height=12),
            resultado_col,
        ],
    )
