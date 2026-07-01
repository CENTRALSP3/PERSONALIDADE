// ===== CONSTANTES OCEAN — TESTEPERSONALIDADE v1.0.0 =====

const INSTRUMENT_VERSION = '1.0.0';
const API_BASE = 'https://personalidade-2j3zlkkcs-price3.vercel.app';  // Latest Vercel API (personalidade-api)
const HUB_URL = 'https://centralsp3.github.io/central/';
const URL_DISC = 'https://centralsp3.github.io/TESTEDISC/';
const URL_PERSONALIDADE = 'https://centralsp3.github.io/PERSONALIDADE/';

const FACTORES_INTERNOS = ['O', 'C', 'E', 'A', 'N'];
const FACTORES = FACTORES_INTERNOS;
const FATORES_DISPLAY = ['O', 'C', 'E', 'A', 'SE'];

// Lógica para habilitar backend: desabilita só em hosts puramente estáticos sem API_BASE configurada
const IS_PURE_STATIC_HOST = window.location.hostname.includes('github.io') || window.location.hostname.includes('pages.dev');
const EFFECTIVE_ENABLE_API = (typeof API_BASE !== 'undefined' && API_BASE) || !IS_PURE_STATIC_HOST && (typeof FLAGS !== 'undefined' ? FLAGS.enableAPI : true);

const DISPLAY_LABELS = {
  O: 'Abertura à Experiência',
  C: 'Conscienciosidade',
  E: 'Extroversão',
  A: 'Amabilidade',
  SE: 'Estabilidade Emocional',
};

