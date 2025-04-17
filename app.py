from flask import Flask, request, jsonify
from flask_cors import CORS
from sympy import symbols, sympify, integrate, Eq, latex, sin, cos, exp, Function, simplify, diff
import traceback
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Global history store – records will be kept for 4 months.
history_records = []

def preprocess_input(expr_str):
    """
    Replace caret '^' with Python's exponentiation operator '**'.
    """
    return expr_str.replace("^", "**")

# --- Separable ODE Solver ---
def separable_solver(eq_str, x, y_sym):
    """
    Solves a separable ODE provided as a string of the form:
         "dy/dx = f(x)*g(y)"
    It validates the format, extracts f(x) and g(y), integrates each side,
    and returns a step-by-step explanation in LaTeX format.
    """
    eq_str = preprocess_input(eq_str)
    parts = eq_str.split("=")
    if len(parts) != 2:
        return "Error: The equation must contain exactly one '=' sign."
    
    lhs = parts[0].strip()
    rhs_str = parts[1].strip()
    
    if lhs != "dy/dx":
        return "Error: The left-hand side must be 'dy/dx'. Please enter the equation in the form 'dy/dx = f(x)*g(y)'."
    
    local_dict = {"x": x, "y": y_sym, "sin": sin, "cos": cos, "exp": exp}
    try:
        expr = sympify(rhs_str, locals=local_dict)
    except Exception as e:
        return f"Error parsing the right-hand side: {e}"
    
    if expr.is_Mul:
        factors = expr.args
    else:
        factors = [expr]
    
    f_expr = 1
    g_expr = 1
    for factor in factors:
        dep = factor.free_symbols
        if len(dep) == 0:
            f_expr *= factor
        elif dep.issubset({x}):
            f_expr *= factor
        elif dep.issubset({y_sym}):
            g_expr *= factor
        else:
            return f"Error: The factor '{factor}' depends on both x and y; the ODE is not separable."
    
    if not (x in f_expr.free_symbols):
        return "Error: Could not extract a valid f(x) from the input."
    if not (y_sym in g_expr.free_symbols):
        return "Error: Could not extract a valid g(y) from the input."
    
    try:
        int_x = integrate(f_expr, x)
    except Exception as e:
        return f"Error integrating f(x): {e}"
    
    try:
        int_y = integrate(1/g_expr, y_sym)
    except Exception as e:
        return f"Error integrating 1/g(y): {e}"
    
    C = symbols("C")
    solution_eq = Eq(int_y, int_x + C)
    
    steps = []
    steps.append(f"$\\text{{You are solving the separable equation:}}$")
    steps.append(f"$\\frac{{dy}}{{dx}}= {latex(expr)}$")
    steps.append(f"$\\text{{In this case }} \\text{{f(x)}} = {latex(f_expr)} \\text{{ and }} \\text{{g(y)}} = {latex(g_expr)}.$")
    print({latex(g_expr)})
    steps.append(f"$\\text{{From here separate the equation: Put everything in terms of y on the right and everything}}$") 
    steps.append(f"$\\text{{in terms of x on the left.}}$")
    steps.append(f"$\\text{{You will arrive at: }} \\frac{{dy}}{latex(g_expr)} = {latex(f_expr)} {{dx}} $")
    steps.append(f"$\\text{{From here integrate both sides. Then compute the individual integrals.}}$")
    steps.append(f"$\\int \\frac{{dy}}{latex(g_expr)} = \\int {latex(f_expr)} {{dx}} $")
    steps.append(f"$\\int \\frac{{dy}}{latex(g_expr)} \\ = {latex(int_y)} + C$")
    steps.append(f"$\\int {latex(f_expr)} dx = {latex(int_x)} + C$")
    steps.append(f"$\\text{{The general solution is then: }}$")
    steps.append(f"$ {latex(solution_eq)} $")
    
    return "\n".join(steps)

