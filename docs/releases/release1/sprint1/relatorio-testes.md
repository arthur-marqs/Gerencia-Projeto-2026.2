# Relatório de Testes — Sprint 1

## 1. Identificação

- **Projeto:** SetupFlow
- **Release:** Release 1
- **Sprint:** Sprint 1
- **Data da execução:** 29/10/2026
- **Responsável pela execução:** Luiz Inácio
- **Ambiente:** Local
- **Banco de testes:** `setupflow_test`
- **Commit testado:** `63354ee6ba1f43a8e567c34a183b98ad1823a841`

## 2. Objetivo

Este relatório registra a execução dos testes automatizados do backend do SetupFlow durante a Sprint 1 da Release 1.

O objetivo da execução foi verificar os cenários implementados para as User Stories US01 a US08 e para o Driver de Qualidade 05, utilizando um banco exclusivo de testes e registrando a evidência da execução por meio do Pytest.

## 3. Ambiente de execução

A execução foi realizada localmente, utilizando:

- Python 3.12.10;
- Pytest 8.4.2;
- ambiente virtual `.venv`;
- PostgreSQL;
- banco exclusivo de testes `setupflow_test`.

Antes da execução da suíte, foi verificada a conexão com o banco de testes por meio de uma consulta simples, que retornou normalmente.

## 4. Comando utilizado

```bash
python -m pytest -v --junitxml="../docs/releases/release1/sprint1/evidencias/pytest.xml" testes
```

O resultado detalhado da execução foi armazenado em:

[Resultado detalhado do Pytest](evidencias/pytest.xml)

## 5. Escopo da execução

A suíte executada contemplou testes automatizados relacionados aos seguintes itens:

- US01 — Realizar login;
- US02 — Acessar funcionalidades conforme o perfil;
- US03 — Cadastrar máquina;
- US04 — Cadastrar produto;
- US05 — Cadastrar família de produtos;
- US06 — Associar produto a uma família;
- US07 — Cadastrar ordem de produção;
- US08 — Definir prazo e prioridade da ordem;
- Driver 05 — Rate Limiting.

Foram considerados neste relatório apenas os testes efetivamente presentes e executados pela suíte.

## 6. Resultado geral

| Métrica | Resultado |
|---|---:|
| Total de testes executados | 87 |
| Aprovados | 87 |
| Falhas | 0 |
| Erros | 0 |
| Ignorados | 0 |

A execução foi concluída com sucesso, com todos os 87 testes aprovados e código de saída igual a `0`.

## 7. Resultados por requisito

| Requisito | Arquivo de teste | Resultado |
|---|---|---|
| Driver 05 — Rate Limiting | `test_driver05_rate_limiting.py` | Aprovado |
| US01 — Realizar login | `test_us01_auth.py` | Aprovado |
| US02 — Acessar funcionalidades conforme o perfil | `test_us02_access_control.py` | Aprovado |
| US03 — Cadastrar máquina | `test_us03_maquinas.py` | Aprovado |
| US04 — Cadastrar produto | `test_us04_produtos.py` | Aprovado |
| US05 — Cadastrar família de produtos | `test_us05_families.py` | Aprovado |
| US06 — Associar produto a uma família | `test_us06_produto_familia.py` | Aprovado |
| US07 — Cadastrar ordem de produção | `test_us07_ordens_producao.py` | Aprovado |
| US08 — Definir prazo e prioridade da ordem | `test_us08_prazo_prioridade_ordem.py` | Aprovado |

## 8. Observações

Uma execução local anterior apresentou erros durante a preparação dos testes devido ao PostgreSQL estar temporariamente em modo de recuperação.

Essa execução anterior não foi utilizada como evidência deste relatório.

A execução registrada neste documento foi realizada posteriormente, com o banco `setupflow_test` acessível e com todos os testes concluídos com sucesso.

## 9. Conclusão

Com base na execução realizada, a suíte automatizada considerada neste relatório apresentou resultado satisfatório.

Foram executados 87 testes, todos aprovados, sem falhas, erros ou testes ignorados.

A evidência detalhada desta execução está registrada no arquivo `pytest.xml` armazenado junto à documentação da Sprint 1.