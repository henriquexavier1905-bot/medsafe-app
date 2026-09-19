import flet as ft

import db
from theme import build_theme, BG
from views.splash import SplashView
from views.login import LoginView
from views.home import HomeView
from views.medicamentos import MedicamentosListView, MedicamentoDetailView, MedicamentoFormView
from views.calculadora import CalculadoraView
from views.checklist import ChecklistView
from views.outras import (
    FavoritosView,
    MaisView,
    ProtocolosListView,
    ProtocoloDetailView,
    ProtocoloFormView,
    ConfiguracoesView,
    SobreView,
)
from views.extras import HistoricoView, EstatisticasView, LogView, InteracoesView

ROTAS_PUBLICAS = {"/", "/login"}


def main(page: ft.Page):
    db.init_db()
    page.usuario_atual = None
    page.title = "MedSafe"
    page.theme = build_theme()
    page.theme_mode = ft.ThemeMode.LIGHT  # ignora o modo escuro do sistema operacional
    page.bgcolor = BG
    # Tamanho de janela só faz sentido em modo desktop; em modo web/mobile isso é ignorado.
    try:
        page.window.width = 420
        page.window.height = 860
    except Exception:
        pass

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        route = page.route

        if route not in ROTAS_PUBLICAS and not getattr(page, "usuario_atual", None):
            page.views.append(LoginView(page))
            page.update()
            return

        if route == "/":
            page.views.append(SplashView(page))
        elif route == "/login":
            page.views.append(LoginView(page))
        elif route == "/home":
            page.views.append(HomeView(page))
        elif route.startswith("/medicamentos"):
            page.views.append(MedicamentosListView(page))
        elif route == "/medicamento/novo":
            page.views.append(MedicamentoFormView(page))
        elif route.startswith("/medicamento/") and route.endswith("/editar"):
            mid = route.split("/medicamento/")[1].split("/editar")[0]
            page.views.append(MedicamentoFormView(page, mid))
        elif route.startswith("/medicamento/"):
            mid = route.split("/medicamento/")[1]
            page.views.append(MedicamentoDetailView(page, mid))
        elif route == "/calculadora":
            page.views.append(CalculadoraView(page))
        elif route == "/checklist":
            page.views.append(ChecklistView(page))
        elif route == "/favoritos":
            page.views.append(FavoritosView(page))
        elif route == "/mais":
            page.views.append(MaisView(page))
        elif route == "/protocolo/novo":
            page.views.append(ProtocoloFormView(page))
        elif route.startswith("/protocolo/") and route.endswith("/editar"):
            pid = route.split("/protocolo/")[1].split("/editar")[0]
            page.views.append(ProtocoloFormView(page, pid))
        elif route.startswith("/protocolo/"):
            pid = route.split("/protocolo/")[1]
            page.views.append(ProtocoloDetailView(page, pid))
        elif route == "/protocolos":
            page.views.append(ProtocolosListView(page))
        elif route == "/configuracoes":
            page.views.append(ConfiguracoesView(page))
        elif route == "/sobre":
            page.views.append(SobreView(page))
        elif route == "/historico":
            page.views.append(HistoricoView(page))
        elif route == "/estatisticas":
            page.views.append(EstatisticasView(page))
        elif route == "/log":
            page.views.append(LogView(page))
        elif route == "/interacoes":
            page.views.append(InteracoesView(page))
        else:
            page.views.append(HomeView(page))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route or "/")


if __name__ == "__main__":
    # Compatível com flet >= 1.0 (ft.run) e versões anteriores (ft.app)
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
