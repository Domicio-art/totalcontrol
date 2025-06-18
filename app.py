from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import pyqrcode
import png
import os

app = Flask(__name__)
app.secret_key = 'TotalControlSegredo2025!'

# Configurações do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contato@totalcontrol.net.br'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or '3AiQ9LDBY66j'
mail = Mail(app)

# --- Funções para gerar o payload Pix e CRC-16 ---

def calcular_crc16(payload: str) -> str:
    pol = 0x1021
    res = 0xFFFF
    for ch in payload:
        res ^= ord(ch) << 8
        for _ in range(8):
            if res & 0x8000:
                res = ((res << 1) ^ pol) & 0xFFFF
            else:
                res = (res << 1) & 0xFFFF
    return f"{res:04X}"


def gerar_payload_pix(chave: str, nome: str, cidade: str, valor: float) -> str:
    # 1) Formata valor
    valor_str = f"{valor:.2f}"

    # 2) Merchant Account Information (GUI + chave)
    gui = "BR.GOV.BCB.PIX"
    sub_00 = f"00{len(gui):02}{gui}"
    sub_01 = f"01{len(chave):02}{chave}"
    mai = sub_00 + sub_01
    mai_full = f"26{len(mai):02}{mai}"

    # Campos fixos
    merchant_category = "52040000"
    currency = "5303986"
    amount = f"54{len(valor_str):02}{valor_str}"
    country = "5802BR"
    merchant_name = f"59{len(nome[:25]):02}{nome[:25]}"
    merchant_city = f"60{len(cidade[:15]):02}{cidade[:15]}"
    additional = "62070503***"

    # Monta payload sem CRC
    payload_sem_crc = (
        "000201"
        + mai_full
        + merchant_category
        + currency
        + amount
        + country
        + merchant_name
        + merchant_city
        + additional
        + "6304"
    )

    # Calcula CRC e retorna payload completo
    crc = calcular_crc16(payload_sem_crc)
    return payload_sem_crc + crc

# --- Gera e salva o QR Code ao iniciar ---
chave_pix = "contato@totalcontrol.net.br"
nome_recebedor = "TOTAL CONTROL"
cidade = "SAO PAULO"
valor = 199.00
payload = gerar_payload_pix(chave_pix, nome_recebedor, cidade, valor)
print("PIX COPIA E COLA:", payload)
qr = pyqrcode.create(payload)
# Garante que a pasta existe
os.makedirs(os.path.join(app.root_path, 'static', 'img'), exist_ok=True)
qr.png(os.path.join(app.root_path, 'static', 'img', 'pix_qr.png'), scale=6)

# --- Rotas do Flask ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funcionalidades')
def funcionalidades():
    return render_template('funcionalidades.html')

@app.route('/planos')
def planos():
    return render_template('planos.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        if not nome or not email or not mensagem:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('contato'))
        try:
            msg = Message(subject=f"Contato pelo site - {nome}",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['MAIL_USERNAME']])
            msg.body = f"Nome: {nome}\nEmail: {email}\nMensagem:\n{mensagem}"
            mail.send(msg)
            flash('Mensagem enviada com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao enviar a mensagem: {str(e)}", 'danger')
        return redirect(url_for('contato'))
    return render_template('contato.html')

@app.route('/pagar_pix')
def pagar_pix():
    return redirect(
        'https://wa.me/5511985463550?text=Quero%20assinar%20o%20Total%20Control%20via%20Pix'
    )

if __name__ == '__main__':
    app.run(debug=True)
