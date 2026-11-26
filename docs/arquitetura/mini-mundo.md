# Domínio do SetupFlow

Uma organização industrial precisa ordenar a produção considerando as ordens em aberto, as máquinas capazes de fabricar cada produto e o tempo de preparação entre famílias.

## Fluxo disponível

Usuários entram com e-mail e senha e podem ter mais de um perfil. O Administrador gerencia contas e perfis. O Planejador mantém os cadastros, monta e compara sequências e aprova a escolhida. O Operador consulta as sequências aprovadas. A API verifica as permissões em cada operação protegida.

O cadastro inclui máquinas, famílias e produtos. Cada produto pode pertencer a uma família e pode ter vínculos com várias máquinas. Somente máquinas ativas e compatíveis entram na geração de sugestões. Os tempos de setup são cadastrados para pares direcionais de famílias. Uma transição ausente aparece como traço na matriz.

Cada ordem referencia um produto. Prazo, prioridade e duração estimada podem ser definidos para o planejamento. O sistema protege o cadastro contra duplicidade no reenvio e trata falhas durante as gravações de cadastro, duração, prazo e prioridade.

O Planejador seleciona e ordena as ordens em um plano manual. O sistema pode gerar uma sugestão para o mesmo conjunto de ordens, considerando as máquinas elegíveis, o setup, a prioridade, o prazo e a duração estimada. A comparação apresenta as duas sequências e os totais de setup. A aprovação guarda a ordem dos itens e a máquina atribuída quando houver. O Operador consulta essa sequência na tela Execução da produção. [Entregas integradas e aceitas](../status-projeto.md)

## Evolução prevista

O escopo de evolução inclui importação de ordens por arquivo, registro de início, conclusão e interrupções da produção, replanejamento com histórico e indicadores de setup e atraso. O modelo conceitual descreve as relações propostas para essa evolução. [Modelo de dados](modelo-de-dados.md)
