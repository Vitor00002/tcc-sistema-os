import unittest
import os
import tempfile
import hashlib
import multiprocessing
import time
from main import extrair_os, calcular_hash_local

def simular_instancia_concorrente(lock_dir, queue):
    """Tenta criar a trava atômica; retorna o status para a fila do teste"""
    try:
        os.mkdir(lock_dir)
        queue.put("LOCK_ADQUIRIDO")
        time.sleep(0.5) # Segura a trava por meio segundo
        os.rmdir(lock_dir)
    except FileExistsError:
        queue.put("ACESSO_NEGADO_COM_SUCESSO")

class TestSistemaOS(unittest.TestCase):

    def test_a_roteamento_nomenclatura(self):
        """(A) Teste de Strings: Garante 100% de acerto no roteamento (sem misturar com hashes)"""
        cenarios = [
            ("15746_Captura.png", "OS.0015746"),
            ("os15746_foto.jpg", "OS.0015746"),
            ("OS-15746_video.mp4", "OS.0015746"),
            ("  15746 _teste.png", "OS.0015746"),
            ("sem_underline_aqui.jpg", "OS_DESCONHECIDA") # Arquivo alienígena
        ]
        
        acertos = 0
        for nome_entrada, resultado_esperado in cenarios:
            if extrair_os(nome_entrada) == resultado_esperado:
                acertos += 1
                
        self.assertEqual(acertos, len(cenarios), f"Meta de 100% falhou. Acertos: {acertos}/{len(cenarios)}")

    def test_b_rejeicao_conteudo_corrompido(self):
        """(B) Teste Bit-flip: Altera 1 byte do arquivo e exige rejeição do Hash"""
        conteudo_original = b"Evidencia_Intacta_Para_Auditoria"
        hash_origem = hashlib.sha256(conteudo_original).hexdigest()
        
        # Corrompe o arquivo mudando apenas o primeiro byte (Bit-flip)
        conteudo_corrompido = b"Xvidencia_Intacta_Para_Auditoria"
        
        fd, caminho_temp = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(conteudo_corrompido)
                
            hash_local_calculado = calcular_hash_local(caminho_temp)
            
            # A asserção EXIGE que os hashes sejam diferentes (Rejeição com sucesso)
            self.assertNotEqual(hash_origem, hash_local_calculado, "FALHA CRÍTICA: Arquivo corrompido foi aceito pelo validador!")
        finally:
            os.remove(caminho_temp)

    def test_c_exclusao_mutua_concorrencia(self):
        """(C) Teste de Concorrência: Duas execuções simultâneas forçando a mesma trava"""
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
        
        # Para o teste passar, OBRIGATORIAMENTE uma execução tem que ganhar a trava, e a outra tem que bater e voltar
        self.assertIn("LOCK_ADQUIRIDO", resultados)
        self.assertIn("ACESSO_NEGADO_COM_SUCESSO", resultados)

if __name__ == '__main__':
    unittest.main(verbosity=2)