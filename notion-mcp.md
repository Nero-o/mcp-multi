/**
 * MODEL CONTEXT PROTOCOL (MCP)
 * Sistema de Operações e Parcelas
 * 
 * Este MCP define as regras, comportamentos e relacionamentos 
 * entre Operações e Parcelas no sistema.
 */

/**
 * ENTIDADES PRINCIPAIS
 */

/**
 * @typedef {Object} Operacao
 * @property {string} status_operacional - "Em Andamento" | "Concluída" | "Cancelada" (Controle Admin)
 * @property {string} status_sistemico - "Disponível" | "Indisponível" | "Expirada" (Controle Sistema/CRON)
 * @property {boolean} habilitado - true | false (Controle Admin ou Parceiro)
 * @property {string} status_financeiro - "A Receber" | "Pago" | "Em Atraso" | etc. (Controle Sistema)
 */

/**
 * @typedef {Object} Parcela
 * @property {string} status_operacional - "Em Andamento" | "Concluída" | "Cancelada" (Controle Admin)
 * @property {string} status_sistemico - "Disponível" | "Indisponível" (Controle Sistema/CRON)
 * @property {boolean} habilitado - true | false (Controle Admin)
 * @property {string} status_financeiro - "A Receber" | "Pago" | "Em Atraso" | etc. (Controle Sistema)
 */

/**
 * CICLO DE VIDA
 * 
 * Fluxo da Operação vs Parcela:
 * 1. [Operação Criada] -> Cria Parcela (Indisponível)
 * 2. [Em Andamento]
 * 3. [Concluída] (via Admin)
 * 4. [Parcela -> Disponível] (Regra Sistêmica ou CRON)
 * 5. [Financeiro -> A Receber / Pago / Em Atraso...]
 */

/**
 * REGRAS DE TRANSIÇÃO
 * 
 * @event OperacaoCriada
 * @action Parcela nasce com status_sistemico="Indisponível"
 * 
 * @event OperacaoConcluida
 * @action CRON/sistema avalia se a Parcela pode ir para status_sistemico="Disponível"
 * 
 * @event ParcelaDisponivel
 * @action Se vencimento ocorrer, ativa lógica financeira
 * 
 * @event OperacaoCancelada
 * @action Parcela permanece Indisponível ou vai para Cancelada via sistema
 * 
 * @event ParcelaConcluida
 * @action Trava novas ações nela (liquidação, encerramento)
 */

/**
 * REGRAS DE VALIDAÇÃO FUNDAMENTAIS
 * 
 * 1. Uma Parcela NUNCA pode estar Disponível se a Operação não estiver Concluída
 * 2. Uma Parcela nunca pode estar Concluída se a Operação não foi Concluída antes
 * 3. Parcela.status_sistemico = "Disponível" só pode acontecer se:
 *    Operacao.status_operacional = "Concluída" E 
 *    Operacao.status_sistemico = "Disponível"
 * 4. Se Operacao.status_sistemico = "Expirada" ou "Indisponível", todas as parcelas 
 *    associadas devem ser ou permanecer Indisponíveis ou Canceladas
 * 5. Se Parcela.status_operacional = "Concluída" mas 
 *    Operacao.status_operacional != "Concluída", lançar exceção ou bloquear update
 * 6. Parcelas não contam no dashboard se estiverem Indisponíveis, Canceladas 
 *    ou associadas a Operações não Concluídas
 */

/**
 * MATRIZ DE ESTADOS VÁLIDOS
 * Representa cenários possíveis e seus resultados esperados
 * 
 * ✅ Estados válidos que geram prosperidade:
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Disponível", status_operacional: "Em Andamento"}
 *   => Prosperou
 * 
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Disponível", status_operacional: "Concluída"}
 *   => Prosperou
 * 
 * ❌ Estados que não prosperam:
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Cancelada"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Cancelada"}
 *   => Não prosperou
 * 
 * - Operação: {status_sistemico: "Expirada", status_operacional: "Em Andamento"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   => Não prosperou
 * 
 * - Operação: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   => Não prosperou
 * 
 * ⚠️ Estados com inconsistências ou em transição:
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Em Andamento"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   => Parcela antecipada?
 * 
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   => Aguardando CRON
 * 
 * - Operação: {status_sistemico: "Expirada", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Disponível", status_operacional: "Em Andamento"}
 *   => Erro lógico
 * 
 * - Operação: {status_sistemico: "Indisponível", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Indisponível", status_operacional: "Em Andamento"}
 *   => Erro lógico
 * 
 * - Operação: {status_sistemico: "Disponível", status_operacional: "Concluída"}
 *   Parcela: {status_sistemico: "Cancelada", status_operacional: "Cancelada"}
 *   => Parcela falhou
 */

