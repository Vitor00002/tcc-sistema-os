import os
import time
import shutil
import hashlib

from main import processar_arquivos

# 1. ALINHAMENTO DE ARQUITETURA
PASTA_RECEPCAO = r"C:\Users\vitor_dfz2to2\Documents\fotos"
PASTA_QUARENTENA = os.path.join(PASTA_RECEPCAO, "QUARENTENA")
ARQUIVO_DESTINOS = "dest.txt"
PASTA_DESTINOS_SIMULADOS = r"C:\Users\vitor_dfz2to2\Documents\destinos_os_teste"

def limpar_ambiente():
    for pasta in [PASTA_RECEPCAO, PASTA_DESTINOS_SIMULADOS]:
        if os.path.exists(pasta):
            shutil.rmtree(pasta, ignore_errors=True)
            
    os.makedirs(PASTA_RECEPCAO, exist_ok=True)
    os.makedirs(PASTA_QUARENTENA, exist_ok=True)
    os.makedirs(PASTA_DESTINOS_SIMULADOS, exist_ok=True)

def criar_arquivo_teste(nome, conteudo, corromper=False):
    caminho_midia = os.path.join(PASTA_RECEPCAO, nome)
    caminho_sidecar = f"{caminho_midia}.sha256"
    
    hash_original = hashlib.sha256(conteudo).hexdigest()
    
    if corromper:
        conteudo = b"Conteudo_Alterado_Por_Ruidos_Na_Rede_Wi-Fi_Ou_Erro_De_Disco"
            
    with open(caminho_midia, 'wb') as f:
        f.write(conteudo)
        
    with open(caminho_sidecar, 'w', encoding='utf-8') as f:
        f.write(hash_original)

def executar_benchmark():
    print("=== INICIANDO BENCHMARK DA ARQUITETURA LOCAL (NODE.JS + PYTHON) ===")
    limpar_ambiente()
    
    os_numeros = ["OS.0015000", "OS.0015001", "OS.0015002"]
    with open(ARQUIVO_DESTINOS, 'w', encoding='utf-8') as f:
        for os_num in os_numeros:
            caminho_os = os.path.join(PASTA_DESTINOS_SIMULADOS, os_num)
            os.makedirs(caminho_os, exist_ok=True)
            f.write(f"{caminho_os}\n")
            
    print("\n[1] Injetando carga de estresse...")
    
    criar_arquivo_teste("OS_15000_foto1.jpg", b"Foto1_Valida")
    criar_arquivo_teste("os15001_foto2.jpg", b"Foto2_Valida")
    criar_arquivo_teste(" 15002 _foto3.jpg", b"Foto3_Valida") 
    
    criar_arquivo_teste("OS_15000_corrompida.jpg", b"Original1", corromper=True)
    criar_arquivo_teste("0S15001_corrompida2.jpg", b"Original2", corromper=True)

    print("[2] Acionando o Motor Python de Validacao (main.py)...")
    t_inicio = time.time()
    
    processar_arquivos()
    
    tempo_total = time.time() - t_inicio
    
    print("\n[3] Calculando Resultados Dinamicamente...")
    
    arquivos_na_quarentena = 0
    if os.path.exists(PASTA_QUARENTENA):
        arquivos_na_quarentena = len([f for f in os.listdir(PASTA_QUARENTENA) if not f.endswith('.sha256')])
    
    arquivos_roteados = 0
    for os_num in os_numeros:
        pasta_fotos = os.path.join(PASTA_DESTINOS_SIMULADOS, os_num, "FOTOS")
        if os.path.exists(pasta_fotos):
            arquivos_roteados += len(os.listdir(pasta_fotos))

    taxa_sucesso_roteamento = (arquivos_roteados / 3) * 100
    taxa_rejeicao_corrupcao = (arquivos_na_quarentena / 2) * 100
        
    # --- CONSTRUÇÃO DO RELATÓRIO EM MEMÓRIA ---
    relatorio = "\n" + "="*50 + "\n"
    relatorio += "[ RELATORIO DINAMICO DE DESEMPENHO E INTEGRIDADE ]\n"
    relatorio += "="*50 + "\n"
    relatorio += f"Arquivos Roteados com Exito : {arquivos_roteados} de 3\n"
    relatorio += f"Midias Barradas (Quarentena): {arquivos_na_quarentena} de 2\n"
    relatorio += f"Tempo Computacional (CPU)   : {tempo_total:.4f} segundos\n"
    relatorio += "-" * 50 + "\n"
    
    if taxa_sucesso_roteamento == 100.0 and taxa_rejeicao_corrupcao == 100.0:
        relatorio += f"[+] STATUS: {taxa_sucesso_roteamento:.0f}% SUCESSO VERIFICADO\n"
        relatorio += "O sistema higienizou nomes, detectou bit-flips e roteou os arquivos reais.\n"
    else:
        relatorio += "[-] STATUS: FALHA DETECTADA\n"
        relatorio += f"Taxa de Acerto em Roteamento: {taxa_sucesso_roteamento:.1f}%\n"
        relatorio += f"Taxa de Deteccao Criptografica: {taxa_rejeicao_corrupcao:.1f}%\n"
    relatorio += "="*50 + "\n"

    # Imprime no Ecrã
    print(relatorio)
    
    # Grava no Ficheiro de Log
    nome_arquivo_log = "relatorio_desempenho_tcc.txt"
    with open(nome_arquivo_log, "w", encoding="utf-8") as f_log:
        f_log.write(relatorio)
    print(f"[+] O relatorio foi salvo em: {nome_arquivo_log}")

if __name__ == "__main__":
    executar_benchmark()