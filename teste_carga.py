import os
import time
import hashlib
import tempfile

# Caminho da sua pasta de entrada (A mesma do main.py)
PASTA_ENTRADA = r"C:\Users\vitor_dfz2to2\Meu Drive\OS_FOTOS_TEMP" 

def injetar_carga(quantidade_arquivos):
    """
    Simula o envio massivo de ficheiros pelo Google Apps Script.
    Cria ficheiros binários aleatórios e os respetivos Sidecars (.sha256).
    """
    print(f"--- INICIANDO INJEÇÃO DE {quantidade_arquivos} FICHEIROS ---")
    inicio_injecao = time.time()
    
    # Cria a pasta de entrada caso ela não exista apenas para garantir
    os.makedirs(PASTA_ENTRADA, exist_ok=True)

    for i in range(quantidade_arquivos):
        # Simula nomes de diferentes OS misturadas
        nome_midia = f"190{i}_foto_stress_{i}.jpg"
        caminho_midia = os.path.join(PASTA_ENTRADA, nome_midia)
        caminho_sidecar = caminho_midia + ".sha256"

        # Gera um ficheiro fictício de 100KB com dados aleatórios
        conteudo_binario = os.urandom(1024 * 100) 
        
        # 1. Escreve a foto falsa
        with open(caminho_midia, 'wb') as f:
            f.write(conteudo_binario)
            
        # 2. Calcula o Hash e escreve o sidecar
        hash_calc = hashlib.sha256(conteudo_binario).hexdigest()
        with open(caminho_sidecar, 'w') as f:
            f.write(hash_calc)

    tempo_injecao = time.time() - inicio_injecao
    print(f"Carga de {quantidade_arquivos} ficheiros injetada em {tempo_injecao:.2f} segundos!")
    print("-> Agora ligue o seu 'main.py' para ver a velocidade de processamento.")

if __name__ == "__main__":
    # Testa o volume equivalente a um dia inteiro de trabalho (aprox. 150 mídias)
    injetar_carga(150)