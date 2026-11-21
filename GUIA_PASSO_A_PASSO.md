# Guia passo a passo (para quem está começando)

Este guia não supõe que você conheça a matéria. Ele explica as ideias em linguagem simples e depois leva você,
clique por clique, por sete exemplos. Cada número mostrado aqui foi conferido no programa.

Para abrir o programa: `streamlit run app.py` (veja a instalação no [README](README.md)).

---

## 1. A ideia em um minuto

Teoria das filas responde perguntas como: *"Se chega um cliente a cada 20 minutos e cada corte leva 15 minutos,
quanto tempo ele espera? Quantas pessoas ficam na fila? Vale contratar outro barbeiro?"*

Você descreve o sistema (quantos chegam, quanto demora cada atendimento, quantos atendentes existem) e o programa
calcula o que acontece **em média** no longo prazo.

## 2. Seis palavras que você precisa conhecer

| Palavra | O que é | Exemplo |
|---|---|---|
| **Cliente** | Quem chega para ser atendido (pessoa, carro, máquina quebrada, ligação…) | Quem entra na barbearia |
| **Atendente** | Quem atende (também chamado de servidor ou canal) | O barbeiro, um caixa, uma pista |
| **λ (lambda)** | **Quantos clientes chegam por unidade de tempo** | 1 cliente a cada 20 min = 3 por hora |
| **μ (mi)** | **Quantos clientes UM atendente consegue atender por unidade de tempo** | Corte de 15 min = 4 por hora |
| **Sistema** | A fila **mais** quem está sendo atendido | Quem espera + quem está na cadeira |
| **Estável** | A fila não cresce para sempre. Exige que cheguem **menos** clientes do que se consegue atender (λ < atendentes × μ) | 3 chegam/h e se atende 4/h: estável |

**Atenção:** λ e μ são taxas, e o enunciado muitas vezes dá o **tempo**. São a mesma informação de formas diferentes:
"1 cliente a cada 20 minutos" é o mesmo que "3 clientes por hora" (60 ÷ 20 = 3). O programa faz essa conversão para você.

**ρ (rô)** é a "taxa de ocupação": a fração do tempo em que o atendente está ocupado. No exemplo, ρ = 3 ÷ 4 = 75%.

## 3. As quatro respostas principais

| Sigla | Significa | Em palavras |
|---|---|---|
| **L** | Clientes no sistema | Quantas pessoas há na barbearia, em média (fila + cadeira) |
| **Lq** | Clientes na fila | Quantas estão só esperando |
| **W** | Tempo no sistema | Quanto tempo uma pessoa passa lá, do momento em que chega até sair |
| **Wq** | Tempo na fila | Quanto tempo uma pessoa espera **antes** de ser atendida |

Regra fácil de lembrar: **W = Wq + tempo do atendimento**, e **L = λ × W** (Lei de Little).
O "q" vem de *queue* (fila): L e W incluem o atendimento; Lq e Wq não.

## 4. Antes de abrir o programa: leia o enunciado com 4 perguntas

1. **Quantos atendentes?** (1 barbeiro, 3 caixas, 2 pistas…)
2. **Cabem quantos no sistema?**
   - Sem limite → o padrão.
   - Há um **máximo** ("o laboratório comporta no máximo 5", "apenas 3 podem esperar") → modelo com **K**.
   - Existem só **poucos clientes possíveis** ("10 máquinas que quebram e voltam") → modelo com **N**.
3. **O que o enunciado me dá?** Tempos ou taxas ("chega um a cada 20 min", "atende 4 por hora") ou **outras
   medidas** ("a taxa de ocupação é 80% e a espera média é 15 min")?
4. **O que ele pede?** Uma média (L, W…), uma **probabilidade** ("qual a chance de esperar mais de 1 hora?"),
   **quantos atendentes** contratar, ou **que taxa** é necessária?

A aba **Teoria → Como ler um enunciado** tem uma tabela com trechos típicos e o que cada um significa.

---

## 5. Exemplo 1 — Uma barbearia (um atendente)

> Um barbeiro. Chega, em média, 1 cliente a cada 20 minutos. Cada corte leva, em média, 15 minutos.
> Quantos clientes há na barbearia? Quanto tempo cada um espera?

