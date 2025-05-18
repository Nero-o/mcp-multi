from app.models.config_model import ConfigModel
from app.extensions.database import db
from app.models.parceiro_model import Parceiro
from app.models.agendamento_model import Agendamento
from flask import current_app

class ConfigTenantRepository:

    @staticmethod   
    def get_config_por_tenant(tenant_url):
        config = (
            db.session.query(ConfigModel)
            .join(Parceiro)
            .filter(Parceiro.tenant_code == tenant_url)
            .first()
        )
        if config:
            config_dict = config.serialize()
            return ConfigTenantRepository._merge_config_e_agendamento(config_dict, config.id)
        return None
    
    @staticmethod   
    def get_config_por_id(id):
        config = ConfigModel.query.get(id)
        if config:
            config_dict = config.serialize()
            return ConfigTenantRepository._merge_config_e_agendamento(config_dict, config.id)
        return None
    
    @staticmethod
    def get_all():
        configs = (
            db.session.query(ConfigModel, Parceiro.nome, Parceiro.logo)
            .join(Parceiro)
            .all()
        )
        
        result = []
        for config, nome, logo in configs:
            config_dict = config.serialize()
            config_dict['parceiro_nome'] = nome
            config_dict['parceiro_logo'] = logo
            config_dict = ConfigTenantRepository._merge_config_e_agendamento(config_dict, config.id)
            result.append(config_dict)
            
        return result
    

    @staticmethod
    def get_by_parceiro_id(parceiro_id):
        config = ConfigModel.query.filter_by(parceiro_id=parceiro_id).first()
        if config:
            config_dict = config.serialize()
            return ConfigTenantRepository._merge_config_e_agendamento(config_dict, config.id)
        return None
    

    @staticmethod
    def _merge_config_e_agendamento(config_dict, config_id):
        """
        Método auxiliar para adicionar informações dos agendamentos à configuração
        """
        # Mapeamento entre campos que vem do frontend e os tipo_tarefa do agendamento
        mapeamento_tarefas = {
            'habilitar_fornecedor_auto': 'habilitar_fornecedor_auto',
            'habilitar_retorno_auto': 'habilitar_retorno_auto', 
            'notificacao_fornecedor_incompleto_auto': 'notificacao_cadastro_incompleto',
            'notificacao_nota_disponivel_auto': 'email_nota_disponivel',
            'notificacao_nota_expirar_auto': 'notificacao_nota_expirar_auto'
        }
        
        # Buscar agendamentos relacionados a esta config
        agendamentos = (
            db.session.query(Agendamento)
            .filter(Agendamento.config_id == config_id)
            .all()
        )
        
        # Adicionar cada agendamento como um campo no dicionário da config
        for campo_config, tipo_agendamento in mapeamento_tarefas.items():
            # Encontrar o agendamento correspondente
            agendamento_encontrado = next(
                (a for a in agendamentos if a.tipo_tarefa == tipo_agendamento), 
                None
            )
            
            if agendamento_encontrado:
                # excluido=0 significa ativo (True), excluido=1 significa inativo (False)
                config_dict[campo_config] = True if agendamento_encontrado.excluido == 0 else False
            else:
                # Se não encontrou o agendamento, define como False por padrão
                config_dict[campo_config] = False
                
        return config_dict
    

    @staticmethod
    def create(data):
        config = ConfigModel(**data)
        db.session.add(config)
        db.session.commit()
        return config


    @staticmethod
    def update(config_id, data):
        config = ConfigModel.query.get(config_id)
        if not config:
            return None

        # Mapeamento entre campos que vem do frontend e os tipo_tarefa do agendamento
        mapeamento_tarefas = {
            'habilitar_fornecedor_auto': 'habilitar_fornecedor_auto',
            'habilitar_retorno_auto': 'habilitar_retorno_auto', 
            'notificacao_fornecedor_incompleto_auto': 'notificacao_cadastro_incompleto',
            'notificacao_nota_disponivel_auto': 'email_nota_disponivel',
            'notificacao_nota_expirar_auto': 'notificacao_nota_expirar_auto'
        }

        # Separar dados especiais para agendamento
        campos_agendamento = mapeamento_tarefas.keys()
        dados_agendamento = {k: v for k, v in data.items() if k in campos_agendamento}
        
        # Campos que existem no modelo ConfigModel
        # Filtrar para apenas campos válidos da config
        campos_config = [c.name for c in ConfigModel.__table__.columns]
        dados_config = {k: v for k, v in data.items() if k in campos_config}
        
        # Atualiza os campos da config
        for campo, valor in dados_config.items():
            # Converte string 'true'/'false' para boolean se necessário
            if isinstance(valor, str) and valor.lower() in ['true', 'false']:
                valor = valor.lower() == 'true'
                
            setattr(config, campo, valor)
        
        # Processa os campos para agendamentos
        for campo, valor in dados_agendamento.items():
            tipo_tarefa = mapeamento_tarefas[campo]
            
            # Converte o valor para boolean caso seja string
            if isinstance(valor, str) and valor.lower() in ['true', 'false']:
                valor = valor.lower() == 'true'
                
            # Busca o agendamento correspondente
            agendamento = (
                db.session.query(Agendamento)
                .filter(
                    Agendamento.config_id == config.id,
                    Agendamento.tipo_tarefa == tipo_tarefa
                )
                .first()
            )
            
            if agendamento:
                # A informação que chega do frontend é se o switch está ligado ou não;
                # Pro frontend basta a pergunta "O switch está ligado?"
                # Pro backend, a pergunta é "O agendamento está excluído logicamente?"
                # Portanto, se o frontend enviar True, 
                # quer dizer que o agendamento está ativo, e portanto, excluido = 0
                # Se o frontend enviar False, quer dizer que o agendamento está inativo, e portanto, excluido = 1
                agendamento.excluido = 0 if valor else 1
                current_app.logger.info(f"Agendamento {tipo_tarefa} atualizado com excluido={agendamento.excluido}")

        db.session.commit()
        
        # Usar o método _merge_config_e_agendamento para obter a config completa com os agendamentos
        config_dict = config.serialize()
        return ConfigTenantRepository._merge_config_e_agendamento(config_dict, config.id)
    
    @staticmethod
    def delete(config_id):
        config = ConfigTenantRepository.get_config_por_id(config_id)
        if config:
            db.session.delete(config)
            db.session.commit()
            return True