// ===== CONSTANTES OCEAN — TESTEPERSONALIDADE v1.0.0 =====

const INSTRUMENT_VERSION = '1.0.0';
const API_BASE = '';  // vazio = offline; configurar URL da API em produção
const HUB_URL = 'https://centralsp3.github.io/central/';
const URL_DISC = 'https://centralsp3.github.io/TESTEDISC/';
const URL_PERSONALIDADE = 'https://centralsp3.github.io/PERSONALIDADE/';

const FACTORES_INTERNOS = ['O', 'C', 'E', 'A', 'N'];
const FACTORES = FACTORES_INTERNOS;
const FATORES_DISPLAY = ['O', 'C', 'E', 'A', 'SE'];

const DISPLAY_LABELS = {
  O: 'Abertura à Experiência',
  C: 'Conscienciosidade',
  E: 'Extroversão',
  A: 'Amabilidade',
  SE: 'Estabilidade Emocional',
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
  meta: { version: '1.0.0', sample_size: 500, source: 'bootstrap_literature_2026' },
  domains: {
    O: { mean: 3.35, sd: 0.72 },
    C: { mean: 3.52, sd: 0.68 },
    E: { mean: 3.18, sd: 0.75 },
    A: { mean: 3.61, sd: 0.65 },
    N: { mean: 2.89, sd: 0.78 },
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
  enableAPI: !!API_BASE,
  enableFacets: false,
  enablePDFExport: true,
};