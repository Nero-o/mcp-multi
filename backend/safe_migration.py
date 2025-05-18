#!/usr/bin/env python3
import subprocess
import sys
import time

def run_command(command):
    try:
        print(f"Executando: {command}")
        result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}", file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Erro ao executar comando: {e}", file=sys.stderr)
        return False

# Inicializar as migrações se necessário
if not run_command("python3 -m flask db current"):
    print("Inicializando migrações...")
    run_command("python3 -m flask db init")

# Tentar executar as migrações com retry
max_retries = 3
for attempt in range(1, max_retries + 1):
    print(f"Tentativa {attempt}/{max_retries} de executar migrações...")
    
    try:
        # Gerar migração
        migrate_success = run_command("python3 -m flask db migrate -m 'Auto migration'")
        
        # Se a migração foi gerada com sucesso, aplicar
        if migrate_success:
            upgrade_success = run_command("python3 -m flask db upgrade")
            if upgrade_success:
                print("Migrações aplicadas com sucesso!")
                sys.exit(0)
        
        if attempt < max_retries:
            print(f"Falha na migração. Tentando novamente em 5 segundos...")
            time.sleep(5)
        else:
            print("AVISO: Não foi possível aplicar migrações após várias tentativas.")
            print("A aplicação continuará, mas pode haver problemas com o banco de dados.")
            sys.exit(1)
    except Exception as e:
        print(f"Exceção durante migração: {e}")
        if attempt < max_retries:
            print(f"Tentando novamente em 5 segundos...")
            time.sleep(5)
        else:
            print("AVISO: Exceção ao aplicar migrações. A aplicação continuará, mas pode haver problemas.")
            sys.exit(1)