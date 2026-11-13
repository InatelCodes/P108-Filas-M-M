# Filas M/M — calculadora de Teoria das Filas

Resolve os seis modelos M/M da disciplina P108 (Otimização II):

| Modelo | Atendentes | Limite do sistema | Quando usar |
|---|---|---|---|
| **M/M/1** | 1 | nenhum | uma fila, um atendente (barbearia, motores em manutenção) |
| **M/M/s** | s ≥ 2 | nenhum | uma fila única, vários atendentes (caixas de banco) |
| **M/M/1/K** | 1 | no máximo **K** clientes (atendimento + fila) | há limite de espaço; quem chega e encontra cheio vai embora |
| **M/M/s/K** | s ≥ 2 | no máximo **K** | idem, com vários atendentes |
| **M/M/1/N** | 1 | população finita de **N** clientes | poucos clientes possíveis (ex.: 20 máquinas que quebram e voltam) |
| **M/M/s/N** | s ≥ 2 | população finita de **N** | idem, com vários atendentes |

Também inclui: os **exercícios do PDF resolvidos** (com conferência contra o gabarito dos slides),
comparação de nº de atendentes com **custos**, descoberta de λ ou de s a partir de uma **meta**,
cálculo de λ/μ a partir de dados e um **decodificador da notação de Kendall**.

---

## 1. Instalação (Windows / PowerShell)

Requer Python 3.10 ou mais novo. Dentro da pasta do projeto:

```powershell
py -m venv .venv # ou python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Se o PowerShell bloquear o `Activate.ps1`, rode antes:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

O núcleo de cálculo e o terminal **não precisam de nenhuma biblioteca**; só a interface web usa o Streamlit.

## 2. Como abrir

**Interface web (recomendado):**
```powershell
streamlit run app.py
```
O navegador abre em `http://localhost:8501`.

**Terminal:**
```powershell
python cli.py                 # menu interativo
python cli.py exercicios      # resolve todos os exercícios do PDF
```

---

## 3. Usando a interface web

A tela tem duas metades: **à esquerda a ficha** (o que você preenche, em passos numerados,
escrita como o enunciado) e **à direita o resultado**, que muda enquanto você digita.

### Aba Calculadora
**Dica:** em *Comece por um exemplo* escolha um exercício do PDF; a ficha inteira é preenchida
e você vê onde cada dado do enunciado entra.

1. **Como é o seu sistema?**
   - *Quantos atendentes trabalham ao mesmo tempo?* (1 = M/M/1; 2 ou mais = M/M/s).
   - *Quantos clientes cabem no sistema?* Três opções: **sem limite**; **limite de K clientes**
     (se estiver cheio, quem chega vai embora); **só existem N clientes no total** (população finita).
   - O programa mostra o modelo detectado, por exemplo `M/M/2/K`. Você não precisa escolher o nome do modelo.
2. **Quanto chega? (λ)** e 3. **Quanto cada atendente atende? (μ)**: escolha a frase que se parece
   com o enunciado e preencha o número e a unidade:
   - *"chega 1 cliente a cada 20 min"* → tempo médio;
   - *"chegam 3 clientes por hora"* → taxa.

   Abaixo de cada campo aparece a conversão (`λ = 3 por hora · 1 a cada 20 min`) para você conferir.
   λ e μ podem estar em unidades diferentes; o programa converte.
4. **Mostrar os tempos do resultado em**: unidade usada na tabela (os tickets escolhem a unidade mais legível).

À direita: quatro "senhas" com **L, Lq, W e Wq**, uma frase explicando em palavras, o desenho do sistema,
a tabela completa, o gráfico de P(n) e as **perguntas de probabilidade**
("Qual a chance de haver exatamente 3 clientes?", "…de esperar mais de 1 hora?").
As chances de esperar mais que um tempo t existem só para M/M/1 e M/M/s.

**Exemplo (barbearia):** escolha o exemplo *Barbearia — M/M/1*. Resposta: L = 3, Lq = 2,25, W = 1 h, Wq = 45 min, P0 = 25%.

> Em **população finita (N)**, λ passa a ser a taxa **de cada cliente que está fora do sistema**
> (ex.: cada máquina quebra, em média, 1 vez a cada 10 horas). O passo 2 muda o texto para deixar isso claro.

### Aba Dimensionar
Usa a mesma ficha (sem a pergunta que a ferramenta descobre):
- **Comparar nº de atendentes (e custos)**: mostra L, Lq, W, Wq para 1, 2, 3… atendentes.
  Preenchendo os custos, indica o número de menor custo total:
  `custo = custo do atendente × s + custo de espera × L (ou Lq) [+ custo × clientes perdidos, no modelo /K]`.
- **Qual λ atinge uma meta?**: ex.: "quero que o tempo médio no sistema fique em até 1,25 h" (item g da barbearia → λ = 3,2 por hora).
- **Quantos atendentes preciso?**: menor número de atendentes para manter, por exemplo, Wq em até 2 minutos.

### Aba Exercícios do PDF
Todos os exercícios M/M do PDF, com resposta, fórmula usada e, quando o slide traz gabarito, a marca ✔ de conferência.

### Aba Ferramentas
- **λ e μ a partir de dados**: número de clientes em um intervalo, tempo médio, ou lista de contagens por período
  (mostra a taxa em segundos, minutos, horas, dias e meses).
