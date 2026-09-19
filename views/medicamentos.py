import datetime
import flet as ft
from theme import app_bar, bottom_nav, view, PRIMARY, ACCENT, DANGER, WARNING, CARD_BG, TEXT_MUTED
import db


def _usuario(page: ft.Page) -> str:
    return getattr(page, "usuario_atual", "") or ""


def _validade_status(validade: str):
    """Retorna (texto, cor) se a validade estiver próxima ou vencida, senão None."""
    if not validade:
        return None
    try:
        d = datetime.date.fromisoformat(validade)
    except ValueError:
        return None
    hoje = datetime.date.today()
    dias = (d - hoje).days
    if dias < 0:
        return (f"Vencido em {d.strftime('%d/%m/%Y')}", DANGER)
    if dias <= 30:
        return (f"Vence em {dias} dia(s) — {d.strftime('%d/%m/%Y')}", WARNING)
    return None


# ---------- LISTA ----------

def MedicamentosListView(page: ft.Page) -> ft.View:
    resultados = ft.Column(spacing=8)

    def render(termo="", apenas_alto_risco=False):
        resultados.controls.clear()
        for m in db.listar(termo, apenas_alto_risco=apenas_alto_risco):
            resultados.controls.append(_med_row(page, m))
        if not resultados.controls:
            resultados.controls.append(ft.Text("Nenhum medicamento encontrado.", color=TEXT_MUTED))
        page.update()

    busca = ft.TextField(
        hint_text="Digite o nome do medicamento",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        filled=True,
    )
    chk_risco = ft.Checkbox(label="Somente alto risco")
    busca.on_change = lambda e: render(busca.value, chk_risco.value)
    chk_risco.on_change = lambda e: render(busca.value, chk_risco.value)

    render()

    return view(
        route="/medicamentos",
        appbar=app_bar("Consultar medicamento", page, show_back=True),
        navigation_bar=bottom_nav(page, 0),
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD, bgcolor=ACCENT, on_click=lambda e: page.go("/medicamento/novo")
        ),
        padding=16,
        controls=[busca, chk_risco, ft.Container(height=4), resultados],
    )


def _med_row(page: ft.Page, m: dict) -> ft.Container:
    validade_info = _validade_status(m.get("validade", ""))
    linhas = [
        ft.Row(
            controls=[
                ft.Icon(ft.Icons.MEDICATION, color=DANGER if m["alto_risco"] else PRIMARY),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(m["nome"], weight=ft.FontWeight.W_600),
                        ft.Text(m["apresentacao"], size=12, color=TEXT_MUTED),
                    ],
                ),
                ft.Icon(ft.Icons.STAR, color="#FBC02D", size=18) if m["favorito"] else ft.Container(width=18),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED),
            ]
        )
    ]
    if validade_info:
        texto, cor = validade_info
        linhas.append(ft.Text(texto, size=11, color=cor, weight=ft.FontWeight.W_600))

    return ft.Container(
        bgcolor=CARD_BG,
        border_radius=12,
        padding=14,
        ink=True,
        on_click=lambda e, mid=m["id"]: page.go(f"/medicamento/{mid}"),
        content=ft.Column(spacing=4, controls=linhas),
    )


# ---------- DETALHE ----------

def MedicamentoDetailView(page: ft.Page, mid: str) -> ft.View:
    m = db.obter(mid)
    if not m:
        return view(
            route=f"/medicamento/{mid}",
            appbar=app_bar("Medicamento não encontrado", page, show_back=True),
            controls=[ft.Text("Medicamento não encontrado ou foi excluído.")],
        )

    def secao(titulo, itens):
        if not itens:
            return ft.Container()
        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, weight=ft.FontWeight.BOLD, size=14),
                *[ft.Row(controls=[ft.Icon(ft.Icons.CIRCLE, size=6, color=TEXT_MUTED), ft.Text(i, size=13, expand=True)]) for i in itens],
                ft.Divider(),
            ],
        )

    def confirmar_exclusao(e):
        def excluir_de_fato(e2):
            db.excluir(mid, usuario=_usuario(page))
            page.close(dlg)
            page.go("/medicamentos")

        dlg = ft.AlertDialog(
            title=ft.Text("Excluir medicamento?"),
            content=ft.Text(f"Isso vai apagar \"{m['nome']}\" permanentemente."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e2: page.close(dlg)),
                ft.TextButton("Excluir", style=ft.ButtonStyle(color=DANGER), on_click=excluir_de_fato),
            ],
        )
        page.open(dlg)

    avisos = []
    if m["alto_risco"]:
        avisos.append(
            ft.Container(
                bgcolor="#FFEBEE",
                border_radius=10,
                padding=12,
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER, color=DANGER),
                        ft.Text(
                            "Medicamento de alto risco — exige dupla checagem antes da administração.",
                            color=DANGER,
                            size=13,
                            expand=True,
                        ),
                    ]
                ),
            )
        )
    validade_info = _validade_status(m.get("validade", ""))
    if validade_info:
        texto, cor = validade_info
        avisos.append(
            ft.Container(
                bgcolor="#FFF3E0",
                border_radius=10,
                padding=12,
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.EVENT_BUSY, color=cor),
                        ft.Text(texto, color=cor, size=13, expand=True),
                    ]
                ),
            )
        )
    if avisos:
        avisos.append(ft.Container(height=8))

    info_extra = []
    if m.get("categoria"):
        info_extra.append(f"Categoria: {m['categoria']}")
    if m.get("validade"):
        info_extra.append(f"Validade: {m['validade']}")

    return view(
        route=f"/medicamento/{mid}",
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/medicamentos")),
            title=ft.Text(m["nome"], weight=ft.FontWeight.BOLD),
            bgcolor="#0F2340",
            color="white",
            actions=[
                ft.IconButton(
                    ft.Icons.STAR if m["favorito"] else ft.Icons.STAR_BORDER,
                    icon_color="#FBC02D" if m["favorito"] else "white",
                    on_click=lambda e: (db.alternar_favorito(mid), page.go(f"/medicamento/{mid}")),
                ),
                ft.IconButton(ft.Icons.EDIT, icon_color="white", on_click=lambda e: page.go(f"/medicamento/{mid}/editar")),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="white", on_click=confirmar_exclusao),
            ],
        ),
        padding=16,
        controls=[
            *avisos,
            ft.Text(m["apresentacao"], color=TEXT_MUTED, size=13),
            ft.Text(" · ".join(info_extra), color=TEXT_MUTED, size=12) if info_extra else ft.Container(),
            ft.Container(height=8),
            secao("Apresentações", m["apresentacoes"]),
            secao("Via de administração", m["via_administracao"]),
            secao("Diluição / Infusão", [x for x in [m["diluicao"], m["capacidade_infusao"]] if x]),
            secao("Cuidados de enfermagem", m["cuidados"]),
            secao("Interações medicamentosas", m["interacoes"]),
        ],
    )