// Descrições aprofundadas baseadas em pesquisa (IPIP-NEO, BFI brasileiro, literatura Costa/McCrae, Goldberg)
const FACTOR_INFO = {
  O: {
    nome: 'Abertura à Experiência',
    descricao: 'Reflete curiosidade intelectual, imaginação, apreciação estética, abertura a novas ideias e experiências. Pessoas altas valorizam variedade, criatividade e pensamento abstrato; baixas preferem o familiar, prático e convencional.',
    altoComportamentos: 'Busca novidades, explora arte e ideias não convencionais, é inovador no trabalho, tolera ambiguidade, gosta de viajar e aprender coisas novas. No dia a dia: lê muito, experimenta hobbies variados, questiona o status quo.',
    baixoComportamentos: 'Prefere rotinas estáveis, soluções comprovadas, ambientes previsíveis. Pode resistir a mudanças radicais ou ideias muito abstratas. No trabalho: excelente em papéis operacionais estruturados.',
    trabalho: 'Alto: ideal para inovação, marketing criativo, pesquisa, design, estratégia. Baixo: forte em execução precisa, compliance, operações.',
    relacoes: 'Alto: traz perspectivas frescas às conversas. Baixo: valoriza tradição e estabilidade compartilhada.',
    sobPressao: 'Alto: gera soluções criativas mas pode dispersar. Baixo: mantém foco prático e direto.'
  },
  C: {
    nome: 'Conscienciosidade',
    descricao: 'Mede organização, responsabilidade, autodisciplina, persistência e orientação para metas. Alta: confiável, planejadora, detalhista. Baixa: mais flexível, espontânea, às vezes desorganizada.',
    altoComportamentos: 'Planeja com antecedência, cumpre prazos, mantém ordem, é persistente e cuidadoso com detalhes. No dia a dia: agendas, listas, ambientes arrumados, decisões ponderadas.',
    baixoComportamentos: 'Vive mais no momento, procrastina ocasionalmente, aceita desordem, é mais espontâneo. Pode ser visto como "boa vibe" mas menos confiável em entregas.',
    trabalho: 'Alto: destaque em gestão de projetos, liderança executiva, finanças, qualidade. Risco de perfeccionismo. Baixo: bom em ambientes ágeis, criativos, que exigem flexibilidade.',
    relacoes: 'Alto: parceiro confiável que cumpre promessas. Baixo: traz leveza mas pode frustrar em compromissos.',
    sobPressao: 'Alto: mantém estrutura e avança passo a passo. Baixo: pode improvisar bem mas descuidar de detalhes.'
  },
  E: {
    nome: 'Extroversão',
    descricao: 'Reflete sociabilidade, energia, assertividade, busca por estímulos e expressividade emocional positiva. Alta: extrovertida, energética em grupos. Baixa: reservada (introvertida), prefere interações profundas ou solitude para recarregar.',
    altoComportamentos: 'Adora socializar, faz amigos facilmente, fala com entusiasmo, busca atividades estimulantes, brilha em grupos. No dia a dia: eventos, conversas longas, liderança natural.',
    baixoComportamentos: 'Prefere tempo sozinho ou com poucos, pensa antes de falar, evita holofotes, recarrega em silêncio. Excelente ouvinte e pensador profundo.',
    trabalho: 'Alto: vendas, RH, liderança de equipes, apresentação, networking. Baixo: pesquisa profunda, programação, escrita, análise independente.',
    relacoes: 'Alto: centro de atenções, energiza grupos. Baixo: conexões autênticas e profundas.',
    sobPressao: 'Alto: usa rede social para apoio. Baixo: processa internamente, precisa de espaço.'
  },
  A: {
    nome: 'Amabilidade',
    descricao: 'Mede compaixão, cooperação, confiança, gentileza e altruísmo. Alta: empática, harmoniosa, generosa. Baixa: mais direta, cética, competitiva, assertiva em conflitos.',
    altoComportamentos: 'Confia nas pessoas, ajuda sem esperar retorno, evita conflitos desnecessários, é diplomático e atencioso. No dia a dia: mediação, voluntariado, bom ouvinte.',
    baixoComportamentos: 'É franco, prioriza própria visão, questiona intenções alheias, compete quando necessário. Pode ser visto como "direto" ou "duro".',
    trabalho: 'Alto: excelente em equipes, customer success, educação, saúde, mediação. Baixo: bom em negociação dura, vendas competitivas, tomada de decisão impopular.',
    relacoes: 'Alto: constrói confiança e harmonia. Baixo: traz honestidade crua (pode precisar aprender diplomacia).',
    sobPressao: 'Alto: busca consenso e apoia outros. Baixo: defende posição com firmeza.'
  },
  N: {
    nome: 'Neuroticismo (inverso: Estabilidade Emocional)',
    descricao: 'Tendência a vivenciar emoções negativas (ansiedade, raiva, tristeza, vulnerabilidade). Alto N = baixa estabilidade: mais reativo. Baixo N / Alta SE: calmo, resiliente, emocionalmente estável.',
    altoComportamentos: ' (para N alto / SE baixo) Preocupa-se facilmente, sente estresse com mais intensidade, humor oscila, demora a se recuperar de contratempos. No dia a dia: ruminação, evitação de riscos.',
    baixoComportamentos: ' (SE alto) Mantém calma sob pressão, recupera rápido, raro de se abalar, pensa positivo mesmo em adversidade. Excelente em crises.',
    trabalho: 'SE alto: liderança em crise, ambientes voláteis, atendimento de alto estresse. N alto pode trazer sensibilidade útil em profissões empáticas mas exige estratégias de regulação.',
    relacoes: 'SE alto: porto seguro emocional. N alto: pode precisar de suporte extra; alta empatia em alguns casos.',
    sobPressao: 'SE alto: analisa friamente e age. N alto: pode entrar em loop de preocupação mas também ser mais vigilante a riscos.'
  }
};

const CORES = {
  O: '#8E44AD',
  C: '#2980B9',
  E: '#F39C12',
  A: '#27AE60',
  SE: '#E74C3C',
  N: '#E74C3C',
};

