"""
Conteúdo de apoio exibido na aba "Teoria": fórmulas de cada modelo, glossário e guia de leitura de enunciados.
As fórmulas seguem o material da disciplina (Hillier & Lieberman) e estão em LaTeX para o st.latex.
"""

# Cada modelo: id, título, quando usar, pressupostos, fórmulas [(rótulo, latex)], dica
MODELOS = [
    dict(
        id="mm1", familia="M/M/1", titulo="M/M/1 — um atendente, fila sem limite",
        quando="Um único atendente, a fila pode crescer à vontade e o tempo de atendimento é exponencial "
               "(\"em média 15 minutos\", sem outra informação).",
        pressupostos=["Chegadas de Poisson (taxa λ)", "Atendimento exponencial (taxa μ)", "Disciplina FIFO",
                      "Estável somente se ρ = λ/μ < 1"],
        formulas=[
            ("Taxa de ocupação", r"\rho = \lambda/\mu"),
            ("Sistema vazio", r"P_0 = 1-\rho"),
            ("n clientes no sistema", r"P_n = (1-\rho)\,\rho^n \qquad P(n>r)=\rho^{\,r+1}"),
            ("Clientes no sistema / na fila", r"L = \dfrac{\lambda}{\mu-\lambda} \qquad L_q = \dfrac{\lambda^2}{\mu(\mu-\lambda)}"),
            ("Tempo no sistema / na fila", r"W = \dfrac{1}{\mu-\lambda} \qquad W_q = \dfrac{\lambda}{\mu(\mu-\lambda)}"),
            ("Distribuição dos tempos", r"P(W>t)=e^{-\mu(1-\rho)t} \qquad P(W_q>t)=\rho\,e^{-\mu(1-\rho)t}"),
        ],
        dica="Se o enunciado dá ρ e um tempo (ex.: ρ = 0,8 e Wq = 15 min), use a opção "
             "\"o enunciado dá outras medidas\" na calculadora para descobrir λ e μ.",
    ),
    dict(
        id="mms", familia="M/M/s", titulo="M/M/s — vários atendentes, fila única, sem limite",
        quando="Dois ou mais atendentes iguais atendendo uma fila única (\"dois caixas, uma fila só\"). "
               "Se cada atendente tiver sua própria fila, são vários M/M/1 separados, cada um com λ/s.",
        pressupostos=["Todos os atendentes têm a mesma taxa μ", "Estável somente se ρ = λ/(sμ) < 1"],
        formulas=[
            ("Taxa de ocupação", r"\rho = \dfrac{\lambda}{s\mu}"),
            ("Sistema vazio", r"P_0=\left[\sum_{n=0}^{s-1}\dfrac{(\lambda/\mu)^n}{n!}+\dfrac{(\lambda/\mu)^s}{s!\,(1-\rho)}\right]^{-1}"),
            ("n clientes no sistema", r"P_n=\dfrac{(\lambda/\mu)^n}{n!}P_0\ (n\le s) \qquad P_n=\dfrac{(\lambda/\mu)^n}{s!\,s^{\,n-s}}P_0\ (n\ge s)"),
            ("Fila e sistema", r"L_q=\dfrac{P_0(\lambda/\mu)^s\rho}{s!\,(1-\rho)^2} \qquad L=L_q+\dfrac{\lambda}{\mu}"),
            ("Tempos", r"W_q=\dfrac{L_q}{\lambda} \qquad W=W_q+\dfrac{1}{\mu}"),
            ("Chance de esperar (Erlang C)", r"P(W_q>0)=\dfrac{P_s}{1-\rho}"),
            ("Distribuição dos tempos", r"P(W_q>t)=P(W_q>0)\,e^{-s\mu(1-\rho)t}"),
            ("", r"P(W>t)=e^{-\mu t}\left[1+\dfrac{P_0(\lambda/\mu)^s}{s!(1-\rho)}\cdot\dfrac{1-e^{-\mu t(s-1-\lambda/\mu)}}{s-1-\lambda/\mu}\right]"),
        ],
        dica="Quando quiser saber quantos atendentes são necessários, use Dimensionar → Quantos atendentes preciso?",
    ),
    dict(
        id="mm1k", familia="M/M/1/K", titulo="M/M/1/K — um atendente, capacidade máxima K",
        quando="O sistema comporta no máximo K clientes (quem está sendo atendido + a fila). Quem chega com o sistema cheio é "
               "perdido. \"Apenas 3 podem esperar\" com 1 atendente significa K = 1 + 3 = 4.",
        pressupostos=["K inclui quem está em atendimento", "Sempre estável (mesmo com λ > μ)"],
        formulas=[
            ("Sistema vazio", r"P_0=\dfrac{1-\rho}{1-\rho^{K+1}}\qquad \rho=\lambda/\mu"),
            ("n clientes", r"P_n=\dfrac{1-\rho}{1-\rho^{K+1}}\,\rho^n \quad (n=0,\dots,K)"),
            ("Bloqueio e λ efetivo", r"P_K=\text{prob. de o sistema estar cheio}\qquad \bar\lambda=\lambda(1-P_K)"),
            ("Clientes", r"L=\dfrac{\rho}{1-\rho}-\dfrac{(K+1)\rho^{K+1}}{1-\rho^{K+1}} \qquad L_q = L-(1-P_0)"),
            ("Tempos (Little com λ efetivo)", r"W=\dfrac{L}{\bar\lambda} \qquad W_q=\dfrac{L_q}{\bar\lambda}"),
        ],
        dica="Clientes perdidos por unidade de tempo = λ·P_K. A calculadora mostra esse valor.",
    ),
    dict(
        id="mmsk", familia="M/M/s/K", titulo="M/M/s/K — vários atendentes, capacidade máxima K",
        quando="Igual ao anterior com s atendentes. K ≥ s. Ex.: estação com 3 boxes e 4 vagas de espera → K = 7.",
        pressupostos=["K inclui os s em atendimento", "Sempre estável"],
        formulas=[
            ("Sistema vazio", r"P_0=\left[\sum_{n=0}^{s}\dfrac{(\lambda/\mu)^n}{n!}+\dfrac{(\lambda/\mu)^s}{s!}\sum_{n=s+1}^{K}\rho^{\,n-s}\right]^{-1}\qquad \rho=\dfrac{\lambda}{s\mu}"),
            ("n clientes", r"P_n=\dfrac{(\lambda/\mu)^n}{n!}P_0\ (n\le s)\qquad P_n=\dfrac{(\lambda/\mu)^n}{s!\,s^{\,n-s}}P_0\ (s\le n\le K)"),
            ("Fila", r"L_q=\dfrac{P_0(\lambda/\mu)^s\rho}{s!(1-\rho)^2}\left[1-\rho^{K-s}-(K-s)\rho^{K-s}(1-\rho)\right]"),
            ("Sistema", r"L=\sum_{n=0}^{s-1}nP_n+L_q+s\left(1-\sum_{n=0}^{s-1}P_n\right)"),
            ("Tempos", r"\bar\lambda=\lambda(1-P_K)\qquad W=\dfrac{L}{\bar\lambda}\qquad W_q=\dfrac{L_q}{\bar\lambda}"),
        ],
        dica="Os tempos de espera P(W>t) e P(Wq>t) também são calculados para os modelos com K e N.",
    ),
    dict(
        id="mm1n", familia="M/M/1/N", titulo="M/M/1/N — um atendente, população finita de N clientes",
        quando="Há só N clientes possíveis (ex.: 10 máquinas que quebram e voltam). Cada cliente que está FORA do sistema "
               "volta com taxa λ; por isso a taxa total de chegada diminui quando há gente no sistema.",
        pressupostos=["λ é a taxa de CADA cliente fora do sistema (1/tempo médio entre quebras)", "Sempre estável"],
        formulas=[
            ("Sistema vazio", r"P_0=\left[\sum_{n=0}^{N}\dfrac{N!}{(N-n)!}\left(\dfrac{\lambda}{\mu}\right)^n\right]^{-1}"),
            ("n clientes", r"P_n=\dfrac{N!}{(N-n)!}\left(\dfrac{\lambda}{\mu}\right)^nP_0"),
            ("Clientes", r"L=N-\dfrac{\mu}{\lambda}(1-P_0)\qquad L_q=N-\dfrac{\lambda+\mu}{\lambda}(1-P_0)"),
            ("λ efetivo e tempos", r"\bar\lambda=\lambda(N-L)\qquad W=\dfrac{L}{\bar\lambda}\qquad W_q=\dfrac{L_q}{\bar\lambda}"),
            ("Em operação", r"\text{máquinas operando}=N-L \qquad \text{fração do tempo de cada uma}=1-\dfrac{L}{N}"),
        ],
        dica="Atenção: a fração de tempo em que o atendente está ocupado é 1 − P0, não N·λ/μ (que é só a carga nominal).",
    ),
    dict(
        id="mmsn", familia="M/M/s/N", titulo="M/M/s/N — vários atendentes, população finita de N clientes",
        quando="Como o anterior, com s atendentes (ex.: 2 técnicos para 5 robôs).",
        pressupostos=["λ é a taxa de cada cliente fora do sistema"],
        formulas=[
            ("Sistema vazio", r"P_0=\left[\sum_{n=0}^{s-1}\dfrac{N!}{(N-n)!\,n!}\left(\dfrac{\lambda}{\mu}\right)^n+\sum_{n=s}^{N}\dfrac{N!}{(N-n)!\,s!\,s^{\,n-s}}\left(\dfrac{\lambda}{\mu}\right)^n\right]^{-1}"),
            ("n clientes", r"P_n=\dfrac{N!}{(N-n)!\,n!}\left(\dfrac{\lambda}{\mu}\right)^nP_0\ (n\le s)\qquad P_n=\dfrac{N!}{(N-n)!\,s!\,s^{\,n-s}}\left(\dfrac{\lambda}{\mu}\right)^nP_0\ (s\le n\le N)"),
            ("Clientes", r"L=\sum_{n=0}^{N}nP_n\qquad L_q=L-\dfrac{\lambda}{\mu}(N-L)"),
            ("Tempos", r"\bar\lambda=\lambda(N-L)\qquad W=\dfrac{L}{\bar\lambda}\qquad W_q=\dfrac{L_q}{\bar\lambda}"),
        ],
        dica="Para comparar 1 técnico com 2 (e o custo), use Dimensionar → Comparar nº de atendentes.",
    ),
    dict(
        id="mg1", familia="M/G/1", titulo="M/G/1 — um atendente, atendimento com distribuição qualquer",
        quando="Um atendente e o tempo de atendimento NÃO é exponencial (constante, Erlang, ou só se conhece a média e o "
               "desvio padrão). Só é preciso saber a média 1/μ e o desvio padrão σ.",
        pressupostos=["Chegadas de Poisson", "Estável somente se ρ = λ/μ < 1", "Só as médias são calculadas (não há P(n) nem P(W>t))"],
        formulas=[
            ("Pollaczek-Khintchine", r"L_q=\dfrac{\lambda^2\sigma^2+\rho^2}{2(1-\rho)}\qquad \rho=\lambda/\mu"),
            ("Demais medidas", r"W_q=\dfrac{L_q}{\lambda}\qquad W=W_q+\dfrac{1}{\mu}\qquad L=\rho+L_q\qquad P_0=1-\rho"),
            ("Casos especiais de σ", r"\text{exponencial: }\sigma=\tfrac1\mu\qquad \text{constante (M/D/1): }\sigma=0\qquad \text{Erlang-}k:\ \sigma=\dfrac{1}{\mu\sqrt{k}}"),
            ("Efeito da variabilidade", r"L_q^{\,M/D/1}=\tfrac12\,L_q^{\,M/M/1}"),
        ],
        dica="Reduzir a variabilidade do atendimento (σ menor) reduz bastante a fila, mesmo sem mudar a média.",
    ),
    dict(
        id="prio", familia="Prioridades", titulo="Filas com prioridades (classes de clientes)",
        quando="Os clientes têm classes (crítico, grave, estável; 1ª classe e econômica…) e as de maior prioridade passam à frente. "
               "Classe 1 = maior prioridade.",
        pressupostos=["Chegadas de Poisson em cada classe", "Atendimento exponencial com a MESMA taxa μ em todas as classes (M/M/s)",
                      "Ou, com 1 atendente, média e desvio próprios por classe (M/G/1 sem interrupção)",
                      "λ total < s·μ"],
        formulas=[
            ("Sem interrupção (termina o atendimento em curso)", r"W_k=\dfrac{1}{A\,B_{k-1}B_k}+\dfrac1\mu\qquad A=\dfrac{s!\,(s\mu-\lambda)}{r^s}\sum_{j=0}^{s-1}\dfrac{r^j}{j!}+s\mu"),
            ("", r"B_k=1-\dfrac{\sum_{i\le k}\lambda_i}{s\mu}\quad (B_0=1)\qquad r=\lambda/\mu\quad \lambda=\sum_i\lambda_i"),
            ("Com interrupção (s = 1)", r"W_k=\dfrac{1/\mu}{B_{k-1}\,B_k}"),
            ("Com interrupção (qualquer s)", r"L_{1..k}=L_{M/M/s}(\lambda_1+\dots+\lambda_k)\qquad W_k=\dfrac{L_{1..k}-L_{1..k-1}}{\lambda_k}"),
            ("Demais medidas", r"L_k=\lambda_kW_k\qquad W_{q,k}=W_k-\dfrac1\mu\qquad L_{q,k}=L_k-\dfrac{\lambda_k}{\mu}"),
            ("M/G/1 sem interrupção (Cobham)", r"W_{q,k}=\dfrac{\sum_i\lambda_i\,E[S_i^2]/2}{(1-\sigma_{k-1})(1-\sigma_k)}\qquad \sigma_k=\sum_{i\le k}\lambda_iE[S_i]\qquad E[S_i^2]=\mathrm{Var}(S_i)+E[S_i]^2"),
        ],
        dica="A média ponderada dos tempos de todas as classes é igual à de uma fila FIFO: a prioridade só redistribui a espera.",
    ),
]

