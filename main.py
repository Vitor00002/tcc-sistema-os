import os
import time
import shutil
import hashlib
import subprocess
import requests
import re
from datetime import datetime

PASTA_ENTRADA = r"C:\Users\vitor_dfz2to2\Documents\fotos"
PASTA_QUARENTENA = os.path.join(PASTA_ENTRADA, "QUARENTENA")
PASTA_PENDENTES = os.path.join(PASTA_ENTRADA, "PENDENTES")
ARQUIVO_DESTINOS = "dest.txt"
ARQUIVO_HISTORICO = "historico.txt"
IP_NOTIFICACAO = "https://192.168.2.129/noti_pasta_ARQ_servidor2"

for pasta in [PASTA_QUARENTENA, PASTA_PENDENTES]:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

def calcular_hash_local(caminho_arquivo):
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def enviar_alerta(titulo, tag, mensagem):
    headers = {"Priority": "5", "Tags": tag, "Title": titulo}
    try:
        requests.post(IP_NOTIFICACAO, data=mensagem, headers=headers, verify=False, timeout=3)
    except:
        pass

def extrair_e_limpar_os(nome_midia):
    padrao = r'(?i)(?:os[-_.\s]*)?0*(\d+)'
    match = re.search(padrao, nome_midia)
    
    if match:
        numeros = match.group(1)
        os_oficial = f"OS.00{str(int(numeros))}"
        nome_limpo = re.sub(padrao, os_oficial, nome_midia, count=1)
        nome_limpo = nome_limpo.replace(" ", "-")
        return os_oficial, nome_limpo
        
    return None, nome_midia.replace(" ", "-")

def registrar_historico(os_numero, nome_arquivo, caminho_destino):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_str = os_numero if os_numero else "SEM_OS"
    linha_log = f"[{agora}] OS: {os_str} | ARQUIVO: {nome_arquivo} | MOVIDO PARA: {caminho_destino}\n"
    try:
        with open(ARQUIVO_HISTORICO, 'a', encoding='utf-8') as f:
            f.write(linha_log)
    except Exception as e:
        print(f"[!] Erro ao gravar histórico: {e}")

def processar_arquivos():
    lock_path = os.path.join(PASTA_ENTRADA, "lock_dir")
    try:
        os.mkdir(lock_path)
    except FileExistsError:
        # TRATAMENTO DE TRAVA VELHA (STALE LOCK / DEADLOCK RECOVERY)
        tempo_atual = time.time()
        try:
            tempo_trava = os.path.getmtime(lock_path)
            # Se a trava existe há mais de 15 minutos (900 segundos), o processo anterior crachou
            if (tempo_atual - tempo_trava) > 900:
                print("[!] Trava morta (Stale Lock) detetada. Removendo bloqueio zumbi...")
                os.rmdir(lock_path)
                os.mkdir(lock_path)  # Adquire a trava recém-libertada
            else:
                return  # O processo atual é recente e ainda está a trabalhar (concorrência normal)
        except Exception:
            return  # Em caso de falha de leitura de I/O, aborta e tenta no próximo ciclo

    try:
        sidecars = [f for f in os.listdir(PASTA_ENTRADA) if f.endswith('.sha256') and os.path.isfile(os.path.join(PASTA_ENTRADA, f))]
        
        for sidecar in sidecars:
            try:
                caminho_sidecar = os.path.join(PASTA_ENTRADA, sidecar)
                nome_midia = sidecar.replace('.sha256', '')
                caminho_midia = os.path.join(PASTA_ENTRADA, nome_midia)

                if not os.path.exists(caminho_midia):
                    continue

                with open(caminho_sidecar, 'r', encoding='utf-8') as f:
                    hash_esperado = f.read().strip()
                    
                if hash_esperado != calcular_hash_local(caminho_midia):
                    print(f"[ERRO CRÍTICO] Bit-flip em {nome_midia}. Movendo para QUARENTENA.")
                    shutil.move(caminho_midia, os.path.join(PASTA_QUARENTENA, nome_midia))
                    shutil.move(caminho_sidecar, os.path.join(PASTA_QUARENTENA, sidecar))
                    continue
                    
                os.remove(caminho_sidecar)

                os_numero, os_limpa = extrair_e_limpar_os(nome_midia)
                extensao = os_limpa.lower().split('.')[-1]
                
                if extensao in ['mp4', 'mov', 'avi', 'mkv']:
                    cmd_ffprobe = ['ffprobe', '-v', 'error', '-select_streams', 'v', '-of', 'default=noprint_wrappers=1:nokey=1', '-show_entries', 'stream=r_frame_rate', caminho_midia]
                    try:
                        saida_fps = subprocess.check_output(cmd_ffprobe).decode('utf-8').strip()
                        num, den = saida_fps.split('/')
                        fps = int(num) / int(den) if int(den) > 0 else int(num)
                        
                        if fps > 30:
                            caminho_temp = os.path.join(PASTA_ENTRADA, f"temp_{nome_midia}")
                            assinatura_metadata = f"Cadeia de Custodia. Hash Original Validado: {hash_esperado}. Triage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            
                            subprocess.run([
                                'ffmpeg', '-i', caminho_midia, '-r', '30', '-c:v', 'libx264', 
                                '-preset', 'fast', '-crf', '23', '-c:a', 'copy', 
                                '-metadata', f'comment={assinatura_metadata}', 
                                caminho_temp, '-y', '-loglevel', 'error'
                            ])
                            os.replace(caminho_temp, caminho_midia)
                    except Exception as e:
                        print(f"Erro ao processar framerate/metadados: {e}")

                pasta_destino = None
                
                if os_numero and os.path.exists(ARQUIVO_DESTINOS):
                    with open(ARQUIVO_DESTINOS, 'r', encoding='utf-8') as f:
                        for linha in f:
                            linha_limpa = linha.strip()
                            padrao_busca = rf"(?:\\|/){os_numero}$"
                            if re.search(padrao_busca, linha_limpa):
                                pasta_destino = linha_limpa
                                break

                if not pasta_destino:
                    nome_erro = os_numero if os_numero else "SEM_OS"
                    enviar_alerta("ERRO--Destino/OS inexistente", "warning,man_shrugging", nome_erro)
                    
                    destino_pendente = os.path.join(PASTA_PENDENTES, os_limpa)
                    shutil.move(caminho_midia, destino_pendente)
                    registrar_historico(os_numero, os_limpa, destino_pendente)
                else:
                    pasta_fotos_final = os.path.join(pasta_destino, "FOTOS")
                    if extensao != 'pdf' and not os.path.exists(pasta_fotos_final):
                        os.makedirs(pasta_fotos_final)
                    
                    pasta_alvo = pasta_fotos_final if extensao != 'pdf' else pasta_destino
                    destino_final = os.path.join(pasta_alvo, os_limpa)
                    shutil.move(caminho_midia, destino_final)
                    registrar_historico(os_numero, os_limpa, destino_final)
            
            except PermissionError:
                continue
            except Exception as e:
                print(f"[!] Erro inesperado no arquivo {sidecar}: {e}")
                continue

    finally:
        # A remoção do lock só ocorre se o script chegar ao fim do ciclo sem crachar
        if os.path.exists(lock_path):
            try:
                os.rmdir(lock_path)
            except Exception:
                pass

if __name__ == "__main__":
    while True:
        processar_arquivos()
        time.sleep(2)