- **Notação de Kendall**: digite `M/M/3/FCFS/10/100` e veja o significado de cada campo e se o projeto resolve o modelo.

> As fontes (Fraunces e IBM Plex) são carregadas do Google Fonts; sem internet o app usa fontes do sistema, sem perder funcionalidade.

---

## 4. Usando o terminal

```powershell
# M/M/1 com tempos médios (20 min entre chegadas, 15 min de atendimento), resultado em horas
python cli.py calcular --lam 20min --mu 15min --unidade hora

# M/M/s: 3 caixas, λ = 0,6 e μ = 0,5 por minuto, com probabilidades extras
python cli.py calcular --lam 0.6 --mu 0.5 --s 3 --unidade minuto --prob "n>5" "W>3min" "Wq>2min"

# M/M/2/K com capacidade 10   |   população finita N = 20
python cli.py calcular --lam 5 --mu 4 --s 2 --K 10
python cli.py calcular --lam 0.1 --mu 4 --N 20

python cli.py kendall M/M/3/FCFS/10/100
```

- `--lam` e `--mu` aceitam um número (**taxa**, na unidade de `--unidade`) ou um número com unidade (**tempo médio**): `20min`, `40s`, `1,5h`.
- Consultas de `--prob`: `n=3`, `n>5`, `W>12min`, `Wq>6min`. **Coloque entre aspas**, senão o PowerShell interpreta `>` como redirecionamento.

---

## 5. Fórmulas (resumo)

Com ρ = λ/(s·μ) e a = λ/μ. O sistema só é estável se **ρ < 1** (nos modelos sem limite).

**M/M/1:** P0 = 1 − ρ · Pn = (1 − ρ)ρⁿ · L = λ/(μ−λ) · Lq = λ²/[μ(μ−λ)] · W = 1/(μ−λ) · Wq = λ/[μ(μ−λ)] ·
P(W>t) = e^(−μ(1−ρ)t) · P(Wq>t) = ρ·e^(−μ(1−ρ)t)

**M/M/s:** P0 = 1 / [ Σₙ₌₀^(s−1) aⁿ/n! + aˢ/(s!(1−ρ)) ] · Pn = aⁿ/n!·P0 (n ≤ s), aⁿ/(s!·s^(n−s))·P0 (n ≥ s) ·
Lq = P0·aˢ·ρ / [s!(1−ρ)²] · Wq = Lq/λ · W = Wq + 1/μ · L = Lq + a

**Modelos finitos (/K e /N):** são resolvidos pela mesma ideia (cadeia de nascimento e morte):
Pn ∝ Π (λᵢ₋₁ / μᵢ), com λn = λ (modelo K, 0 em n = K) ou (N − n)·λ (modelo N) e μn = min(n, s)·μ.
Depois: L = Σ n·Pn · Lq = Σ (n−s)·Pn · λef = Σ λn·Pn · W = L/λef · Wq = Lq/λef.
No modelo K, a **probabilidade de bloqueio** é P_K e os clientes perdidos são λ·P_K por unidade de tempo.

Relações válidas em todos: **L = λef·W**, **Lq = λef·Wq**, **W = Wq + 1/μ**.

## 6. Dúvidas comuns

| Mensagem / situação | O que fazer |
|---|---|
| "Fila instável: λ ≥ s·μ" | Chegam mais clientes do que o sistema atende. Aumente μ ou s, ou reduza λ. Só ocorre em modelos sem limite. |
| "K precisa ser ≥ s" | A capacidade K inclui quem está sendo atendido; precisa ser pelo menos o nº de atendentes. |
| P(W>t) indisponível | Só existe para M/M/1 e M/M/s. Nos modelos /K e /N use as médias e P(n). |
| Resultados em "d" ou "min" em vez da unidade escolhida | Os tempos são mostrados na unidade mais legível; o valor na unidade escolhida aparece entre parênteses na tabela. |
| 1 mês | Considerado como 30 dias (usado no exercício dos motores). |
| M/G/1 e modelos com prioridade | Fora do escopo deste projeto (que cobre M/M). |

## 7. Estrutura e uso como biblioteca

```
filas-mm/
├── app.py              interface web (Streamlit)
├── cli.py              terminal
├── requirements.txt
├── filas/
│   ├── modelos.py      motor de cálculo dos 6 modelos + dimensionamento
│   ├── unidades.py     unidades de tempo, conversões, formatação
│   ├── exercicios.py   exercícios do PDF resolvidos
│   ├── kendall.py      decodificador de Kendall
│   └── relatorio.py    textos de resultado
└── tests/test_modelos.py
```

```python
from filas import Fila

f = Fila(lam=0.6, mu=0.5, s=3)          # M/M/3
r = f.resultado()
print(r.L, r.Lq, r.W, r.Wq, r.P0)       # medidas principais
print(f.P(3), f.P_mais_que(5))          # P(n=3), P(n>5)
print(f.P_W_maior(3), f.P_Wq_maior(2))  # P(W>3), P(Wq>2)

Fila(lam=5, mu=4, s=2, K=10).resultado().p_bloqueio   # M/M/2/10
Fila(lam=0.1, mu=4, s=1, N=20).resultado().L          # M/M/1/N
```

`lam` e `mu` devem estar **na mesma unidade de tempo**; os tempos devolvidos ficam nessa unidade.

**Testes:** `python -m unittest discover tests -v`
