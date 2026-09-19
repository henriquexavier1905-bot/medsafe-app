import flet as ft
from theme import app_bar, bottom_nav, view, PRIMARY, ACCENT, DANGER, CARD_BG, TEXT_MUTED
import db


# ---------- FAVORITOS ----------

def FavoritosView(page: ft.Page) -> ft.View:
    favoritos = db.listar(apenas_favoritos=True)

    linhas = []
    for m in favoritos:
        linhas.append(
            ft.Container(
                bgcolor=CARD_BG,
                border_radius=12,
                padding=14,
                ink=True,
                on_click=lambda e, mid=m["id"]: page.go(f"/medicamento/{mid}"),
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.STAR, color="#FBC02D"),
                        ft.Text(m["nome"], expand=True, weight=ft.FontWeight.W_600),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED),
                    ]
                ),
            )
        )

    if not linhas:
        linhas = [ft.Text("Nenhum favorito ainda.", color=TEXT_MUTED)]

    return view(
        route="/favoritos",
        appbar=app_bar("Favoritos", page, show_back=True),
        navigation_bar=bottom_nav(page, 3),
        padding=16,
        controls=linhas,
    )


# ---------- MAIS (menu) ----------

def MaisView(page: ft.Page) -> ft.View:
    opcoes = [
        ("Interações cruzadas", ft.Icons.SYNC_ALT, "/interacoes"),
        ("Histórico de administração", ft.Icons.HISTORY, "/historico"),
        ("Estatísticas", ft.Icons.BAR_CHART, "/estatisticas"),
        ("Log de alterações", ft.Icons.FACT_CHECK_OUTLINED, "/log"),
        ("Protocolos", ft.Icons.DESCRIPTION_OUTLINED, "/protocolos"),
        ("Configurações", ft.Icons.SETTINGS_OUTLINED, "/configuracoes"),
        ("Sobre o app", ft.Icons.INFO_OUTLINE, "/sobre"),
    ]
    linhas = [
        ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=14,
            ink=True,
            on_click=lambda e, rota=rota: page.go(rota),
            content=ft.Row(controls=[ft.Icon(icon, color=PRIMARY), ft.Text(nome, expand=True), ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED)]),
        )
        for nome, icon, rota in opcoes
    ]

    def sair(e):
        page.usuario_atual = None
        page.go("/login")

    usuario_atual = getattr(page, "usuario_atual", "") or ""
    linhas.append(ft.Container(height=8))
    linhas.append(
        ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=14,
            ink=True,
            on_click=sair,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=DANGER),
                    ft.Text(f"Sair ({usuario_atual})" if usuario_atual else "Sair", expand=True, color=DANGER),
                ]
            ),
        )
    )

    return view(
        route="/mais",
        appbar=app_bar("Mais", page, show_back=True),
        navigation_bar=bottom_nav(page, 4),
        padding=16,
        controls=linhas,
    )


# ---------- PROTOCOLOS ----------

def ProtocolosListView(page: ft.Page) -> ft.View:
    linhas = []
    for p in db.listar_protocolos():
        linhas.append(
            ft.Container(
                bgcolor=CARD_BG,
                border_radius=12,
                padding=14,
                ink=True,
                on_click=lambda e, pid=p["id"]: page.go(f"/protocolo/{pid}"),
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color=PRIMARY),
                        ft.Text(p["titulo"], expand=True, weight=ft.FontWeight.W_600),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED),
                    ]
                ),
            )
        )
    if not linhas:
        linhas = [ft.Text("Nenhum protocolo cadastrado.", color=TEXT_MUTED)]

    return view(
        route="/protocolos",
        appbar=app_bar("Protocolos", page, show_back=True),
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD, bgcolor=ACCENT, on_click=lambda e: page.go("/protocolo/novo")
        ),
        padding=16,
        controls=linhas,
    )


