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
<<<<<<< HEAD
=======

import pyqrcode
import png


# Chave Pix e dados fixos
chave_pix = "construsilva.loja01@gmail.com"
nome_recebedor = "TOTAL CONTROL"
cidade = "SAO PAULO"
valor = "199.00"  # valor fixo em reais, pode mudar

# Payload no padrão Pix Copia e Cola
payload = f"""00020126360014BR.GOV.BCB.PIX0114{chave_pix}520400005303986540{valor}5802BR5913{nome_recebedor}6009{cidade}62070503***6304"""

# Criar e salvar QR Code como PNG
qr = pyqrcode.create(payload)
qr.png("static/img/pix_qr.png", scale=6)

>>>>>>> 1bd739c (Melhorias na seção de pagamento via Pix com QR e email atualizado)

# Configurações do Flask-Mail (substitua pelos seus dados)
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contato@totalcontrol.net.br'
app.config['MAIL_PASSWORD'] = '3AiQ9LDBY66j'

mail = Mail(app)



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