RELACOES = [
    ("Lei de Little", r"L=\lambda W\qquad L_q=\lambda W_q"),
    ("Tempo de serviço", r"W=W_q+\dfrac1\mu\qquad L=L_q+\dfrac\lambda\mu"),
    ("Modelos com perda ou população finita", r"\text{use }\bar\lambda\ \text{no lugar de }\lambda"),
    ("Poisson (nº de eventos em um intervalo)", r"P(X=k)=\dfrac{e^{-m}m^k}{k!}\qquad m=\text{taxa}\times\text{tempo}"),
    ("Exponencial (tempo entre eventos)", r"P(T>t)=e^{-\lambda t}\qquad E[T]=\dfrac1\lambda"),
]

KENDALL = (
    "A/B/m/C/K/N — **A**: distribuição das chegadas · **B**: distribuição do atendimento · **m**: nº de atendentes · "
    "**C**: disciplina (FCFS, LCFS, SIRO…) · **K**: capacidade do sistema · **N**: tamanho da população. "
    "Letras: **M** exponencial (Poisson), **D** constante, **Ek** Erlang, **G** qualquer. "
    "Campos omitidos valem FCFS, K = ∞ e N = ∞."
)

GLOSSARIO = [
    ("λ (lambda)", "Taxa de chegada: clientes que chegam por unidade de tempo. É o inverso do tempo médio entre chegadas."),
    ("μ (mi)", "Taxa de atendimento de UM atendente: clientes atendidos por unidade de tempo. É o inverso do tempo médio de atendimento."),
    ("s", "Número de atendentes (canais, caixas, pistas) trabalhando em paralelo sobre a mesma fila."),
    ("ρ (rô)", "Taxa de ocupação: fração do tempo em que cada atendente está ocupado. Nos modelos sem limite, ρ = λ/(s·μ) e precisa ser menor que 1."),
    ("L e Lq", "Número médio de clientes no sistema (fila + atendimento) e só na fila."),
    ("W e Wq", "Tempo médio que um cliente passa no sistema (fila + atendimento) e só esperando na fila."),
    ("Pn", "Probabilidade de haver exatamente n clientes no sistema, em regime estável."),
    ("P0", "Probabilidade de o sistema estar vazio."),
    ("K", "Capacidade máxima do sistema, contando quem está sendo atendido. Quem chega com o sistema cheio é perdido (bloqueado)."),
    ("N", "Tamanho da população finita. Cada cliente fora do sistema volta com taxa λ."),
    ("λef (λ efetivo)", "Taxa de clientes que realmente entram: λ·(1 − P_K) nos modelos com K; λ·(N − L) nos modelos com N."),
    ("Bloqueio (P_K)", "Probabilidade de um cliente chegar e encontrar o sistema cheio."),
    ("σ", "Desvio padrão do tempo de atendimento (M/G/1). Mede a variabilidade; σ = 0 é atendimento constante."),
    ("Regime estável", "Situação em que a fila não cresce sem limite. Nos modelos sem K ou N exige λ < s·μ."),
    ("FCFS / FIFO", "O primeiro a chegar é o primeiro a ser atendido."),
    ("Com / sem interrupção", "Em prioridades: com interrupção, a chegada de uma classe maior tira o atendimento da menor; sem interrupção, o atendimento em curso termina."),
    ("Percentil", "Valor abaixo do qual fica uma certa fração dos casos. \"95% esperam até 3 min\" é o percentil 95 do tempo de espera."),
]