const BANDA_T_LIMIARES = {
  muito_baixo: { max: 37.9 },
  baixo: { min: 38, max: 43.9 },
  medio: { min: 44, max: 56.9 },
  alto: { min: 57, max: 62.9 },
  muito_alto: { min: 63 },
};

const DISCREPANCY_THRESHOLD = 3;

const NORMS = {
  meta: { version: '2.0.0', sample_size: 3565, source: 'BFI_Brasil_2023_Roiz_CostaMastrascusa (adaptado para referência IPIP-like)' },
  domains: {
    O: { mean: 3.78, sd: 0.59 },
    C: { mean: 3.74, sd: 0.64 },
    E: { mean: 3.30, sd: 0.74 },
    A: { mean: 3.68, sd: 0.54 },
    N: { mean: 2.95, sd: 0.81 },
  },
};

// Lookup table normalCDF: z ∈ [-3.0, +3.0], passo 0.06 (101 entradas)
const NORMAL_CDF_TABLE = [
  0.0013, 0.0015, 0.0017, 0.0020, 0.0023, 0.0027, 0.0032, 0.0037, 0.0043, 0.0050,
  0.0059, 0.0069, 0.0080, 0.0093, 0.0107, 0.0124, 0.0143, 0.0164, 0.0188, 0.0216,
  0.0247, 0.0282, 0.0322, 0.0366, 0.0416, 0.0472, 0.0534, 0.0603, 0.0680, 0.0764,
  0.0856, 0.0957, 0.1066, 0.1184, 0.1312, 0.1449, 0.1596, 0.1753, 0.1919, 0.2094,
  0.2278, 0.2469, 0.2667, 0.2871, 0.3078, 0.3289, 0.3500, 0.3712, 0.3922, 0.4130,
  0.4334, 0.4532, 0.4722, 0.4904, 0.5076, 0.5240, 0.5394, 0.5538, 0.5672, 0.5796,
  0.5910, 0.6014, 0.6109, 0.6195, 0.6273, 0.6343, 0.6406, 0.6463, 0.6514, 0.6560,
  0.6602, 0.6640, 0.6675, 0.6707, 0.6736, 0.6764, 0.6790, 0.6814, 0.6837, 0.6859,
  0.6880, 0.6900, 0.6920, 0.6939, 0.6957, 0.6975, 0.6993, 0.7010, 0.7027, 0.7044,
  0.7060, 0.7076, 0.7092, 0.7108, 0.7123, 0.7138, 0.7153, 0.7168, 0.7182, 0.7197,
  0.7211,
];

function normalCDF(z) {
  const clamped = Math.max(-3, Math.min(3, z));
  const idx = Math.round((clamped + 3) / 0.06);
  return NORMAL_CDF_TABLE[Math.min(idx, NORMAL_CDF_TABLE.length - 1)];
}

function toDisplayFactor(f) {
  return f === 'N' ? 'SE' : f;
}

function classificarBandaT(tScore) {
  if (tScore < 38) return 'Muito Baixo';
  if (tScore < 44) return 'Baixo';
  if (tScore < 57) return 'Médio';
  if (tScore < 63) return 'Alto';
  return 'Muito Alto';
}

function classificarBandaDisplay(f, tScoreInterno) {
  const tDisplay = f === 'N' ? (100 - tScoreInterno) : tScoreInterno;
  return classificarBandaT(tDisplay);
}

function invertForDisplay(f, scores) {
  if (f !== 'N') return { ...scores, displayFactor: f };
  return {
    mean: 6 - scores.mean,
    tScore: 100 - scores.tScore,
    percentil: 100 - scores.percentil,
    ui: -scores.ui,
    displayFactor: 'SE',
    label: 'Estabilidade Emocional',
  };
}

const FLAGS = {
  enableAPI: true,  // backend habilitado para coleta, normas dinâmicas e PDF servidor (pode ser sobrescrito em hosts estáticos)
  enableFacets: true,
  enablePDFExport: true,
};

