# [BUG] Aprovação publica sugestão com máquina que deixou de ser elegível

**Acompanhamento em 26/11/2026** — Registrado na [issue #30 / BUG-004](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30). Correção validada localmente e aguardando integração. [Relatório de reteste](reteste-bug004.md)

**RELEASE:** R2  
**SPRINT:** 3  
**SEVERIDADE:** Alta  
**PRIORIDADE:** Alta — sugestão para triagem  
**RESPONSÁVEL:** A definir  
**REPORTADO POR:** A confirmar  
**US RELACIONADA:** US17 — Aprovar planejamento de produção. Relacionada à US15 — Compatibilidade entre produtos e máquinas.  
**DRIVER RELACIONADO:** Não se aplica.

## DESCRIÇÃO

Uma sugestão já gerada continua disponível para aprovação após a desativação da máquina atribuída ou a remoção da compatibilidade entre ela e o produto. Ao aprovar a sugestão, o sistema grava essa atribuição e a disponibiliza ao Operador para execução.

## AMBIENTE

- **Ambiente:** Local, FastAPI TestClient com PostgreSQL 18.6 dedicado.
- **Navegador / versão:** Não se aplica.
- **Sistema operacional:** Windows 11 26H2, build 26300.
- **Versão / commit / branch:** `08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`, branch local `docs/qualidade` no mesmo commit de `origin/main`.
- **Alterações locais incluídas:** Nenhuma no produto. Script de investigação avulso.
- **Pré-condições e dados de teste:** Planejador e Operador fictícios, ordem pendente `OP01`, produto `PROD-OP01`, máquina ativa `M01` como única máquina compatível e nenhuma aprovação existente.

## PASSOS PARA REPRODUZIR

1. Como Planejador, gere uma sugestão para `OP01` e guarde o identificador retornado. Use `POST /api/planejamentos/sugestoes` com `{"ordens_ids":["<id-op01>"]}`.
2. Desative `M01` com `PATCH /api/maquinas/<id-m01>/status` e `{"ativo":false}`. Em uma execução independente, mantenha a máquina ativa e retire a compatibilidade com `PUT /api/produtos/<id-prod-op01>/maquinas` e `{"maquinas_ids":[]}`.
3. Consulte os candidatos em `GET /api/planejamentos/aprovacoes/candidatos` e aprove a sugestão original em `POST /api/planejamentos/aprovacoes` com `{"origem":"sugerida","origem_id":"<id-sugestao>","ordens_ids":["<id-op01>"]}`.
4. Consulte `GET /api/planejamentos/aprovacoes` como Operador e confira a máquina atribuída. Como controle, uma nova geração para `OP01` após o passo 2 retorna HTTP 422.

Com `TEST_DATABASE_URL` apontando para PostgreSQL local descartável, execute na pasta `backend`:

```sh
python -m pytest -q -s -p testes.integration.conftest ../docs/qualidade/release-2/auditoria-bugs/evidencias/test_qa_aprovacao.py
```

## RESULTADO ESPERADO

Uma nova aprovação deve disponibilizar para execução uma sequência elegível, conforme a US17 e a restrição de compatibilidade da US15. O sistema deve recusar a aprovação, informar que a sugestão ficou indisponível e preservar seu histórico.

## RESULTADO OBTIDO

Em 2 de 2 variantes, a sugestão permaneceu entre os candidatos. A aprovação retornou HTTP 201 com status `APROVADO`. A atribuição à `M01` foi persistida e apareceu na consulta do Operador, que retornou HTTP 200. A geração de uma nova sugestão retornou HTTP 422 nas duas variantes.

## EVIDÊNCIAS

- [Registro dos resultados](evidencias/aprovacao-maquina-inelegivel.json)
- [Script de reprodução](evidencias/test_qa_aprovacao.py)
- [Código da aprovação no commit avaliado](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f/backend/app/api/routes/aprovacoes_planejamento.py#L124-L166)
- **Forma de confirmação:** Execução integrada da API em processo com PostgreSQL e consultas independentes.
- **Limitações:** Foram testadas alterações anteriores a uma nova aprovação. A corrida entre alterações e aprovação e o tratamento de aprovações preexistentes ficaram fora da reprodução.

## CRITÉRIO DE CORREÇÃO

    Dado que uma sugestão persistida contém uma ordem atribuída a uma máquina elegível na geração
    E que a máquina foi desativada ou perdeu a compatibilidade com o produto antes da aprovação
    Quando o Planejador tentar aprovar essa sugestão
    Então o sistema deve recusar a aprovação e informar que é necessário gerar uma sugestão atualizada
    E nenhuma aprovação deve ser gravada ou disponibilizada ao Operador
    E a sugestão original deve permanecer disponível para consulta histórica

## CHECKLIST DE ENCERRAMENTO

- [ ] Causa identificada e registrada nos comentários
- [ ] Correção feita via Pull Request que referencia esta issue
- [ ] Teste de regressão criado ou atualizado
- [ ] Correção verificada pelo QA
