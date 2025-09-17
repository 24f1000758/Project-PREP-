import re
import sympy as sp
import numexpr as ne
from sympy import symbols, Function, Eq, dsolve, Derivative, Sum, oo
from sympy.core.numbers import ComplexInfinity, nan

# Initialize printing for a nicer output
sp.init_printing(use_unicode=True)

def is_math_query(expr: str) -> bool:
    """
    Determines if the input string is likely a math query.
    Only accepts pure math-like strings or explicit math keywords.
    """
    expr_lower = expr.lower().strip()

    # Explicit math-related keywords
    keywords = [
        "integrate", "integral", "differentiate", "derivative",
        "solve", "equation", "root", "roots", "limit",
        "ln", "log", "evaluate", "simplify", "summation",
        "ode", "differential equation"
    ]
    if any(k in expr_lower for k in keywords):
        return True

    # Regex: only digits, operators, variables (x,y,z,t), and parentheses allowed
    math_pattern = r'^[0-9xXyYzZtT+\-*/^().= ]+$'
    return bool(re.fullmatch(math_pattern, expr))


def clean_math_text(expr: str) -> str:
    """
    Cleans and preprocesses a mathematical expression string for SymPy.

    This function handles:
    - Normalizing minus signs and power notation.
    - Adding implicit multiplication.
    - Removing common filler words and symbols.
    - Handling common functions like ln and log.

    Args:
        expr: The raw input string.

    Returns:
        A cleaned string ready for symbolic evaluation.
    """
    s = expr.strip()
    # Normalize common mathematical notations and non-standard characters
    s = s.replace("−", "-").replace("−", "-").replace("^", "**")
    
    s_lower = s.lower()
    # Replace natural log and constants
    s_lower = s_lower.replace("ln(", "log(")
    s_lower = s_lower.replace("pi", str(sp.pi))
    s_lower = s_lower.replace("e", str(sp.E))

    # Pattern to protect function names with spaces
    funcs = ["sin", "cos", "tan", "cot", "sec", "csc",
             "asin", "acos", "atan", "acot", "asec", "acsc",
             "sinh", "cosh", "tanh", "exp", "log", "sqrt"]
    for f in funcs:
        s_lower = re.sub(rf"\b{f}\s*\(", f"FUNC_{f}(", s_lower)
    
    # Remove filler words with word boundaries
    filler_words = [
        "solve", "solution", "sum", "answer", "for", "the",
        "equation", "find", "roots?", "of", "approximate",
        "calculate", "compute", "differentiate", "derivative",
        "integrate", "integral", "limit", "evaluate", "simplify",
        "summation", "with respect to", "what is", "is", "a",
        "an", "to"
    ]
    pattern_filler = r"\b(" + "|".join(filler_words) + r")\b"
    s_lower = re.sub(pattern_filler, "", s_lower)
    
    # Add implicit multiplication where a digit is followed by a variable/paren or vice-versa
    s_lower = re.sub(r"(\d|\))([a-zA-Z\(])", r"\1*\2", s_lower)
    # Add implicit multiplication for parentheses next to each other
    s_lower = re.sub(r"(\))(\()", r"\1*\2", s_lower)
    
    # Remove all spaces for symbolic evaluation
    s_lower = re.sub(r"\s+", "", s_lower)

    # Restore protected function names
    for f in funcs:
        s_lower = s_lower.replace(f"FUNC_{f}(", f + "(")

    return s_lower

def _pick_var(expr: sp.Expr) -> sp.Symbol:
    """
    Picks a symbolic variable from an expression, defaulting to 'x'.
    """
    free_symbols = list(expr.free_symbols)
    if not free_symbols:
        return sp.Symbol("x")
    
    # Prioritize common variables
    preferred_vars = ["x", "y", "z", "t"]
    for p_var in preferred_vars:
        for sym in free_symbols:
            if str(sym) == p_var:
                return sym
    
    return free_symbols[0]

