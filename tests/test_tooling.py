"""Testes dos mecanismos de preservação e da integridade da avaliação."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate

spec = importlib.util.spec_from_file_location("build_runtime", ROOT / "scripts/build-runtime.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.case = dict(id="one", category="fidelidade", operation="rewrite", instruction="Revisar.",
                         context={}, draft="Custa R$ 10 por mês.", criteria=["Manter condição."],
                         protected=["R$ 10"], unchanged=True)
        self.response = dict(case_id="one", variant="compact", output=self.case["draft"], model="test", parameters={})

    def test_runtime_ignores_surrounding_document(self):
        self.assertEqual(builder.render("intro" + builder.START + "\nregras\n" + builder.END + "fim"), "regras\n")

    def test_runtime_rejects_ambiguous_or_empty_markers(self):
        for text in ("sem bloco", builder.START + builder.END, builder.END + "x" + builder.START,
                     builder.START + "x" + builder.START + builder.END):
            with self.subTest(text=text), self.assertRaises(ValueError):
                builder.render(text)

    def test_duplicate_cases_rejected(self):
        with self.assertRaises(ValueError):
            evaluate.validate_cases([self.case, self.case])

    def test_protected_token_must_exist_in_input(self):
        self.case["protected"] = ["inventado"]
        with self.assertRaises(ValueError):
            evaluate.validate_cases([self.case])

    def test_expected_answers_are_not_exposed(self):
        prepared = evaluate.prepare(self.case, "compact", "regras")
        self.assertNotIn("criteria", prepared["messages"][1]["content"])
        self.assertNotIn("unchanged", prepared["messages"][1]["content"])
        self.assertNotIn("protected", prepared["messages"][1]["content"])

    def test_immutable_reply_must_be_exact(self):
        self.assertEqual(evaluate.check_response(self.case, self.case["draft"]), [])
        self.assertTrue(evaluate.check_response(self.case, "Custa R$ 10."))

    def test_changed_price_is_detected(self):
        self.case["unchanged"] = False
        self.assertTrue(evaluate.check_response(self.case, "Custa R$ 20 por mês."))

    def test_mechanical_check_does_not_claim_semantic_fidelity(self):
        self.case["unchanged"] = False
        self.assertEqual(evaluate.check_response(self.case, "Não custa R$ 10 por mês."), [])

    def test_duplicates_unknown_ids_and_missing_rows_rejected(self):
        for rows in ([self.response, self.response], [{**self.response, "case_id":"unknown"}], []):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                evaluate.score({"one":self.case}, rows, ["compact"])

    def test_partial_is_explicit_and_missing_metrics_are_not_zero(self):
        result = evaluate.score({"one":self.case}, [], ["compact"], allow_partial=True)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["metrics"]["compact"]["input_tokens"]["mean"])

    def test_invalid_metrics_rejected(self):
        for value in (-1, float("nan"), float("inf"), True, "10", 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate.score({"one":self.case}, [{**self.response,"input_tokens":value}], ["compact"])

    def test_empty_output_requires_explicit_policy(self):
        c = copy.deepcopy(self.case)
        c.update(operation="generate", protected=[], unchanged=False)
        self.assertTrue(evaluate.check_response(c, ""))
        c["context"]["allow_empty"] = True
        self.assertEqual(evaluate.check_response(c, ""), [])


if __name__ == "__main__":
    unittest.main()
