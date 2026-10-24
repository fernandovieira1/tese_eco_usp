# Publicação da base paralela de custos — 24/10/2026

Autorização explícita do usuário para publicar a pasta paralela em main. Escopo: base_custos_investigacao e cinco auditorias diretamente relacionadas. Base3, base2/complemento_conab e piloto antigo não são modificados/publicados por este commit.

Antes das adequações de portabilidade, os 190 hashes históricos conferiram. Os testes tinham dependências de origens locais não publicadas e um caminho absoluto; agora verificam as cópias incluídas e preservacao_publicacao.json (110 arquivos de dados/fontes e base3 já versionada). O inventário histórico original permanece intacto. Nenhuma transformação de valores ou reespecificação dos modelos foi feita.

Teste em clone limpo do HEAD remoto anterior, acrescido apenas da pasta autorizada: sete comandos de construção/reprodução/teste passaram. Inclui sete testes unitários de núcleo, sete de avaliação e duas reproduções isoladas de núcleo, cada cultura, pecuária e regiões. Seis notebooks (23 células de código) executaram sem erro nesse clone. Há avisos de diretório temporário IPython e transporte local do kernel, sem falha. Evidências completas em validacao_checkout_limpo.json e validacao_notebooks_checkout.json.

Insumos necessários copiados já estavam na pasta fontes. DAP e painel base3 requeridos estão versionados no repositório. Não é necessário publicar os antigos complementos. Reextração a partir de XLSX IMEA e brutos geográficos continua dependente dos arquivos do ambiente pai; reprodução local comprovada é dos extratos incluídos, cujos hashes foram conferidos. Não há coleta de rede no build.

Não há .github/workflows no checkout. Verificação remota de commit/status deve ser informada na entrega, sem atribuir aprovação de CI inexistente. Sem force push.

Revisão de staging: 159 caminhos explícitos (154 na base paralela e cinco auditorias), bytes idênticos aos arquivos locais. git diff --check acusa CRLF e espaços literais preservados em CSVs. Com cr-at-eol, restam 559 avisos exclusivamente em CSVs; não foram normalizados para evitar alterar os hashes e o conteúdo de origem. Nenhum aviso fora de CSV.