Perguntas do item 4: 1 atendente · sem limite · o enunciado dá **tempos** · pede médias.

**No programa**, aba **Calculadora**:

1. Deixe *Tipo de sistema* em **Filas M/M**.
2. **Passo 1 — Como é o seu sistema?** Atendentes: `1`. Clientes que cabem: **Sem limite**. Aparece
   *Modelo: M/M/1*.
3. **Passo 2 — O que o enunciado informa?** Deixe **"A chegada (λ) e o atendimento (μ)"**.
4. **Passo 3 — Quanto chega?** Deixe marcada a frase **"chega 1 cliente a cada…"**, digite `20` e escolha
   **minutos**. O programa confirma: `λ = 3 por hora`.
5. **Passo 4 — Quanto cada atendente atende?** Deixe **"cada atendimento leva…"**, digite `15`, **minutos**.
   Confirma: `μ = 4 por hora`.
6. Em *Mostrar os tempos do resultado em*, deixe **horas**.

**Resultado (à direita):**

| Senha | Valor | Significa |
|---|---|---|
| No sistema | 3,000 | 3 clientes na barbearia, em média |
| Na fila | 2,250 | 2,25 só esperando |
| Tempo no sistema | 1 h | cada um passa 1 hora lá |
| Tempo na fila | 45 min | e espera 45 min antes de ser atendido |

A tabela abaixo também mostra **ρ = 75%** (o barbeiro está ocupado 75% do tempo) e **P0 = 25%** (a chance de a
barbearia estar vazia).

## 6. Exemplo 2 — Vários atendentes (um banco com 3 caixas e fila única)

> Um banco tem 3 caixas e uma fila única. Chegam 0,6 clientes por minuto. Cada atendimento leva, em média, 2 minutos.

1. **Passo 1:** Atendentes `3`. Sem limite. (*Modelo: M/M/s*.)
2. **Passo 3 — Quanto chega?** Agora o dado é uma **taxa**: marque a frase **"chegam 5 clientes por hora"**,
   digite `0,6` e escolha **minuto** (fica *0,6 clientes por minuto*).
3. **Passo 4:** **"cada atendimento leva…"**, `2`, **minutos**.
4. *Mostrar os tempos do resultado em*: **minutos**.

**Resultado:** L = 1,294 · Lq = 0,094 · W = 2,16 min · Wq = 9,41 s. A ocupação de cada caixa é 40%.
Quase ninguém espera: a espera média é de só 9 segundos.

> **Dica:** "cada atendente atende 4 clientes por hora" fala de **UM** atendente. Nunca informe o total dos caixas.
> O programa multiplica pelo número de atendentes.

## 7. Exemplo 3 — Com limite de espaço (modelo com K)

> Um único box de lavagem. Os carros chegam, em média, 1 a cada 4 minutos e cada lavagem leva 3 minutos.
> Só **3 carros** cabem esperando; se o pátio está cheio, o carro vai embora.

1. **Passo 1:** Atendentes `1`. Em *Quantos clientes cabem no sistema?* escolha **Limite de K clientes**.
2. Aparece *O enunciado informa…*. Como o enunciado diz "só 3 cabem esperando", marque
   **"só os lugares de espera, além dos atendentes"** e digite `3`. O programa mostra
   `K = 1 em atendimento + 3 esperando = 4`. (Se o enunciado dissesse "o sistema comporta 4 carros no total",
   você marcaria *o máximo de clientes no sistema (K)* e digitaria `4`.)
3. **Chegada:** "chega 1 cliente a cada…", `4`, minutos. **Atendimento:** "leva…", `3`, minutos.
4. Tempos em **minutos**.

**Resultado:** L = 1,444 · Lq = 0,772 · W = 6,45 min · Wq = 3,45 min.
Na tabela: **probabilidade de bloqueio = 10,37%** (a chance de o pátio estar cheio quando um carro chega) e
**clientes perdidos** por minuto (≈ 1,56 por hora).

> Nos modelos com K o sistema é sempre estável, mesmo se chegar mais gente do que se atende, porque quem encontra
> cheio vai embora.

## 8. Exemplo 4 — Poucos clientes possíveis (população finita, N)