def ProtocoloDetailView(page: ft.Page, pid: str) -> ft.View:
    p = db.obter_protocolo(pid)
    if not p:
        return view(
            route=f"/protocolo/{pid}",
            appbar=app_bar("Não encontrado", page, show_back=True),
            controls=[ft.Text("Protocolo não encontrado ou foi excluído.")],
        )

    def confirmar_exclusao(e):
        def excluir_de_fato(e2):
            db.excluir_protocolo(pid)
            page.close(dlg)
            page.go("/protocolos")

        dlg = ft.AlertDialog(
            title=ft.Text("Excluir protocolo?"),
            content=ft.Text(f"Isso vai apagar \"{p['titulo']}\" permanentemente."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e2: page.close(dlg)),
                ft.TextButton("Excluir", style=ft.ButtonStyle(color=DANGER), on_click=excluir_de_fato),
            ],
        )
        page.open(dlg)

    return view(
        route=f"/protocolo/{pid}",
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/protocolos")),
            title=ft.Text(p["titulo"], weight=ft.FontWeight.BOLD),
            bgcolor="#0F2340",
            color="white",
            actions=[
                ft.IconButton(ft.Icons.EDIT, icon_color="white", on_click=lambda e: page.go(f"/protocolo/{pid}/editar")),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="white", on_click=confirmar_exclusao),
            ],
        ),
        padding=16,
        controls=[ft.Text(p["conteudo"], size=14)],
    )


def ProtocoloFormView(page: ft.Page, pid: str = None) -> ft.View:
    existente = db.obter_protocolo(pid) if pid else None
    eh_edicao = existente is not None

    titulo = ft.TextField(label="Título *", value=existente["titulo"] if eh_edicao else "", filled=True)
    conteudo = ft.TextField(
        label="Conteúdo do protocolo",
        value=existente["conteudo"] if eh_edicao else "",
        multiline=True,
        min_lines=6,
        filled=True,
    )
    erro = ft.Text("", color=DANGER, size=12)

    def salvar(e):
        if not titulo.value.strip():
            erro.value = "Informe um título."
            page.update()
            return
        if eh_edicao:
            db.atualizar_protocolo(pid, titulo.value.strip(), conteudo.value.strip())
            page.go(f"/protocolo/{pid}")
        else:
            novo_id = db.criar_protocolo(titulo.value.strip(), conteudo.value.strip())
            page.go(f"/protocolo/{novo_id}")

    return view(
        route=f"/protocolo/{pid}/editar" if eh_edicao else "/protocolo/novo",
        appbar=app_bar("Editar protocolo" if eh_edicao else "Novo protocolo", page, show_back=True),
        padding=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[titulo, conteudo, erro, ft.ElevatedButton("Salvar", bgcolor=ACCENT, color="white", height=45, on_click=salvar)],
    )


# ---------- CONFIGURAÇÕES ----------

def ConfiguracoesView(page: ft.Page) -> ft.View:
    def ligado(chave):
        return db.get_config(chave, "0") == "1"

    def linha_switch(label, chave, icone):
        sw = ft.Switch(value=ligado(chave))

        def mudou(e):
            db.set_config(chave, "1" if sw.value else "0")

        sw.on_change = mudou
        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=14,
            content=ft.Row(controls=[ft.Icon(icone, color=PRIMARY), ft.Text(label, expand=True), sw]),
        )

    return view(
        route="/configuracoes",
        appbar=app_bar("Configurações", page, show_back=True),
        padding=16,
        controls=[
            linha_switch("Notificações", "notificacoes", ft.Icons.NOTIFICATIONS_OUTLINED),
            linha_switch("Modo escuro", "modo_escuro", ft.Icons.DARK_MODE_OUTLINED),
            ft.Container(height=8),
            ft.Text("Idioma: Português (Brasil)", size=13, color=TEXT_MUTED),
        ],
    )


# ---------- SOBRE ----------

def SobreView(page: ft.Page) -> ft.View:
    return view(
        route="/sobre",
        appbar=app_bar("Sobre o app", page, show_back=True),
        padding=16,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=ACCENT, size=48),
                    ft.Text("MedSafe", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Versão 1.0.0", size=12, color=TEXT_MUTED),
                    ft.Container(height=12),
                    ft.Text(
                        "Aplicativo de apoio à segurança na administração de medicamentos, "
                        "com consulta rápida, cálculo de gotejamento e checklist de verificação.",
                        size=13,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            )
        ],
    )