# --- Linear ODE Solver ---
def linear_solver(eq_str, x):
    from sympy import exp,simplify,integrate,latex
    """
    Solves a linear ODE of the form:
         a(x) dy/dx + b(x) y = c(x)
    where a(x) is nonzero.
    
    The solver:
      - Replaces 'dy/dx' with 'y.diff(x)' where y is defined as a function of x.
      - Parses the left- and right-hand sides to extract a(x), b(x), and c(x).
      - Divides through by a(x) to obtain the standard form: dy/dx + P(x)y = Q(x)
         with P(x)=b(x)/a(x) and Q(x)=c(x)/a(x).
      - Computes the integrating factor μ(x)=exp(∫ P(x) dx) and then the general solution.
    """
    eq_str = preprocess_input(eq_str)
    parts = eq_str.split("=")
    if len(parts) != 2:
        return "Error: The equation must contain exactly one '=' sign."
    
    lhs_str = parts[0].strip()
    rhs_str = parts[1].strip()
    
    if "dy/dx" not in lhs_str:
        return "Error: The left-hand side must contain 'dy/dx'. Please input in the form 'a(x) dy/dx + b(x)y = c(x)'."
    
    lhs_str_processed = lhs_str.replace("dy/dx", "y.diff(x)")
    
    # Define y as a function of x.
    y_func = Function("y")
    y_expr = y_func(x)
    
    local_dict = {"x": x, "y": y_expr, "sin": sin, "cos": cos, "exp": exp}
    try:
        lhs_expr = sympify(lhs_str_processed, locals=local_dict)
    except Exception as e:
        return f"Error parsing the left-hand side: {e}"
    try:
        rhs_expr = sympify(rhs_str, locals=local_dict)
    except Exception as e:
        return f"Error parsing the right-hand side: {e}"
    
    # Construct the ODE: a(x)*y.diff(x) + b(x)*y - c(x) = 0.
    ode_expr = lhs_expr - rhs_expr
    
    a_expr = simplify(ode_expr.coeff(y_expr.diff(x)))
    b_expr = simplify(ode_expr.coeff(y_expr))
    remainder = simplify(ode_expr - (a_expr * y_expr.diff(x) + b_expr * y_expr))
    c_expr = -simplify(remainder)
    
    if a_expr == 0:
        return "Error: a(x) is zero. The equation must be of the form a(x) dy/dx + b(x)y = c(x) with a(x) ≠ 0."
    
    P_expr = simplify(b_expr / a_expr)
    Q_expr = simplify(c_expr / a_expr)

    try: 
        int_p = integrate(P_expr, x)
    except Exception as e:
        return f"Could not integrate P: {e}"
    mu_expr = exp(int_p)
    try:
        int_muQ = integrate(mu_expr * Q_expr, x)
    except Exception as e:
        return f"Error integrating μ(x)*Q(x): {e}"
    
    C = symbols("C")
    solution_expr = simplify((int_muQ + C) / mu_expr)
    
    steps = []
    steps.append(f"$\\text{{You are solving the linear equation: }}$")
    steps.append(f"${latex(a_expr)} \\frac{{dy}}{{dx}} + \\left({latex(b_expr)} \\right)y = {latex(c_expr)}$")
    steps.append(f"$\\text{{Always make sure the coefficient of }} \\frac{{dy}}{{dx}} \\text{{ is }} 1. $")
    steps.append(f"$ \\text{{Therefore, divide by }} {latex(a_expr)} \\text{{ to get: }}$")
    steps.append(f"$ \\frac{{dy}}{{dx}} + \\left({latex(P_expr)} \\right)y = {latex(Q_expr)}$")
    steps.append(f"$ \\text{{From here, compute the integrating factor:}}$")
    steps.append(f"$$\\mu(x)= e^{{\\int {latex(P_expr)} \\,dx}} = e^{{ {latex(int_p)}}} = {latex(mu_expr)}$$")
    steps.append(f"$\\text{{Then, multiply by the integrating factor on both sides.}}$")
    steps.append(f"$\\text{{The new ODE you are solving is now: }}$")
    if Q_expr == 1:
        steps.append(f"${latex(mu_expr)} \\frac{{dy}}{{dx}} + \\left({latex(mu_expr)} \\right) \\left({latex(P_expr)} \\right) y ={latex(mu_expr)} $")
        steps.append(f"$\\text{{Which you can automatically write as: }}$")
        steps.append(f"$\\frac{{d}}{{dx}} \\left( {latex(mu_expr)} y \\right) = {latex(mu_expr)}$")
    else:
        steps.append(f"${latex(mu_expr)} \\frac{{dy}}{{dx}} + \\left({latex(mu_expr)} \\right) \\left({latex(P_expr)} \\right) y =\\left({latex(mu_expr)} \\right) {latex(Q_expr)}$")
        steps.append(f"$\\text{{Which you can automatically write as: }}$")
        rhs = simplify(mu_expr * Q_expr)
        steps.append(f"$\\frac{{d}}{{dx}} \\left( {latex(mu_expr)} y \\right) = {rhs}$")
    steps.append(f"$\\text{{Integrate both sides: integrating the left hand side just gives you }} {latex(mu_expr)} y.$")
    steps.append(f"$\\text{{Integrating the right hand side gives you: }} {latex(int_muQ)} + C.$")
    steps.append(f"$\\text{{The overall solution is then: }} {latex(mu_expr)} \\text{{y}} = {latex(int_muQ)} + C.$")
    steps.append(f"$\\text{{Which can be simplified to: }} y = {latex(solution_expr)}.$")
    
    return "\n".join(steps)

