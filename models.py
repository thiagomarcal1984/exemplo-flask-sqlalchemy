from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, validates

class Base():
    erros = dict()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Pessoa(db.Model, Base):
    __tablename__ = 'pessoas'
    id = mapped_column(Integer, primary_key=True)
    nome = mapped_column(String, nullable=False)
    email = mapped_column(String, nullable=False)

    @validates('email')
    def validar_email(self, chave, valor):
        if self.erros.get(chave):
            del(self.erros[chave])
        if '@' not in valor:
            self.erros[chave] = 'O e-mail precisa de uma arroba.'
        if self.erros.get(chave):
            raise ValueError(self.erros[chave])
        return valor


    telefones = relationship("Telefone")

class Telefone(db.Model, Base):
    __tablename__ = 'telefones'
    id = mapped_column(Integer, primary_key=True)
    id_pessoa = mapped_column(Integer, ForeignKey("pessoas.id"), nullable=False)
    numero = mapped_column(String(9), nullable=False)

    @property
    def pessoa(self):
        return db.session.execute(db.select(Pessoa).filter_by(id=self.id_pessoa)).scalar()
    
    @validates('numero')
    def validar_numero(self, chave, valor):
        if self.erros.get(chave):
            del(self.erros[chave])
        if not valor:
            self.erros[chave] = "O número está vazio."
        import re
        separadores = r'[\-\.\s]*'
        regex = r'[0-9]{4,5}' + separadores + r'[0-9]{4}'
        if not re.search(regex, str(valor)):
            self.erros[chave] = "O número de telefone está com formato inválido."
        else:
            valor = re.sub(separadores, "", valor)

        if self.erros.get(chave):
            raise ValueError(self.erros[chave])
            
        return valor


def initialize(db):
    # Base.metadata.drop_all(engine)      # Apaga todas as tabelas.
    # Base.metadata.create_all(engine)    # Cria todas as tabelas.
    nomes = ['Fulano', 'Siclano', 'Deltrano']
    telefones = [' 9876 4321', '98888-4444', '  9963-3692  ']
    for nome in nomes:
        p = Pessoa(nome=nome.capitalize(), email=f'{nome.lower()}@{nome.lower()}.com')
        db.session.add(p)
        db.session.commit()
        for tel in telefones:
            db.session.add(Telefone(numero=tel, id_pessoa=p.id))
        db.session.commit()

def mostrar(db):
    for p in db.session.execute(db.select(Pessoa)).scalars():
        print(p.nome)
        for t in p.telefones:
            print('\t', t.numero)

def reset_bd(app):
    with app.app_context():
        try:
            db.init_app(app)
        except:
            print("O banco de dados já inicializou a aplicação Flask.")
        db.drop_all()
        db.create_all()
        initialize(db)
        mostrar(db)


if __name__ == '__main__':
    from app import app
    reset(app)
