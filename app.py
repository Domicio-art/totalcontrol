from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import pyqrcode
import png
from flask import send_file
from io import BytesIO


app = Flask(__name__)
app.secret_key = 'TotalControlSegredo2025!'  # Necessário para usar flash() e sessões
import os
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Configurações do Flask-Mail (substitua pelos seus dados)
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contato@totalcontrol.net.br'
app.config['MAIL_PASSWORD'] = '3AiQ9LDBY66j'

mail = Mail(app)

@app.route('/gerar_pix/<float:valor>')
def gerar_pix(valor):
    # Substitua com seus dados reais
    chave_pix = 'construsilva.loja01@gmail.com'
    nome_recebedor = 'CONSTRUSILVA LTDA'
    cidade = 'São Paulo'

    payload = f"""
    000201
    26{len(f'0014br.gov.bcb.pix01{len(chave_pix):02}{chave_pix}')}0014br.gov.bcb.pix01{len(chave_pix):02}{chave_pix}
    52040000
    5303986
    540{len(f'{valor:.2f}'):02}{valor:.2f}
    5802BR
    59{len(nome_recebedor):02}{nome_recebedor}
    60{len(cidade):02}{cidade}
    62070503***        
    """.replace("\n", "").replace(" ", "")

    # CRC-16 do Pix
    from crc16 import crc16xmodem
    payload_sem_crc = payload + "6304"
    crc = format(crc16xmodem(payload_sem_crc.encode('utf-8')), '04X')
    payload_completo = payload + "6304" + crc

    # Gerar QR code
    qr = pyqrcode.create(payload_completo)
    buffer = BytesIO()
    qr.png(buffer, scale=6)
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


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


# Rota da página de contato
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

            corpo = f"Nome: {nome}\nEmail: {email}\nMensagem:\n{mensagem}"
            msg.body = corpo
            mail.send(msg)
            flash('Mensagem enviada com sucesso!', 'success')
            return redirect(url_for('contato'))
        except Exception as e:
            flash(f'Erro ao enviar a mensagem: {str(e)}', 'danger')
            return redirect(url_for('contato'))

    return render_template('contato.html')


@app.route('/pagar_pix')
def pagar_pix():
    # Redireciona para o WhatsApp após exibir a opção de pagar via Pix
    return redirect('https://wa.me/seu_numero_whatsapp?text=Quero%20assinar%20o%20Total%20Control%20via%20Pix')

if __name__ == '__main__':
    app.run(debug=True)
