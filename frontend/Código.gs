// Retorna a interface HTML para o navegador/celular
function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Sistema OS - Triagem')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// Recebe o arquivo comprimido, salva e cria o arquivo sidecar (.sha256)
function processUpload(base64Data, fileName, fileHash, osNumber) {
  try {
    // ID da pasta OS_FOTOS_TEMP criada automaticamente
    var folderId = "ID_OCULTADO-POR_MOTIVOS_DE_SEGURANÇA"; 
    var folder = DriveApp.getFolderById(folderId);
    
    // Normalização básica do número da OS (remove espaços e garante caixa alta)
    var cleanOsNumber = osNumber.trim().toUpperCase().replace(/\s+/g, '-');
    var finalFileName = cleanOsNumber + "_" + fileName;
    
    // Verifica se o base64 chegou no formato correto
    if (!base64Data || base64Data.indexOf(',') === -1) {
      throw new Error("Os dados do arquivo (Base64) chegaram vazios ou em formato inválido.");
    }
    
    // 1. Decodifica o Base64 e salva o arquivo de mídia (Imagem/Vídeo)
    var splitBase = base64Data.split(',');
    var contentType = splitBase[0].split(':')[1].split(';')[0];
    var bytes = Utilities.base64Decode(splitBase[1]);
    
    var blob = Utilities.newBlob(bytes, contentType, finalFileName);
    var file = folder.createFile(blob);
    
    // 2. Cria o arquivo Sidecar (A Assinatura Criptográfica de Origem)
    var sidecarName = finalFileName + ".sha256";
    folder.createFile(sidecarName, fileHash, MimeType.PLAIN_TEXT);
    
    return "✅ Mídia enviada com sucesso! Hash: " + fileHash.substring(0,8) + "...";
    
  } catch (erro) {
    // Devolve o motivo exato para a tela do celular
    return "Erro no servidor: " + erro.message;
  }
}