def _format_numeric_solutions(solutions, real_only=True, tol=1e-12, ndigits=12):
    """
    Formats a list of numeric solutions, removing duplicates and handling precision.
    """
    out, seen = [], []
    def _is_close(a, b, eps=1e-8):
        return abs(a - b) < eps
    
    for r in solutions:
        if isinstance(r, (ComplexInfinity, nan)):
            continue
        r_c = complex(r.evalf()) if hasattr(r, "evalf") else complex(r)
        
        if real_only and abs(r_c.imag) < tol:
            val = round(r_c.real, ndigits)
        else:
            val = complex(round(r_c.real, ndigits), round(r_c.imag, ndigits))
        
        is_new = True
        for x in seen:
            if isinstance(val, float) and isinstance(x, float) and _is_close(val, x):
                is_new = False
                break
            if isinstance(val, complex) and isinstance(x, complex) and _is_close(val.real, x.real) and _is_close(val.imag, x.imag):
                is_new = False
                break
        if is_new:
            seen.append(val)
            out.append(val)
            
    return out

def _solve_system(equations: list[str]) -> str:
    """
    Solves a system of linear or non-linear equations.
    """
    try:
        sym_eqs = []
        syms = set()
        for eq in equations:
            if '=' not in eq:
                continue
            lhs, rhs = eq.split('=', 1)
            lhs_e = sp.sympify(clean_math_text(lhs))
            rhs_e = sp.sympify(clean_math_text(rhs))
            sym_eqs.append(Eq(lhs_e, rhs_e))
            syms.update(lhs_e.free_symbols)
            syms.update(rhs_e.free_symbols)
        
        variables = sorted(list(syms), key=str)
        
        # Use solveset for robust symbolic solving
        solutions = sp.nonlinsolve(sym_eqs, variables)
        
        if isinstance(solutions, sp.EmptySet):
            return "No solution found."
        
        if isinstance(solutions, sp.FiniteSet):
            output = "Solutions: "
            for sol_tuple in solutions:
                sol_str = ", ".join([f"{var} = {sol}" for var, sol in zip(variables, sol_tuple)])
                output += f"({sol_str})"
            return output
        
        return f"Solutions: {solutions}"
        
    except Exception as e:
        return f"❌ Unable to solve system: {e}"

def solve_equation(lhs_e, rhs_e, var):
    """
    Solves a single-variable equation using SymPy's solvers.
    """
    f = sp.simplify(lhs_e - rhs_e)
    if not f:
        return ["True for all values"]
    
    # Attempt a symbolic solution first with solveset
    sol_set = sp.solveset(sp.Eq(f, 0), var, domain=sp.S.Reals)
    
    # If a finite set of solutions is found, return it
    if isinstance(sol_set, sp.FiniteSet):
        return list(sol_set)
    
    # If the symbolic solver returns an unevaluated set, try `solve`
    if isinstance(sol_set, (sp.sets.conditionset.ConditionSet, sp.EmptySet)):
        try:
            sol = sp.solve(sp.Eq(f, 0), var)
            if sol:
                return sol
        except Exception:
            pass
            
    # As a last resort, use nsolve for numeric solutions
    seeds = [-10, -5, -3, -2, -1, 0, 1, 2, 3, 5, 10]
    roots = []
    for seed in seeds:
        try:
            root = sp.nsolve(f, var, seed)
            if root not in roots:
                roots.append(root)
        except Exception:
            pass
    
    return roots

