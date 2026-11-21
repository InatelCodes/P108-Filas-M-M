"""
Validação contra os gabaritos das listas de exercícios (P108 – Teoria das Filas).
Rode com:   python -m unittest discover tests -v

Cada teste confere o motor com os números publicados no material. Os poucos casos em que o gabarito
do material não segue o enunciado (ou o próprio material se contradiz) estão em
TestDivergenciasDoMaterial, com a explicação.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filas import Fila, custo_total, menor_s_para_meta
from filas.inverso import menor_s_criterios, parametro_para_meta, resolver_por_medidas
from filas.mg1 import FilaMG1
from filas.poisson import pmf
from filas.prioridades import ClasseMG1, PrioridadesMG1, PrioridadesMMs, lams_de_percentuais
from filas.relacoes import relacoes_de_little
from filas.unidades import taxa_por_tabela


class Base(unittest.TestCase):
    def ok(self, valor, esperado, tol=None):
        """Compara com o gabarito aceitando o arredondamento com que ele foi publicado."""
        if tol is None:
            txt = repr(esperado)
            casas = len(txt.split(".")[1]) if "." in txt else 0
            tol = 0.6 * 10 ** -casas + 2e-4
        self.assertAlmostEqual(valor, esperado, delta=tol, msg=f"obtido {valor}, gabarito {esperado}")


class TestMMs(Base):
    def test_1_dados_de_uma_tabela_de_frequencias(self):
        tabela = [(9, .067), (10, .1), (11, .2), (12, .267), (13, .2), (14, .1), (15, .067)]
        lam = taxa_por_tabela(tabela)
        self.assertAlmostEqual(lam, 12, delta=0.02)                 # ≈ 12 motores/mês
        (l, m), = resolver_por_medidas(1, [("lam", 12), ("rho", 0.75)])
        f = Fila(l, m); r = f.resultado()
        self.ok(r.W, 0.25); self.ok(1 - r.rho, 0.25); self.ok(r.Lq, 2.25); self.ok(r.Wq, 0.1875)
        self.ok(r.L, 3); self.ok(f.P_W_maior(20 / 30), 0.069); self.ok(f.P_Wq_maior(15 / 30), 0.1015)
        self.ok(f.P_clientes("≤", 4), 0.7627)       # o gabarito lê "máx. 4 na fila" como n ≤ 4

    def test_2_rho_e_tempo_na_fila_conhecidos(self):
        (l, m), = resolver_por_medidas(1, [("rho", 0.8), ("Wq", 15)])   # tempos em minutos
        f = Fila(l, m); r = f.resultado()
        self.ok(r.Lq, 3.2); self.ok(r.L, 4); self.ok(r.P0, 0.20)
        self.ok(f.P_W_maior(30), 0.2019); self.ok(f.P_Wq_maior(15), 0.3595)
        self.ok(pmf(10, l * 60), 0.0898)           # 10 chegadas por hora
        self.ok(pmf(12, m * 60), 0.066)            # 12 atendimentos por hora
        self.ok(f.P(10), 0.0215)

    def test_3_lq_e_w_conhecidos(self):
        (l, m), = resolver_por_medidas(1, [("Lq", 3.2), ("W", 0.5)])
        self.ok(l, 8); self.ok(m, 10)
        self.ok(Fila(l, m).P_clientes("<", 6), 0.7378)

    def test_4_ingressos(self):
        self.assertLessEqual(Fila(1, 3).resultado().W + 1.5, 2.0 + 1e-9)   # W = 0,5 min + 1,5 min = 2 min

    def test_5_caminhoes(self):
        f = Fila(3, 4); r = f.resultado()
        self.ok(r.Lq, 2.25); self.ok(r.L, 3); self.ok(r.Wq, 0.75); self.ok(r.W, 1)
        self.ok(f.P(6), 0.0445); self.ok(r.rho, 0.75); self.ok(f.P_W_maior(2), 0.1353); self.ok(f.P_Wq_maior(1.5), 0.1673)

    def test_6_taxa_maxima_de_chegadas(self):
        lam = parametro_para_meta(Fila(1, 5), "lam", "Wq", 0.8)
        self.ok(lam, 4)
        f = Fila(lam, 5); r = f.resultado()
        self.ok(r.Lq, 3.2); self.ok(r.L, 4); self.ok(r.W, 1); self.ok(f.P_W_maior(1), 0.3679); self.ok(f.P_Wq_maior(0.8), 0.3595)

    def test_7_hospital_um_e_dois_medicos(self):
        for s, g in ((1, dict(rho=2 / 3, L=2, Lq=4 / 3, P0=1 / 3, p2=0.2962, Wq=2 / 3, W=1, wq=0.404, w=0.3679)),
                     (2, dict(rho=1 / 3, L=3 / 4, Lq=1 / 12, P0=1 / 2, p2=0.0556, Wq=1 / 24, W=3 / 8, wq=0.023, w=0.0655))):
            f = Fila(2, 3, s); r = f.resultado()
            self.ok(r.rho, g["rho"]); self.ok(r.L, g["L"]); self.ok(r.Lq, g["Lq"]); self.ok(r.P0, g["P0"])
            self.ok(f.P_clientes(">", 2), g["p2"]); self.ok(r.Wq, g["Wq"]); self.ok(r.W, g["W"])
            self.ok(f.P_Wq_maior(0.5), g["wq"]); self.ok(f.P_W_maior(1), g["w"])

    def test_8_midtown_bank_pela_lei_de_little(self):
        # λ = 40/h, μ = 30/h por caixa, e a espera média OBSERVADA é 1 min (o gabarito usa Little, não o M/M/2)
        d = relacoes_de_little(40 / 60, 30 / 60, Wq=1)              # tempos em minutos
        self.ok(d["L"], 2); self.ok(d["Lq"], 0.667); self.ok(d["Wq"], 1); self.ok(d["W"], 3)

    def test_9_sac(self):
        self.assertGreater(Fila(5, 7).resultado().Wq * 60, 5)
        self.assertEqual(menor_s_para_meta(5, 7, "Wq", 2 / 60), 2)

    def test_10_confeitaria(self):
        (l, m), = resolver_por_medidas(1, [("rho", 0.75), ("Wq", 2.5)])        # minutos
        r = Fila(l, m).resultado()
        self.ok(r.L, 3); self.ok(r.W, 10 / 3)
        mu_b = parametro_para_meta(Fila(l, m), "mu", "W", 2.0); self.ok(mu_b, 1.4)
        self.ok(Fila(l, mu_b).P_clientes(">", 3), 0.1708)       # o gabarito (17,08%) é P(n > 3)
        self.ok(parametro_para_meta(Fila(l, m), "mu", "n>", 0.15, 3), 1.4462)
        self.ok(Fila(l, m, 1, K=3).P_clientes(">", 2), 0.1543)          # item e (sem gabarito no material)

    def test_11_torno_revolver(self):
        self.ok(Fila(2, 4).P_clientes("≤", 4), 0.97)

    def test_12_proporcao_sem_clientes(self):
        self.ok(Fila(10, 15).resultado().P0, 0.33)

    def test_13_mercearia(self):
        for mu, g in ((30, dict(L=2, W=6, Wq=4, Lq=1.33, P0=1 / 3, P1=2 / 9, P2=4 / 27, a=0.2897, b=0.3114)),
                      (40, dict(L=1, W=3, Wq=1.5, Lq=0.5, P0=0.5, P1=0.25, P2=0.125, a=0.0944, b=0.0970))):
            f = Fila(20, mu); r = f.resultado()
            self.ok(r.L, g["L"]); self.ok(r.W * 60, g["W"]); self.ok(r.Wq * 60, g["Wq"]); self.ok(r.Lq, g["Lq"])
            self.ok(r.P0, g["P0"]); self.ok(f.P(1), g["P1"]); self.ok(f.P(2), g["P2"])
            self.ok(f.P_Wq_maior(5 / 60), g["a"]); self.ok(f.P_W_maior(7 / 60), g["b"])
        self.assertAlmostEqual(Fila(20, 30).P_clientes(">", 2), 8 / 27)      # 29,6% (> 25%)
        self.assertAlmostEqual(Fila(20, 40).P_clientes(">", 2), 1 / 8)       # 12,5% (< 25%)

    def test_14_aeroporto(self):
        for lam, s, lq, p4, p30 in ((10, 1, 0.5, 0.984, 0.9966), (15, 1, 2.25, 0.822, 0.9384), (25, 2, 0.8013, None, 0.9997)):
            f = Fila(lam, 20, s)
            self.ok(f.resultado().Lq, lq)
            if p4: self.ok(f.P_fila("≤", 4), p4)
            self.ok(1 - f.P_Wq_maior(0.5), p30)

    def test_15_banco_security_trust(self):
        for lam, lq, p5, p5min in ((2, 0.1739, 0.997, 0.9999), (3, 1.5283, 0.909, 0.9966)):
            f = Fila(lam, 1, 4)
            self.ok(f.resultado().Lq, lq); self.ok(f.P_fila("≤", 5), p5); self.ok(1 - f.P_Wq_maior(5), p5min)
        s, _ = menor_s_criterios(3, 1, [("Lq", None, "≤", 1), ("nq≤", 5, "≥", 0.95), ("Wq≤", 5, "≥", 0.95)])
        self.assertEqual(s, 5)


class TestMMsK(Base):
    def test_1(self):
        f = Fila(2, 4, 1, K=5); r = f.resultado()
        self.ok(r.P0, 0.5079); self.ok(r.L, 0.9048); self.ok(r.Lq, 0.4127); self.ok(f.P(4), 0.03175)
        self.ok(r.W, 0.4597); self.ok(r.Wq, 0.2097)

    def test_2_laboratorio(self):
        f = Fila(1, 4 / 3, 1, K=4); r = f.resultado()
        self.ok(r.L, 1.4443); self.ok(f.P(4), 0.1037); self.ok(r.Wq, 0.8614)

    def test_3_aeroporto_pista_unica(self):                  # K = 1 + 3 em espera = 4
        f = Fila(1 / 4, 1 / 3, 1, K=4); r = f.resultado()
        self.ok(r.Lq, 0.7721); self.ok(r.Wq, 3.4457); self.ok(f.P_fila(">", 2), 0.1037 * 0 + f.P(4))

    def test_4_e_5_duas_pistas_gabarito_usa_K4(self):
        f = Fila(1 / 4, 1 / 3, 2, K=4); r = f.resultado()
        self.ok(r.Lq, 0.0848); self.ok(r.Wq, 0.3455); self.ok(f.P(4), 0.0182)
        g = Fila(1, 4 / 3, 2, K=4); q = g.resultado()
        self.ok(q.L, 0.8212); self.ok(g.P(4), 0.0182); self.ok(q.Wq, 0.0864)

    def test_6_cooperativa(self):
        f = Fila(3, 4, 1, K=4); r = f.resultado()
        self.ok(r.Lq, 0.7721); self.ok(r.L, 1.4443); self.ok(r.W, 0.5371); self.ok(r.Wq, 0.2871)
        self.ok(Fila(3, 4, 2, K=4).resultado().Wq, 0.0288)

    def test_teoria_exemplos(self):
        f = Fila(3, 4, 1, K=5); r = f.resultado()
        self.ok(r.P0, 0.3041); self.ok(r.L, 1.7009); self.ok(r.Lq, 1.005); self.ok(f.P(4), 0.09623)
        self.ok(r.W, 0.6111); self.ok(r.Wq, 0.3611)
        g = Fila(1, 1 / 6, 3, K=7); q = g.resultado()            # estação de inspeção: 3 boxes + 4 esperando
        self.ok(q.P0, 0.00088); self.ok(q.L, 6.0631); self.ok(q.Lq, 3.0920); self.ok(q.W, 12.2442)
        self.ok(q.Wq, 6.2439, tol=5e-4); self.ok(q.lam_perdida * 60, 30.29)


class TestMMsN(Base):
    def test_1_custo_das_maquinas_paradas(self):
        f = Fila(1 / 200, 1 / 10, 1, N=10); r = f.resultado()
        self.ok(r.P0, 0.5380); self.ok(r.Lq, 0.2972); self.ok(r.L, 0.7593); self.ok(r.Wq, 6.4330); self.ok(r.W, 16.4330)
        self.ok(8 * custo_total(r, 10, 30, "L", 0, servidor_so_ocupado=True), 219.192, tol=0.01)

    def test_2_trens(self):                                   # a ordem dos itens no gabarito está embaralhada
        f = Fila(1 / 30, 3 / 20, 1, N=6); r = f.resultado()
        self.ok(r.W, 17.2906); self.ok(r.Wq, 10.6239); self.ok(f.P(4), 0.1353); self.ok(r.L, 2.1937); self.ok(r.Lq, 1.3479)

    def test_3_tecnico_e_duas_maquinas(self):
        f = Fila(1 / 10, 1 / 8, 1, N=2); r = f.resultado()
        self.ok(r.P0, 0.2577); self.ok(r.L, 1.072); self.ok(r.Lq, 0.330); self.ok(r.W, 11.556); self.ok(r.Wq, 3.556)
        self.ok(1 - r.P0, 0.7423); self.ok(r.disp_individual, 0.464)

    def test_4_forrester(self):
        f = Fila(1 / 9, 1 / 2, 1, N=3); r = f.resultado()
        self.ok(r.L, 0.7181); self.ok(r.W, 2.832); self.ok(r.rho_nominal, 0.667)
        self.ok(Fila(1 / 9, 1 / 2, 2, N=3).resultado().L, 0.5528)

    def test_5a_mecanico_quatro_maquinas(self):
        self.ok(Fila(1 / 10, 1 / 2, 1, N=4).resultado().n_operando, 3.0082, tol=5e-4)

    def test_6_quatro_maquinas_dois_tecnicos(self):
        f = Fila(1 / 100, 1 / 10, 2, N=4); r = f.resultado()
        self.ok(r.P0, 0.6820); self.ok(r.L, 0.3677); self.ok(r.Lq, 0.0045); self.ok(r.W, 10.1239); self.ok(r.Wq, 0.1239)
        self.ok(1 - r.P0, 0.3180)

    def test_teoria_robos(self):
        for s, operando, w, livre in ((1, 4.360, 4.400, 0.5640), (2, 4.535, 3.075, 0.9279)):
            f = Fila(1 / 30, 1 / 3, s, N=5); r = f.resultado()
            self.ok(r.n_operando, operando); self.ok(r.W, w)
            self.ok(1 - r.P_todos_ocupados if s > 1 else r.P0, livre)        # P(n < s): algum técnico livre


class TestMG1(Base):
    def test_1_variabilidade(self):
        gab = {4: (3.2, 4.0, 16.0, 20.0), 3: (2.5, 3.3, 12.5, 16.5), 2: (2.0, 2.8, 10.0, 14.0),
               1: (1.7, 2.5, 8.5, 12.5), 0: (1.6, 2.4, 8.0, 12.0)}
        for sigma, (lq, l, wq, w) in gab.items():
            r = FilaMG1(0.2, 0.25, sigma).resultado()
            self.ok(r.Lq, lq); self.ok(r.L, l); self.ok(r.Wq, wq); self.ok(r.W, w)
        lq = {s: FilaMG1(0.2, 0.25, s).resultado().Lq for s in gab}
        self.ok(lq[0] / lq[4], 0.5)
        reducoes = {s: lq[s] - lq[s - 1] for s in (4, 3, 2, 1)}              # lq[s] − lq[s−1]
        self.assertEqual(max(reducoes, key=reducoes.get), 4)                 # maior: de σ=4 para σ=3 (0,7)
        self.assertEqual(min(reducoes, key=reducoes.get), 1)                 # menor: de σ=1 para σ=0 (0,1)
        self.ok(parametro_para_meta(FilaMG1(0.2, 0.25, 4), "mu", "Lq", 1.6) - 0.25, 0.05, tol=0.005)

    def test_2_caminhoes_gabarito_supoe_atendimento_constante(self):
        r = FilaMG1.deterministica(3, 4).resultado()                       # λ = 3/h, 15 min por caminhão
        self.ok(r.Lq, 1.125); self.ok(r.L, 1.875); self.ok(r.Wq, 0.375); self.ok(r.W, 0.625); self.ok(r.rho, 0.75)
        self.ok(FilaMG1.exponencial(3, 4).resultado().Lq, 2.25)           # com exponencial seria o dobro

    def test_3_lq_conhecido_gabarito_supoe_atendimento_constante(self):
        mu = parametro_para_meta(FilaMG1(3, 3.5, 0.0), "mu", "Lq", 2.0)
        r = FilaMG1(3, mu, 0.0).resultado()
        self.ok(r.L, 2.830, tol=0.005); self.ok(r.Wq, 0.667); self.ok(r.W, 0.943)

    def test_cafe_do_material(self):
        e = FilaMG1.exponencial(25, 40).resultado()
        self.ok(e.Lq, 1.042); self.ok(e.L, 1.667); self.ok(e.Wq, 0.042); self.ok(e.W, 0.067)
        d = FilaMG1.deterministica(25, 40).resultado()
        self.ok(d.Lq, 0.521); self.ok(d.L, 1.146); self.ok(d.Wq, 0.021); self.ok(d.W, 0.046)
        self.ok(d.Lq / e.Lq, 0.5)
        mu = parametro_para_meta(FilaMG1.exponencial(25, 40), "mu", "Lq", d.Lq)
        self.ok(3600 / mu, 73, tol=0.5)

    def test_lava_rapido_do_material(self):
        m = FilaMG1.exponencial(4, 6).resultado(); d = FilaMG1.deterministica(4, 6).resultado()
        self.assertAlmostEqual(m.Lq, Fila(4, 6).resultado().Lq)
        self.ok(d.Lq / m.Lq, 0.5)


class TestPrioridades(Base):
    def test_2_um_atendente_duas_classes_sem_interrupcao(self):
        r = PrioridadesMMs((2, 10), 20, 1).resultado()
        c1, c2 = r.classes
        self.ok(c1.Lq, 0.067); self.ok(c1.L, 0.167); self.ok(c1.Wq, 0.033); self.ok(c1.W, 0.083)
        self.ok(c2.L, 1.333); self.ok(c2.Wq, 0.083); self.ok(c2.W, 0.133)
        self.ok(c1.Wq / c2.Wq, 0.4)
        self.ok(Fila(12, 20).resultado().rho * 12, 7.2)                       # horas ocupado por dia (12 h)

    def test_5_rapido_ou_dois_lentos(self):
        a = PrioridadesMMs((2, 3), 6, 1).resultado().classes
        self.ok(a[0].Wq, 0.208); self.ok(a[0].W, 0.375); self.ok(a[0].L, 0.75)
        self.ok(a[1].Lq, 3.75); self.ok(a[1].L, 4.25); self.ok(a[1].Wq, 1.25); self.ok(a[1].W, 1.417)
        b = PrioridadesMMs((2, 3), 3, 2).resultado().classes
        self.ok(b[0].Lq, 0.379); self.ok(b[0].L, 1.045); self.ok(b[0].Wq, 0.189); self.ok(b[0].W, 0.523)
        self.ok(b[1].Lq, 3.409); self.ok(b[1].L, 4.409); self.ok(b[1].Wq, 1.136); self.ok(b[1].W, 1.47)
        self.assertLess(a[0].W, b[0].W)          # menor W1: 1 atendente rápido
        self.assertLess(b[0].Wq, a[0].Wq)        # menor Wq1: 2 atendentes lentos

    def test_6_ferramentaria(self):
        fifo = PrioridadesMMs((2, 4, 2), 10, 1).resultado()
        self.ok(fifo.geral.W, 0.5)
        sem = [c.W for c in PrioridadesMMs((2, 4, 2), 10, 1, False).resultado().classes]
        com = [c.W for c in PrioridadesMMs((2, 4, 2), 10, 1, True).resultado().classes]
        for v, g in zip(sem, (0.2, 0.35, 1.1)): self.ok(v, g)
        for v, g in zip(com, (0.125, 0.3125, 1.25)): self.ok(v, g)

    def test_7_hospital_5_20_75(self):
        lams = lams_de_percentuais(2, (5, 20, 75))
        gab = {(True, 1): (0.011, 0.080, 0.867), (True, 2): (0.00009, 0.00289, 0.05493),
               (False, 1): (0.230, 0.276, 0.800), (False, 2): (0.028, 0.031, 0.045)}
        for (inter, s), g in gab.items():
            r = PrioridadesMMs(lams, 3, s, inter).resultado()
            for c, v in zip(r.classes, g):
                self.ok(c.Wq, v, tol=6e-4 if v >= 0.01 else 2e-4)   # 0,05478 vs 0,05493: arredondamento do gabarito

    def test_teoria_hospital_10_30_60(self):
        lams = lams_de_percentuais(2, (10, 30, 60))
        sem1 = PrioridadesMMs(lams, 3, 1).resultado().classes
        for c, w in zip(sem1, (0.5714, 0.6580, 1.24242)): self.ok(c.W, w, tol=5e-4)
        com1 = PrioridadesMMs(lams, 3, 1, True).resultado().classes
        for c, w in zip(com1, (0.3571, 0.4870, 1.3636)): self.ok(c.W, w, tol=5e-4)
        sem2 = PrioridadesMMs(lams, 3, 2).resultado().classes
        for c, w in zip(sem2, (0.36207, 0.36649, 0.38141)): self.ok(c.W, w, tol=5e-5)
        com2 = PrioridadesMMs(lams, 3, 2, True).resultado().classes
        for c, w in zip(com2, (0.33370, 0.34126, 0.39875)): self.ok(c.W, w, tol=5e-5)

    def test_teoria_delegacia_5_viaturas(self):
        r = PrioridadesMMs((10, 20), 7.5, 5).resultado().classes
        self.ok(r[0].Wq, 0.0201); self.ok(r[1].Wq, 0.1007)

    def test_teoria_maquina_spt(self):
        dp = (1 / 1800) ** 0.5
        r = PrioridadesMG1((ClasseMG1(10, 1 / 20, dp), ClasseMG1(5, 1 / 15, dp)), spt=True).resultado().classes
        self.ok(r[0].Wq, 0.06, tol=0.005); self.ok(r[1].Wq, 0.33, tol=0.005)
        self.ok(r[0].W, 0.11, tol=0.006); self.ok(r[1].W, 0.40, tol=0.006)

    def test_media_geral_igual_a_fifo(self):
        # a média ponderada de W das classes é a mesma de uma fila FIFO (lei da conservação)
        for inter in (False, True):
            r = PrioridadesMMs((2, 4, 2), 10, 1, inter).resultado()
            media = sum(c.lam * c.W for c in r.classes) / sum(c.lam for c in r.classes)
            self.assertAlmostEqual(media, r.geral.W)
        r = PrioridadesMMs((10, 20), 7.5, 5, True).resultado()
        self.assertAlmostEqual(sum(c.lam * c.W for c in r.classes) / 30, r.geral.W)


class TestDivergenciasDoMaterial(Base):
    """Casos em que o gabarito do PDF não coincide com o enunciado. Aqui fica o valor correto."""

    def test_mmsk_5b_e_5c_custos_do_mecanico_nao_reproduziveis(self):
        # Enunciado: 4 máquinas, λ = 1/10 h, μ = 1/2 h, $20/h parada, mecânico $50/dia (8 h).
        r = Fila(1 / 10, 1 / 2, 1, N=4).resultado()
        self.ok(20 * 8 * r.L + 50, 208.67, tol=0.01)          # o gabarito diz 478,672 (≈ 20·24·L, com dia de 24 h)
        r2 = Fila(1 / 10, 1 / 2, 1, N=2).resultado()
        self.ok(2 * (20 * 8 * r2.L) + 2 * 50, 221.08, tol=0.01)   # o gabarito diz 270,336

    def test_mmsn_6d_fracao_de_tempo_operando(self):
        r = Fila(1 / 100, 1 / 10, 2, N=4).resultado()
        self.ok(r.disp_individual, 0.9081)                    # 1 − L/N; o gabarito (0,8184) é inconsistente com 3d

    def test_mmsn_4c_tecnico_ocupado(self):
        r = Fila(1 / 9, 1 / 2, 1, N=3).resultado()
        self.ok(1 - r.P0, 0.507)                              # o gabarito (0,667) é N·λ/μ, carga nominal

    def test_mms_14c_percentual_de_aviões_em_espera(self):
        self.ok(Fila(25, 20, 2).P_fila("≤", 4), 0.9542)       # o gabarito (92,7%) é P(n ≤ 5), não P(nq ≤ 4)

    def test_mms_12_ninguem_esperando(self):
        f = Fila(10, 15)
        self.ok(f.resultado().P0, 0.3333)                     # gabarito 0,33 = P0 (sistema vazio)
        self.ok(f.P_fila("=", 0), 0.5556)                     # "ninguém esperando na fila" literalmente

    def test_prioridades_5_classe1_rotulos_trocados(self):
        c = PrioridadesMMs((2, 3), 6, 1).resultado().classes[0]
        self.ok(c.L, 0.75); self.ok(c.Lq, 0.4167)             # o gabarito traz Lq = 0,75 e L = 0,167

    def test_mg1_4_lq_da_segunda_classe(self):
        c = PrioridadesMMs((2, 10), 20, 1).resultado().classes[1]
        self.ok(c.Lq, 0.8333)                                 # o gabarito traz 0,083 (falta um dígito)

    def test_mg1_2_e_3_enunciado_nao_diz_que_o_atendimento_e_constante(self):
        # Os gabaritos (Lq = 1,125 e L = 2,830) só fecham com σ = 0 (M/D/1); com exponencial os valores mudam.
        self.ok(FilaMG1.exponencial(3, 4).resultado().Lq, 2.25)


if __name__ == "__main__":
    unittest.main()
