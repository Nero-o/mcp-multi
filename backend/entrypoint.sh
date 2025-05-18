#!/bin/sh

# Aplicar migrações
echo "Aplicando migrações..."
python3 -m flask db upgrade

# Verificar estado final das migrações
echo "Estado final das migrações:"
python3 -m flask db current

echo "Iniciando a aplicação..."
exec gunicorn --bind 0.0.0.0:5000 run:app