def solve_math(expr: str) -> str:
    """
    A comprehensive function to solve various mathematical problems.
    """
    try:
        expr_lower = expr.lower()
        
        # Check for multiple equations to solve as a system
        if expr_lower.count('=') > 1:
            equations = re.split(r'\s{1,}', expr.strip())
            return _solve_system(equations)

        # --- Handle ODEs ---
        if "differential equation" in expr_lower or "ode" in expr_lower:
            return "ODEs and systems of equations are not yet supported for general parsing."
        
        # --- Handle Summation ---
        # Matches patterns like "sum i from 1 to 5 of i^2"
        m = re.search(r"sum\s+([a-zA-Z])\s+from\s*(\-?\d+)\s*to\s*(\-?\d+|inf)\s*(?:of|:)?\s*(.*)", expr_lower)
        if m:
            var_name, start_str, end_str, func_str = m.groups()
            var = symbols(var_name)
            start = sp.sympify(start_str)
            end = sp.sympify(end_str) if end_str != "inf" else oo
            func = sp.sympify(clean_math_text(func_str))
            
            result = Sum(func, (var, start, end)).doit()
            return f"Summation: {sp.simplify(result)}"
        
        # --- Handle Differentiation ---
        if "differentiate" in expr_lower or "derivative" in expr_lower:
            m = re.search(r"(differentiate|derivative)\s*(.*)", expr_lower)
            if m:
                func_str = clean_math_text(m.group(2))
                f = sp.sympify(func_str)
                var = _pick_var(f)
                result = sp.simplify(sp.diff(f, var))
                return f"Derivative: {result}"

        # --- Handle Integration ---
        if "integrate" in expr_lower or "integral" in expr_lower:
            m = re.search(r"(integrate|integral)\s*(.*)", expr_lower)
            if m:
                func_str = clean_math_text(m.group(2))
                f = sp.sympify(func_str)
                var = _pick_var(f)
                result = sp.integrate(f, var)
                return f"Integral: {sp.simplify(result)}"

        # --- Handle Limits ---
        if "limit" in expr_lower:
            m = re.search(r"limit\s*(.*)\s*as\s*([a-zA-Z])\s*->\s*(\S*)", expr_lower)
            if m:
                func_str, var_name, point_str = m.groups()
                f = sp.sympify(clean_math_text(func_str))
                var = sp.Symbol(var_name)
                point = sp.sympify(point_str)
                result = sp.limit(f, var, point)
                return f"Limit: {result}"
        
        # --- Handle Equations with '=' ---
        expr_clean = clean_math_text(expr)
        if "=" in expr_clean:
            lhs, rhs = expr_clean.split("=", 1)
            lhs_e = sp.sympify(lhs)
            rhs_e = sp.sympify(rhs)
            var = _pick_var(lhs_e - rhs_e)
            
            solutions = solve_equation(lhs_e, rhs_e, var)
            
            if solutions and solutions != ["True for all values"]:
                # Use symbolic representation if possible, otherwise numeric
                formatted_solutions = [str(sp.N(s)) for s in solutions]
                return f"Solutions for {var}: {', '.join(formatted_solutions)}"
            elif solutions == ["True for all values"]:
                return "The equation is true for all values."
            else:
                return "No solutions found."

        # --- Handle direct simplification or calculation ---
        val = sp.sympify(expr_clean)
        
        if len(val.free_symbols) == 0:
            # Numeric evaluation with NumExpr for speed on simple arithmetic
            if re.fullmatch(r"[0-9.\+\-*/()\s]+", expr_clean):
                try:
                    ne_result = ne.evaluate(expr_clean).item()
                    return f"Result: {ne_result}"
                except Exception:
                    pass # Fall back to SymPy if NumExpr fails
            return f"Result: {sp.N(val)}"
        else:
            # Symbolic simplification
            return f"Simplified: {sp.simplify(val)}"

    except Exception as e:
        return f"❌ Unable to solve: {e}"

# # Example Usage
# if __name__ == "__main__":
#     test_cases = [
#         "solve 3x+y=10 x-2y=1", # The user's specific problem
#         "integrate sin(x)",
#         "differentiate x^3 + 4x",
#         "solve x^2 - 4 = 0",
#         "summation k from 1 to 5 of k^2"
#     ]

#     for q in test_cases:
#         print("Query:", q)
#         print("Result:", solve_math(q))
#         print("-" * 20)