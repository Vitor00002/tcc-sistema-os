import os
import shutil
import hashlib
import re
import time

# --- CONFIGURAÇÕES DO AMBIENTE ---
# Pasta sincronizada pelo Google Drive Desktop
PASTA_ENTRADA = r"C:\caminho\exemplo\Google_Drive\OS_FOTOS_TEMP"
# Servidor local corporativo
PASTA_DESTINO = r"C:\caminho\exemplo\Servidor_Local\OS_Finais"
LOCK_DIR = os.path.join(PASTA_ENTRADA, "lock_dir")
ARQUIVO_LOG = "historico_auditoria.log"

def calcular_hash_local(caminho_arquivo):
    """Calcula o SHA-256 do arquivo físico no disco (hashlib)"""
    sha256 = hashlib.sha256()
    try:
        with open(caminho_arquivo, "rb") as f:
            for bloco in iter(lambda: f.read(4096), b""):
                sha256.update(bloco)
        return sha256.hexdigest()
    except Exception as e:
        registrar_log(f"ERRO ao ler arquivo para hash: {e}")
        return None

def registrar_log(mensagem):
    """Gera log estruturado para a auditoria do TCC (Forçando UTF-8)"""
    data_hora = time.strftime('%d/%m/%Y %H:%M:%S')
    linha = f"[{data_hora}] {mensagem}\n"
    # Tenta imprimir no terminal (ignora erros de acento se o CMD for antigo)
    try:
        print(linha.strip())
    except UnicodeEncodeError:
        print(linha.encode('ascii', 'ignore').decode('ascii').strip())
        
    # Salva no arquivo de histórico com padrão universal UTF-8
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linha)

def extrair_os(nome_arquivo):
    """Engenharia de Software: Padronização rígida para o formato OS.00XXXX"""
    if '_' in nome_arquivo:
        # Pega a primeira parte antes do '_' (o que foi digitado no celular)
        texto_digitado = nome_arquivo.split('_')[0]
        
        # Extrai EXATAMENTE apenas os números do que o técnico digitou
        apenas_numeros = "".join(filter(str.isdigit, texto_digitado))
        
        if apenas_numeros:
            # Força o padrão da empresa. Se digitou 15746, vira OS.0015746
            # Se a OS tiver menos dígitos e precisar de zeros à esquerda, avise que ajustamos!
            return f"OS.00{apenas_numeros}"
            
    return "OS_DESCONHECIDA"

def processar_arquivos():
    """Motor central atômico e validado"""
    
    # 0. Tratamento de Exceção Arquitetural: Verifica se o volume (Drive) está montado
    if not os.path.exists(PASTA_ENTRADA):
        registrar_log(f"AGUARDANDO CONEXÃO: O diretório base {PASTA_ENTRADA} está inacessível. O Google Drive está rodando?")
        return

    # 1. Operação Atômica (Mutex) para evitar concorrência (exigência do prof.)
    try:
        os.mkdir(LOCK_DIR)
    except FileExistsError:
        # Se a pasta já existir, outro script está rodando ou ocorreu crash. Aborta silenciosamente.
        return

    try:
        arquivos = os.listdir(PASTA_ENTRADA)
        sidecars = [f for f in arquivos if f.endswith('.sha256')]

        for sidecar in sidecars:
            caminho_sidecar = os.path.join(PASTA_ENTRADA, sidecar)
            nome_midia = sidecar.replace('.sha256', '')
            caminho_midia = os.path.join(PASTA_ENTRADA, nome_midia)

            # Verifica se a mídia de fato chegou e não está corrompida na origem
            if not os.path.exists(caminho_midia):
                continue

            # 2. Lê o Hash de Origem (do Celular)
            with open(caminho_sidecar, "r") as f:
                hash_origem = f.read().strip()

            # 3. Calcula o Hash de Destino (Local)
            hash_destino = calcular_hash_local(caminho_midia)

            # 4. Validação de Integridade de Ponta a Ponta
            # 4. Validação de Integridade de Ponta a Ponta
            if hash_origem == hash_destino:
                os_limpa = extrair_os(nome_midia)
                pasta_os_destino = os.path.join(PASTA_DESTINO, os_limpa)

                # Cria o diretório da OS se não existir
                os.makedirs(pasta_os_destino, exist_ok=True)

                # Reconstrói o nome da foto para ela também começar com OS.00
                if '_' in nome_midia:
                    resto_do_nome = nome_midia.split('_', 1)[1]
                    nome_foto_padronizado = f"{os_limpa}_{resto_do_nome}"
                else:
                    nome_foto_padronizado = nome_midia

                caminho_final = os.path.join(pasta_os_destino, nome_foto_padronizado)
                
                # Move e renomeia a mídia, e limpa o lixo temporário (Sidecar)
                shutil.move(caminho_midia, caminho_final)
                os.remove(caminho_sidecar)
                
                registrar_log(f"SUCESSO: {nome_foto_padronizado} -> Integridade 100% Validada. Pasta: {os_limpa}")
            else:
                registrar_log(f"FALHA CRÍTICA: Corrupção detectada em {nome_midia}. Hash incompatível.")
                
    except Exception as e:
        registrar_log(f"EXCEÇÃO NÃO TRATADA: {e}")
    finally:
        # Sempre libera a trava no final, garantindo continuidade do sistema
        if os.path.exists(LOCK_DIR):
            os.rmdir(LOCK_DIR)

if __name__ == "__main__":
    registrar_log("--- Iniciando ciclo de monitoramento do motor Python ---")
    # Loop infinito rodando em background (A cada 10 segundos)
    while True:
        processar_arquivos()
        time.sleep(10)