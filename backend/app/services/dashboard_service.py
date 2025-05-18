from flask import current_app
from sqlalchemy import func, and_
from app.repositories.parceiro_repository import ParceiroRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.fornecedor_parceiro_repository import FornecedorParceiroRepository
from app.services.fornecedor_parceiro_service import FornecedorParceiroService
from app.models.fornecedor_nota_model import FornecedorNota

class DashboardService:

    @staticmethod
    def get_base_query(usuario_logado, session_data, tenant_code):
        parceiro = ParceiroRepository.get_parceiro_por_tenant(tenant_code)
        
        query = FornecedorNota.query
        query = query.filter(FornecedorNota.parceiro_id == parceiro.id)

        if usuario_logado['role'][0] == 'Fornecedor':

            if not 'user' in session_data or not 'fornecedor_selected' in session_data['user']:
                current_app.logger.info("Fornecedor não selecionado")
                return False, "Fornecedor não selecionado"
            
            fornecedor = session_data['user']['fornecedor_selected']

            query = query.filter(FornecedorNota.fornecedor_id == fornecedor['id'])
            # usuario_fornecedor = UsuarioRepository.get_usuario_por_id(usuario_logado['id'])
            # query = query.filter(FornecedorNota.fornecedor_id == usuario_fornecedor.fornecedor_id)
            
        return True, query
    

    def _soma_db(query, column):
        return query.with_entities(
            func.sum(column)
        ).scalar() or 0

    @staticmethod
    def get_dashboard_data(usuario_logado, session_data, tenant_code):
        # Query base com filtros de acordo com o papel do usuário
        result, base_query = DashboardService.get_base_query(usuario_logado, session_data, tenant_code)
        
        if not result:
            return result, base_query
        
        coluna_base_calculos = FornecedorNota.vlr_disp_antec

        
        # Contagem de notas por status
        qtde_notas_disponivel = base_query.filter_by(status_id=1).count()
        qtde_notas_andamento = base_query.filter_by(status_id=2).count()
        qtde_notas_concluidas = base_query.filter_by(status_id=4).count()

        # Valores totais por status
        total_disponivel = DashboardService._soma_db(
            base_query.filter_by(status_id=1),
            coluna_base_calculos
        )
        total_andamento = DashboardService._soma_db(
            base_query.filter_by(status_id=2),
            coluna_base_calculos
        )   
        total_concluido = DashboardService._soma_db(
            base_query.filter_by(status_id=4),
            coluna_base_calculos
        )
        valor_total_notas = total_disponivel + total_andamento + total_concluido
        # Cálculo dos percentuais
        percentual_notas = (qtde_notas_concluidas / (qtde_notas_disponivel + qtde_notas_andamento + qtde_notas_concluidas)) * 100 if (qtde_notas_disponivel + qtde_notas_andamento + qtde_notas_concluidas) > 0 else 0
        
        # Buscar notas por status
        notas_disponiveis = base_query.filter_by(status_id=1).order_by(FornecedorNota.id.desc()).limit(5).all()
        notas_andamento = base_query.filter_by(status_id=2).order_by(FornecedorNota.id.desc()).limit(5).all()
        notas_concluidas = base_query.filter_by(status_id=4).order_by(FornecedorNota.id.desc()).limit(5).all()
        
        # Serialização das notas
        serializar_notas_disponiveis = lambda nota: {
            'id': nota.id,
            'documento': nota.documento,
            'sacado': nota.sacado,
            'valor': nota.vlr_disp_antec
        }
        
        serializar_notas_andamento = lambda nota: {
            'id': nota.id,
            'documento': nota.documento,
            'cedente': nota.fornecedor.razao_social if nota.fornecedor else '',
            'valor': nota.vlr_disp_antec
        }

        dashboard_data = {
            'valorTotalNotas': valor_total_notas,
            'totalDisponivel': total_disponivel,
            'totalAndamento': total_andamento,
            'totalConcluido': total_concluido,
            'qtdeNotasDisponivel': qtde_notas_disponivel,
            'qtdeNotasAndamento': qtde_notas_andamento,
            'qtdeNotasConcluidas': qtde_notas_concluidas,
            'percentualNotas': percentual_notas,
            'notasDisponiveis': [serializar_notas_disponiveis(nota) for nota in notas_disponiveis],
            'notasAndamento': [serializar_notas_andamento(nota) for nota in notas_andamento],
            'notasConcluidas': [serializar_notas_disponiveis(nota) for nota in notas_concluidas],
        }
        if usuario_logado['role'][0] == 'Fornecedor':
            # Buscar dados para o gráfico
            dados_grafico = base_query.filter_by(status_id=1)\
                .with_entities(
                    func.date(FornecedorNota.dt_fluxo).label('data'),
                    func.sum(FornecedorNota.vlr_disp_antec).label('total')
                )\
                .group_by(func.date(FornecedorNota.dt_fluxo))\
                .order_by(func.date(FornecedorNota.dt_fluxo))\
                .all()

            # Formatar dados do gráfico
            grafico = [{
                'date': data.strftime('%d/%b').lower(),
                'totalValue': float(total)
            } for data, total in dados_grafico]

            dashboard_data['grafico'] = grafico
            

        if usuario_logado['role'][0] in ['Administrador', 'Parceiro', 'ParceiroAdministrador']:
                        # Buscar fornecedores habilitados
            parceiro = ParceiroRepository.get_parceiro_por_tenant(tenant_code)

            fornecedores_habilitados = FornecedorParceiroRepository.count_fornecedores_por_status(parceiro.id, excluido=False)
            fornecedores_desabilitados = FornecedorParceiroRepository.count_fornecedores_por_status(parceiro.id, excluido=True)
            
            total_fornecedores = fornecedores_habilitados + fornecedores_desabilitados
            percentual_fornecedores = (fornecedores_habilitados / total_fornecedores * 100) if total_fornecedores > 0 else 0
            
            # Buscar top 5 fornecedores com maiores valores antecipados
            top_fornecedores = FornecedorParceiroRepository.get_top_fornecedores_por_valor(
                parceiro_id=parceiro.id,
                status_ids=[2, 4],
                limit=5
            )
            serializar_fornecedores = lambda f: {
                'id': f.fornecedor_id,
                'razaoSocial': f.razao_social,
                'valorDisponivelAntecipacao': float(f.valorTotalAntecipado) if f.valorTotalAntecipado else 0
            }
            parceiro_data = {
                'percentualFornecedores': percentual_fornecedores,  # Você precisa definir a lógica para este cálculo
                'fornecedoresHabilitados': fornecedores_habilitados,
                'fornecedoresDesabilitados': fornecedores_desabilitados,
                'fornecedores': [serializar_fornecedores(f) for f in top_fornecedores],
            }

            dashboard_data.update(parceiro_data)

        return True, dashboard_data