> Uma fábrica tem **10 máquinas**. Cada máquina quebra, em média, a cada 200 horas de funcionamento. Um único
> técnico conserta cada máquina em 10 horas, em média.

Aqui os "clientes" são as máquinas: quando uma está quebrada ela está "no sistema"; quando funciona, está "fora".

1. **Passo 1:** Atendentes `1`. **Só existem N clientes no total** → `N = 10`.
2. **Passo 2 — Com que frequência os clientes voltam?** Aqui o λ é de **CADA** máquina que está funcionando.
   Marque **"cada cliente volta a cada…"**, digite `200` e escolha **horas**.
3. **Passo 3:** "leva…", `10`, **horas**. Tempos em **horas**.

**Resultado:** L = 0,759 máquina quebrada em média · W = 16,43 h (de a máquina quebrar até voltar a funcionar) ·
Wq = 6,43 h esperando o técnico. A tabela mostra ainda **máquinas funcionando em média = 9,24** e que o técnico
fica ocupado 46,2% do tempo (1 − P0).

## 9. Exemplo 5 — O enunciado não dá λ nem μ, mas outras medidas

> Em uma loja, o atendente fica ocupado 80% do tempo e os clientes esperam em média 15 minutos na fila.
> Qual a taxa de chegada e a de atendimento?

1. **Passo 1:** Atendentes `1`, sem limite.
2. **Passo 2 — O que o enunciado informa?** Marque **"Outras medidas: ρ, L, Lq, W, Wq, P0…"**.
3. **Passo 3 — Quais medidas o enunciado dá?** Na primeira linha deixe **taxa de ocupação (ρ)** e digite `0,8`
   (digitar `80` também vale: o programa entende como 80%). Na segunda, **tempo médio na fila (Wq)**, `15`, **minutos**.
4. O programa descobre: **λ = 12,8 por hora e μ = 16 por hora**, e já mostra o resultado completo (L = 4, Lq = 3,2,
   W = 18,75 min…).

Você pode informar **quaisquer duas** entre ρ, L, Lq, P0, W, Wq, λ e μ. Duas medidas que só dependem de ρ
(por exemplo ρ e L) **não bastam**: falta uma que tenha tempo ou taxa. O programa avisa.

## 10. Exemplo 6 — Probabilidades ("qual a chance de…?")

Use o Exemplo 1 (barbearia). Na parte de baixo do resultado há **Consultas de probabilidade**. Cada linha é uma
pergunta: **variável + comparação + valor**.

| Pergunta | Como montar a linha | Resultado |
|---|---|---|
| "Qual a chance de haver **mais de 2** clientes?" | `Clientes no sistema (n)` · `>` · `2` | 42,19% |
| "Qual a chance de esperar **mais de 1 hora** na fila?" | `Tempo na fila (Wq)` · `>` · `1` · **horas** | 27,59% |
| "Qual a chance de **não** precisar esperar?" | `Tempo na fila (Wq)` · `= 0 (não espera)` | 25% |
| "**95%** dos clientes esperam **até** quanto?" | `Percentil de Wq` · `95` | 2,71 h |

Clique em **+ Adicionar consulta** para criar mais linhas. Atenção às unidades do tempo: o campo de unidade de cada
linha começa em *minutos*.

## 11. Exemplo 7 — "Quantos atendentes preciso?"

> Chegam 3 clientes por minuto e cada atendente atende 1 por minuto. Quantos atendentes são necessários para que a
> espera média na fila seja de, no máximo, 30 segundos?

Aba **Dimensionar** → **Quantos atendentes preciso?**

1. Preencha a ficha: λ = `3` **por minuto**, μ = `1` **por minuto**, tempos em **minutos**. (Aqui não se pergunta
   o nº de atendentes: é isso que o programa vai descobrir.)
2. **Passo 4 — Quais são os critérios?** Medida: **tempo médio na fila (Wq)**, `deve ser ≤` `0,5` **minutos**.

**Resposta:** **5 atendentes**. A tabela mostra que com 4 a espera seria de 30,6 s (quase, mas não cumpre) e com 5 cai
para 7,1 s. Use **+ Critério** para exigir várias condições ao mesmo tempo.

