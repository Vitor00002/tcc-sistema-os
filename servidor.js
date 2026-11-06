const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8081;

// Diretório onde os arquivos e os hashes serão recebidos
const uploadDir = 'C:\\Users\\vitor_dfz2to2\\Documents\\fotos';
if (!fs.existsSync(uploadDir)) { fs.mkdirSync(uploadDir, { recursive: true }); }

// Servirá a pasta "public" onde deve ficar o seu index.html
app.use(express.static('public'));

app.post('/upload-binario', (req, res) => {
  // 1. Lê o nome completo (já com o prefixo OS.00) e o Hash enviados pelo celular
  const fileName = decodeURIComponent(req.headers['x-file-name']);
  const fileHash = req.headers['x-file-hash']; 

  if (!fileName || !fileHash) {
    return res.status(400).json({ error: 'Cabeçalhos x-file-name ou x-file-hash ausentes.' });
  }

  const finalPath = path.join(uploadDir, fileName);
  const hashPath = path.join(uploadDir, `${fileName}.sha256`);

  const stream = fs.createWriteStream(finalPath);
  
  // 2. Despeja os bytes vindos da rede diretamente no HD (Sem sobrecarregar a RAM)
  req.pipe(stream);

  stream.on('close', () => {
    console.log(`✅ Arquivo Salvo no HD: ${fileName}`);
    
    // 3. ATOMICIDADE: Grava o Hash lado a lado com a mídia APENAS quando a mídia termina de gravar.
    // Isso é o que "acorda" o motor Python ou Batch com segurança.
    fs.writeFileSync(hashPath, fileHash);
    console.log(`🔐 Hash Sidecar Gravado: ${fileName}.sha256`);
    
    res.json({ status: 'OK' });
  });

  stream.on('error', (err) => {
    console.error("Erro ao gravar no HD:", err);
    res.status(500).json({ error: 'Erro de I/O local' });
  });

  req.on('aborted', () => {
    console.log(`⚠️ Conexão interrompida antes do fim: ${fileName}`);
    // Limpeza automática se o técnico sair do alcance do Wi-Fi no meio do upload
    if (fs.existsSync(finalPath)) {
        fs.unlinkSync(finalPath);
    }
  });
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Servidor Node.js operando na porta ${PORT}`);
});

// A BLINDAGEM: Desliga ABSOLUTAMENTE TODOS os limites de tempo do Node.js
// Isso permite transferir vídeos de 2GB, 5GB ou 10GB na rede local sem o servidor derrubar a conexão.
server.timeout = 0;
server.keepAliveTimeout = 0;
server.headersTimeout = 0;
server.requestTimeout = 0;