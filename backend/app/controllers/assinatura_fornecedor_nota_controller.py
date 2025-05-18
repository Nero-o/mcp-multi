import hashlib
import uuid
from datetime import datetime
from flask import current_app, render_template
from app.services.assinatura_fornecedor_nota_service import AssinaturaFornecedorNotaService
from app.controllers.usuario_controller import UsuarioController
from app.services.fornecedor_nota_service import FornecedorNotaService
from app.services.fornecedor_service import FornecedorService
from app.services.parceiro_service import ParceiroService
from app.services.config_tenant_service import ConfigTenantService
from app.utils.envia_email import envia_email
from app.utils.enums import meses
from app.utils.formata_monetario import formata_float_para_moeda


class AssinaturaFornecedorNotaController:

    @staticmethod
    def registrar_assinatura_nota(usuario_logado, tenant_code, notas_id):
        # Validação inicial de usuário e parceiro
        usuarios_validos, mensagem = AssinaturaFornecedorNotaController._validar_usuario_parceiro(usuario_logado, tenant_code)

        if not usuarios_validos:
            return False, mensagem

        # Validação das notas
        notas = FornecedorNotaService.get_fornecedor_nota_por_multiplos_ids(notas_id)
        resultado_validacao = AssinaturaFornecedorNotaController._validar_notas(notas, usuarios_validos)

        if not resultado_validacao['sucesso']:
            return False, resultado_validacao['mensagem']

        # Processar as assinaturas conforme o método definido em cada nota
        resultado_processamento = AssinaturaFornecedorNotaController._processar_assinaturas_por_metodo(
            notas, 
            usuarios_validos, 
            usuario_logado['ip']
        )
        
        # Verificar se alguma assinatura interna (AECO) foi realizada para enviar emails
        AssinaturaFornecedorNotaController._processar_envio_emails_assinaturas_aeco(
            resultado_processamento['resultados'], 
            notas, 
            tenant_code,
            resultado_processamento['valores_calculados']['valor_total_liquido'],
            resultado_processamento['valores_calculados']['valor_total_disponivel']
        )
        
        # Preparar retorno com base nos resultados
        return AssinaturaFornecedorNotaController._preparar_resposta_assinatura(resultado_processamento['resultados'])
    
    @staticmethod
    def _processar_assinaturas_por_metodo(notas, usuarios_validos, ip):
           
        resultados = []
        # Obter os valores calculados da operação
        valores_calculados = AssinaturaFornecedorNotaController._calcular_operacao(notas)
        
        for nota in notas:
            metodo_assinatura = nota.metodo_assinatura or 'aeco'
            current_app.logger.info(f"Processando assinatura da nota {nota.id} com método: {metodo_assinatura}")
            
            # Encontra o usuário vinculado a esta nota específica
            usuario_vinculado = next((u for u in usuarios_validos if u.fornecedor_id == nota.fornecedor_id), None)
            if not usuario_vinculado:
                resultados.append({
                    'nota_id': nota.id,
                    'sucesso': False,
                    'mensagem': 'Usuário não tem vínculo com o fornecedor desta nota',
                    'metodo': metodo_assinatura
                })
                continue
            
            try:
                        
                try:
                    from app.services.d4sign_service import D4SignService
                    d4sign = True
                except ImportError as e:
                    d4sign = False
                    current_app.logger.warning(f"Erro ao importar D4SignService: {e}")

                try:
                    from app.services.docusign_service import DocuSignService
                    docusign = True
                except ImportError as e:
                    docusign = False
                    current_app.logger.warning(f"Erro ao importar DocuSignService: {e}")


                if (not docusign and not d4sign) or metodo_assinatura == 'aeco':
                    resultado = AssinaturaFornecedorNotaController._processar_assinatura_interna(nota, usuario_vinculado, ip)
                elif metodo_assinatura == 'docusign' and docusign:
                    resultado = AssinaturaFornecedorNotaController._processar_assinatura_docusign(nota, DocuSignService())
                elif metodo_assinatura == 'd4sign' and d4sign:
                    resultado = AssinaturaFornecedorNotaController._processar_assinatura_d4sign(nota, D4SignService())
                else:
                    resultado = {
                        'sucesso': False,
                        'mensagem': f'Método de assinatura não reconhecido: {metodo_assinatura}',
                        'metodo': metodo_assinatura
                    }
                    
                resultado['nota_id'] = nota.id
                resultado['metodo'] = metodo_assinatura

                resultados.append(resultado)
                
            except Exception as e:
                current_app.logger.error(f"Erro ao processar assinatura da nota {nota.id}: {str(e)}")
                resultados.append({
                    'nota_id': nota.id,
                    'sucesso': False,
                    'mensagem': f'Erro ao processar assinatura: {str(e)}',
                    'metodo': metodo_assinatura
                })
        
        # Adiciona os valores calculados aos resultados
        return {
            'resultados': resultados,
            'valores_calculados': valores_calculados
        }
    
    @staticmethod
    def _processar_assinatura_interna(nota, usuario, ip):
        """
        Processa assinatura interna (método AECO).
        Retorna um dicionário com o resultado da operação.
        """
        lote_id = str(uuid.uuid4())
        try:
            nova_assinatura = AssinaturaFornecedorNotaController.create_assinatura_nota(
                usuario.id,
                nota.id,
                ip,
                lote_id
            )

            if not nova_assinatura:
                return {
                    'sucesso': False, 
                    'mensagem': f"Falha ao registrar a assinatura da nota {nota.id}"
                }

            # Atualizar status da nota para assinada
            FornecedorNotaService.update_fornecedor_nota(
                nota.id,
                {
                    'status_id': 2,
                    'data_assinatura': datetime.now(),
                    'data_alteracao': datetime.now()
                }
            )

            return {
                'sucesso': True,
                'assinatura': nova_assinatura
            }
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinatura interna da nota {nota.id}: {str(e)}")
            return {
                'sucesso': False,
                'mensagem': f"Erro ao processar assinatura interna: {str(e)}"
            }

    @staticmethod
    def _processar_assinatura_docusign(nota, docusign_service):
        """
        Processa assinatura via DocuSign.
        Retorna um dicionário com o resultado da operação.
        """
        try:

            resultado = docusign_service.create_signature_request(nota.id)
            
            if resultado and 'envelope_id' in resultado:
                FornecedorNotaService.update_fornecedor_nota(
                    nota.id,
                    {
                        'docusign_envelope_id': resultado.get('envelope_id'),
                        'status_id': 7,  # Status para assinatura externa iniciada
                        'data_alteracao': datetime.now()
                    }
                )
                return {
                    'sucesso': True,
                    'mensagem': 'Solicitação de assinatura DocuSign criada com sucesso',
                    'url_assinatura': resultado.get('signing_url_cedente')
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': 'Falha ao criar solicitação de assinatura DocuSign'
                }
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinatura DocuSign da nota {nota.id}: {str(e)}")
            return {
                'sucesso': False,
                'mensagem': f"Erro ao processar assinatura DocuSign: {str(e)}"
            }
        

    @staticmethod
    def _processar_assinatura_d4sign(nota, d4sign_service):
        """
        Processa assinatura via D4Sign.
        Retorna um dicionário com o resultado da operação.
        """
        try:
            resultado = d4sign_service.create_signature_request(nota.id)
            
            if resultado and 'document_uuid' in resultado:
                FornecedorNotaService.update_fornecedor_nota(
                    nota.id,
                    {
                        'd4sign_document_uuid': resultado.get('document_uuid'),
                        'status_id': 7,  # Status para assinatura externa iniciada
                        'data_alteracao': datetime.now()
                    }
                )
                return {
                    'sucesso': True,
                    'mensagem': 'Solicitação de assinatura D4Sign criada com sucesso',
                    'url_assinatura': resultado.get('signing_url_cedente')
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': 'Falha ao criar solicitação de assinatura D4Sign'
                }
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinatura D4Sign da nota {nota.id}: {str(e)}")
            return {
                'sucesso': False,
                'mensagem': f"Erro ao processar assinatura D4Sign."
            }
        

    @staticmethod
    def _processar_envio_emails_assinaturas_aeco(resultados, notas, tenant_code, valor_total_liquido=None, valor_total_disponivel=None):
        """
        Processa o envio de emails para assinaturas do tipo AECO.
        """
        # Filtrar assinaturas internas com sucesso
        sucessos = [r for r in resultados if r['sucesso']]
        assinaturas_aeco = [r.get('assinatura') for r in sucessos if r['metodo'] == 'aeco' and r.get('assinatura')]
        
        if not assinaturas_aeco:
            return
        
        # Filtrar notas com assinatura interna bem-sucedida
        notas_aeco_ids = [r['nota_id'] for r in sucessos if r['metodo'] == 'aeco']
        notas_aeco = [nota for nota in notas if nota.id in notas_aeco_ids]
        
        if not notas_aeco:
            return
        
        # Se os valores não foram fornecidos, calculamos aqui
        if valor_total_liquido is None or valor_total_disponivel is None:
            valor_total_liquido = sum(nota.valor_liquido or 0 for nota in notas_aeco)
            valor_total_disponivel = sum(nota.vlr_disp_antec or 0 for nota in notas_aeco)
        
        # Enviar emails
        AssinaturaFornecedorNotaController._enviar_emails_assinatura(
            assinaturas_aeco,
            notas_aeco,
            [nota.id for nota in notas_aeco],
            tenant_code,
            valor_total_liquido,
            valor_total_disponivel
        )
        
    @staticmethod
    def _preparar_resposta_assinatura(resultados):
        """
        Prepara a resposta a ser retornada com base nos resultados das assinaturas.
        """
        if not resultados:
            return False, "Nenhuma nota processada"
        
        sucessos = [r for r in resultados if r['sucesso']]
        falhas = [r for r in resultados if not r['sucesso']]
        
        if not falhas:  # Todos com sucesso
            return True, f"Todas as {len(sucessos)} nota(s) foram assinadas com sucesso."
        elif not sucessos:  # Todos falharam
            erros = '; '.join([f"Nota {r['nota_id']}: {r['mensagem']}" for r in falhas])
            return False, f"Falha em todas as assinaturas: {erros}"
        else:  # Alguns sucessos, algumas falhas
            return True, f"{len(sucessos)} nota(s) assinada(s) com sucesso. {len(falhas)} falha(s)."
        
    @staticmethod
    def get_resumo_operacao(usuario_logado, tenant_code, notas_id):
        try:
            usuarios_validos, mensagem = AssinaturaFornecedorNotaController._validar_usuario_parceiro(
                usuario_logado=usuario_logado,
                tenant_code=tenant_code
            )
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinaturas: {e}")
            return {'msg': "Requisição inválida. 1"}, 400
        
        if not usuarios_validos:
            return {'msg': mensagem}, 400
        
        try:
            notas = AssinaturaFornecedorNotaController.get_fornecedor_nota_por_multiplos_ids(notas_id)
            resultado_validacao_notas = AssinaturaFornecedorNotaController._validar_notas(
                notas=notas, 
                usuarios_validos=usuarios_validos
            )
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinaturas: {e}")
            return {'msg': "Requisição inválida. 2"}, 400
        
        if not resultado_validacao_notas['sucesso']:
            return {'msg': resultado_validacao_notas['mensagem']}, 400
        
        try:
            # Usando o método de cálculo de operação diretamente
            valores_calculados = AssinaturaFornecedorNotaController._calcular_operacao(notas)
            # Adiciona sucesso para manter compatibilidade
            valores_calculados['sucesso'] = True
        except Exception as e:
            current_app.logger.error(f"Erro ao processar assinaturas: {e}")
            return {'msg': "Requisição inválida. 3"}, 400
        
        # Retorna o resultado do cálculo diretamente
        return valores_calculados
    

    @staticmethod
    def get_fornecedor_nota_por_multiplos_ids(notas_id):
        return FornecedorNotaService.get_fornecedor_nota_por_multiplos_ids(notas_id)
        

    @staticmethod
    def _validar_usuario_parceiro(usuario_logado, tenant_code):
        return UsuarioController.valida_vinculo_usuario_parceiro_logado(
            usuario_logado,
            tenant_code,
            retorna_lista_usuarios=True
        )

    @staticmethod
    def _validar_notas(notas, usuarios_validos):
        for nota in notas:
            if not nota:
                return {'sucesso': False, 'mensagem': "Falha ao registrar a assinatura da nota. 1"}

            if not FornecedorNotaService.nota_disponivel(nota):
                return {'sucesso': False, 'mensagem': "Nota não está disponível para antecipação."}

            usuarios_com_vinculo = [
                usuario for usuario in usuarios_validos if usuario.fornecedor_id == nota.fornecedor_id
            ]
            usuario_tem_vinculo = usuarios_com_vinculo[0] if usuarios_com_vinculo else None

            if not usuario_tem_vinculo:
                current_app.logger.error(
                    f"Fornecedor tentou registrar a assinatura da nota {nota.id} de outro fornecedor.\n"
                    f"Fornecedores do usuário: {[usuario.fornecedor_id for usuario in usuarios_validos]}\n"
                    f"Fornecedor da nota: {nota.fornecedor_id}"
                )
                return {'sucesso': False, 'mensagem': "Falha ao registrar a assinatura da nota. 2"}

            assinatura_existente = AssinaturaFornecedorNotaService.get_assinatura_por_nota_e_usuario(
                nota.id, 
                usuario_tem_vinculo.id
            )
            if assinatura_existente:
                return {'sucesso': False, 'mensagem': f"A nota {nota.id} já foi assinada pelo usuário."}

        return {'sucesso': True}

    
    @staticmethod
    def _calcular_operacao(notas):
        """
        Calcula os valores totais da operação e serializa as notas.
        Retorna um dicionário com os valores calculados.
        """
        notas_serializadas = []
        valor_total_liquido = 0
        valor_total_disponivel = 0
        valor_total_face = 0

        for nota in notas:
            valor_total_liquido += nota.valor_liquido or 0
            valor_total_disponivel += nota.vlr_disp_antec or 0
            valor_total_face += nota.vlr_face or 0
            notas_serializadas.append(nota.serialize())

        return {
            'notas': notas_serializadas,
            'valor_total_liquido': valor_total_liquido,
            'valor_total_disponivel': valor_total_disponivel,
            'valor_total_face': valor_total_face
        }

    @staticmethod
    def _enviar_emails_assinatura(assinaturas, notas, notas_id, tenant_code, valor_total_liquido, valor_total_disponivel):
        fornecedor = FornecedorService.get_fornecedor_por_id(notas[0].fornecedor_id)
        parceiro = ParceiroService.get_parceiro_por_tenant(tenant_code)
        config_tenant = ConfigTenantService.get_config_by_parceiro_id(parceiro.id)
        
        for nota in notas:
            nota.dt_emis_formatada = nota.dt_emis.strftime('%d/%m/%Y') if nota.dt_emis else ''
            nota.dt_fluxo_formatado = nota.dt_fluxo.strftime('%d/%m/%Y') if nota.dt_fluxo else ''
            
            nota.vlr_face_formatado = formata_float_para_moeda(nota.vlr_face)
            nota.vlr_disp_antec_formatado = formata_float_para_moeda(nota.vlr_disp_antec)
            nota.valor_liquido_formatado = formata_float_para_moeda(nota.valor_liquido)

        # Email para o fornecedor
        result, status_code = envia_email(
            destinatarios=[fornecedor.email],
            assunto=f"{parceiro.nome} - Declaração de recebimento",
            corpo=render_template(
                'email_declaracao_recebimento_antecipacao.html',
                fornecedor=fornecedor,
                notas_id=notas_id,
                notas=notas,
                assinaturas=assinaturas,
                meses=meses,
                parceiro=parceiro,
                valor_total_liquido=valor_total_liquido,
                valor_total_disponivel=valor_total_disponivel,
            )
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email DECLARACAO RECEBIMENTO para o fornecedor. [backend/app/controllers/assinatura_fornecedor_nota_controller]: {result}")


        # Email para o admin
        result, status_code = envia_email(
            destinatarios=[config_tenant['email_admin']],
            assunto=f"{parceiro.nome} - Carta cessão",
            corpo=render_template(
                'email_carta_cessao_antecipacao.html',
                notas=notas,
                notas_id=notas_id,
                assinaturas=assinaturas,
                meses=meses,
                parceiro=parceiro,
                valor_total_liquido=valor_total_liquido,
                valor_total_disponivel=valor_total_disponivel,
            )
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email CARTA CESSÃO para o parceiro. [backend/app/controllers/assinatura_fornecedor_nota_controller]: {result}")


    @staticmethod
    def create_assinatura_nota(usuario_id, nota_id, ip, lote_id):
        now = datetime.now()
        timestamp = now.isoformat()
        data_string = f"{usuario_id}|{nota_id}|{timestamp}|assinou_nota"

        hash_object = hashlib.sha256(data_string.encode())
        hex_dig = hash_object.hexdigest()

        dados_assinatura = {
            'hash': hex_dig,
            'ip': ip,
            'acao': 'assinou_nota',
            'lote_id': lote_id,
            'assinatura': f"Hash: {hex_dig} - IP: {ip} - Registrado em: {now.strftime('%d/%m/%Y %H:%M:%S')}",
            'data_cadastro': now
        }

        return AssinaturaFornecedorNotaService.registrar_assinatura_nota(usuario_id, nota_id, dados_assinatura)
