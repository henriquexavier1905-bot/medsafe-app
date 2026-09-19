import flet as ft
import db
from main import main as app_main

# Mesmo app do main.py, mas servido como página web na rede local,
# para abrir no navegador do tablet (Chrome) sem precisar instalar nada.
#
# Como usar:
#   1. Rode: python main_web.py
#   2. No terminal vai aparecer algo como "App running at http://0.0.0.0:8550"
#   3. Descubra o IP do seu PC na rede local: no PowerShell, rode "ipconfig"
#      e procure "Endereço IPv4" (algo como 192.168.0.15)
#   4. No tablet (mesma rede Wi-Fi do PC), abra o Chrome e digite:
#      http://SEU_IP_AQUI:8550   (ex: http://192.168.0.15:8550)
#
# Observação: o PC precisa continuar ligado e com esse script rodando
# enquanto o tablet estiver usando o app. Feche com Ctrl+C no terminal.

if __name__ == "__main__":
    db.init_db()
    ft.app(target=app_main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)
