import { tema } from "../configuracaoTema"

// Marca da loja redesenhada em codigo a partir da camiseta da bonequinha:
// coroa, nome e linha com coracao. O tamanho vem do font-size de .logo.
// Tudo em span porque ela fica dentro de <h1> e de <button>.
export default function Logo({ className = "" }) {
  return (
    <span className={`logo ${className}`} role="img" aria-label={tema.nome}>
      <svg className="logo-coroa" viewBox="0 0 64 42" aria-hidden="true">
        <path d="M9 31 5 13l13 9L32 7l14 15 13-9-4 18z" />
        <rect x="9" y="33.5" width="46" height="4.5" rx="1.5" />
        <circle cx="5" cy="10" r="3" />
        <circle cx="32" cy="4" r="3" />
        <circle cx="59" cy="10" r="3" />
      </svg>
      <span className="logo-gc">GC</span>
      <span className="logo-styllus">STYLLUS</span>
      <span className="logo-linha" aria-hidden="true">
        <i />
        <svg viewBox="0 0 24 22">
          <path d="M12 21 2.6 11.4a5.7 5.7 0 0 1 8-8.1L12 4.7l1.4-1.4a5.7 5.7 0 0 1 8 8.1z" />
        </svg>
        <i />
      </span>
    </span>
  )
}