# --- Exact / Integrating Factor / Homogeneous Solver ---

    """
    Solves (or sets up further) an ODE given in the form:
         M(x,y) dx + N(x,y) dy = 0
    This function first converts M_str and N_str into symbolic expressions,
    then checks if the ODE is exact (i.e. ∂M/∂y = ∂N/∂x).
    
    If the ODE is exact, it computes the potential function f(x,y) by integrating M with respect
    to x and adjusting by a function of y.
    
    If the ODE is not exact, it attempts to compute an integrating factor of the form μ(x) or μ(y),
    displays the computed factors and shows the new M and N after multiplication. If one of these
    integrating factors makes the ODE exact, that information is displayed to the user.
    """
    from sympy import diff, simplify, integrate, latex, exp
    
    # Preprocess the inputs.
    M_str = preprocess_input(M_str)
    N_str = preprocess_input(N_str)
    
    if not M_str.strip():
        return "Error: M(x,y) is empty. Please input a valid function for M(x,y)."
    if not N_str.strip():
        return "Error: N(x,y) is empty. Please input a valid function for N(x,y)."
    
    local_dict = {"x": x, "y": y, "sin": sin, "cos": cos, "exp": exp}
    try:
        M_expr = sympify(M_str, locals=local_dict)
    except Exception as e:
        return "Error converting M(x,y): " + str(e)
    try:
        N_expr = sympify(N_str, locals=local_dict)
    except Exception as e:
        return "Error converting N(x,y): " + str(e)
    
    steps = []
    steps.append("$$\\textbf{Step 1: Check Exactness}$$")
    M_y = diff(M_expr, y)
    N_x = diff(N_expr, x)
    steps.append("$$\\frac{\\partial M}{\\partial y} = " + latex(M_y) + "$$")
    steps.append("$$\\frac{\\partial N}{\\partial x} = " + latex(N_x) + "$$")
    
    if simplify(M_y - N_x) == 0:
        steps.append("$$\\textbf{The ODE is exact.}$$")
        # Compute potential function via integration (as before)
        steps.append("$$\\textbf{Step 2: Integrate } M(x,y) \\text{ with respect to } x:$$")
        f_x = integrate(M_expr, x)
        steps.append("$$f(x,y)= \\int M(x,y)\\,dx = " + latex(f_x) + "$$")
        steps.append("$$\\textbf{Step 3: Differentiate with respect to } y:$$")
        f_y_partial = diff(f_x, y)
        steps.append("$$\\frac{\\partial}{\\partial y} f(x,y) = " + latex(f_y_partial) + "$$")
        steps.append("$$\\textbf{Step 4: Compute the missing component: }\\Delta(y)= N(x,y) - \\frac{\\partial}{\\partial y} f(x,y)$$")
        diff_expr = simplify(N_expr - f_y_partial)
        steps.append("$$\\Delta(y)= " + latex(diff_expr) + "$$")
        steps.append("$$\\textbf{Step 5: Integrate } \\Delta(y) \\text{ with respect to } y:$$")
        h_y = integrate(diff_expr, y)
        steps.append("$$h(y)= " + latex(h_y) + "$$")
        f_potential = simplify(f_x + h_y)
        steps.append("$$\\textbf{Step 6: The potential function is:}$$")
        steps.append("$$f(x,y)= " + latex(f_potential) + " \\quad \\text{and the general solution is } f(x,y)= C$$")
        return "\n".join(steps)
    else:
        steps.append("$$\\textbf{The ODE is not exact.}$$")
        
        # Attempt integrating factor depending solely on x.
        found_option = False
        integrating_factors_text = ""
        
        if N_expr != 0:
            factor_x = simplify((M_y - N_x) / N_expr)
            if factor_x.free_symbols.issubset({x}):
                mu_x = exp(integrate(factor_x, x))
                integrating_factors_text += "$$\\textbf{Integrating factor } \\mu(x)= e^{\\int \\frac{M_y-N_x}{N}dx} = " + latex(mu_x) + "$$\n"
                # Multiply the original M and N by mu_x.
                new_M = simplify(mu_x * M_expr)
                new_N = simplify(mu_x * N_expr)
                new_My = diff(new_M, y)
                new_Nx = diff(new_N, x)
                integrating_factors_text += "$$\\textbf{After multiplying by } \\mu(x):$$\n"
                integrating_factors_text += "$$\\tilde{M}(x,y)= " + latex(new_M) + ", \\quad \\tilde{N}(x,y)= " + latex(new_N) + "$$\n"
                integrating_factors_text += "$$\\frac{\\partial \\tilde{M}}{\\partial y}= " + latex(new_My) + ", \\quad \\frac{\\partial \\tilde{N}}{\\partial x}= " + latex(new_Nx) + "$$\n"
                if simplify(new_My - new_Nx) == 0:
                    integrating_factors_text += "$$\\textbf{The ODE becomes exact when multiplied by } \\mu(x).$$\n"
                    found_option = True
                else:
                    integrating_factors_text += "$$\\textbf{Warning: The ODE is still not exact with } \\mu(x).$$\n"
        
        # Attempt integrating factor depending solely on y.
        if M_expr != 0:
            factor_y = simplify((N_x - M_y) / M_expr)
            if factor_y.free_symbols.issubset({y}):
                mu_y = exp(integrate(factor_y, y))
                integrating_factors_text += "$$\\textbf{Integrating factor } \\mu(y)= e^{\\int \\frac{N_x-M_y}{M}dy} = " + latex(mu_y) + "$$\n"
                # Multiply the original M and N by mu_y.
                new_M2 = simplify(mu_y * M_expr)
                new_N2 = simplify(mu_y * N_expr)
                new_My2 = diff(new_M2, y)
                new_Nx2 = diff(new_N2, x)
                integrating_factors_text += "$$\\textbf{After multiplying by } \\mu(y):$$\n"
                integrating_factors_text += "$$\\tilde{M}(x,y)= " + latex(new_M2) + ", \\quad \\tilde{N}(x,y)= " + latex(new_N2) + "$$\n"
                integrating_factors_text += "$$\\frac{\\partial \\tilde{M}}{\\partial y}= " + latex(new_My2) + ", \\quad \\frac{\\partial \\tilde{N}}{\\partial x}= " + latex(new_Nx2) + "$$\n"
                if simplify(new_My2 - new_Nx2) == 0:
                    integrating_factors_text += "$$\\textbf{The ODE becomes exact when multiplied by } \\mu(y).$$\n"
                    found_option = True
                else:
                    integrating_factors_text += "$$\\textbf{Warning: The ODE is still not exact with } \\mu(y).$$\n"
        
        steps.append(integrating_factors_text)
        if not found_option:
            steps.append("$$\\textbf{No integrating factor of the form } \\mu(x) \\textbf{ or } \\mu(y) \\textbf{ could be found to make the ODE exact.}$$")
        return "\n".join(steps)

