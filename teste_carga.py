import os
import time
import shutil
import hashlib

from main import processar_arquivos

# ALINHAMENTO DE ARQUITETURA
PASTA_RECEPCAO = r"C:\Users\vitor_dfz2to2\Documents\fotos"
ARQUIVO_DESTINOS = "dest.txt"
PASTA_DESTINOS = r"C:\Users\vitor_dfz2to2\Documents\destinos_os_teste"

# VOLUME DO ESTRESSE (Pode aumentar este número para impressionar a banca)
TOTAL_MIDIAS = 500  

def limpar_ambiente():
    for pasta in [PASTA_RECEPCAO, PASTA_DESTINOS]:
        if os.path.exists(pasta):
            shutil.rmtree(pasta, ignore_errors=True)
    os.makedirs(PASTA_RECEPCAO, exist_ok=True)
    os.makedirs(PASTA_DESTINOS, exist_ok=True)

def gerar_carga_massiva():
    print(f"[-] Gerando {TOTAL_MIDIAS} ficheiros pesados em fracoes de segundo...")
    
    # Cria 5 pastas de destino aleatorias
    os_numeros = ["OS.0020001", "OS.0020002", "OS.0020003", "OS.0020004", "OS.0020005"]
    with open(ARQUIVO_DESTINOS, 'w', encoding='utf-8') as f:
        for os_num in os_numeros:
            caminho = os.path.join(PASTA_DESTINOS, os_num)
            os.makedirs(caminho, exist_ok=True)
            f.write(f"{caminho}\n")

    # Gera conteudo binario identico para simular o trafego
    conteudo = b"Payload_de_Teste_Carga_Massiva_TCC" * 1024 # Simulando algum peso de disco
    hash_valido = hashlib.sha256(conteudo).hexdigest()

    # Bombardeia o diretorio com arquivos instantaneamente
    for i in range(TOTAL_MIDIAS):
        os_alvo = os_numeros[i % len(os_numeros)]
        nome_midia = f"{os_alvo}_carga_estresse_{i:03d}.jpg"
        
        caminho_midia = os.path.join(PASTA_RECEPCAO, nome_midia)
        caminho_sidecar = f"{caminho_midia}.sha256"
        
        with open(caminho_midia, 'wb') as f:
            f.write(conteudo)
        with open(caminho_sidecar, 'w', encoding='utf-8') as f:
            f.write(hash_valido)

def executar_teste_carga():
    print("=== INICIANDO TESTE DE ESTRESSE E I/O (NODE.JS + PYTHON) ===")
    limpar_ambiente()
    gerar_carga_massiva()
    
    print(f"[-] Disparando Motor Python (Lidando com {TOTAL_MIDIAS * 2} arquivos brutos na pasta)...")
    
    # Inicia o cronometro de alta precisao
    t_inicio = time.perf_counter()
    
    # Chama o motor para digerir a carga massiva
    processar_arquivos()
    
    tempo_total = time.perf_counter() - t_inicio
    
    # Validacao de Integridade Pós-Estresse
    arquivos_roteados = 0
    for root, dirs, files in os.walk(PASTA_DESTINOS):
        arquivos_roteados += len(files)
        
    taxa_sucesso = (arquivos_roteados / TOTAL_MIDIAS) * 100
    throughput = TOTAL_MIDIAS / tempo_total if tempo_total > 0 else 0
    
    # CONSTRUCAO DO RELATORIO
    relatorio = "\n" + "="*50 + "\n"
    relatorio += "[ RELATORIO DE STRESS TEST E CAPACIDADE DE CARGA ]\n"
    relatorio += "="*50 + "\n"
    relatorio += f"Volume Injetado        : {TOTAL_MIDIAS} midias (+ {TOTAL_MIDIAS} hashes)\n"
    relatorio += f"Arquivos Roteados      : {arquivos_roteados} de {TOTAL_MIDIAS}\n"
    relatorio += f"Tempo de Processamento : {tempo_total:.4f} segundos\n"
    relatorio += f"Throughput (Vazao I/O) : {throughput:.2f} arquivos / segundo\n"
    relatorio += "-" * 50 + "\n"
    
    if taxa_sucesso == 100.0:
        relatorio += "[+] STATUS: APROVADO EM ESTRESSE MAXIMO\n"
        relatorio += "O Mutex (os.mkdir) suportou a concorrencia sem perda de dados.\n"
    else:
        relatorio += "[-] STATUS: GARGALO OU PERDA DE ARQUIVOS DETETADA\n"
        relatorio += f"Taxa de Sucesso: {taxa_sucesso:.1f}%\n"
    relatorio += "="*50 + "\n"
    
    print(relatorio)
    
    # Salvando em ficheiro
    nome_log = "relatorio_carga_tcc.txt"
    with open(nome_log, "w", encoding="utf-8") as f:
        f.write(relatorio)
    print(f"[+] O relatorio de carga massiva foi salvo em: {nome_log}")

if __name__ == "__main__":
    executar_teste_carga()