# MedSafe — projeto inicial em Flet

Base funcional do app mostrado no mockup, usando **Flet** (Python → Flutter). Já inclui a navegação principal e 6 telas implementadas; as demais (Protocolos, Configurações, Sobre) estão como placeholders em `views/outras.py`.

## Como rodar

```bash
pip install flet
python main.py
```

Isso abre o app como uma janela desktop (tamanho de celular, 420x860). Para rodar como app mobile/web:

```bash
flet run main.py           # detecta a plataforma
python main.py             # roda como app desktop
flet build apk              # gera .apk Android (precisa Android SDK configurado)
flet build ipa               # gera .ipa iOS (precisa macOS + Xcode)
```

Para testar no navegador rapidamente:
```python
# em main.py, troque a última linha por:
ft.app(target=main, view=ft.AppView.WEB_BROWSER)
```

## Estrutura do projeto

```
medsafe_flet/
├── main.py              # roteamento entre telas (equivalente ao Navigator)
├── theme.py             # cores, AppBar e NavigationBar reutilizáveis
├── data.py              # dados de exemplo dos medicamentos (mock)
├── views/
│   ├── splash.py        # 1. Tela de splash
│   ├── login.py         # 2. Login/Cadastro
│   ├── home.py           # 3. Tela inicial (menu de atalhos)
│   ├── medicamentos.py    # 4 e 5. Consulta + Ficha do medicamento
│   ├── calculadora.py     # 7/8. Cálculo de gotejamento
│   ├── checklist.py       # 9. Checklist de segurança
│   └── outras.py          # 12/13/14. Favoritos e Mais (placeholders)
└── assets/                # ícones/imagens (adicione aqui e referencie por "assets/nome.png")
```

## Como o roteamento funciona

O Flet usa `page.route` como uma URL. Cada tela retorna um `ft.View`, e `main.py` decide qual `View` mostrar com base na rota, de forma parecida com um `Navigator` do Flutter:

```python
page.go("/calculadora")       # navega
page.go(f"/medicamento/{id}") # navega com parâmetro dinâmico
page.go_back()                 # ou o botão de voltar do AppBar
```

## Próximos passos sugeridos

1. **Persistência real**: troque `data.py` (mock) por SQLite (`sqlite3` embutido) ou uma API própria.
2. **Autenticação**: a tela de login está com um "TODO" — plugue Firebase Auth, Supabase, ou seu backend.
3. **Favoritos persistentes**: hoje é um `set()` em memória (`views/outras.py`); use `page.client_storage` (Flet) para salvar entre sessões, ou banco de dados.
4. **Telas restantes**: Protocolos, Configurações e Sobre — o padrão já está estabelecido, é só copiar a estrutura de `checklist.py` ou `medicamentos.py`.
5. **Ícone/splash real**: troque os `ft.Icon` por imagens em `assets/` usando `ft.Image(src="assets/logo.png")`.
6. **Empacotar para celular**: use `flet build apk` / `flet build ipa` quando o app estiver pronto (exige configurar os SDKs nativos).

## Dica sobre o design

O mockup usa cantos bem arredondados, sombras suaves e uma paleta azul petróleo + ciano — isso já está em `theme.py` (`PRIMARY_DARK`, `ACCENT`). Para chegar mais perto do visual do Figma, ajuste esses valores hexadecimais e o `border_radius` dos `Container`.