// 30 Facets do IPIP-NEO (6 por domínio)
const FACETS = {
  O: [
    { code: 'O1', name: 'Imaginação', desc: 'Tendência a ter uma imaginação vívida e a fantasiar.' },
    { code: 'O2', name: 'Interesses Artísticos', desc: 'Apreciação pela arte, beleza e experiências estéticas.' },
    { code: 'O3', name: 'Emocionalidade', desc: 'Consciência e expressão profunda das próprias emoções.' },
    { code: 'O4', name: 'Aventureirismo', desc: 'Abertura a novas experiências, viagens e mudanças.' },
    { code: 'O5', name: 'Intelecto', desc: 'Curiosidade intelectual, gosto por ideias abstratas e debates.' },
    { code: 'O6', name: 'Liberalismo', desc: 'Abertura a valores não tradicionais e diversidade.' },
  ],
  C: [
    { code: 'C1', name: 'Autoeficácia', desc: 'Confiança na própria capacidade de realizar tarefas.' },
    { code: 'C2', name: 'Organização', desc: 'Preferência por ordem, limpeza e estrutura.' },
    { code: 'C3', name: 'Diligência', desc: 'Senso de dever e cumprimento de obrigações.' },
    { code: 'C4', name: 'Busca por Realização', desc: 'Motivação para alcançar metas e excelência.' },
    { code: 'C5', name: 'Autodisciplina', desc: 'Capacidade de persistir em tarefas apesar de distrações.' },
    { code: 'C6', name: 'Deliberação', desc: 'Tendência a pensar antes de agir, cautela.' },
  ],
  E: [
    { code: 'E1', name: 'Amabilidade', desc: 'Calor e facilidade em fazer amigos.' },
    { code: 'E2', name: 'Gregariedade', desc: 'Gosto por companhia de outras pessoas e eventos sociais.' },
    { code: 'E3', name: 'Assertividade', desc: 'Facilidade em tomar a liderança e expressar opiniões.' },
    { code: 'E4', name: 'Nível de Atividade', desc: 'Energia e ritmo acelerado nas atividades.' },
    { code: 'E5', name: 'Busca por Excitação', desc: 'Procura por estímulos fortes e aventuras.' },
    { code: 'E6', name: 'Alegria', desc: 'Experiência frequente de emoções positivas.' },
  ],
  A: [
    { code: 'A1', name: 'Confiança', desc: 'Crença na boa intenção das pessoas.' },
    { code: 'A2', name: 'Moralidade', desc: 'Honestidade e integridade nas interações.' },
    { code: 'A3', name: 'Altruísmo', desc: 'Preocupação genuína com o bem-estar dos outros.' },
    { code: 'A4', name: 'Cooperação', desc: 'Disposição para ceder e evitar conflitos.' },
    { code: 'A5', name: 'Modéstia', desc: 'Humildade e baixa necessidade de atenção.' },
    { code: 'A6', name: 'Compaixão', desc: 'Empatia e sensibilidade aos sentimentos alheios.' },
  ],
  N: [
    { code: 'N1', name: 'Ansiedade', desc: 'Tendência a se preocupar e sentir tensão.' },
    { code: 'N2', name: 'Raiva', desc: 'Facilidade em se irritar ou sentir hostilidade.' },
    { code: 'N3', name: 'Depressão', desc: 'Experiência de tristeza e desânimo.' },
    { code: 'N4', name: 'Autoconsciência', desc: 'Vergonha e desconforto social fácil.' },
    { code: 'N5', name: 'Impulsividade', desc: 'Dificuldade em controlar desejos e impulsos.' },
    { code: 'N6', name: 'Vulnerabilidade', desc: 'Dificuldade em lidar com estresse e pressão.' },
  ],
};

// Mapeamento de facet code para domínio (para scoring)
const FACET_TO_DOMAIN = {};
Object.keys(FACETS).forEach(domain => {
  FACETS[domain].forEach(f => {
    FACET_TO_DOMAIN[f.code] = domain;
  });
});