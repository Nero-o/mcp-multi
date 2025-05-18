from flask import Blueprint, request, jsonify
from notion_client import Client
from datetime import datetime
import os

support_bp = Blueprint('support', __name__)
notion = Client(auth=os.getenv('NOTION_TOKEN'))
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

def get_last_ticket_number():
    try:
        # Busca os tickets ordenados pelo título em ordem decrescente
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[{
                "property": "Title",
                "direction": "descending"
            }],
            page_size=1
        )
        
        if not response['results']:
            return 0
            
        # Extrai o número do último ticket
        last_title = response['results'][0]['properties']['Title']['title'][0]['text']['content']
        # Encontra o número no título (últimos 4 dígitos)
        number = ''.join(filter(str.isdigit, last_title))
        return int(number) if number else 0
    except:
        return 0

@support_bp.route('/support_ticket', methods=['POST'])
def create_ticket():
    data = request.json
    
    try:
        # Obtém o próximo número do ticket
        next_number = get_last_ticket_number() + 1
        
        # Criar página no Notion
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": f"Ticket {data['type']}{next_number:04d}"
                            }
                        }
                    ]
                },
                "Type": {
                    "select": {
                        "name": data['type']
                    }
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": data['description']
                            }
                        }
                    ]
                },
                "URL": {
                    "rich_text": [
                        {
                            "text": {
                                "content": data.get('url', '')
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "Backlog"
                    }
                },
                "Created": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
        )
        
        return jsonify({"message": "Ticket created successfully"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 