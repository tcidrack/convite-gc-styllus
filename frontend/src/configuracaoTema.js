// =====================================================================
//  EDITE AQUI  -  todos os dados do convite ficam neste arquivo.
//  Nao e preciso mexer em mais nenhum outro lugar.
// =====================================================================

export const tema = {
  id: 'inauguracaoGcStyllus',
  tipo: 'inauguracao',
  nome: 'GC STYLLUS',
  iniciais: 'GC',
  tituloEvento: 'Inauguração',

  // << EDITE AQUI >> data e hora do evento
  dataEvento: {
    dia: '21',
    mes: 'Novembro',
    ano: '2026',
    hora: '09',
    minuto: '00',
  },

  // << EDITE AQUI >> os tres destaques da primeira tela (o do meio fica em rosa)
  destaques: [
    { icone: 'cafe', titulo: 'Coffee break', detalhe: 'Delicioso café da manhã' },
    { valor: '10%', sufixo: 'OFF', detalhe: 'Em qualquer modelinho', periodo: 'De 21 a 28/11' },
    { icone: 'balao', titulo: 'Estoura balão', detalhe: 'Com brindes de looks maravilhosos' },
  ],

  // Convite para confirmar, embaixo do botao
  chamada: 'Confirme e veja tudo o que preparamos',

  // << EDITE AQUI >> o que so aparece depois de confirmar, uma novidade por vez
  novidades: {
    intervalo: 4500, // ms que cada novidade fica na tela
    itens: [
      {
        icone: 'presente',
        titulo: 'Mimos',
        texto: 'Tem mimos no dia da inauguração!',
      },
      {
        icone: 'cabide',
        titulo: 'Muita novidade em looks',
        texto: 'No plus size e no slim.',
      },
      {
        icone: 'bolsa',
        titulo: 'Não é só roupa!',
        lista: ['Brincos', 'Colares', 'Anéis', 'Braceletes', 'Sandálias', 'Bolsas', 'Maquiagens'],
        fim: 'e muito mais...',
      },
      {
        icone: 'etiqueta',
        titulo: '10% de desconto',
        texto: 'Em qualquer modelinho, do dia 21/11 ao dia 28/11. Acessórios não inclusos no desconto.',
      },
    ],
  },

  // Textos do envelope (pagina inicial)
  envelope: {
    convite: 'Você recebeu um convite',
    clique: 'Toque no envelope para abrir',
    abrindo: 'Abrindo...',
  },

  recursos: {
    // gerados por arte/gerar-video.py
    video: '/assets/bonequinha.mp4',
    videoPoster: '/assets/bonequinha-poster.webp',
    videoAnimado: '/assets/bonequinha-animado.webp',
    audioReserva: '/assets/bonequinha-audio.m4a',
    // Em segundos do video inteiro. Cada parte (boneca_gc-N.mp4) dura 10s, entao
    // a parte 2 comeca em 10, a 3 em 20... Se uma frase aparecer adiantada ou
    // atrasada, e so mexer nestes numeros.
    legendas: [
      // parte 1
      { inicio: 0.15, fim: 1.05, texto: 'Oi, gente!' },
      { inicio: 1.05, fim: 5.0, texto: 'Vamos inaugurar nossa loja física no dia 21, na Granja Portugal,' },
      { inicio: 5.0, fim: 8.3, texto: 'Rua Londrina, 965, casa A,' },
      { inicio: 8.3, fim: 10.0, texto: 'a partir das 9h da manhã!' },
      // parte 2
      { inicio: 10.9, fim: 13.9, texto: 'No dia da inauguração vai ter coffee break,' },
      { inicio: 13.9, fim: 15.85, texto: 'estoura balão com brindes,' },
      { inicio: 15.85, fim: 19.8, texto: 'looks maravilhosos e muitos mimos!' },
      // parte 3
      { inicio: 21.0, fim: 23.85, texto: 'E tem mais: 10% de desconto em qualquer modelinho,' },
      { inicio: 23.85, fim: 26.8, texto: 'do dia 21 ao dia 28 de novembro!' },
      { inicio: 26.85, fim: 29.9, texto: 'E muita novidade em looks plus size e slim!' },
      // parte 4
      { inicio: 30.7, fim: 32.45, texto: 'E não é só roupa, não!' },
      { inicio: 32.45, fim: 35.65, texto: 'Tem brincos, colares, anéis, braceletes,' },
      { inicio: 35.65, fim: 39.9, texto: 'sandálias, bolsas, maquiagens e muito mais!' },
      // parte 5
      { inicio: 40.9, fim: 43.2, texto: 'Esperamos todos vocês lá!' },
      { inicio: 43.2, fim: 45.6, texto: 'Venham comemorar com a gente!' },
      // Parte nova (boneca_gc-6.mp4...): rode arte/gerar-video.py e acrescente as
      // frases aqui com os tempos de "fala" que ele imprime no fim.
    ],
    videoDescricao: 'Bonequinha da GC STYLLUS convidando para a inauguração',
  },

  // Janela de agradecimento (abre depois de confirmar)
  agradecimento: {
    titulo: 'Presença confirmada!',
    subtitulo: 'Te esperamos! Olha o que mais vai ter:',
    botaoVer: 'Ver tudo o que preparamos',
    botaoAgenda: 'Adicionar à agenda',
    botaoMapa: 'Ver no mapa',
  },

  // Assinatura discreta no rodape do convite
  assinatura: {
    texto: 'Feito por',
    nome: 'Thalison Cidrack',
    instagram: '@cidrack.dev',
    url: 'https://instagram.com/cidrack.dev',
  },

  calendario: {
    // << EDITE AQUI >> endereco, link do maps e horarios
    endereco: 'Rua Londrina, 965, Casa A - Granja Portugal',
    // A cidade so entra no link do mapa: o endereco enviado nao trazia a cidade.
    mapsUrl:
      'https://www.google.com/maps/search/?api=1&query=Rua%20Londrina%2C%20965%2C%20Granja%20Portugal%2C%20Fortaleza%20-%20CE',
    eventoNome: 'Inauguração da GC STYLLUS',
    dataInicio: '09:00 21/11/2026', // formato HH:MM DD/MM/AAAA
    dataFim: '', // opcional; vazio usa o mesmo horario de inicio
  },

  // Funcoes do Supabase (ver database.sql)
  funcaoConfirmar: 'confirmar_presenca_gc_styllus',
  // A /admin le a lista por esta funcao, que pede a senha (database.sql, bloco 6)
  funcaoListar: 'listar_confirmados_gc_styllus',
}

function converterDataGoogle(dataBR) {
  if (!dataBR) return '';
  const [horaMinuto, data] = dataBR.split(' ');
  const [hora, minuto] = horaMinuto.split(':');
  const [dia, mes, ano] = data.split('/');
  return `${ano}${mes}${dia}T${hora}${minuto}00`;
}

export function criarUrlCalendario(tema) {
  if (!tema.calendario.dataInicio) return '#';
  const nomeCodificado = encodeURIComponent(tema.calendario.eventoNome || tema.nome);
  const enderecoCodificado = encodeURIComponent(tema.calendario.endereco);
  const dataInicio = converterDataGoogle(tema.calendario.dataInicio);
  const dataFim = tema.calendario.dataFim ? converterDataGoogle(tema.calendario.dataFim) : dataInicio;
  return `https://www.google.com/calendar/render?action=TEMPLATE&text=${nomeCodificado}&dates=${dataInicio}/${dataFim}&location=${enderecoCodificado}`;
}
