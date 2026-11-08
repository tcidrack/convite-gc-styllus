// Brilhos dourados que ficam atras do conteudo. Compartilhado entre o
// envelope, o convite e a /admin para as tres telas parecerem uma so.

// Posicoes fixas (e nao Math.random) para o desenho nao mudar a cada render.
const BRILHOS = [
  { x: 12, y: 8, t: 14, d: 0 },
  { x: 86, y: 14, t: 10, d: 1.1 },
  { x: 70, y: 4, t: 8, d: 2.3 },
  { x: 6, y: 38, t: 9, d: 0.6 },
  { x: 93, y: 46, t: 12, d: 1.8 },
  { x: 18, y: 64, t: 8, d: 2.9 },
  { x: 82, y: 72, t: 11, d: 0.3 },
  { x: 48, y: 90, t: 9, d: 1.5 },
  { x: 8, y: 88, t: 12, d: 2.1 },
  { x: 92, y: 94, t: 8, d: 0.9 },
]

export default function Cenario() {
  return (
    <div className="cenario" aria-hidden="true">
      {BRILHOS.map((b, i) => (
        <span
          key={i}
          className="brilho"
          style={{
            left: `${b.x}%`,
            top: `${b.y}%`,
            fontSize: `${b.t}px`,
            animationDelay: `${b.d}s`,
          }}
        >
          ✦
        </span>
      ))}
    </div>
  )
}
