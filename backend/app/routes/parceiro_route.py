from flask import Blueprint, request, jsonify
from app.controllers.parceiro_controller import ParceiroController

parceiro_bp = Blueprint('parceiro', __name__)

# Rota para criar um parceiro
@parceiro_bp.route('/create_parceiro', methods=['POST'])
def criar():
    dados = request.json
    novo_parceiro = ParceiroController.create_parceiro(dados)
    
    if isinstance(novo_parceiro, tuple):
        return novo_parceiro
    
    return jsonify(novo_parceiro.serialize()), 201

# Rota para get_all todos os parceiros
@parceiro_bp.route('/lista_parceiro', methods=['GET'])
def get_all():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    parceiros = ParceiroController.get_all_parceiro(page, per_page)

    if parceiros:
        return jsonify(parceiros), 200
    return {"msg":"Erro ao get_all parceiros."}, 400

# Rota para obter um parceiro específico
@parceiro_bp.route('/get_parceiro', methods=['GET'])
def obter():
    parceiro_id = request.args.get('parceiro_id')
    parceiro = ParceiroController.get_parceiro_por_id(parceiro_id)
    if parceiro:
        return jsonify(parceiro.serialize()), 200
    return jsonify({'error': 'Parceiro não encontrado'}), 404

# Rota para atualizar um parceiro
@parceiro_bp.route('/update_parceiro', methods=['PUT'])
def atualizar():
    parceiro_id = request.args.get('parceiro_id')
    dados = request.json
    parceiro_atualizado = ParceiroController.update_parceiro(parceiro_id, dados)
    if parceiro_atualizado:
        return jsonify(parceiro_atualizado.serialize()), 200
    return jsonify({'error': 'Parceiro não encontrado'}), 404

# Rota para deletar um parceiro
@parceiro_bp.route('/delete_parceiro', methods=['DELETE'])
def deletar():
    parceiro_id = request.args.get('parceiro_id')
    resultado, msg = ParceiroController.delete_parceiro(parceiro_id)
    if resultado:
        return jsonify({'msg': msg}), 200
    return jsonify({'error': msg}), 400