/**
 * REGRAS DE CRON
 * 
 * 1. Expiração Automática:
 *    - Operações ou Parcelas que não forem concluídas até a data de validade 
 *      devem ser automaticamente expiradas
 *    - Status muda para "Expirada", desconsideradas do dashboard e futuras ações
 * 
 * 2. Promoção de Status:
 *    - Verificar periodicamente Operações Concluídas com Parcelas Indisponíveis
 *    - Se Operação estiver Concluída e Disponível, promover Parcela para Disponível
 */

/**
 * REGRAS DE UI/DASHBOARD
 * 
 * 1. Somente Parcelas com status_sistemico="Disponível" e habilitado=true 
 *    devem ser consideradas em totais, gráficos e listas operacionais
 * 
 * 2. Demais itens são histórico ou itens inválidos
 * 
 * 3. Agrupamentos de Status:
 *    - Financeiro: Pago, A Receber, Vencido, A Pagar
 *    - Operacional: Habilitado, Desabilitado, Em Andamento, Pendente, Cancelado, Concluído
 *    - Sistema: Disponível, Indisponível, Expirado
 *    - Bancário: Integração Bancos
 *    - ERP: Integração Siengs
 */

/**
 * NOTAS IMPORTANTES
 * 
 * 1. Distinção Operacional vs. Sistêmico:
 *    - Operacional é controlado por humanos (Admin)
 *    - Sistêmico é controlado por processos automatizados (Sistema/CRON)
 * 
 * 2. Prosperidade verdadeira só ocorre quando:
 *    - Operação: Disponível + Concluída
 *    - Parcela: Disponível + Em Andamento (ou Concluída)
 * 
 * 3. Cancelamentos:
 *    - Quando uma Operação é Cancelada, é necessário Cancelar também a Parcela Vinculada
 *    - Cancelamentos devem impedir movimentação financeira e remover dos dashboards
 */

/**
 * IMPLEMENTAÇÃO RECOMENDADA
 * 
 * Funções de Validação de Estado:
 */

// Exemplo de uma função para validar a transição de status da Parcela para Disponível
function podePromoverParcelaParaDisponivel(operacao, parcela) {
  // Regra 3 do MCP: Parcela só pode ir para Disponível se Operação for Concluída e Disponível
  return (
    operacao.status_operacional === "Concluída" &&
    operacao.status_sistemico === "Disponível" &&
    parcela.status_sistemico === "Indisponível"
  );
}

// Exemplo de função para validar o status consolidado de uma operação
function isProsperidadeValida(operacao, parcela) {
  // Prosperidade verdadeira: Operação (Disponível+Concluída) e Parcela (Disponível + status_operacional válido)
  const operacaoProspera = 
    operacao.status_sistemico === "Disponível" && 
    operacao.status_operacional === "Concluída";
    
  const parcelaProspera = 
    parcela.status_sistemico === "Disponível" && 
    (parcela.status_operacional === "Em Andamento" || parcela.status_operacional === "Concluída");
    
  return operacaoProspera && parcelaProspera;
}

// Exemplo de função para detectar estados inconsistentes
function detectarEstadoInconsistente(operacao, parcela) {
  // Detecta estados que não deveriam existir conforme a matriz de estados
  
  // Erro lógico: Operação expirada mas parcela disponível
  if (operacao.status_sistemico === "Expirada" && 
      parcela.status_sistemico === "Disponível") {
    return "Erro lógico: Operação expirada com parcela disponível";
  }
  
  // Erro lógico: Parcela concluída mas operação não concluída
  if (parcela.status_operacional === "Concluída" && 
      operacao.status_operacional !== "Concluída") {
    return "Erro lógico: Parcela concluída com operação não concluída";
  }
  
  // Não há inconsistência detectada
  return null;
}

// Exemplo de implementação do CRON para promoção de parcelas
async function cronPromoverParcelasElegiveis() {
  // Buscar todas as operações concluídas e disponíveis
  const operacoesElegiveis = await buscarOperacoes({
    status_operacional: "Concluída",
    status_sistemico: "Disponível"
  });
  
  for (const operacao of operacoesElegiveis) {
    // Buscar parcelas indisponíveis desta operação
    const parcelasIndisponiveis = await buscarParcelas({
      operacao_id: operacao.id,
      status_sistemico: "Indisponível"
    });
    
    // Promover parcelas para disponível se elegíveis
    for (const parcela of parcelasIndisponiveis) {
      if (podePromoverParcelaParaDisponivel(operacao, parcela)) {
        await atualizarStatusSistemicoParcela(parcela.id, "Disponível");
        console.log(`Parcela ${parcela.id} promovida para Disponível`);
      }
    }
  }
}

// Exemplo de implementação para dashboard (filtrar apenas parcelas válidas)
async function buscarParcelasParaDashboard() {
  // Somente parcelas disponíveis e habilitadas são mostradas
  return await buscarParcelas({
    status_sistemico: "Disponível",
    habilitado: true
  });
}