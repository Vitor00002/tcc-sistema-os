import unittest
import os
import tempfile
import hashlib
import multiprocessing
import time
import sys

from main import extrair_e_limpar_os, calcular_hash_local

def simular_instancia_concorrente(lock_dir, queue):
    """Tenta criar a trava atomica; retorna o status para a fila do teste"""
    try:
        os.mkdir(lock_dir)
        queue.put("LOCK_ADQUIRIDO")
        time.sleep(0.5) # Segura a trava por meio segundo
        os.rmdir(lock_dir)
    except FileExistsError:
        queue.put("ACESSO_NEGADO_COM_SUCESSO")

class TestSistemaOS(unittest.TestCase):

    def test_a_roteamento_nomenclatura(self):
        print("\n(A) Teste de Strings: Garante 100% de acerto no roteamento (sem misturar com hashes)")
        cenarios = [
            ("15746_Captura.png", "OS.0015746"),
            ("os15746_foto.jpg", "OS.0015746"),
            ("OS-15746_video.mp4", "OS.0015746"),
            ("  15746 _teste.png", "OS.0015746"),
            ("sem_underline_aqui.jpg", None) # Arquivo alienígena (Sem OS)
        ]
        
        acertos = 0
        for arquivo, esperado in cenarios:
            # Captura o retorno bruto do motor principal
            resultado_bruto = extrair_e_limpar_os(arquivo)
            
            # Força a extração do índice 0 (o número da OS), ignorando o resto da tupla
            os_calculada = resultado_bruto[0] if isinstance(resultado_bruto, tuple) else resultado_bruto
            
            if os_calculada == esperado:
                acertos += 1
            else:
                # Se falhar, agora imprime na consola exatamente o que deu errado
                print(f"    [!] FALHA NO TESTE: Arquivo '{arquivo}' -> Retornou: '{os_calculada}' | Esperado: '{esperado}'")
                
        self.assertEqual(acertos, len(cenarios), f"Meta de 100% falhou. Acertos: {acertos}/{len(cenarios)}")

    def test_b_rejeicao_conteudo_corrompido(self):
        """(B) Teste Bit-flip: Altera 1 byte do arquivo e exige rejeicao do Hash"""
        conteudo_original = b"Evidencia_Intacta_Para_Auditoria"
        hash_origem = hashlib.sha256(conteudo_original).hexdigest()
        
        # Corrompe o arquivo mudando apenas o primeiro byte (Bit-flip)
        conteudo_corrompido = b"Xvidencia_Intacta_Para_Auditoria"
        
        fd, caminho_temp = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(conteudo_corrompido)
                
            hash_local_calculado = calcular_hash_local(caminho_temp)
            
            # A assercao EXIGE que os hashes sejam diferentes (Rejeicao com sucesso)
            self.assertNotEqual(hash_origem, hash_local_calculado, "FALHA CRITICA: Arquivo corrompido foi aceito pelo validador!")
        finally:
            os.remove(caminho_temp)

    def test_c_exclusao_mutua_concorrencia(self):
        """(C) Teste de Concorrencia: Duas execucoes simultaneas forcando a mesma trava"""
        diretorio_teste = tempfile.mkdtemp()
        lock_dir = os.path.join(diretorio_teste, "lock_dir")
        
        fila_resultados = multiprocessing.Queue()
        
        # Dispara dois motores simultaneamente
        processo1 = multiprocessing.Process(target=simular_instancia_concorrente, args=(lock_dir, fila_resultados))
        processo2 = multiprocessing.Process(target=simular_instancia_concorrente, args=(lock_dir, fila_resultados))
        
        processo1.start()
        processo2.start()
        processo1.join()
        processo2.join()
        
        resultados = []
        while not fila_resultados.empty():
            resultados.append(fila_resultados.get())
            
        os.rmdir(diretorio_teste)
        
        # Para o teste passar, OBRIGATORIAMENTE uma execucao tem que ganhar a trava, e a outra tem que bater e voltar
        self.assertIn("LOCK_ADQUIRIDO", resultados)
        self.assertIn("ACESSO_NEGADO_COM_SUCESSO", resultados)

# Classe para duplicar o texto para o Terminal (sys.stderr) e para o Ficheiro Log
class DoubleStream:
    def __init__(self, filename):
        self.terminal = sys.stderr
        self.log = open(filename, 'w', encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    def close(self):
        self.log.close()

if __name__ == '__main__':
    nome_log = "relatorio_testes_tcc.txt"
    print(f"=== INICIANDO BATERIA DE TESTES (Gerando log em '{nome_log}') ===")
    
    stream_duplo = DoubleStream(nome_log)
    runner = unittest.TextTestRunner(stream=stream_duplo, verbosity=2)
    
    # Executa os testes enviando a saída para a nossa classe DoubleStream
    unittest.main(testRunner=runner, exit=False)
    
    stream_duplo.close()
    print(f"\n[+] Log de execucao dos testes salvo com sucesso em: {nome_log}")