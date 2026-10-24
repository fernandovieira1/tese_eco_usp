# Registro local da base paralela de custos

Pasta: modelos/base_custos_investigacao. Núcleo CONAB e câmbio BCB auditados; extrato regional IMEA incorporado em tabelas separadas após conferir SHA256 exato. Sete testes aprovados, notebook com oito células executadas e duas reproduções isoladas dos 16 CSVs com hashes idênticos. Base3 publicada preservada byte a byte. Sem commit/push ou regressões H1.

CONAB: 188 planilhas, 158 candidatas no alvo, 85 estritas após reconciliação de componentes; 850 valores estritos convertidos em USD2024/ha. IMEA: 195 unidades planilha/coluna, 585 células (525 numéricas), 195 valores candidatos descritivos; todos em quarentena para comparabilidade e sem conversão USD. Pacotes truncados não utilizados; somente o CSV regional do último pacote foi materializado e validado, sem alegação de validação do ZIP inteiro. Notas e auditoria originais regionais ainda não materializadas localmente. Limites e hashes em README.md, manifesto.json e relatorio_qualidade.md.

Atualização: 143 notas e audit regional recebidos integralmente, hashes exatos conferidos e validação estrutural adicionada ao construtor. Duas exclusões CONAB documentadas e confrontadas por leitura com a amostra e os holdouts do piloto, sem alterá-lo.