def exact_integratingFactor_Homogenous_solver(M_str, N_str, x, y):
    """
    Solves (or sets up further) an ODE given in the form:
         M(x,y) dx + N(x,y) dy = 0
    by performing the following steps:
    
      1. Convert the input strings to symbolic expressions.
      2. Check whether the ODE is exact (i.e. ∂M/∂y = ∂N/∂x). If it is, the potential
         function f(x,y) is computed by integrating M with respect to x and adjusting by h(y).
      3. If not exact, attempt to compute integrating factors μ(x) and μ(y) (depending solely on x or y).
         If one of them results in an exact ODE, multiply the original ODE by that factor and solve it (using our exact solver helper).  
         If both are available, μ(x) is chosen (with an annotation about the alternate).
      4. If no integrating factor can be found, check if the ODE is homogeneous (i.e. if M(tx,ty)=t^aM(x,y) 
         and N(tx,ty)=t^aN(x,y) for the same exponent a). If it is homogeneous, apply the substitution 
         y = u·x (so that dy/dx = u + x du/dx) to convert the ODE into a separable ODE in u and x,
         solve it via the separable_solver, and finally note that u = y/x.
      5. If none of these approaches work, return an error message.
    """
    from sympy import diff, simplify, integrate, latex, exp, symbols
    t = symbols("t", positive=True)
    
    # --- Helper function: Solve exact ODE and return steps ---
    def solve_exact_ode(M_expr, N_expr, x, y):
        steps_exact = []
        steps_exact.append("$$\\textbf{Solving the exact ODE:}$$")
        f_x = integrate(M_expr, x)
        steps_exact.append("$$f(x,y)= \\int M(x,y)\\,dx = " + latex(f_x) + "$$")
        f_y_partial = diff(f_x, y)
        steps_exact.append("$$\\frac{\\partial}{\\partial y} f(x,y) = " + latex(f_y_partial) + "$$")
        diff_expr = simplify(N_expr - f_y_partial)
        steps_exact.append("$$\\Delta(y)= N(x,y) - \\frac{\\partial}{\\partial y} f(x,y) = " + latex(diff_expr) + "$$")
        h_y = integrate(diff_expr, y)
        steps_exact.append("$$h(y)= \\int \\Delta(y)\\,dy = " + latex(h_y) + "$$")
        f_potential = simplify(f_x + h_y)
        steps_exact.append("$$\\textbf{Potential function: } f(x,y)= " + latex(f_potential) + " = C$$")
        return "\n".join(steps_exact)
    # Preprocess inputs.
    M_str = preprocess_input(M_str)
    N_str = preprocess_input(N_str)
    
    if not M_str.strip():
        return "Error: M(x,y) is empty. Please input a valid function for M(x,y)."
    if not N_str.strip():
        return "Error: N(x,y) is empty. Please input a valid function for N(x,y)."
    
    local_dict = {"x": x, "y": y, "sin": sin, "cos": cos, "exp": exp}
    try:
        M_expr = sympify(M_str, locals=local_dict)
    except Exception as e:
        return "Error converting M(x,y): " + str(e)
    try:
        N_expr = sympify(N_str, locals=local_dict)
    except Exception as e:
        return "Error converting N(x,y): " + str(e)
    
    steps = []
    steps.append("$$\\textbf{Step 1: Check Exactness of the Original ODE}$$")
    M_y = diff(M_expr, y)
    N_x = diff(N_expr, x)
    steps.append("$$\\frac{\\partial M}{\\partial y} = " + latex(M_y) + "$$")
    steps.append("$$\\frac{\\partial N}{\\partial x} = " + latex(N_x) + "$$")
    
    if simplify(M_y - N_x) == 0:
        steps.append("$$\\textbf{The ODE is exact.}$$")
        steps.append(solve_exact_ode(M_expr, N_expr, x, y))
        return "\n".join(steps)
    else:
        steps.append("$$\\textbf{The ODE is not exact.}$$")
        integrating_factor_used = None
        alt_if_message = ""
        
        # --- Integrating Factor Attempts ---
        # Attempt integrating factor μ(x)
        mu_x = None
        if N_expr != 0:
            candidate_factor_x = simplify((M_y - N_x) / N_expr)
            if candidate_factor_x.free_symbols.issubset({x}):
                mu_x = exp(integrate(candidate_factor_x, x))
                steps.append("$$\\textbf{Candidate integrating factor (function of x): } \\mu(x)= e^{\\int \\frac{M_y-N_x}{N}dx} = " + latex(mu_x) + "$$")
                new_M_x = simplify(mu_x * M_expr)
                new_N_x = simplify(mu_x * N_expr)
                new_M_y = diff(new_M_x, y)
                new_N_x_deriv = diff(new_N_x, x)
                steps.append("$$\\textbf{New M and N after multiplying by } \\mu(x):$$")
                steps.append("$$\\tilde{M}(x,y)= " + latex(new_M_x) + ",\\quad \\tilde{N}(x,y)= " + latex(new_N_x) + "$$")
                steps.append("$$\\frac{\\partial \\tilde{M}}{\\partial y}= " + latex(new_M_y) + ",\\quad \\frac{\\partial \\tilde{N}}{\\partial x}= " + latex(new_N_x_deriv) + "$$")
                if simplify(new_M_y - new_N_x_deriv) == 0:
                    steps.append("$$\\textbf{The ODE becomes exact when multiplied by } \\mu(x).$$")
                    integrating_factor_used = ("x", mu_x, new_M_x, new_N_x)
                else:
                    steps.append("$$\\textbf{Warning: The ODE is still not exact with } \\mu(x).$$")
        
        # Attempt integrating factor μ(y)
        mu_y = None
        if M_expr != 0:
            candidate_factor_y = simplify((N_x - M_y) / M_expr)
            if candidate_factor_y.free_symbols.issubset({y}):
                mu_y = exp(integrate(candidate_factor_y, y))
                steps.append("$$\\textbf{Candidate integrating factor (function of y): } \\mu(y)= e^{\\int \\frac{N_x-M_y}{M}dy} = " + latex(mu_y) + "$$")
                new_M_y_candidate = simplify(mu_y * M_expr)
                new_N_y_candidate = simplify(mu_y * N_expr)
                new_M_y_candidate_diff = diff(new_M_y_candidate, y)
                new_N_y_candidate_diff = diff(new_N_y_candidate, x)
                steps.append("$$\\textbf{New M and N after multiplying by } \\mu(y):$$")
                steps.append("$$\\tilde{M}(x,y)= " + latex(new_M_y_candidate) + ",\\quad \\tilde{N}(x,y)= " + latex(new_N_y_candidate) + "$$")
                steps.append("$$\\frac{\\partial \\tilde{M}}{\\partial y}= " + latex(new_M_y_candidate_diff) + ",\\quad \\frac{\\partial \\tilde{N}}{\\partial x}= " + latex(new_N_y_candidate_diff) + "$$")
                if simplify(new_M_y_candidate_diff - new_N_y_candidate_diff) == 0:
                    steps.append("$$\\textbf{The ODE becomes exact when multiplied by } \\mu(y).$$")
                    if integrating_factor_used is None:
                        integrating_factor_used = ("y", mu_y, new_M_y_candidate, new_N_y_candidate)
                    else:
                        alt_if_message = "$$\\textbf{Note: An alternative integrating factor } \\mu(y)= " + latex(mu_y) + " \\textbf{ was also found.}$$"
                else:
                    steps.append("$$\\textbf{Warning: The ODE is still not exact with } \\mu(y).$$")
        
        # If an integrating factor worked, use it:
        if integrating_factor_used:
            if alt_if_message:
                steps.append(alt_if_message)
            factor_choice, mu_used, new_M, new_N = integrating_factor_used
            steps.append("$$\\textbf{Using integrating factor } \\mu(" + factor_choice + ")= " + latex(mu_used) + " \\textbf{ to solve the new exact ODE.}$$")
            steps.append("$$\\textbf{New ODE: } \\tilde{M}(x,y)dx + \\tilde{N}(x,y)dy = 0$$")
            steps.append(solve_exact_ode(new_M, new_N, x, y))
            return "\n".join(steps)
        # --- Homogeneity Check ---
        else:
            # Check if the ODE is homogeneous.
            M_t = simplify(M_expr.subs({x: t*x, y: t*y}))
            N_t = simplify(N_expr.subs({x: t*x, y: t*y}))
            ratio_M = None
            ratio_N = None
            if M_expr != 0:
                ratio_M = simplify(M_t / M_expr)
            if N_expr != 0:
                ratio_N = simplify(N_t / N_expr)
            if (ratio_M is not None and ratio_M.free_symbols.issubset({t}) and
                ratio_N is not None and ratio_N.free_symbols.issubset({t}) and
                simplify(ratio_M - ratio_N) == 0):
                steps.append("$$\\textbf{The ODE is homogeneous.}$$")
                steps.append("$$M(tx,ty)= " + latex(M_t) + "$$")
                steps.append("$$N(tx,ty)= " + latex(N_t) + "$$")
                steps.append("$$\\textbf{Apply the substitution } y=ux \\text{ (i.e., } u=y/x\\text{)}.$$")
                u = symbols("u")
                # Express M and N in terms of u: M(x,ux) and N(x,ux)
                M1_u = simplify(M_expr.subs({y: u*x}))
                N1_u = simplify(N_expr.subs({y: u*x}))
                steps.append("$$M(x,ux)= " + latex(M1_u) + "$$")
                steps.append("$$N(x,ux)= " + latex(N1_u) + "$$")
                # Under this substitution, note that:
                # dy/dx = u + x du/dx.
                # The ODE becomes:
                # M(x,ux) + N(x,ux) (u + x du/dx) = 0.
                # Rearranging:
                # x N(x,ux) du/dx = -[M(x,ux) + u N(x,ux)]
                # or: du/dx = -[M(x,ux) + u N(x,ux)]/[x N(x,ux)]
                new_ode = simplify(- (M1_u + u * N1_u) / (x * N1_u))
                steps.append("$$\\textbf{Transformed ODE: } \\frac{du}{dx} = \\frac{1}{x}\\,\\phi(u)$$")
                steps.append("$$\\phi(u)= " + latex(simplify(new_ode*x)) + "$$")
                # Formulate the new separable ODE as a string.
                # To reuse separable_solver, we temporarily replace u with y.
                new_eq_str = "dy/dx = (1/x)*(" + str(new_ode) + ")"
                steps.append("$$\\textbf{New separable ODE: } " + new_eq_str + "$$")
                u_sym = symbols("u")
                # Replace "dy/dx" with our separable format (it doesn't matter if the dependent variable is called y here).
                solution_separable = separable_solver(new_eq_str.replace("du/dx", "dy/dx").replace("u", "y"), x, u_sym)
                steps.append("$$\\textbf{Solution of the transformed ODE:}$$")
                steps.append(solution_separable)
                steps.append("$$\\textbf{Finally, substitute back } u=\\frac{y}{x} \\textbf{ in the solution.}$$")
                
                return "\n".join(steps)
            else:
                steps.append("$$\\textbf{No integrating factor of the form } \\mu(x) \\textbf{ or } \\mu(y) \\textbf{ could be found, and the ODE is not homogeneous.}$$")
                steps.append("$$\\textbf{It appears that the chosen method may not be applicable to this ODE.}$$")
                return "\n".join(steps)

