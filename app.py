from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mail import Mail, Message
import pyqrcode
import png
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'TotalControlSegredo2025!'  # Necessário para usar flash() e sessões

# Configurações do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contato@totalcontrol.net.br'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or '3AiQ9LDBY66j'

mail = Mail(app)

# === Funções para gerar payload Pix ===

def gerar_payload_pix(chave, nome, cidade, valor):
    valor_formatado = f"{valor:.2f}"
    payload_sem_crc = (
        "000201"
        "26360014BR.GOV.BCB.PIX"
        f"0114{chave}"
        "52040000"
        "5303986"
        f"540{len(valor_formatado):02}{valor_formatado}"
        "5802BR"
        f"5913{nome[:13]}"
        f"6009{cidade[:9]}"
        "62070503***"
    )
    crc = calcular_crc16(payload_sem_crc + "6304")
    return payload_sem_crc + f"6304{crc}"

def calcular_crc16(payload):
    polinomio = 0x1021
    resultado = 0xFFFF
    for char in payload:
        resultado ^= ord(char) << 8
        for _ in range(8):
            if resultado & 0x8000:
                resultado = (resultado << 1) ^ polinomio
            else:
                resultado <<= 1
            resultado &= 0xFFFF
    return format(resultado, '04X')

# === Dados do Pix e geração do QR Code ===

chave_pix = "construsilva.loja01@gmail.com"
nome_recebedor = "TOTAL CONTROL"
cidade = "SAO PAULO"
valor = 199.00

payload = gerar_payload_pix(chave_pix, nome_recebedor, cidade, valor)
qr = pyqrcode.create(payload)
qr.png("static/img/pix_qr.png", scale=6)

# === Rotas principais ===

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
            flash(f'Erro ao enviar a mensagem: {str(e)}', 'danger')

        return redirect(url_for('contato'))

    return render_template('contato.html')

@app.route('/pagar_pix')
def pagar_pix():
    return redirect('https://wa.me/seu_numero_whatsapp?text=Quero%20assinar%20o%20Total%20Control%20via%20Pix')

if __name__ == '__main__':
    app.run(debug=True)
