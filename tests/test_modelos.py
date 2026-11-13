"""Testes: rode com   python -m unittest discover tests -v"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filas import Fila, FilaInstavel, NaoDisponivel, comparar_servidores, lambda_para_meta, menor_s_para_meta
from filas.exercicios import todos
from filas.kendall import decodificar
from filas.unidades import converter_taxa, fmt_tempo, ler_taxa


class TestFormulasDosSlides(unittest.TestCase):
    def test_mm1_barbearia(self):
        f = Fila(3, 4); r = f.resultado()
        self.assertAlmostEqual(r.P0, 0.25)
        self.assertAlmostEqual(r.L, 3); self.assertAlmostEqual(r.Lq, 2.25)
        self.assertAlmostEqual(r.W, 1); self.assertAlmostEqual(r.Wq, 0.75)
        self.assertAlmostEqual(f.P_W_maior(1), math.exp(-1))
        self.assertAlmostEqual(f.P_Wq_maior(1), 0.75 * math.exp(-1))
        self.assertAlmostEqual(lambda_para_meta(f, "W", 1.25), 3.2, places=6)

    def test_mms_banco(self):
        f = Fila(0.6, 0.5, 3); r = f.resultado()
        self.assertAlmostEqual(r.rho, 0.4)
        self.assertAlmostEqual(r.L, 1.294, places=3); self.assertAlmostEqual(r.Lq, 0.094, places=3)
        self.assertAlmostEqual(r.P0, 0.294, places=3)
        self.assertAlmostEqual(f.P_W_maior(3), 0.2506, places=4)
        self.assertAlmostEqual(f.P_Wq_maior(2), 0.0233, places=4)

    def test_mms_sobrecarga(self):
        f = Fila(30, 20, 2); r = f.resultado()
        self.assertAlmostEqual(r.Lq, 13.5 / 7); self.assertAlmostEqual(r.P0, 1 / 7)
        self.assertAlmostEqual(f.P(3), 3.375 / 4 / 7)

    def test_mm1_motores(self):
        f = Fila(11, 12.5); r = f.resultado()
        self.assertAlmostEqual(r.W * 30, 20); self.assertAlmostEqual(r.Wq * 30, 17.6)
        self.assertAlmostEqual(r.L, 22 / 3); self.assertAlmostEqual(r.P0, 0.12)


class TestConsistencia(unittest.TestCase):
    def test_little(self):
        for f in [Fila(3, 4), Fila(5, 4, 2, K=7), Fila(0.2, 1, 2, N=9), Fila(8, 3, 4)]:
            r = f.resultado()
            self.assertAlmostEqual(r.L, r.lam_ef * r.W); self.assertAlmostEqual(r.Lq, r.lam_ef * r.Wq)
            self.assertAlmostEqual(r.W - r.Wq, 1 / f.mu)

    def test_soma_das_probabilidades(self):
        for f in [Fila(5, 4, 2, K=7), Fila(0.2, 1, 2, N=9), Fila(1, 4, 1, K=3)]:
            self.assertAlmostEqual(sum(f.distribuicao()), 1)
        self.assertAlmostEqual(sum(Fila(8, 3, 4).distribuicao(400)), 1, places=6)

    def test_finito_converge_para_infinito(self):
        inf, fin = Fila(3, 4).resultado(), Fila(3, 4, 1, K=200).resultado()
        self.assertAlmostEqual(inf.L, fin.L, places=6); self.assertAlmostEqual(inf.Wq, fin.Wq, places=6)

    def test_mm1k_formula_fechada(self):  # P_K = (1-ρ)ρ^K / (1-ρ^(K+1))
        rho, K = 0.75, 5
        self.assertAlmostEqual(Fila(3, 4, 1, K=K).resultado().p_bloqueio, (1 - rho) * rho**K / (1 - rho**(K + 1)))

    def test_cauda(self):
        f = Fila(0.6, 0.5, 3)
        self.assertAlmostEqual(f.P_mais_que(5), 1 - sum(f.P(n) for n in range(6)))
        self.assertAlmostEqual(f.P_W_maior(0), 1)

    def test_caso_especial_s_menos_1_igual_a_a(self):  # s-1-λ/μ = 0
        f = Fila(1, 1, 2)
        self.assertTrue(0 < f.P_W_maior(1.0) < 1)

    def test_s1_pw_igual_exponencial(self):
        f = Fila(3, 4)
        self.assertAlmostEqual(f.P_W_maior(0.3), math.exp(-1 * 0.3))


class TestErros(unittest.TestCase):
    def test_instavel(self):
        with self.assertRaises(FilaInstavel): Fila(40, 20)
        with self.assertRaises(FilaInstavel): Fila(60, 20, 3)
    def test_validacoes(self):
        for kw in [dict(lam=0, mu=1), dict(lam=1, mu=-1), dict(lam=1, mu=2, s=0),
                   dict(lam=1, mu=2, s=3, K=2), dict(lam=1, mu=2, K=3, N=4)]:
            with self.assertRaises(ValueError): Fila(**kw)
    def test_tempo_em_modelo_finito(self):
        with self.assertRaises(NaoDisponivel): Fila(1, 2, K=3).P_W_maior(1)
    def test_finito_aceita_lambda_maior_que_mu(self):
        self.assertTrue(Fila(10, 2, 1, K=5).resultado().rho <= 1)


class TestFerramentas(unittest.TestCase):
    def test_comparar_e_menor_s(self):
        self.assertEqual([r.fila.s for r in comparar_servidores(30, 20, 1, 4)], [2, 3, 4])
        self.assertEqual(menor_s_para_meta(30, 20, "Wq", 0.01), 3)

    def test_unidades(self):
        self.assertAlmostEqual(converter_taxa(30, "hora", "minuto"), 0.5)
        self.assertAlmostEqual(ler_taxa("20 min", "hora"), 3)
        self.assertAlmostEqual(ler_taxa("0,5", "hora"), 0.5)
        self.assertEqual(fmt_tempo(0.75, "hora"), "45 min")

    def test_kendall(self):
        k = decodificar("M/M/3/FCFS/10/100")
        self.assertEqual((k.m, k.K, k.N), (3, 10, 100))
        self.assertIsNone(k.modelo_do_projeto()[0])
        self.assertEqual(decodificar("M/M/2/8").modelo_do_projeto()[0], {"s": 2, "K": 8, "N": None})
        self.assertIsNone(decodificar("M/G/1").modelo_do_projeto()[0])
        with self.assertRaises(ValueError): decodificar("M/M")

    def test_exercicios_conferem_com_gabarito(self):
        for ex in todos():
            for it in ex.itens:
                self.assertIsNot(it.confere, False, f"{ex.id} item {it.letra}")


if __name__ == "__main__":
    unittest.main()