def bernoulli_solver(eq_str, x):
    """
    Solves a Bernoulli ODE of the form:
         a(x) dy/dx + b(x)y = c(x)y^n
    where n is a natural number different from 0 and 1.

    Steps:
      1. Convert input string by replacing "dy/dx" with "y.diff(x)".
      2. Extract a(x) and b(x) from the left-hand side.
      3. From the right-hand side, extract c(x) and exponent n (using as_coeff_exponent on a dummy symbol).
         If n equals 0 or 1, return an error.
      4. Divide the equation by a(x) to get the standard form:
             dy/dx + P(x)y = Q(x)y^n,
         where P(x)= b(x)/a(x) and Q(x)= c(x)/a(x).
      5. Perform the substitution u = y^(1-n). Then,
             du/dx + (1-n)P(x)u = (1-n)Q(x),
         which is a linear ODE in u.
      6. Call linear_solver (by temporarily representing u as y in the string) to obtain the solution for u.
      7. Finally, instruct the user to substitute back u = y^(1-n) in the solution.
    """
    from sympy import sympify, simplify, symbols, Function, sin, cos, exp, diff, latex, integrate

    # Preprocess the input.
    eq_str = preprocess_input(eq_str)
    parts = eq_str.split("=")
    if len(parts) != 2:
        return "Error: The equation must contain exactly one '=' sign."
    lhs_str = parts[0].strip()
    rhs_str = parts[1].strip()

    if "dy/dx" not in lhs_str:
        return "Error: The left-hand side must contain 'dy/dx'."

    # Define y as a function of x.
    y_func = Function("y")
    y_expr = y_func(x)
    
    # For extraction of the exponent in the RHS, use a dummy symbol Y.
    Y = symbols("Y")

    # Replace dy/dx with y.diff(x) in the LHS.
    lhs_str = lhs_str.replace("dy/dx", "y.diff(x)")
    
    # Build the local dictionary for parsing.
    local_dict = {"x": x, "y": y_expr, "sin": sin, "cos": cos, "exp": exp}
    try:
        lhs_expr = sympify(lhs_str, locals=local_dict)
    except Exception as e:
        return "Error parsing LHS: " + str(e)
    try:
        rhs_expr = sympify(rhs_str, locals=local_dict)
    except Exception as e:
        return "Error parsing RHS: " + str(e)
    
    # Extract a(x) and b(x) from the LHS.
    a_expr = simplify(lhs_expr.coeff(y_expr.diff(x)))
    b_expr = simplify(lhs_expr.coeff(y_expr))
    if a_expr == 0:
        return "Error: a(x) is zero."
    
    # For the RHS, substitute y_expr with dummy symbol Y to extract coefficient and exponent.
    rhs_expr_sub = rhs_expr.subs(y_expr, Y)
    coeff_c, exponent_n = rhs_expr_sub.as_coeff_exponent(Y)
    # Check that exponent is not 0 or 1.
    if exponent_n == 0 or exponent_n == 1:
        return "Error: In Bernoulli equations, the exponent n must be different from 0 and 1."
    
    # Compute P(x) and Q(x): divide the equation by a(x).
    P_expr = simplify(b_expr / a_expr)
    Q_expr = simplify(coeff_c / a_expr)
    
    # Standard form: dy/dx + P(x)*y = Q(x)*y^n.
    # Under the substitution u = y^(1-n), we have:
    #     du/dx + (1-n)P(x)u = (1-n)Q(x)
    factor = 1 - exponent_n
    new_P = simplify(factor * P_expr)
    new_Q = simplify(factor * Q_expr)
    
    steps = []
    steps.append("$$\\textbf{Transformed Bernoulli ODE in u:}$$")
    steps.append("After dividing by a(x), the standard form is:")
    steps.append("$$\\frac{dy}{dx} + " + latex(P_expr) + " y = " + latex(Q_expr) + " y^{" + latex(exponent_n) + "}$$")
    steps.append("With the substitution \\(u = y^{1-" + latex(exponent_n) + "}\\), the ODE becomes:")
    steps.append("$$\\frac{du}{dx} + " + latex(new_P) + " u = " + latex(new_Q) + "$$")
    steps.append("We have computed (without showing all intermediate steps) that:")
    steps.append("$$\\frac{du}{dx} = \\frac{d}{dx}\\left(y^{1-" + latex(exponent_n) + "}\\right)$$")
    steps.append("The resulting ODE in \\(u\\) is linear and will be solved below.")
    
    # Build a new ODE string for the linear ODE in u.
    # For linear_solver, we temporarily represent u as y (the linear_solver expects "dy/dx" with dependent variable y).
    new_eq_str = "dy/dx + (" + str(new_P) + ")*y = " + str(new_Q)
    steps.append("$$\\textbf{Transformed linear ODE: } " + new_eq_str + "$$")
    
    # Solve the transformed linear ODE using our existing linear_solver.
    linear_solution = linear_solver(new_eq_str, x)
    steps.append("$$\\textbf{Solution of the transformed linear ODE:}$$")
    steps.append(linear_solution)
    steps.append("$$\\textbf{Finally, substitute back } u = y^{1-" + latex(exponent_n) + "} \\textbf{ in the solution.}$$")
    
    return "\n".join(steps)