# (o que o enunciado diz, o que significa para o modelo)
COMO_LER = [
    ("\"chegam segundo Poisson\", \"aleatoriamente\"", "Chegadas exponenciais: o primeiro M do modelo."),
    ("\"tempo de atendimento exponencial com média de 15 min\"", "O segundo M, com μ = 1/15 por minuto = 4 por hora."),
    ("\"tempo de atendimento constante / exatamente 90 s\"", "Atendimento determinístico: M/D/1 (M/G/1 com σ = 0)."),
    ("\"apenas um canal / um caixa / uma pista\"", "s = 1."),
    ("\"dois caixas e uma fila única\"", "s = 2 (M/M/s). Se houver filas separadas, são dois M/M/1 com λ/2 cada."),
    ("\"o sistema comporta no máximo 5 clientes\"", "K = 5 (conta quem está sendo atendido)."),
    ("\"apenas 3 podem esperar\" (com 1 atendente)", "K = 1 + 3 = 4. Na calculadora, escolha informar \"só os lugares de espera\"."),
    ("\"o pátio comporta 3 caminhões\"", "Em geral são os lugares de ESPERA; confira se o enunciado inclui quem descarrega."),
    ("\"3 máquinas (N = 10)\", \"o tempo entre quebras é de 200 h\"", "População finita: N = 10 e λ = 1/200 por hora, POR máquina."),
    ("\"taxa de ocupação de 75%\"", "ρ = 0,75. Com mais uma medida (λ, μ, Wq…), a opção \"outras medidas\" descobre λ e μ."),
    ("\"os clientes esperam em média 1 min na fila\" (valor observado)", "Wq = 1 min. Use a aba Ferramentas → Lei de Little para obter Lq, L e W sem supor modelo."),
    ("\"clientes de primeira classe passam na frente\"", "Prioridades. \"Sem interrupção\" se o atendimento em curso termina."),
    ("\"10 chegadas por hora\" como probabilidade", "É uma contagem de Poisson, não uma medida da fila: Ferramentas → Contagens de Poisson."),
    ("\"no máximo 4 na fila\" / \"nunca mais que 4 no sistema\"", "Confira: nq ≤ 4 é n ≤ s + 4. Na calculadora, escolha Clientes na fila (nq) ou no sistema (n)."),
]
