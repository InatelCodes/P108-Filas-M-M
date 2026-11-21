# Calculadora de Teoria das Filas

Resolve os modelos da disciplina P108 (Otimização II) e foi validada contra **todas as listas de exercícios**
do material (M/M/s, M/M/s/K, M/M/s/N, M/G/1 e filas com prioridades).

| Modelo | Atendentes | Limite do sistema | Quando usar |
|---|---|---|---|
| **M/M/1** | 1 | nenhum | uma fila, um atendente |
| **M/M/s** | s ≥ 2 | nenhum | fila única, vários atendentes (caixas de banco) |
| **M/M/1/K**, **M/M/s/K** | 1 ou s | no máximo **K** clientes (atendimento + fila) | há limite de espaço; quem chega e encontra cheio vai embora |
| **M/M/1/N**, **M/M/s/N** | 1 ou s | população finita de **N** clientes | poucos clientes possíveis (ex.: 10 máquinas que quebram e voltam) |
| **M/G/1** | 1 | nenhum | atendimento que **não** é exponencial (constante, Erlang, ou só se sabe média e desvio padrão) |
| **Prioridades** | 1 ou s | nenhum | clientes de classes diferentes, com ou sem interrupção do atendimento |

Além do cálculo direto, o app resolve os problemas **"ao contrário"** (o enunciado dá ρ, Lq, W… e pede λ e μ, ou pede
a taxa necessária para atingir uma meta), calcula custos, probabilidades de Poisson, a Lei de Little e tem uma
aba de **teoria** (fórmulas, glossário, como ler um enunciado).

---

## 1. Instalação (Windows / PowerShell)

Requer Python 3.10 ou mais novo. Dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Se o PowerShell bloquear o `Activate.ps1`, rode antes:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

O núcleo de cálculo e o terminal **não precisam de nenhuma biblioteca**; só a interface web usa o Streamlit.

## 2. Como abrir

```powershell
streamlit run app.py        # interface web (recomendado)
python cli.py               # terminal, menu interativo
```

---

## 3. Usando a interface web

A tela tem duas metades: **à esquerda a ficha** (o que você preenche, em passos numerados, escrita como o
enunciado) e **à direita o resultado**, que muda enquanto você digita. Todos os campos começam vazios.

### Aba Calculadora

Escolha o **tipo de sistema** no topo: *Filas M/M*, *M/G/1* ou *Com prioridades*.

#### Filas M/M
1. **Como é o seu sistema?**
   - *Quantos atendentes trabalham ao mesmo tempo?* (1 = M/M/1; 2 ou mais = M/M/s).
   - *Quantos clientes cabem no sistema?* **Sem limite**, **limite de K** (quem chega com o sistema cheio vai embora)
     ou **só existem N clientes** (população finita).
   - Se o enunciado diz **"apenas 3 podem esperar"**, escolha *"só os lugares de espera"*: o programa calcula
     K = atendentes + 3. O modelo detectado aparece na hora (`M/M/2/K`).
2. **O que o enunciado informa?** (só nos modelos sem limite)
   - **A chegada (λ) e o atendimento (μ)**: escolha a frase que se parece com o enunciado, por exemplo
     *"chega 1 cliente a cada 12 min"* (tempo médio) ou *"chegam 5 clientes por hora"* (taxa).
   - **Outras medidas**: informe **duas** entre ρ, L, Lq, P0, W, Wq, λ e μ (ex.: ρ = 0,8 e Wq = 15 min; Lq = 3,2 e W = 0,5 h;
     λ e ρ). O programa descobre λ e μ.
3. **Quanto cada atendente atende (μ)**, com o mesmo formato de frase.

À direita: quatro "senhas" (**L, Lq, W, Wq**), uma frase explicando o resultado, o desenho do sistema, a tabela
com todas as medidas (inclui bloqueio e clientes perdidos nos modelos com K; clientes em operação e fração do tempo
de cada cliente nos modelos com N), o gráfico e a tabela de P(n), as **fórmulas do modelo** e as
**consultas de probabilidade**.