def reduction_to_separation_solver(f_str, A_str, B_str, C_str, x):
    """
    Solves an ODE of the form:
         dy/dx = f(Ax + By + C)
    The user supplies the function f and constants A, B, and C.
    
    We use the substitution:
         u = Ax + By + C.
    Then, since du/dx = A + B*dy/dx, we have:
         dy/dx = (du/dx - A)/B   (with B ≠ 0).
    
    Replacing into the ODE gives:
         (du/dx - A)/B = f(u),
    or equivalently:
         du/dx = A + B f(u).
    
    This new separable ODE in u and x can be integrated:
         ∫ du/(A+B f(u)) = ∫ dx.
         
    Finally, we substitute back u = Ax+By+C to obtain the final answer.
    """
    from sympy import symbols, sympify, integrate, latex, simplify, sin, cos, exp

    # Parse constants A, B, C as provided by the user.
    try:
        A = sympify(A_str)
        B = sympify(B_str)
        C = sympify(C_str)
    except Exception as e:
        return "Error parsing constants A, B, C: " + str(e)
    if B == 0:
        return "Error: B cannot be zero for this method."
    print(A)
    print(B)
    print(C)

    # Define u as the substitution variable and define y as a symbol for display purposes.
    u = symbols("u")
    y = symbols("y")
    
    # Modify the input function string.
    # If the user enters, for example, "sinx" we want to treat it as "sin(u)".
    # So if f_str doesn't already involve "u", replace "x" with "u".
    f_str_modified = f_str
    if "u" not in f_str_modified:
        f_str_modified = f_str_modified.replace("x", "u")
    
    try:
        # Parse f(u) using the modified string.
        f_expr = sympify(f_str_modified, locals={"u": u, "sin": sin, "cos": cos, "exp": exp})
    except Exception as e:
        return "Error parsing f(u): " + str(e)

    steps = []
    steps.append("$$\\textbf{Reduction to Separation of Variables:}$$")
    
    # The original ODE is dy/dx = f(Ax+By+C). Substitute u = Ax+By+C.
    u_expr = A*x + B*y + C  # This will insert the actual values provided.
    steps.append("We start with the ODE:")
    # Here we substitute u_expr into f(u) so that the user sees the constants in place.
    steps.append("$$\\frac{dy}{dx} = " + latex(f_expr.subs(u, u_expr)) + "$$")
    
    steps.append("Apply the substitution:")
    steps.append("$$u = Ax + By + C = " + latex(u_expr) + "$$")
    steps.append("Differentiate with respect to \\(x\\):")
    steps.append("$$\\frac{du}{dx} = A + B\\frac{dy}{dx}.$$")
    steps.append("Solve for \\(\\frac{dy}{dx}\\):")
    steps.append("$$\\frac{dy}{dx} = \\frac{du/dx - A}{B}.$$")
    steps.append("Substitute this expression into the original ODE:")
    steps.append("$$\\frac{1}{B}\\frac{du}{dx} - \\frac{A}{B} = f(u).$$")
    steps.append("Multiply both sides by \\(B\\):")
    steps.append("$$\\frac{du}{dx} - {A} = B f(u),$$")
    steps.append("which gives:")
    steps.append("$$\\frac{du}{dx} = A + B f(u).$$")
    steps.append("This is now a separable ODE in \\(u\\) and \\(x\\):")
    steps.append("$$\\int \\frac{du}{A + B f(u)} = \\int dx.$$")
    
    try:
        integral_expr = integrate(1/(A+B*f_expr), u)
        integral_expr = simplify(integral_expr)
    except Exception as e:
        integral_expr = "Cannot compute the integral symbolically: " + str(e)
    
    steps.append("$$\\textbf{Result of integration:}$$")
    steps.append("$$\\int \\frac{du}{A+B f(u)} = " + latex(integral_expr) + " = x + C.$$")
    steps.append("Finally, substitute back \\(u = Ax+By+C\\) in the solution.")
    
    return "\n".join(steps)

