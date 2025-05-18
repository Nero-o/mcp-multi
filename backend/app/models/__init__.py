import os
import time
os.environ['TZ'] = 'America/Sao_Paulo'
try:
    time.tzset()  # Tenta aplicar a mudança de fuso horário em sistemas Unix-like
except:
    pass  # Ignora o erro em sistemas Windows


from datetime import datetime
from app.extensions.database import db

class BaseModel(db.Model):
    __abstract__ = True  # Não cria tabela diretamente, serve apenas para herança

    # Colunas padrão
    data_cadastro = db.Column(db.DateTime, default=datetime.now())
    data_alteracao = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    excluido = db.Column(db.Boolean, default=False) 

    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
    
    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id}>'

    def serialize(self):
        """
        Serializa automaticamente todos os campos de um modelo.
        Pode ser sobrescrito ou expandido em modelos específicos, se necessário.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}