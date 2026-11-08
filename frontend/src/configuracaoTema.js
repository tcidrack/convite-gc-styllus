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

  // << EDITE AQUI >> o endereco em destaque. O link do mapa e o da agenda
  // ficam em `calendario`, mais abaixo.
  local: {
    titulo: 'Onde vai ser',
    rua: 'Rua Londrina, 965, Casa A',
    bairro: 'Granja Portugal',
    botaoMapa: 'Ver no mapa',
    botaoAgenda: 'Salvar na agenda',
  },

  // << EDITE AQUI >> embaixo do endereco, uma novidade por vez
  novidades: {
    titulo: 'Olha o que mais vai ter',
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
    // `parte` e o nome do arquivo (boneca_gc-2.mp4 -> '2', boneca_gc-3b.mp4 ->
    // '3b'); inicio e fim em segundos DENTRO dessa parte, no arquivo original.
    // Onde cada parte cai no video e os cortes saem de src/partesVideo.js, entao
    // trocar ou cortar uma parte nao mexe nas legendas das outras. Se uma frase
    // aparecer adiantada ou atrasada, e so mexer nestes numeros.
    legendas: [
      { parte: '1', inicio: 0.15, fim: 1.05, texto: 'Oi, gente!' },
      { parte: '1', inicio: 1.05, fim: 5.0, texto: 'Vamos inaugurar nossa loja física no dia 21, na Granja Portugal,' },
      { parte: '1', inicio: 5.0, fim: 8.3, texto: 'Rua Londrina, 965, casa A,' },
      { parte: '1', inicio: 8.3, fim: 10.0, texto: 'a partir das 9h da manhã!' },

      { parte: '2', inicio: 0.9, fim: 3.9, texto: 'No dia da inauguração vai ter coffee break,' },
      { parte: '2', inicio: 3.9, fim: 5.85, texto: 'estoura balão com brindes,' },
      { parte: '2', inicio: 5.85, fim: 9.8, texto: 'looks maravilhosos e muitos mimos!' },

      { parte: '3', inicio: 1.0, fim: 4.4, texto: 'E tem mais: 10% de desconto em qualquer modelinho,' },
      { parte: '3', inicio: 4.4, fim: 6.85, texto: 'do dia 21 ao dia 28 de novembro!' },
      { parte: '3', inicio: 6.85, fim: 10.15, texto: 'E muita novidade em looks plus size e slim!' },

      { parte: '4', inicio: 0.7, fim: 2.45, texto: 'E não é só roupa, não!' },
      { parte: '4', inicio: 2.45, fim: 5.65, texto: 'Tem brincos, colares, anéis, braceletes,' },
      { parte: '4', inicio: 5.65, fim: 9.9, texto: 'sandálias, bolsas, maquiagens e muito mais!' },

      { parte: '5', inicio: 0.9, fim: 3.2, texto: 'Esperamos todos vocês lá!' },
      { parte: '5', inicio: 3.2, fim: 5.6, texto: 'Venham comemorar com a gente!' },
      // Parte nova: rode arte/gerar-video.py e acrescente as frases com os tempos
      // de "fala" que ele imprime no fim.
    ],
    videoDescricao: 'Bonequinha da GC STYLLUS convidando para a inauguração',
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

  // O convite e aberto: nao pede mais confirmacao. A /admin continua mostrando
  // quem confirmou antes, por esta funcao, que pede a senha (database.sql, bloco 6)
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
