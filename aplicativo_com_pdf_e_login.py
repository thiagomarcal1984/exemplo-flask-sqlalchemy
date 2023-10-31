#Requirements
#Flask==3.0.0
#Flask-SQLAlchemy==3.1.1
#Flask-WTF==1.2.1
#xhtml2pdf==0.2.11

 

from flask import (
    Flask, 
    flash,
    render_template, 
    redirect, 
    request, 
    url_for, 
    send_file,
    session,
    make_response,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'

@app.route('/')
def index():
    return render_template('index.html')

from functools import wraps
def login_obrigatorio(rota_flask):
    @wraps(rota_flask)
    def testa_login(*args, **kwargs):
        if session.get('user') and len(session.get('user')) >= 3:
            return rota_flask(*args, *kwargs)
        return redirect(url_for('login'))
    return testa_login

@app.route('/imagem')
@login_obrigatorio
def imagem():
    return send_file('away.png')

@app.route('/xhtml2pdf')
@login_obrigatorio
def xhtml2pdf():
    from xhtml2pdf import pisa
    source_html = """
        <html>
        <head>
        <style>
            @page {
                size: a4 portrait;
                @frame header_frame {           /* Static Frame */
                    -pdf-frame-content: header_content;
                    left: 50pt; width: 512pt; top: 50pt; height: 40pt;
                }
                @frame content_frame {          /* Content Frame */
                    left: 50pt; width: 512pt; top: 90pt; height: 632pt;
                }
                @frame footer_frame {           /* Another static Frame */
                    -pdf-frame-content: footer_content;
                    left: 50pt; width: 512pt; top: 772pt; height: 20pt;
                }
            }
        </style>
        </head>

        <body>
            <!-- Content for Static Frame 'header_frame' -->
            <div id="header_content">Lyrics-R-Us</div>

            <!-- Content for Static Frame 'footer_frame' -->
            <div id="footer_content">(c) - page <pdf:pagenumber>
                of <pdf:pagecount>
            </div>

            <!-- HTML Content -->
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sed pulvinar urna. Quisque vitae bibendum lacus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Morbi sit amet justo eu neque pretium ullamcorper at sed neque. Phasellus sit amet pellentesque risus, in blandit ligula. Nam eu tristique quam, sit amet placerat quam. In porta, lacus ac aliquet accumsan, eros est posuere eros, sit amet elementum ligula tortor et eros. Aliquam ac aliquam enim. Duis vel nunc semper, semper orci hendrerit, egestas tellus. Suspendisse quis ante quis tortor ultrices ullamcorper. Vestibulum feugiat libero in nisi porta, sed cursus mi elementum. Sed id nisl hendrerit, consectetur neque non, maximus dolor. Ut mollis vel nisl quis luctus.</p>
        </body>
        </html>
    """
    result_file = open('temp.pdf', 'wb+')
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result
    result_file.close()
    return send_file(result_file.name)
    response = make_response(result_file)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=output.pdf"
    # Caso você precise redefinir os cabeçalhos HTML:
    if pisa_status.err:
        flash('Arquivo não foi gerado.', 'error')
        return redirect(url_for('index'))
    else:
        return response

@app.route('/logout')
def logout():
    session.clear()
    flash('Usuário saiu do sistema.', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    usuarios = {
        'tma' : 'senha',
        'zina' : 'away',
    }
    if request.method == 'POST':
        if request.form['senha'] == usuarios[request.form['user']]:
            session['user'] = request.form['user']
            endereco = url_for('index')
            flash('Usuário autenticado com sucesso.', 'success')
            return redirect(endereco)
        else: 
            flash('Usuário não autenticado.', 'error')
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
