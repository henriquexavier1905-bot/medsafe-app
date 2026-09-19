import math
import flet as ft
from theme import app_bar, bottom_nav, view, ACCENT, PRIMARY, CARD_BG, TEXT_MUTED


def _resultado_card():
    resultado = ft.Text("", size=26, weight=ft.FontWeight.BOLD, color=ACCENT)
    subtitulo = ft.Text("", size=12, color=TEXT_MUTED)
    card = ft.Container(
        bgcolor=CARD_BG,
        border_radius=14,
        padding=20,
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[resultado, subtitulo],
        ),
        shadow=ft.BoxShadow(blur_radius=8, color="#1A000000"),
    )
    return card, resultado, subtitulo


def CalculadoraView(page: ft.Page) -> ft.View:
    # ---------- Modo 1: Gotejamento ----------
    g_volume = ft.TextField(label="Volume (mL)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    g_tempo = ft.TextField(label="Tempo (horas)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    g_fator = ft.TextField(label="Fator de gotas (gotas/mL)", value="20", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    g_card, g_resultado, g_subtitulo = _resultado_card()

    def calcular_gotejamento(e):
        try:
            v = float(g_volume.value or 0)
            t = float(g_tempo.value or 0)
            fg = float(g_fator.value or 20)
            if t <= 0:
                raise ValueError
            gotas_min = (v * fg) / (t * 60)
            ml_h = v / t
            g_resultado.value = f"{gotas_min:.0f} gotas/min"
            g_subtitulo.value = f"Equivalente a {ml_h:.1f} mL/h"
        except ValueError:
            g_resultado.value = "Valores inválidos"
            g_subtitulo.value = "Confira volume e tempo informados"
        page.update()

    secao_gotejamento = ft.Column(
        controls=[
            g_volume, g_tempo, g_fator,
            ft.ElevatedButton("Calcular", bgcolor=ACCENT, color="white", height=45, on_click=calcular_gotejamento),
            ft.Container(height=16),
            g_card,
        ]
    )

    # ---------- Modo 2: Dose por peso (mg/kg) ----------
    p_peso = ft.TextField(label="Peso do paciente (kg)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    p_dose_kg = ft.TextField(label="Dose prescrita (mg/kg)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    p_card, p_resultado, p_subtitulo = _resultado_card()

    def calcular_peso(e):
        try:
            peso = float(p_peso.value or 0)
            dose_kg = float(p_dose_kg.value or 0)
            if peso <= 0:
                raise ValueError
            total = peso * dose_kg
            p_resultado.value = f"{total:.1f} mg"
            p_subtitulo.value = f"{dose_kg:g} mg/kg × {peso:g} kg"
        except ValueError:
            p_resultado.value = "Valores inválidos"
            p_subtitulo.value = "Confira peso e dose informados"
        page.update()

    secao_peso = ft.Column(
        controls=[
            p_peso, p_dose_kg,
            ft.ElevatedButton("Calcular", bgcolor=ACCENT, color="white", height=45, on_click=calcular_peso),
            ft.Container(height=16),
            p_card,
        ]
    )

    # ---------- Modo 3: Superfície corporal (Mosteller) ----------
    s_altura = ft.TextField(label="Altura (cm)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    s_peso = ft.TextField(label="Peso (kg)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    s_dose_m2 = ft.TextField(label="Dose por m² (opcional, mg/m²)", keyboard_type=ft.KeyboardType.NUMBER, filled=True)
    s_card, s_resultado, s_subtitulo = _resultado_card()

    def calcular_sc(e):
        try:
            altura = float(s_altura.value or 0)
            peso = float(s_peso.value or 0)
            if altura <= 0 or peso <= 0:
                raise ValueError
            sc = math.sqrt((altura * peso) / 3600)
            if s_dose_m2.value:
                dose_m2 = float(s_dose_m2.value)
                total = sc * dose_m2
                s_resultado.value = f"{total:.1f} mg"
                s_subtitulo.value = f"Superfície corporal: {sc:.2f} m² (fórmula de Mosteller)"
            else:
                s_resultado.value = f"{sc:.2f} m²"
                s_subtitulo.value = "Superfície corporal (fórmula de Mosteller)"
        except ValueError:
            s_resultado.value = "Valores inválidos"
            s_subtitulo.value = "Confira altura e peso informados"
        page.update()

    secao_sc = ft.Column(
        controls=[
            s_altura, s_peso, s_dose_m2,
            ft.ElevatedButton("Calcular", bgcolor=ACCENT, color="white", height=45, on_click=calcular_sc),
            ft.Container(height=16),
            s_card,
        ]
    )

    # ---------- Seletor de modo ----------
    secoes = {"gotejamento": secao_gotejamento, "peso": secao_peso, "sc": secao_sc}
    botoes = {}

    def mostrar(modo):
        for nome, secao in secoes.items():
            secao.visible = nome == modo
        for nome, btn in botoes.items():
            btn.bgcolor = ACCENT if nome == modo else CARD_BG
            btn.color = "white" if nome == modo else PRIMARY
        page.update()

    def botao_modo(nome, label):
        b = ft.ElevatedButton(label, on_click=lambda e, n=nome: mostrar(n), expand=True)
        botoes[nome] = b
        return b

    seletor = ft.Row(
        spacing=8,
        controls=[
            botao_modo("gotejamento", "Gotejamento"),
            botao_modo("peso", "Dose/peso"),
            botao_modo("sc", "Superfície"),
        ],
    )

    secao_gotejamento.visible = True
    secao_peso.visible = False
    secao_sc.visible = False
    botoes["gotejamento"].bgcolor = ACCENT
    botoes["gotejamento"].color = "white"
    botoes["peso"].bgcolor = CARD_BG
    botoes["peso"].color = PRIMARY
    botoes["sc"].bgcolor = CARD_BG
    botoes["sc"].color = PRIMARY

    return view(
        route="/calculadora",
        appbar=app_bar("Calculadora", page, show_back=True),
        navigation_bar=bottom_nav(page, 1),
        padding=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            seletor,
            ft.Container(height=12),
            secao_gotejamento,
            secao_peso,
            secao_sc,
        ],
    )