**Consultas de probabilidade** (clique em *+ Adicionar consulta* para quantas quiser; valem nos seis modelos):

| Variável | Comparações | Exemplo |
|---|---|---|
| Clientes no sistema (n) | `=`, `<`, `≤`, `>`, `≥`, `entre` | P(2 ≤ n ≤ 6) |
| Clientes na fila (nq) | `=`, `<`, `≤`, `>`, `≥`, `entre` | P(nq > 2) |
| Tempo no sistema (W) | `>`, `≤` (com unidade) | P(W > 3 min) |
| Tempo na fila (Wq) | `>`, `≤`, `= 0 (não espera)` | P(Wq ≤ 30 s) |
| Percentil de W / Wq | valor em % | "em 95% dos casos o cliente espera até…" |

#### M/G/1
Informe λ, a média do atendimento e **quanto o atendimento varia**: *exponencial* (σ = média), *constante* (σ = 0),
*Erlang com k fases* ou *conheço o desvio padrão σ*. Além das medidas, a tabela **"E se a variabilidade mudar?"**
compara vários valores de σ (ex.: `4, 3, 2, 1, 0`) mostrando a redução da fila.
O M/G/1 calcula as **médias** (não há P(n) nem P(W>t)).

#### Com prioridades
- **Exponencial e igual para todas as classes (M/M/s)**: informe atendentes, se a prioridade é *com* ou *sem
  interrupção*, o número de classes, λ de cada classe (ou λ total e a **porcentagem** de cada uma) e μ.
- **Cada classe com seu tempo de atendimento (1 atendente, M/G/1)**: média e desvio padrão por classe; opção de
  ordenar pelo menor tempo de atendimento (**SPT**).

A tabela mostra L, Lq, W e Wq de cada classe e a média geral (que é igual à de uma fila FIFO). No M/M/s há ainda a
comparação **FIFO × sem interrupção × com interrupção**.

### Aba Dimensionar
- **Comparar nº de atendentes (e custos)**: L, Lq, W, Wq para 1, 2, 3… atendentes. Com custos preenchidos, indica o
  menor custo: `custo = Cs·(atendentes) + Cw·(L ou Lq) [+ Cb·clientes perdidos]`. Opções: o atendente só é pago
  enquanto está ocupado (usa o nº médio de atendentes ocupados) e **custo por período** (ex.: dia de 8 horas).
- **Qual λ ou μ atinge uma meta?** (M/M e M/G/1): ex.: "que taxa de atendimento faz o cliente ficar só 2 min no
  sistema?" ou "que μ faz P(n > 3) ser 15%?". A meta pode ser L, Lq, W, Wq, ρ, P0, bloqueio ou uma probabilidade.
- **Quantos atendentes preciso?**: menor número de atendentes que cumpre **vários critérios ao mesmo tempo**
  (ex.: Lq ≤ 1, P(nq ≤ 5) ≥ 95% e P(Wq ≤ 5 min) ≥ 95%). A tabela mostra cada número testado.

### Aba Ferramentas
- **Calcular λ e μ a partir de dados**: número de clientes em um intervalo, tempo médio, lista de contagens ou
  **tabela de frequências** (valor e frequência, absoluta ou relativa).
- **Contagens de Poisson**: P(X = k), P(X ≤ k)… de eventos em um intervalo (ex.: 10 chegadas em 1 hora).
- **Lei de Little**: dados λ, μ e **uma** medida observada (L, Lq, W ou Wq), calcula as outras três sem supor modelo.
- **Notação de Kendall**: decodifica `M/M/3/FCFS/10/100` e diz como resolver.

### Aba Teoria
Fórmulas de cada modelo, relações gerais, **como ler um enunciado** (o que cada trecho vira na calculadora),
glossário e notação de Kendall.

> As fontes (Fraunces e IBM Plex) são carregadas do Google Fonts; sem internet o app usa fontes do sistema.

---

## 4. Usando o terminal