# --- /solve Endpoint ---
@app.route("/solve", methods=["POST"])
def solve():
    global history_records
    try:
        data = request.get_json()
        method = data.get("method", "")
        order = data.get("order", "")
        
        if order != "1":
            return jsonify({"steps": "This is so cool.", "solution": ""})
        
        x = symbols("x")
        result = {}
        if method == "Separable":
            y_sym = symbols("y")
            eq_str = data.get("equation", "")
            result = separable_solver(eq_str, x, y_sym)
        elif method == "Linear":
            eq_str = data.get("equation", "")
            result = linear_solver(eq_str, x)
        elif method == "Exact / Integrating Factor / Homogeneous":
            M_input = data.get("Mxy", "")
            N_input = data.get("Nxy", "")
            y_sym = symbols("y")
            result = exact_integratingFactor_Homogenous_solver(M_input, N_input, x, y_sym)
        elif method == "Bernoulli":
            eq_str = data.get("equation", "")
            result = bernoulli_solver(eq_str, x)
        elif method == "Reduction to Separation of Variables":
            fInputVal = data.get("fInput", "")
            A_val = data.get("A", "")
            B_val = data.get("B", "")
            C_val = data.get("C", "")
            result = reduction_to_separation_solver(fInputVal, A_val, B_val, C_val, x)
        else:
            result = {"steps": "This method is not implemented in the new design.", "solution": ""}
        
        # Ensure result is a dictionary.
        if isinstance(result, str):
            result = {"steps": result, "solution": ""}
        
        # Construct user input string.
        if data.get("equation", ""):
            user_input = data.get("equation", "")
        else:
            parts = [data.get("Mxy", ""), data.get("Nxy", ""), data.get("fInput", "")]
            user_input = " ; ".join([p for p in parts if p]).strip(" ;")
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "solution": result.get("solution", "")
        }
        history_records.append(record)
        
        return jsonify(result)
    except Exception as e:
        error_msg = "Backend Error:\n" + traceback.format_exc()
        return jsonify({"steps": error_msg, "solution": ""})

# --- /history Endpoint ---
@app.route("/history", methods=["GET"])
def history_api():
    cutoff = datetime.now() - timedelta(days=120)  # roughly 4 months
    recent_history = [
        {"input": rec.get("input", ""), "solution": rec.get("solution", "")}
        for rec in history_records
        if datetime.fromisoformat(rec["timestamp"]) >= cutoff
    ]
    return jsonify({"history": recent_history}), 200

if __name__ == '__main__':
    print("🔥 Flask backend is starting...")
    app.run(port=5000, debug=True)





