from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()

fmt_data = "%d/%m/%Y"

# Criação da tabela associativa, sem a necessidade de criar uma classe.
Turma = db.Table(
    "turmas",
    db.Model.metadata,
    db.Column("id_aluno", db.Integer, db.ForeignKey('alunos.id'), primary_key=True),
    db.Column("id_curso", db.Integer, db.ForeignKey('cursos.id'), primary_key=True),
)

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = mapped_column(db.Integer, primary_key=True)
    nome = mapped_column(db.String, nullable=False)
    email = mapped_column(db.String, nullable=False)
    ativo = mapped_column(db.Boolean, default=True, nullable=False)
    data_nascimento = mapped_column(db.Date)

    telefones = relationship("Telefone")
    cursos = relationship("Curso", secondary=Turma, back_populates='alunos')

    def __repr__(self) -> str:
        return str(self)
        # return  f"Nome: {self.nome}; " \
        #         f"E-mail: {self.email}; " \
        #         f"Data de Nascimento: {self.data_nascimento.strftime(fmt_data)}"
    
    def __str__(self) -> str:
        return f"<Aluno: {self.nome} ({self.email})>"

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = mapped_column(db.Integer, primary_key=True)
    nome = mapped_column(db.String, nullable=False, unique=True)
    data_inicio = mapped_column(db.Date, nullable=False)
    id_aluno = mapped_column(db.Integer, db.ForeignKey("alunos.id"))

    alunos = relationship("Aluno", secondary=Turma, back_populates='cursos')

    @property
    def aluno(self):
        return db.session.execute(db.select(Aluno).filter_by(id=self.id_aluno)).scalar()

    def __repr__(self) -> str:
        return  f"Nome: {self.nome}; " \
                f"Aluno: {self.aluno.nome}; " \
                f"Data de Início: {self.data_nascimento.strftime(fmt_data)}"
    
    def __str__(self) -> str:
        return f"<Curso: {self.nome} ({self.data_inicio.strftime(fmt_data)})>"

class Telefone(db.Model):
    __tablename__ = 'telefones'
    id = mapped_column(db.Integer, primary_key=True)
    numero = mapped_column(db.String, nullable=False, unique=True)
    id_aluno = mapped_column(db.ForeignKey('alunos.id'), nullable=False)

    @property
    def pessoa(self):
        return db.session.execute(db.select(Aluno).filter_by(id=self.id_aluno)).scalar()

    def __repr__(self) -> str:
        return  f"Número: {self.numero}; " \
                f"Pessoa: {self.pessoa.nome} "
    
    def __str__(self) -> str:
        return f"<Telefone de {self.pessoa.nome}: {self.numero} >"
    

def criar_alunos(db):
    lista = []
    a = Aluno(**{
        'nome': 'Thiago',
        'email': 'tma@cdtn.br',
        'data_nascimento': date(1984, 11, 18),
    })
    lista.append(a)

    a = Aluno(**{
        'nome': 'Fulano',
        'email': 'fulano@fulano',
        'data_nascimento': date(1983, 3, 3),
    })
    lista.append(a)

    a = Aluno(**{
        'nome': 'Siclano',
        'email': 'siclano@siclano',
        'ativo': False,
        'data_nascimento': date(1985, 5, 5),
    })
    lista.append(a)

    a = Aluno(**{
        'nome': 'Deltrano',
        'email': 'deltrano@deltrano',
        'data_nascimento': date(1988, 8, 8),
    })
    lista.append(a)

    for aluno in lista:
        db.session.add(aluno)
    db.session.commit()

def mostrar(db, classe):
    lista = db.session.execute(db.select(classe)).scalars()
    for objeto in lista:
        # print(repr(objeto))
        print(objeto)
    
        if isinstance(objeto, Curso):
            print(f'Imprimindo os alunos do curso "{objeto.nome}":')
            for aluno in objeto.alunos:
                print(f"\t{aluno}")

def criar_telefones(db):
    lista = []
    t = Telefone(**{
        'numero': '9999-9999',
        'id_aluno': 1,
    })
    lista.append(t)
    t = Telefone(**{
        'numero': '8888-8888',
        'id_aluno': 3,
    })
    lista.append(t)
    t = Telefone(**{
        'numero': '5555-5555',
        'id_aluno': 4,
    })
    lista.append(t)
    for tel in lista:
        db.session.add(tel)
    db.session.commit()


def criar_cursos(db):
    lista = []
    c = Curso(**{
        'nome': 'Curso de Flask',
        'data_inicio': date(2023, 11, 30),
        'id_aluno': 2,
    })
    lista.append(c)

    c = Curso(**{
        'nome': 'Curso de Django',
        'data_inicio': date(2022, 5, 16),
        'id_aluno': 4,
    })
    lista.append(c)

    for curso in lista:
        db.session.add(curso)
    db.session.commit()

def criar_turmas(db):
    curso = db.session.execute(db.select(Curso).filter_by(id=2)).scalar()
    aluno = db.session.execute(db.select(Aluno).filter_by(id=4)).scalar()
    curso.alunos.append(aluno)

    curso = db.session.execute(db.select(Curso).filter_by(id=1)).scalar()
    aluno = db.session.execute(db.select(Aluno).filter_by(id=1)).scalar()
    curso.alunos.append(aluno)

    aluno = db.session.execute(db.select(Aluno).filter_by(id=2)).scalar()
    curso.alunos.append(aluno)

    db.session.commit()

def criar(db):
    criar_alunos(db)
    criar_cursos(db)
    criar_telefones(db)
    criar_turmas(db)


if __name__ == '__main__':
    from aplicativo import app
    with app.app_context():
        db.init_app(app)
        db.drop_all()
        db.create_all()

        criar_alunos(db)
        criar_cursos(db)
        criar_telefones(db)
        criar_turmas(db)

        # mostrar(db, Aluno)
        # mostrar(db, Turma)
        mostrar(db, Curso)
        # mostrar(db, Telefone)
