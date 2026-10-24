# Reprodução do pacote publicado

A construção usa os extratos incluídos em fontes, sem depender de base2/complemento_conab. As avaliações usam também dois arquivos já publicados em base3: fontes_v2/dap_official_2000_2023.csv e painel_h1_base3_v4.csv. Não requer coleta de rede. Python 3.12 e biblioteca padrão bastam para scripts e testes; notebooks requerem nbformat, nbclient e ipykernel.

Na pasta base_custos_investigacao, executar:

```sh
python construir.py
python verificar_reproducao.py
python -m unittest test_base_custos.py
python avaliacao_preditiva/testar.py
python pecuaria/integrar.py
python regionalizacao/integrar.py
python testar_integracao_final.py
```

O teste agrícola reconstrói duas vezes cada cultura em diretórios isolados e compara os CSVs. Os testes finais fazem o mesmo para pecuária e regionalização. preservacao_publicacao.json verifica os dados e insumos publicados e os arquivos versionados de base3. A auditoria histórica de 190 arquivos permanece em avaliacao_preditiva/preservacao_antes.json como evidência da execução original; inclui arquivos locais fora do escopo que não são necessários ao build. Não se afirma que esses arquivos históricos estejam disponíveis num checkout limpo.

Os brutos XLSX IMEA e geográficos continuam no ambiente de coleta pai. O pacote reproduz a integração dos extratos verificados, não a reextração desses brutos indisponíveis. Os endereços de publicação IMEA são vivos e uma nova coleta pode diferir do snapshot. Testes locais e de checkout limpo estão documentados na auditoria de publicação.
