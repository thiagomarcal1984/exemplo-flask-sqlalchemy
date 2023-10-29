from flask import Flask, render_template, url_for, redirect, flash, request

app = Flask(__name__)

app.config.from_pyfile('config.py')

from models import db, reset_bd, initialize, Pessoa, Telefone

@app.route('/')
def index():
    return redirect(url_for('pessoas'))    

@app.route('/pessoas')
def pessoas():
    pessoas = db.session.execute(db.select(Pessoa)).scalars()
    return render_template(
        'pessoas/lista.html',
        pessoas = pessoas
    )

@app.route('/pessoas/inserir', methods=['GET', 'POST'])
def inserir_pessoa():
    if request.method == 'POST':
        pessoa = Pessoa(**request.form)
        db.session.add(pessoa)
        db.session.commit()
        flash('Pessoa inserida com sucesso.', 'success')
        return redirect(url_for('pessoas'))
    return render_template('pessoas/form.html', form = Pessoa().__dict__)

@app.route('/pessoas/<int:id_pessoa>/telefones/inserir', methods=['GET', 'POST'])
def inserir_telefone(id_pessoa):
    pessoa = db.session.execute(db.select(Pessoa).filter_by(id=id_pessoa)).scalar()
    if pessoa:
        if request.method == 'POST':
            telefone = Telefone(id_pessoa=id_pessoa, numero = request.form['telefone'])
            db.session.add(telefone)
            db.session.commit()
            flash('Telefone inserido com sucesso.', 'success')
            return redirect(url_for('atualizar_pessoa', id=id_pessoa))
    else:
        flash('Pessoa não localizada', 'error')
        return redirect(url_for('pessoas'))

@app.route('/pessoas/<int:id>/update', methods=['GET', 'POST'])
def atualizar_pessoa(id):
    pessoa = db.session.execute(db.select(Pessoa).filter_by(id=id)).scalar()
    if pessoa:
        if request.method == 'POST':
            try:
                pessoa.nome = request.form['nome']
                pessoa.email = request.form['email']
                db.session.commit()
                flash('Pessoa atualizada com sucesso.', 'success')
                return redirect(url_for('pessoas'))
            except:
                for (erro, valor) in pessoa.erros.items():
                    flash(valor, 'error')
                return render_template('pessoas/form.html', form = request.form, pessoa=pessoa)
        else:
            return render_template('pessoas/form.html', form = pessoa.__dict__, pessoa=pessoa)
    else:
        flash('Pessoa não localizada', 'error')
        return redirect(url_for('pessoas'))

@app.route('/telefones/<int:id>/delete')
def deletar_telefone(id):
    telefone = db.session.execute(db.select(Telefone).filter_by(id=id)).scalar()
    if telefone:
        db.session.delete(telefone)
        db.session.commit()
        flash(f'Telefone removido com sucesso.', 'success')
    else:
        flash('Pessoa não encontrada.', 'error')
    return redirect(url_for('atualizar_pessoa', id=telefone.id_pessoa))

@app.route('/pessoas/<int:id>/delete')
def deletar_pessoa(id):
    pessoa = db.session.execute(db.select(Pessoa).filter_by(id=id)).scalar()
    if pessoa:
        for tel in pessoa.telefones:
            db.session.delete(tel)
        db.session.commit()
        db.session.delete(pessoa)
        db.session.commit()
        flash(f'Pessoa de nome {pessoa.nome} removida com sucesso.', 'success')
    else:
        flash('Pessoa não encontrada.', 'error')
    return redirect(url_for('pessoas'))

@app.route('/reset')
def reset():
    if app.debug:
        reset_bd(app)
        flash('Banco de dados reiniciado com sucesso.', 'success')
    else:
        flash('Não é possível executar este comando em produção.', 'error')
    return redirect(url_for('index'))

@app.context_processor
def injetar_modo_debug_no_template():
    return dict(debug=app.debug)

if __name__ == '__main__':
    reset_bd(app) # Limpa e recria o banco de dados.
    # db.init_app(app) # Inicia o banco já existente.
    app.run(debug=True)
