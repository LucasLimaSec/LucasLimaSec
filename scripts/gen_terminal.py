# Uso: python scripts/gen_terminal.py > assets/terminal.svg
"""Gera assets/terminal.svg: um terminal animado (SMIL, em loop) para o README."""
import sys
from html import escape


BG, BORDER, BAR = "#111210", "#2a2c27", "#1a1b18"
FG, MUTED, LIME, BLUE, ORANGE = "#E9E9E3", "#8A8C86", "#C5F06A", "#7f9fcf", "#E57F4C"

W, PAD_X, TOP, LH, FS = 860, 24, 64, 22, 14
CHAR = 8.4          # largura de célula da grade (0.6em a 14px)
TYPE_SPEED = 0.045  # segundos por caractere digitado
HOLD = 4.0          # tempo parado no fim antes de reiniciar

PROMPT = [("lucas", LIME), ("@", MUTED), ("lanatech", LIME), (":", MUTED), ("~", BLUE), ("$ ", MUTED)]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)

# (tipo, conteúdo). "cmd" é digitado; "out" aparece de uma vez.
SCRIPT = [
    ("cmd", "whoami"),
    ("out", [("Lucas de Oliveira Lima", FG), ("  //  Engenheiro de Software & Segurança Ofensiva", MUTED)]),
    ("gap", None),
    ("cmd", "cat sobre.txt"),
    ("out", [("› ", LIME), ("Ex-Cabo do Exército Brasileiro: liderança e trabalho em equipe", FG)]),
    ("out", [("› ", LIME), ("Engenharia de Software @ Unicesumar  ·  Maringá, PR", FG)]),
    ("out", [("› ", LIME), ("Encontro a falha, escrevo a correção e ensino o time a evitá-la", FG)]),
    ("gap", None),
    ("cmd", "nmap -sV --top-skills lucas"),
    ("out", [("PORT        STATE  SERVICE", MUTED)]),
    ("out", [("443/tcp     ", FG), ("open   ", LIME), ("pentest-web-api-mobile", FG)]),
    ("out", [("4444/tcp    ", FG), ("open   ", LIME), ("red-team", FG)]),
    ("out", [("8080/tcp    ", FG), ("open   ", LIME), ("appsec-devsecops", FG)]),
    ("out", [("3000/tcp    ", FG), ("open   ", LIME), ("full-stack-dev", FG)]),
    ("out", [("11434/tcp   ", FG), ("open   ", LIME), ("ia-local-automacao", FG)]),
    ("gap", None),
]

# --- linha do tempo -----------------------------------------------------------
t = 0.6
events = []  # (tipo, y, start, end, conteúdo)
y = TOP
for kind, content in SCRIPT:
    if kind == "gap":
        y += LH * 0.5
        continue
    if kind == "cmd":
        t += 0.5                                  # prompt aparece, pausa, digita
        dur = len(content) * TYPE_SPEED
        events.append(("cmd", y, t, t + dur, content))
        t += dur + 0.45
    else:
        events.append(("out", y, t, t, content))
        t += 0.09
    y += LH
final_prompt_y = y
events.append(("final", y, t + 0.3, t + 0.3, None))
TOTAL = t + 0.3 + HOLD
H = int(y + 34)


def kt(x):
    return f"{min(max(x / TOTAL, 0), 1):.4f}"


def appear(start):
    """Opacidade 0 -> 1 em `start`, segura até o fim, reinicia no loop."""
    return (f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{kt(start)};{kt(start)};1" '
            f'dur="{TOTAL:.2f}s" repeatCount="indefinite"/>')


def col_x(col):
    return PAD_X + col * CHAR


def spans(parts, col=0):
    """Cada caractere recebe um x fixo: grade monospace exata, seja qual for a fonte disponível."""
    out = []
    for s, c in parts:
        xs = " ".join(f"{col_x(col + k):.1f}" for k in range(len(s)))
        out.append(f'<tspan fill="{c}" x="{xs}">{escape(s)}</tspan>')
        col += len(s)
    return "".join(out)


body = []
for i, (kind, y, start, end, content) in enumerate(events):
    if kind in ("cmd", "final"):
        prompt_at = start - 0.5 if kind == "cmd" else start
        body.append(f'<text y="{y}" opacity="0">{spans(PROMPT)}{appear(prompt_at)}</text>')
    if kind == "cmd":
        x0 = col_x(PROMPT_LEN)
        # revela um caractere por vez (passos discretos alinhados à grade)
        times = [0] + [start + k * TYPE_SPEED for k in range(len(content) + 1)]
        widths = [0] + [k * CHAR for k in range(len(content) + 1)]
        body.append(
            f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="{y - 16}" height="22" width="0">'
            f'<animate attributeName="width" calcMode="discrete" '
            f'values="{";".join(f"{w:.1f}" for w in widths)}" '
            f'keyTimes="{";".join(kt(x) for x in times)}" dur="{TOTAL:.2f}s" repeatCount="indefinite"/>'
            f'</rect></clipPath>'
            f'<text y="{y}" clip-path="url(#c{i})">{spans([(content, FG)], PROMPT_LEN)}</text>'
        )
    elif kind == "out":
        body.append(f'<text y="{y}" opacity="0">{spans(content)}{appear(start)}</text>')
    elif kind == "final":
        cx = col_x(PROMPT_LEN)
        body.append(
            f'<rect x="{cx:.1f}" y="{y - 13}" width="9" height="17" fill="{LIME}" opacity="0">'
            f'{appear(start)}</rect>'
            f'<rect x="{cx:.1f}" y="{y - 13}" width="9" height="17" fill="{BG}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;0.5;1" calcMode="discrete" '
            f'dur="1s" repeatCount="indefinite"/></rect>'
        )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: whoami — Lucas de Oliveira Lima, Engenheiro de Software e Segurança Ofensiva">
<style>
  text {{ font-family: 'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-size: {FS}px; white-space: pre; }}
</style>
<defs>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{LIME}" stop-opacity="0.10"/>
    <stop offset="0.5" stop-color="{LIME}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#ffffff" opacity="0.018"/>
  </pattern>
</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="url(#glow)"/>
<path d="M0.5 36 V12.5 A12 12 0 0 1 12.5 0.5 H{W - 12.5} A12 12 0 0 1 {W - 0.5} 12.5 V36 Z" fill="{BAR}"/>
<line x1="0.5" y1="36" x2="{W - 0.5}" y2="36" stroke="{BORDER}"/>
<circle cx="22" cy="18" r="6" fill="{ORANGE}"/>
<circle cx="42" cy="18" r="6" fill="{LIME}"/>
<circle cx="62" cy="18" r="6" fill="{MUTED}"/>
<text x="{W / 2}" y="23" fill="{MUTED}" text-anchor="middle" style="font-size:12px">lucas@lanatech: ~ — zsh</text>
<text x="{W - 20}" y="23" fill="{LIME}" text-anchor="end" style="font-size:12px">● online</text>
{chr(10).join(body)}
<rect x="1" y="37" width="{W - 2}" height="{H - 38}" fill="url(#scan)" pointer-events="none"/>
</svg>
'''

sys.stdout.buffer.write(svg.encode("utf-8"))
print(f"ok {W}x{H}, loop {TOTAL:.1f}s", file=sys.stderr)