```powershell
python cli.py calcular --lam 12min --mu 8min --unidade hora                     # M/M/1
python cli.py calcular --lam 2 --mu 0.7 --s 4 --unidade minuto --prob "n>=5" "nq=0" "Wq<=1min" "p95:Wq"
python cli.py calcular --lam 5 --mu 4 --s 2 --K 6 --prob "Wq>30min" "W<=1h"    # M/M/2/K
python cli.py calcular --lam 0.1 --mu 4 --N 20                                  # M/M/1/N
python cli.py calcular --lam 25 --mu 40 --sigma 0                               # M/G/1 com atendimento constante
python cli.py calcular --lam 25 --mu 40 --erlang 4                              # M/G/1 Erlang-4
python cli.py prioridades --lams 0.1 0.4 1.5 --mu 3 --s 1 --interrupcao         # prioridades
python cli.py descobrir --s 1 --conhecido rho=0.8 Wq=15min --unidade hora       # descobre λ e μ
python cli.py poisson --taxa 12.8 --tempo 1 --prob "=10" "<=8"                  # Poisson
python cli.py little --lam 40 --mu 30 --medida Wq=1min --unidade hora           # Lei de Little
python cli.py kendall M/M/3/FCFS/10/100
```

- Taxas aceitam um número (**taxa**, na unidade de `--unidade`) ou um número com unidade (**tempo médio**): `20min`, `40s`, `1,5h`.
- Consultas de `--prob` (**sempre entre aspas**, senão o PowerShell interpreta `>` como redirecionamento):
  `n=3`, `n>=5`, `n:2-6` · `nq>2` · `W>12min`, `W<=1h`, `Wq>6min`, `Wq=0` · `p95:Wq`, `p90:W`.

---

## 5. Restrições dos valores

| Dado | Regra | O que acontece se violar |
|---|---|---|
| λ, μ | maiores que zero (qualquer número real) | mensagem de erro |
| s (atendentes) | inteiro ≥ 1; testado até 5000 | — |
| K | inteiro ≥ s (inclui quem está sendo atendido) | mensagem de erro |
| N | inteiro ≥ 1 | — |
| K e N | não podem ser usados juntos | mensagem de erro |
| Modelos sem limite | **λ < s·μ** (ρ < 1) | "Fila instável": a fila cresceria sem parar |
| Modelos com K ou N | sem restrição (sempre estáveis, mesmo com λ > μ) | — |
| M/G/1 | λ < μ e σ ≥ 0 | mensagem de erro |
| Prioridades | soma dos λ < s·μ (M/M/s) ou Σ λi·E[Si] < 1 (M/G/1); 1 a 8 classes na tela | mensagem de erro |
| n, r, k nas consultas | inteiros ≥ 0, **sem limite superior**; em "entre", o 2º valor ≥ o 1º | — |
| t (tempo) | ≥ 0 | — |
| Percentil | maior que 0 e menor que 100 | — |
| Dimensionar | testa até 100 atendentes | avisa que nenhum cumpre |

Desempenho medido: modelos com K ou N na casa dos milhares de estados respondem em décimos de segundo, inclusive
percentis. A tabela e o gráfico de P(n) dos modelos sem limite param quando a cauda fica abaixo de 0,1% (no máximo 200 valores).

---

## 6. Fórmulas (resumo)

Com ρ = λ/(s·μ) e a = λ/μ. Relações válidas em todos: **L = λef·W**, **Lq = λef·Wq**, **W = Wq + 1/μ**.

**M/M/1:** P0 = 1 − ρ · Pn = (1 − ρ)ρⁿ · L = λ/(μ−λ) · Lq = λ²/[μ(μ−λ)] · W = 1/(μ−λ) · Wq = λ/[μ(μ−λ)] ·
P(W>t) = e^(−μ(1−ρ)t) · P(Wq>t) = ρ·e^(−μ(1−ρ)t)

**M/M/s:** P0 = 1 / [ Σₙ₌₀^(s−1) aⁿ/n! + aˢ/(s!(1−ρ)) ] · Lq = P0·aˢ·ρ / [s!(1−ρ)²] · Wq = Lq/λ · W = Wq + 1/μ · L = Lq + a

