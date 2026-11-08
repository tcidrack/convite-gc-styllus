// Abre uma pagina num navegador de verdade, captura erro de console,
// elemento vazando na horizontal, e print.
//
//   node ferramentas/olhar-pagina.cjs <url> [largura] [saida.png]
//
// Existe porque tres bugs seguidos chegaram ao usuario sem eu ver: print
// nao mostra erro de JavaScript, e analise estatica nao mostra o que o
// navegador faz. Isto mostra os dois.
//
// CommonJS de proposito: o pacote playwright-core instalado aqui nao traz
// o index.mjs, entao `import` falha e `require` funciona.
const { chromium } = require('playwright-core')

const url = process.argv[2]
const largura = Number(process.argv[3] || 390)
const saida = process.argv[4] || null

;(async () => {
  const navegador = await chromium.launch()
  const pagina = await navegador.newPage({
    viewport: { width: largura, height: 844 },
    deviceScaleFactor: 2,
  })

  const erros = []
  pagina.on('console', (m) => {
    if (m.type() === 'error' || m.type() === 'warning') erros.push([m.type(), m.text()])
  })
  pagina.on('pageerror', (e) => erros.push(['pageerror', e.stack || e.message]))
  pagina.on('requestfailed', (r) =>
    erros.push(['requisicao', `${r.url()} -> ${(r.failure() || {}).errorText}`]))

  await pagina.goto(url, { waitUntil: 'networkidle', timeout: 45000 })
  await pagina.waitForTimeout(1500)

  const raiz = await pagina.evaluate(() => {
    const r = document.getElementById('root')
    return { filhos: r ? r.children.length : -1, texto: (r && r.innerText || '').slice(0, 150) }
  })

  console.log(`\nURL: ${url}  (${largura}px)`)
  console.log(`#root: ${raiz.filhos} filho(s)`)
  console.log(`texto visivel: ${JSON.stringify(raiz.texto)}`)

  const vaza = await pagina.evaluate(() => {
    const maus = []
    const limite = document.documentElement.clientWidth
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect()
      if (r.width && (r.right > limite + 1 || r.left < -1)) {
        const cls = (el.className || '').toString().split(' ')[0]
        maus.push(`${el.tagName.toLowerCase()}.${cls} (${Math.round(r.left)}..${Math.round(r.right)} de ${limite})`)
      }
    }
    return [...new Set(maus)].slice(0, 8)
  })
  console.log(`vazando na horizontal: ${vaza.length ? '\n  ' + vaza.join('\n  ') : 'nenhum'}`)

  // Container de rolagem aninhado: a rolagem engancha porque o dedo gasta os
  // primeiros pixels rolando um elemento interno antes de a pagina andar.
  // Aconteceu de verdade: `overflow-x: hidden` numa pagina promove o eixo
  // vertical a `auto` (regra da especificacao), e o buque em `bottom: -14px`
  // dava 14px de rolagem interna. Daqui em diante isso aparece aqui.
  const aninhados = await pagina.evaluate(() =>
    [...document.querySelectorAll('body *')]
      .filter((el) => {
        const sobra = el.scrollHeight - el.clientHeight
        if (sobra < 2) return false
        const o = getComputedStyle(el).overflowY
        return o === 'auto' || o === 'scroll'
      })
      .map((el) => `${el.tagName.toLowerCase()}.${(el.className || '').toString().split(' ')[0]} (+${el.scrollHeight - el.clientHeight}px)`)
      .slice(0, 8))
  console.log(`rolagem interna: ${aninhados.length ? '\n  ' + aninhados.join('\n  ') : 'nenhuma'}`)

  console.log(`\nconsole (${erros.length}):`)
  for (const [tipo, txt] of erros.slice(0, 12)) console.log(`  [${tipo}] ${String(txt).slice(0, 500)}`)

  if (saida) { await pagina.screenshot({ path: saida, fullPage: true }); console.log(`\nprint: ${saida}`) }
  await navegador.close()
  process.exit(erros.some((e) => e[0] === 'pageerror') || raiz.filhos === 0 ? 1 : 0)
})()
