"""
Motor de inferência seguro para regras OCEAN.
Variáveis *_natural/*_adapted contêm T-scores (N = neuroticismo canônico).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Union

FACTORS = ("O", "C", "E", "A", "N")
COMPARISON_OPS = (">=", "<=", "==", ">", "<")

TOKEN_RE = re.compile(
    r"(?P<NUM>-?\d+(?:\.\d+)?)"
    r"|(?P<VAR>O_natural|C_natural|E_natural|A_natural|N_natural"
    r"|O_adapted|C_adapted|E_adapted|A_adapted|N_adapted"
    r"|O_diff|C_diff|E_diff|A_diff|N_diff"
    r"|O_t|C_t|E_t|A_t|N_t"
    r"|[OCEAN])"
    r"|(?P<OP>[+\-])"
    r"|(?P<SKIP>\s+)"
)

Expr = Union["NumExpr", "VarExpr", "BinExpr"]


class ParseError(ValueError):
    pass


@dataclass(frozen=True)
class NumExpr:
    value: float


@dataclass(frozen=True)
class VarExpr:
    name: str


@dataclass(frozen=True)
class BinExpr:
    left: Expr
    op: str
    right: Expr


def build_context(t_scores: dict[str, dict[str, float]]) -> dict[str, float]:
    ctx: dict[str, float] = {}
    for f in FACTORS:
        n = float(t_scores["natural"][f])
        a = float(t_scores["adapted"][f])
        ctx[f"{f}_natural"] = n
        ctx[f"{f}_adapted"] = a
        ctx[f"{f}_diff"] = a - n
        ctx[f"{f}_t"] = n
        ctx[f] = n
    return ctx


def tokenize(expression: str) -> list[tuple[str, str]]:
    pos = 0
    tokens: list[tuple[str, str]] = []
    while pos < len(expression):
        match = TOKEN_RE.match(expression, pos)
        if not match:
            raise ParseError(f"Token inválido em: {expression[pos:pos + 20]!r}")
        if match.lastgroup != "SKIP":
            kind = "NUM" if match.group("NUM") else "VAR" if match.group("VAR") else "OP"
            tokens.append((kind, match.group(kind)))
        pos = match.end()
    return tokens


def _parse_term(tokens: list[tuple[str, str]], idx: int) -> tuple[Expr, int]:
    if idx >= len(tokens):
        raise ParseError("Expressão incompleta")
    kind, value = tokens[idx]
    if kind == "NUM":
        node: Expr = NumExpr(float(value))
        idx += 1
    elif kind == "VAR":
        node = VarExpr(value)
        idx += 1
    else:
        raise ParseError(f"Termo inválido: {value}")
    while idx < len(tokens) and tokens[idx][0] == "OP":
        op = tokens[idx][1]
        idx += 1
        right_kind, right_val = tokens[idx]
        right: Expr = NumExpr(float(right_val)) if right_kind == "NUM" else VarExpr(right_val)
        node = BinExpr(node, op, right)
        idx += 1
    return node, idx


def parse_expression(expression: str) -> Expr:
    tokens = tokenize(expression.strip())
    if not tokens:
        raise ParseError("Expressão vazia")
    result, idx = _parse_term(tokens, 0)
    if idx != len(tokens):
        raise ParseError(f"Tokens extras: {expression!r}")
    return result


def evaluate_expression(expr: Expr, context: dict[str, float]) -> float:
    if isinstance(expr, NumExpr):
        return expr.value
    if isinstance(expr, VarExpr):
        if expr.name not in context:
            raise ParseError(f"Variável desconhecida: {expr.name}")
        return float(context[expr.name])
    left = evaluate_expression(expr.left, context)
    right = evaluate_expression(expr.right, context)
    if expr.op == "+":
        return left + right
    if expr.op == "-":
        return left - right
    raise ParseError(f"Operador inválido: {expr.op}")


def split_comparison(condition: str) -> tuple[str, str, str]:
    for op in COMPARISON_OPS:
        idx = condition.find(op)
        if idx == -1:
            continue
        left = condition[:idx].strip()
        right = condition[idx + len(op):].strip()
        if left and right:
            return left, op, right
    raise ParseError(f"Comparação inválida: {condition!r}")


def evaluate_condition(condition: str, context: dict[str, float]) -> bool:
    left_expr, op, right_expr = split_comparison(condition.strip())
    left_val = evaluate_expression(parse_expression(left_expr), context)
    right_val = evaluate_expression(parse_expression(right_expr), context)
    if op == ">":
        return left_val > right_val
    if op == ">=":
        return left_val >= right_val
    if op == "<":
        return left_val < right_val
    if op == "<=":
        return left_val <= right_val
    if op == "==":
        return left_val == right_val
    raise ParseError(f"Operador desconhecido: {op}")


def rule_matches(rule: dict[str, Any], context: dict[str, float]) -> bool:
    conditions = rule.get("when", [])
    if not isinstance(conditions, list):
        return False
    try:
        return all(evaluate_condition(cond, context) for cond in conditions)
    except (ParseError, KeyError, TypeError):
        return False


def infer_profile(
    rules: list[dict[str, Any]],
    t_scores: dict[str, dict[str, float]],
) -> dict[str, Any]:
    context = build_context(t_scores)
    matched = [r for r in rules if rule_matches(r, context)]
    result: dict[str, Any] = {
        "natural": {f: context[f"{f}_natural"] for f in FACTORS},
        "adapted": {f: context[f"{f}_adapted"] for f in FACTORS},
        "diff": {f: context[f"{f}_diff"] for f in FACTORS},
        "matched_rules": [r.get("id", "UNKNOWN") for r in matched],
        "matched_count": len(matched),
    }
    if not matched:
        result.update({
            "profile": None,
            "interpretation": None,
            "confidence": 0.0,
            "evidence": [],
        })
        return result
    best = max(matched, key=lambda r: float(r.get("confidence", 0)))
    result.update({
        "profile": best.get("id", "UNKNOWN"),
        "interpretation": best.get("interpretation"),
        "confidence": float(best.get("confidence", 0)),
        "evidence": best.get("evidence", []),
        "category": best.get("category"),
    })
    return result