# ---------- CADASTRAR / EDITAR ----------

def MedicamentoFormView(page: ft.Page, mid: str = None) -> ft.View:
    """mid=None => cadastro novo. mid=<id> => edição."""
    existente = db.obter(mid) if mid else None
    eh_edicao = existente is not None

    def lista_para_texto(lst):
        return "\n".join(lst or [])

    def texto_para_lista(txt):
        return [linha.strip() for linha in (txt or "").split("\n") if linha.strip()]

    nome = ft.TextField(label="Nome do medicamento *", value=existente["nome"] if eh_edicao else "", filled=True)
    apresentacao = ft.TextField(
        label="Resumo da apresentação (ex: 500mg/mL)", value=existente["apresentacao"] if eh_edicao else "", filled=True
    )
    categoria = ft.TextField(
        label="Categoria (ex: Antibiótico, Analgésico)", value=existente.get("categoria", "") if eh_edicao else "", filled=True
    )
    validade = ft.TextField(
        label="Validade (AAAA-MM-DD, opcional)", value=existente.get("validade", "") if eh_edicao else "", filled=True,
        hint_text="ex: 2027-03-31",
    )
    alto_risco = ft.Switch(label="Medicamento de alto risco", value=existente["alto_risco"] if eh_edicao else False)
    apresentacoes = ft.TextField(
        label="Apresentações (uma por linha)",
        value=lista_para_texto(existente["apresentacoes"]) if eh_edicao else "",
        multiline=True,
        min_lines=2,
        filled=True,
    )
    via_administracao = ft.TextField(
        label="Vias de administração (uma por linha)",
        value=lista_para_texto(existente["via_administracao"]) if eh_edicao else "",
        multiline=True,
        min_lines=2,
        filled=True,
    )
    diluicao = ft.TextField(label="Diluição", value=existente["diluicao"] if eh_edicao else "", filled=True)
    capacidade_infusao = ft.TextField(
        label="Infusão / velocidade", value=existente["capacidade_infusao"] if eh_edicao else "", filled=True
    )
    cuidados = ft.TextField(
        label="Cuidados de enfermagem (um por linha)",
        value=lista_para_texto(existente["cuidados"]) if eh_edicao else "",
        multiline=True,
        min_lines=3,
        filled=True,
    )
    interacoes = ft.TextField(
        label="Interações medicamentosas (uma por linha)",
        value=lista_para_texto(existente["interacoes"]) if eh_edicao else "",
        multiline=True,
        min_lines=2,
        filled=True,
    )
    erro = ft.Text("", color=DANGER, size=12)

    def salvar(e):
        if not nome.value.strip():
            erro.value = "Informe o nome do medicamento."
            page.update()
            return
        if validade.value.strip():
            try:
                datetime.date.fromisoformat(validade.value.strip())
            except ValueError:
                erro.value = "Data de validade inválida. Use o formato AAAA-MM-DD."
                page.update()
                return

        dados = {
            "nome": nome.value.strip(),
            "apresentacao": apresentacao.value.strip(),
            "categoria": categoria.value.strip(),
            "validade": validade.value.strip(),
            "alto_risco": alto_risco.value,
            "apresentacoes": texto_para_lista(apresentacoes.value),
            "via_administracao": texto_para_lista(via_administracao.value),
            "diluicao": diluicao.value.strip(),
            "capacidade_infusao": capacidade_infusao.value.strip(),
            "cuidados": texto_para_lista(cuidados.value),
            "interacoes": texto_para_lista(interacoes.value),
        }

        usuario = _usuario(page)
        if eh_edicao:
            db.atualizar(mid, dados, usuario=usuario)
            page.go(f"/medicamento/{mid}")
        else:
            novo_id = db.criar(dados, usuario=usuario)
            page.go(f"/medicamento/{novo_id}")

    return view(
        route=f"/medicamento/{mid}/editar" if eh_edicao else "/medicamento/novo",
        appbar=app_bar("Editar medicamento" if eh_edicao else "Novo medicamento", page, show_back=True),
        padding=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            nome,
            apresentacao,
            categoria,
            validade,
            alto_risco,
            apresentacoes,
            via_administracao,
            diluicao,
            capacidade_infusao,
            cuidados,
            interacoes,
            erro,
            ft.ElevatedButton("Salvar", bgcolor=ACCENT, color="white", height=45, on_click=salvar),
        ],
    )