**Modelos com K ou N:** cadeia de nascimento e morte, Pn ∝ Π (λᵢ₋₁/μᵢ), com λn = λ (K, 0 em n = K) ou (N − n)·λ (N) e
μn = min(n, s)·μ. λef = Σ λn·Pn; L = Σ n·Pn; Lq = Σ (n−s)·Pn; W = L/λef. Tempos de espera: quem entra encontrando n ≥ s
espera n−s+1 saídas (Erlang).

**M/G/1:** Lq = (λ²σ² + ρ²) / [2(1 − ρ)] · Wq = Lq/λ · W = Wq + 1/μ · L = ρ + Lq

**Prioridades (M/M/s, mesma μ):**
sem interrupção: Wk = 1/(A·B(k−1)·Bk) + 1/μ, A = s!(sμ−λ)/rˢ · Σⱼ₌₀^(s−1) rʲ/j! + sμ, Bk = 1 − Σᵢ≤ₖλᵢ/(sμ);
com interrupção: L(1..k) = L do M/M/s com λ1+…+λk, Wk = [L(1..k) − L(1..k−1)]/λk.
**M/G/1 com classes (sem interrupção):** Wq,k = [Σ λᵢE[Sᵢ²]/2] / [(1 − σ(k−1))(1 − σk)], σk = Σᵢ≤ₖ λᵢE[Sᵢ].

A aba **Teoria** do app traz todas elas formatadas.

---

## 7. Validação e observações sobre os gabaritos

```powershell
python -m unittest discover tests -v
```

70 testes: as fórmulas contra os exemplos da teoria, **todos os itens das listas de exercícios**
(`tests/test_gabaritos.py`) e propriedades que valem para qualquer entrada: Lei de Little, soma das probabilidades = 1,
modelo com K enorme convergindo para o sem limite, integral da cauda de P(W>t) igual ao tempo médio, percentis que fecham
a conta de volta, média ponderada das classes igual à FIFO.

Em alguns itens o **gabarito do material não segue o enunciado** (ou se contradiz). O programa dá o valor
correto; os testes registram cada caso (`TestDivergenciasDoMaterial`):

| Lista / item | Gabarito do material | O que o programa calcula e por quê |
|---|---|---|
| M/M/s ex. 1 (c) | 0,7627 | O enunciado pede o nº na **fila** ≤ 4: P(nq ≤ 4) = 0,8220. O gabarito é P(n ≤ 4) no sistema (também disponível). |
| M/M/s ex. 2 (a) | W = 9,375 "dias" | W = 18,75 min (= 0,3125 h). O gabarito parece converter horas em "dias". |
| M/M/s ex. 8 | L = 2, Lq = 0,667, W = 3 min | Usa o Wq = 1 min **informado** e a Lei de Little. É a ferramenta Lei de Little; o modelo M/M/2 daria Wq = 1,6 min. |
| M/M/s ex. 10 (c) | 17,08% "menos de 4" | 17,08% é P(n > 3); P(n < 4) = 82,92%. |
| M/M/s ex. 12 | 0,33 "ninguém esperando" | 0,33 é P0 (sistema vazio); P(nq = 0) = 0,5556. |
| M/M/s ex. 14 (c) | 92,7% | P(nq ≤ 4) = 95,42%; o gabarito é P(n ≤ 5), que só vale com 1 pista. |
| M/M/s/K ex. 4, 5 e 6 (e) | calculados com **K = 4** | Os enunciados (2 pistas/terminais com 3 vagas de espera, ou "máximo de 5 pacientes") dariam K = 5. Os testes usam K = 4 para reproduzir o gabarito. No app, as duas leituras são possíveis. |
| M/M/s/N ex. 4 (c) | 0,667 "técnico ocupado" | 0,667 é a carga nominal N·λ/μ (mostrada como tal); a fração de tempo ocupado é 1 − P0 = 0,507. |
| M/M/s/N ex. 5 (b) e (c) | R$ 478,672 e R$ 270,336 | Não foi possível reproduzir: com $20/h, dia de 8 h e mecânico a $50/dia dá R$ 208,67 (1 mecânico) e R$ 221,08 (2). O 478,672 é ≈ 20·24·L (dia de 24 h). |
| M/M/s/N ex. 6 (d) | 0,8184 | 1 − L/N = 0,9081, coerente com o ex. 3 (d). |
| M/G/1 ex. 2 e 3 | Lq = 1,125 e L = 2,83 | Só fecham com atendimento **constante** (σ = 0), que o enunciado não diz. Com exponencial, Lq = 2,25. |
| Prioridades ex. 5 (classe 1, 1 atendente) | "Lq = 0,75; L = 0,167" | L = 0,75 e Lq = 0,4167 (rótulos trocados e valor diferente). |
| M/G/1 ex. 4 (classe 2) | Lq = 0,083 | Lq = 0,8333 (falta um dígito). |
| Prioridades ex. 7 (2 atendentes, com interrupção, classe 3) | Wq = 0,05493 | 0,05478 (acúmulo de arredondamentos no gabarito). |