Outras ferramentas da aba **Dimensionar**:
- **Comparar nº de atendentes (e custos):** mostra os resultados de 1, 2, 3… atendentes e, se você informar os custos,
  qual número sai mais barato.
- **Qual λ ou μ atinge uma meta?:** por exemplo, "que taxa de atendimento faz o cliente ficar só 2 minutos no sistema?".

## 12. Quando o atendimento não é "exponencial" (M/G/1) e quando há classes (prioridades)

Os exemplos acima supõem que os tempos de atendimento variam de forma aleatória "normal" (exponencial). Se o enunciado
disser que o atendimento é **constante** ("sempre exatamente 90 segundos"), ou der o **desvio padrão** do tempo de
atendimento, use *Tipo de sistema* → **M/G/1**:

1. Preencha λ e a média do atendimento (como no Exemplo 1).
2. Em *Quanto o tempo de atendimento varia?* escolha **Constante**, **Erlang**, ou **Conheço o desvio padrão σ**.
   Quanto mais o tempo varia, maior a fila; por isso o atendimento constante dá **metade** da fila do exponencial.

Se os clientes têm **classes de prioridade** (emergência, urgente, normal), use **Com prioridades**: informe quantas
classes, λ de cada uma (ou o λ total e a porcentagem de cada classe) e μ. Marque *com interrupção* se a chegada de um
cliente mais importante tira o atendimento do menos importante, e *sem interrupção* se o atendimento em curso termina.
A tabela mostra os tempos de cada classe e compara as três disciplinas.

---

## 13. Como saber se o resultado faz sentido

- **L = λ × W** e **Lq = λ × Wq** (com λ e os tempos na mesma unidade). No Exemplo 1: 3 por hora × 1 hora = 3 ✔.
- **W é sempre maior que Wq**, e a diferença é o tempo de atendimento (1/μ). Exemplo 1: 60 − 45 = 15 min ✔.
- **ρ precisa ser menor que 100%** nos modelos sem limite. Se aparecer "Fila instável", chega mais gente do que se atende.
- Se você **aumenta o número de atendentes**, a espera cai, com ganhos cada vez menores a cada atendente a mais (no Exemplo 7: 30,6 s com 4 atendentes, 7,1 s com 5 e 2,0 s com 6).

## 14. Erros comuns

| O que aconteceu | Causa provável |
|---|---|
| "Fila instável" | λ maior ou igual ao total que os atendentes conseguem atender. Confira se não trocou tempo por taxa (20 min não é 20 por hora). |
| Resultados absurdos (milhares de horas) | Unidade errada. Confira as unidades de λ e μ e de *Mostrar os tempos em*. |
| Tempos de espera minúsculos ou enormes nas consultas | A unidade do campo de tempo da consulta é independente: confira se está em minutos ou horas. |
| Em população finita, o resultado não parece certo | λ é o de **cada** cliente fora do sistema (1 a cada 200 h por máquina), não o total. |
| Com limite, o K não bate com o gabarito | Verifique se o enunciado fala do **total** (K) ou só dos **lugares de espera** (K = atendentes + lugares). |
| Mais de uma solução em "outras medidas" | Raro. O programa usa a primeira e avisa. |

## 15. Onde clicar para cada tipo de pergunta

| O enunciado pede… | Vá em |
|---|---|
| Médias (L, Lq, W, Wq, ocupação) | **Calculadora** |
| Uma **probabilidade** ("qual a chance de…") | **Calculadora** → *Consultas de probabilidade* |
| **Quantos atendentes** ou comparar custos | **Dimensionar** |
| **Que taxa** (λ ou μ) é necessária para atingir uma meta | **Dimensionar** → *Qual λ ou μ atinge uma meta?* |
| λ e μ a partir de dados observados | **Ferramentas** → *Calcular λ e μ a partir de dados* |
| "Em 1 hora chegam em média 12 clientes; qual a chance de chegarem 10?" | **Ferramentas** → *Contagens de Poisson* |
| Uma espera **observada** ("os clientes esperam 1 min") e quer as outras medidas | **Ferramentas** → *Lei de Little* |
| Entender uma fórmula, uma sigla ou um enunciado | **Teoria** |

Quando travar, a aba **Teoria** tem as fórmulas de cada modelo, um glossário e a tabela *Como ler um enunciado*.