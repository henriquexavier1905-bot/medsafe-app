import flet as ft
from theme import PRIMARY_DARK, ACCENT, view
import db


def LoginView(page: ft.Page) -> ft.View:
    # Só é possível criar conta quando ainda não existe nenhuma — depois que
    # a primeira pessoa cria a conta, todo mundo entra só com login, usando
    # essas mesmas credenciais compartilhadas (sem opção de criar outra).
    sem_nenhum_usuario = not db.existe_algum_usuario()
    modo_cadastro = {"ativo": sem_nenhum_usuario}

    email = ft.TextField(
        label="E-mail",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=10,
        filled=True,
    )
    senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=10,
        filled=True,
    )
    erro = ft.Text("", color="red", size=12)
    titulo = ft.Text("", size=20, color="white", weight=ft.FontWeight.BOLD)
    subtitulo = ft.Text("", color="#B0BEC5", size=13)
    botao_principal = ft.ElevatedButton(width=400, height=45, bgcolor=ACCENT, color="white")
    link_alternar = ft.TextButton(style=ft.ButtonStyle(color=ACCENT))

    def atualizar_textos():
        if modo_cadastro["ativo"]:
            titulo.value = "Criar sua conta"
            subtitulo.value = "Primeiro acesso? Cadastre-se para começar."
            botao_principal.text = "Criar conta"
            link_alternar.text = "Já tem conta? Entrar"
        else:
            titulo.value = "Bem-vindo de volta"
            subtitulo.value = "Entre com sua conta para continuar."
            botao_principal.text = "Entrar"
            link_alternar.text = "Não tem conta? Criar conta"
        # Só mostra o link de alternar cadastro/login enquanto NENHUMA conta
        # existir ainda. Depois que a primeira é criada, ninguém mais pode
        # se auto-cadastrar — só entrar com a conta compartilhada.
        link_alternar.visible = sem_nenhum_usuario
        erro.value = ""
        page.update()

    def alternar_modo(e):
        modo_cadastro["ativo"] = not modo_cadastro["ativo"]
        atualizar_textos()

    def submeter(e):
        em = (email.value or "").strip()
        se = senha.value or ""
        if not em or not se:
            erro.value = "Preencha e-mail e senha."
            page.update()
            return
        if len(se) < 4:
            erro.value = "A senha precisa ter pelo menos 4 caracteres."
            page.update()
            return

        if modo_cadastro["ativo"]:
            criado = db.criar_usuario(em, se)
            if not criado:
                erro.value = "Já existe uma conta com esse e-mail."
                page.update()
                return
            page.usuario_atual = em.lower()
            page.go("/home")
        else:
            if db.autenticar(em, se):
                page.usuario_atual = em.lower()
                page.go("/home")
            else:
                erro.value = "E-mail ou senha incorretos."
                page.update()

    botao_principal.on_click = submeter
    link_alternar.on_click = alternar_modo
    atualizar_textos()

    return view(
        route="/login",
        bgcolor=PRIMARY_DARK,
        padding=24,
        controls=[
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=ACCENT, size=56),
                    ft.Text("MedSafe", size=26, color="white", weight=ft.FontWeight.BOLD),
                    titulo,
                    subtitulo,
                    ft.Container(height=6),
                    email,
                    senha,
                    erro,
                    botao_principal,
                    link_alternar,
                ],
            )
        ],
    )