O exercício 2 de M/M/s/N tem os itens do gabarito em **ordem embaralhada** (ex.: o valor dado para "nº médio na
fila" é o do tempo de espera); os valores existem, só mudam de rótulo.

---

## 8. Estrutura e uso como biblioteca

```
filas-mm/
├── app.py               interface web (Streamlit)
├── cli.py               terminal
├── requirements.txt
├── .streamlit/config.toml   tema
├── filas/
│   ├── modelos.py       motor dos modelos M/M (6 modelos), tempos de espera, percentis, custos
│   ├── mg1.py           M/G/1 (Pollaczek-Khintchine)
│   ├── prioridades.py   prioridades com e sem interrupção; M/G/1 com classes e SPT
│   ├── inverso.py       descobrir λ/μ a partir de medidas; λ ou μ para uma meta; vários critérios
│   ├── relacoes.py      Lei de Little
│   ├── poisson.py       contagens de Poisson
│   ├── unidades.py      unidades de tempo, conversões, formatação
│   ├── kendall.py       decodificador de Kendall
│   ├── relatorio.py     textos de resultado
│   └── teoria.py        fórmulas, glossário e guia de enunciados exibidos no app
└── tests/
    ├── test_modelos.py     fórmulas e propriedades
    └── test_gabaritos.py   listas de exercícios
```

```python
from filas import Fila
from filas.mg1 import FilaMG1
from filas.prioridades import PrioridadesMMs
from filas.inverso import resolver_por_medidas, parametro_para_meta

f = Fila(lam=0.6, mu=0.5, s=3)                      # M/M/3
r = f.resultado(); print(r.L, r.Lq, r.W, r.Wq, r.P0)
print(f.P_clientes("entre", 2, 6), f.P_fila(">", 2))   # P(2≤n≤6), P(nq>2)
print(f.P_W_maior(3), f.P_Wq_maior(2))              # vale também para /K e /N
print(f.tempo_percentil(0.95, "Wq"))                # 95% esperam até este tempo

Fila(lam=5, mu=4, s=2, K=6).resultado().p_bloqueio   # M/M/2/6
Fila(lam=0.1, mu=4, s=1, N=20).resultado().L         # M/M/1/N
FilaMG1.deterministica(25, 40).resultado().Lq        # M/D/1

(lam, mu), = resolver_por_medidas(1, [("rho", 0.8), ("Wq", 15)])   # λ = 0,2133 e μ = 0,2667 (por min)
parametro_para_meta(Fila(0.9, 1.2), "mu", "W", 2.0)                 # μ para W = 2 min
PrioridadesMMs((0.1, 0.4, 1.5), mu=3, s=1, interrupcao=True).resultado().classes
```

`lam` e `mu` devem estar **na mesma unidade de tempo**; os tempos devolvidos ficam nessa unidade.
