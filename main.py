import os
import time
import shutil
import hashlib
import subprocess
import requests

PASTA_ENTRADA = r"D:\RECEPCAO\FOTOS"
PASTA_QUARENTENA = os.path.join(PASTA_ENTRADA, "QUARENTENA")
ARQUIVO_DESTINOS = "dest.txt"
IP_NOTIFICACAO = "https://192.168.2.129/noti_pasta_ARQ_servidor2"

if not os.path.exists(PASTA_QUARENTENA):
    os.makedirs(PASTA_QUARENTENA)

def calcular_hash_local(caminho_arquivo):
    """Calcula o SHA-256 do arquivo localmente em blocos para não sobrecarregar a RAM"""
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

def processar_arquivos():
    lock_path = os.path.join(PASTA_ENTRADA, "lock_dir")
    try:
        os.mkdir(lock_path)  # Trava atômica (Mutex de SO)
    except FileExistsError:
        return  # Outra instância já está processando

    try:
        # Busca apenas os arquivos .sha256 gerados pelo Node.js
        sidecars = [f for f in os.listdir(PASTA_ENTRADA) if f.endswith('.sha256') and os.path.isfile(os.path.join(PASTA_ENTRADA, f))]
        
        for sidecar in sidecars:
            caminho_sidecar = os.path.join(PASTA_ENTRADA, sidecar)
            nome_midia = sidecar.replace('.sha256', '')
            caminho_midia = os.path.join(PASTA_ENTRADA, nome_midia)

            if not os.path.exists(caminho_midia):
                continue # Mídia ainda não terminou de baixar ou falhou

            # 1. VALIDAÇÃO CRIPTOGRÁFICA (Zero-Trust)
            with open(caminho_sidecar, 'r', encoding='utf-8') as f:
                hash_esperado = f.read().strip()
                
            hash_calculado = calcular_hash_local(caminho_midia)

            if hash_esperado != hash_calculado:
                print(f"[ERRO CRÍTICO] Bit-flip detectado em {nome_midia}. Movendo para QUARENTENA.")
                shutil.move(caminho_midia, os.path.join(PASTA_QUARENTENA, nome_midia))
                shutil.move(caminho_sidecar, os.path.join(PASTA_QUARENTENA, sidecar))
                continue
                
            print(f"[SUCESSO] Integridade confirmada para {nome_midia}")
            os.remove(caminho_sidecar) # Apaga o sidecar, pois a mídia é válida

            # 2. LIMPEZA DA NOMENCLATURA (Regras do seu Batch)
            os_limpa = nome_midia.replace("0S", "OS").replace("0s", "OS").replace("os", "OS").replace("OS_", "OS.00")
            os_numero = os_limpa[:10] # Extrai "OS.00XXXXX"

            # 3. VERIFICAÇÃO DE VÍDEO E FRAMERATE (FFMPEG)
            extensao = os_limpa.lower().split('.')[-1]
            if extensao in ['mp4', 'mov', 'avi', 'mkv']:
                cmd_ffprobe = ['ffprobe', '-v', 'error', '-select_streams', 'v', '-of', 'default=noprint_wrappers=1:nokey=1', '-show_entries', 'stream=r_frame_rate', caminho_midia]
                try:
                    saida_fps = subprocess.check_output(cmd_ffprobe).decode('utf-8').strip()
                    num, den = saida_fps.split('/')
                    fps = int(num) / int(den) if int(den) > 0 else int(num)
                    
                    if fps > 30:
                        print(f"Vídeo com {fps} fps. Comprimindo para 30fps...")
                        caminho_temp = os.path.join(PASTA_ENTRADA, f"temp_{nome_midia}")
                        subprocess.run(['ffmpeg', '-i', caminho_midia, '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-c:a', 'copy', caminho_temp, '-y', '-loglevel', 'error'])
                        os.replace(caminho_temp, caminho_midia)
                except Exception as e:
                    print(f"Erro ao processar framerate: {e}")

            # 4. ROTEAMENTO PARA A PASTA DE DESTINO
            pasta_destino = None
            if os.path.exists(ARQUIVO_DESTINOS):
                with open(ARQUIVO_DESTINOS, 'r', encoding='utf-8') as f:
                    for linha in f:
                        if os_numero in linha:
                            pasta_destino = linha.strip()
                            break

            if not pasta_destino:
                print(f"---Pasta {os_numero} não encontrada---")
                enviar_alerta("ERRO--Pasta inexistente", "warning,man_shrugging", os_numero)
            else:
                pasta_fotos_final = os.path.join(pasta_destino, "FOTOS")
                if not extensao == 'pdf':
                    if not os.path.exists(pasta_fotos_final):
                        os.makedirs(pasta_fotos_final)
                    shutil.move(caminho_midia, os.path.join(pasta_fotos_final, nome_midia))
                else:
                    shutil.move(caminho_midia, os.path.join(pasta_destino, nome_midia))

    finally:
        os.rmdir(lock_path) # Libera a trava

if __name__ == "__main__":
    while True:
        processar_arquivos()
        time.sleep(2)