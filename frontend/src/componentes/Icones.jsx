// Icones em SVG inline: evitam depender de uma fonte de icones externa,
// que quando nao carrega aparece como texto cru na tela.
//
// Os solidos levam a classe `icone-solido`, que o CSS pinta com
// currentColor. Os de contorno ficam sem ela, para o fill="none" do
// proprio SVG valer.

function Contorno({ children }) {
  return (
    <svg className="icone" viewBox="0 0 24 24" aria-hidden="true" fill="none"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  )
}

export function IconePin() {
  return (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" />
    </svg>
  )
}

export function IconeCheck({ preenchido = false }) {
  return preenchido ? (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1.2 14.6-4.2-4.2 1.4-1.4 2.8 2.8 5.2-5.2 1.4 1.4-6.6 6.6z" />
    </svg>
  ) : (
    <Contorno>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12.3 2.7 2.7L16 9.7" />
    </Contorno>
  )
}

export function IconeSom({ mudo = false }) {
  return (
    <Contorno>
      <path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5z" />
      {mudo ? (
        <path d="m16 9.5 5 5m0-5-5 5" />
      ) : (
        <path d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.5a7.8 7.8 0 0 1 0 11" />
      )}
    </Contorno>
  )
}

export function IconeCafe() {
  return (
    <Contorno>
      <path d="M4 9h13v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z" />
      <path d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17" />
      <path d="M8 3c-.8 1 .8 2 0 3M12.5 3c-.8 1 .8 2 0 3" />
    </Contorno>
  )
}

export function IconeBalao() {
  return (
    <Contorno>
      <path d="M12 2.5c3.6 0 6 2.8 6 6.2 0 3.8-3.2 7.3-6 7.3s-6-3.5-6-7.3c0-3.4 2.4-6.2 6-6.2z" />
      <path d="m10.8 16-.8 1.6h4l-.8-1.6" />
      <path d="M12 17.6c0 1.5-1.5 2-1.5 3.9" />
    </Contorno>
  )
}

export function IconePresente() {
  return (
    <Contorno>
      <rect x="3" y="8" width="18" height="4" rx="1" />
      <path d="M5 12v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8M12 8v13" />
      <path d="M12 8S10.5 3 7.8 3a2.5 2.5 0 0 0 0 5zM12 8s1.5-5 4.2-5a2.5 2.5 0 0 1 0 5z" />
    </Contorno>
  )
}

export function IconeEtiqueta() {
  return (
    <Contorno>
      <path d="M3 4v7.2a2 2 0 0 0 .6 1.4l8.8 8.8a2 2 0 0 0 2.8 0l6.2-6.2a2 2 0 0 0 0-2.8l-8.8-8.8a2 2 0 0 0-1.4-.6H5a2 2 0 0 0-2 2z" />
      <circle cx="8" cy="8" r="1.4" />
    </Contorno>
  )
}

export function IconeCabide() {
  return (
    <Contorno>
      <path d="M12 8.5c0-1.3 2.5-1.5 2.5-3.5a2.5 2.5 0 0 0-5 0" />
      <path d="M12 8.5 2.8 15.3A1.8 1.8 0 0 0 3.9 18.5h16.2a1.8 1.8 0 0 0 1.1-3.2z" />
    </Contorno>
  )
}

export function IconeBolsa() {
  return (
    <Contorno>
      <path d="M5 9h14l1.2 10.8a1 1 0 0 1-1 1.2H4.8a1 1 0 0 1-1-1.2z" />
      <path d="M8.5 12V6.5a3.5 3.5 0 0 1 7 0V12" />
    </Contorno>
  )
}
