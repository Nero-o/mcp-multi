import json
from flask import current_app, jsonify

class RedisService:

    @staticmethod
    def save_session(session_id, session_data, expiration_time):
        # Armazena no Redis com tempo de expiração (por exemplo, 1 hora)
        current_app.redis_client.setex(
            session_id,
            expiration_time,
            json.dumps(session_data)
        )

    @staticmethod
    def get_session(session_id):
        data = current_app.redis_client.get(session_id)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    def delete_session(session_id):
        current_app.redis_client.delete(session_id)