from flask import Flask, request, jsonify
from flask_cors import CORS
from sympy import symbols, sympify, integrate, Eq, latex, sin, cos, exp,tan,cot,sec,csc,cosh,log,sinh,tanh,sech,csch,ln,cbrt, Function, simplify, diff,sqrt,log,Matrix,Derivative
import traceback
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

x = symbols("x")
y = symbols("y")
dy = symbols("dy")
dx = symbols("dx")
y_prime = symbols("y'")
C = symbols("C")
def separable_solver(f_x_str, g_y_str):
    steps = []
    f_x = sympify(f_x_str)
    g_y = sympify(g_y_str)
    if g_y == 0: 
        steps.append(f"$ \\text{{Error: }} {latex(g_y)}  \\text{{ cannot be zero.}}$")
        return "\n".join(steps)
    eq = Eq(dy/dx, f_x*g_y)
    steps.append(f"$\\text{{You are solving the separable differential equation: }} {latex(eq)}.$")
    steps.append(f"$\\text{{Separate the equation! Put everything in terms of {latex(x)} on the right and everything in terms of {latex(y)} on the left.}}$")
    lhs = simplify(1/g_y)
    steps.append(f"$\\text{{Your differential equation is now: }} {latex(lhs)} dy = {latex(f_x)} dx.$")
    steps.append(f"$\\text{{Integrate both sides.}}$")
    G_y = simplify(integrate(lhs,y))
    steps.append(f"$\\int {latex(lhs)} dy= {latex(G_y)}.$")
    F_x = simplify(integrate(f_x,x))
    steps.append(f"$\\int {latex(f_x)} dx = {latex(F_x + C)}.$")
    eq = Eq(G_y, F_x + C)
    steps.append(f"$\\text{{The overall solution is therefore: }} {latex(eq)}.$")
    import sympy
    sol = sympy.solve(eq,y)
    eq = Eq(y, sol[0])
    steps.append(f"$\\text{{ which can be simplified to: }} {latex(eq)}.$")
    return "\n".join(steps)

def linear_solver(a_str,b_str,c_str):
    steps = []
    a_x = sympify(a_str)
    if a_x == 0: 
        steps.append(f"\\text{{Error: a(x) cannot be zero }}")
        return "\n".join(steps)
    b_x = sympify(b_str)
    c_x = sympify(c_str)
    eq = Eq(a_x*y_prime + b_x*y , c_x)
    steps.append(f"$\\text{{You are solving the differential equaiton: }} {latex(eq)}.$")
    P_x = b_x / a_x
    Q_x = c_x / a_x
    eq = Eq(y_prime + P_x*y, Q_x)
    if a_x != 1:
        steps.append(f"$\\text{{First make sure you divide by }} {latex(a_x)} \\text{{ to get the new equation: }} {latex(eq)}.$")
    steps.append(f"$\\text{{Proceed to compute an integrating factor: }}$")
    int_P_x = integrate(P_x,x)
    steps.append(f"$\\text{{start off by computing }} \\int {latex(P_x)} dx = {latex(int_P_x)}.$")
    mu = simplify(exp(int_P_x))
    steps.append(f"$\\text{{then an integrating factor is the exponential of the result we just obtained: }} \\mu =  {latex(mu)}.$")
    eq = Eq(mu*y_prime + mu*P_x*y, mu*Q_x)
    steps.append(f"$\\text{{From here multiply the integrating factor on both sides of the equation to get: }} {latex(eq)}.$")
    rhs = simplify(mu*Q_x)
    d = symbols("d")
    steps.append(f"$\\text{{which you can automatically rewrite as: }} {latex(d/dx)} [{latex(mu*y)}] = {latex(rhs)}.$")
    rhs = simplify(mu*Q_x)
    steps.append(f"$\\text{{From here, integrate both sides to get: }} {latex(mu*y)} = \\int {latex(rhs)} dx.$")
    rhs = simplify(integrate(rhs,x))
    eq = Eq(mu*y, rhs + C)
    steps.append(f"$\\text{{Which reduces to: }} {latex(eq)}.$")
    rhs = simplify((rhs + C)/ mu)
    eq = Eq(y, rhs)
    steps.append(f"$\\text{{Therefore, the overall solution is: }} {latex(eq)}.$")
    return "\n".join(steps)

def exact_integratingFactor_Homogenous_solver(M_str, N_str):
    steps = []
    def solve_exact_ode(M_xy, N_xy):
        steps.append(f"$\\text{{Recall that the potential function is a function}} f \\text{{ such that }} \\frac{{\\partial f}}{{\\partial x}} = M(x,y).$")
        steps.append(f"$\\text{{In this case, }} \\frac{{\\partial f}}{{\\partial x}} = {latex(M_xy)}.$")
        M = integrate(M_xy, x, conds = 'none')
        steps.append(f"$\\text{{Integrate both sides to get with respect to x: }} f(x,y) = {latex(M)} + h(y).$")
        steps.append(f"$\\text{{We added a function of y because we integrated with respect to x and any function of y is}}$")
        steps.append(f"$\\text{{constant in the eyes of x.}}$")
        M_y = diff(M,y)
        steps.append(f"$\\text{{We still need to find h(y). Differentiate both sides with respect to y to get: }} \\frac{{\\partial f}}{{\\partial y}} = {latex(M_y)} + h'(y).$")
        steps.append(f"$\\text{{But recall that }} \\frac{{\\partial f}}{{\\partial y}} = N(x,y) = {latex(N_xy)}.$")
        h_prime_y = simplify(N_xy - M_y)
        steps.append(f"$\\text{{Therefore, h'(y) = }} {latex(h_prime_y)}.$")
        h_y = integrate(h_prime_y,y, conds= 'none')
        steps.append(f"$\\text{{Integrating, we get h(y) = }} {latex(h_y)} + C.$")
        result = h_y + M
        steps.append(f"$\\text{{A potential function is therefore f(x,y) = }} {latex(result)}.$")
        steps.append(f"$\\text{{The overall solution is therefore: }} {latex(result)} = C.$")
        return "\n".join(steps)
    
    M_xy = sympify(M_str)
    N_xy = sympify(N_str)

    if M_xy == 0: 
        steps.append(f"$\\text{{Error: M(x,y) cannot be zero.}}$")
        return "\n".join(steps)
    if N_xy == 0: 
        steps.append(f"$\\text{{Error: N(x,y) cannot be zero.}}$")
        return "\n".join(steps)
    
    steps.append(f"$\\text{{You are solving the differential equaiton: }} ({latex(M_xy)} )dx +  ({latex(N_xy)}) dy = 0 .$")
    steps.append(f"$\\text{{Step 1: Check if it is exact.}}$")
    M_y = diff(M_xy, y)
    steps.append(f"$\\frac{{\\partial}}{{\\partial y}} ({latex(M_xy)}) = {latex(M_y)}.$")
    N_x = diff(N_xy, x)
    steps.append(f"$\\frac{{\\partial}}{{\\partial x}} ({latex(N_xy)})= {latex(N_x)}.$")
    
    if simplify(M_y - N_x) == 0:
        steps.append(f"$\\text{{Observe that }} \\frac{{\\partial}}{{\\partial y}} ({latex(M_xy)}) = \\frac{{\\partial}}{{\\partial x}} ({latex(N_xy)}).$")
        steps.append(f"$\\text{{Hence the ODE is exact! Proceed to find the potential function.}}$")
        solve_exact_ode(M_xy,N_xy)
        return "\n".join(steps)
    else:
        steps.append(f"$\\text{{The ODE is not exact! Proceed to step 2.}}$")
        steps.append(f"$\\text{{Step 2: Make the ODE exact via integrting factors.}}$")
        candidate_x = simplify((M_y - N_x) / (N_xy))
        m_y = symbols("M_y")
        n_x = symbols("N_x")
        n_xy = symbols("N")
        eq = Eq((m_y - n_x) / (n_xy), candidate_x)
        steps.append(f"$\\text{{Start off by computing the following: }} {latex(eq)}.$")
        if diff(candidate_x, y) == 0:
            steps.append(f"$\\text{{Notice that the computed quantitiy is only a function of x! Hence we can find an integrating factor.}}$")
            mu_x= simplify(integrate(candidate_x,x))
            steps.append(f"$\\text{{Integrate the latter quantity to get: }} {latex(mu_x)}.$")
            mu_x = simplify(exp(mu_x))
            steps.append(f"$\\text{{An integrating factor in this case is the exponential of what we just computed: }} {latex(mu_x)}.$")
            M_xy = simplify(mu_x * M_xy)
            N_xy = simplify(mu_x * N_xy)
            steps.append(f"$\\text{{Update M(x,y) and N(x,y) respectively to: }} {latex(M_xy)}, {latex(N_xy)}.$")
            steps.append(f"$\\text{{The resulting ODE is now exact!}}.$")
            solve_exact_ode(M_xy,N_xy)
            return "\n".join(steps)
        else: 
            steps.append(f"$\\text{{This integrating factor depends on both x and y. Try another one.}}$")
            candidate_y = simplify((N_x - M_y) / (M_xy))
            m = symbols("M")
            eq = Eq((n_x - m_y) / m, candidate_y)
            steps.append(f"$\\text{{Start off by computing the following: }} {latex(eq)}.$")
            if diff(candidate_y,x) == 0:
                steps.append(f"$\\text{{Notice that the computed quantitiy is only a function of y! Hence we can find an integrating factor.}}$")
                mu_y = simplify(integrate(candidate_y,y))
                steps.append(f"$\\text{{Integrate the latter quantity to get: }} {latex(mu_y)}.$")
                mu_y = simplify(exp(mu_y))
                steps.append(f"$\\text{{An integrating factor in this case is the exponential of what we just computed: }} {latex(mu_y)}.$")
                M_xy = simplify(mu_y * M_xy)
                N_xy = simplify(mu_y * N_xy)
                steps.append(f"$\\text{{Update M(x,y) and N(x,y) respectively to: }} {latex(M_xy)}, {latex(N_xy)}.$")
                steps.append(f"$\\text{{The resulting ODE is now exact!}}.$")
                solve_exact_ode(M_xy,N_xy)
                return "\n".join(steps)
            else:
                steps.append(f"$\\text{{Looks like there are no integrating factors! Proceed to step 3.}}$")
                t = symbols("t", positive=True)
                a = symbols("a")
                cool = simplify(t**a)
                steps.append(f"$\\text{{Check if the equation if Homogeneous, i.e, }} M(tx,ty) = {latex(cool)} M(x,y) \\text{{ and }} N(tx,ty) = {latex(cool)} N(x,y) $")
                M_t = simplify(M_xy.subs({x: t*x, y: t*y}))
                N_t = simplify(N_xy.subs({x: t*x, y: t*y}))
                steps.append(f"$\\text{{Compute M(tx,ty) to get: }} {latex(M_t)}.$")
                steps.append(f"$\\text{{Compute N(tx,ty) to get: }} {latex(N_t)}.$")
                ratio_M = simplify(M_t / M_xy)
                ratio_N = simplify(N_t / N_xy)
                if ratio_M.free_symbols.issubset({t}) and ratio_N.free_symbols.issubset({t}) and simplify(ratio_M - ratio_N) == 0:
                    u = symbols("u")
                    du = symbols("du")
                    eq = Eq(u, y/x)
                    steps.append(f"$\\text{{Notice that your ODE is Homogeneous which can be solved via the substitution: }} {latex(eq)}.$")
                    eq = Eq(u, y/x)
                    steps.append(f"$\\text{{Since }} {latex(eq)} \\text{{ then }} y = ux \\text{{ which means that }} dy = xdu + udx.$")
                    steps.append(f"$\\text{{From here, replace into the differential equaiton to get a new ODE: }}$")
                    M_ux = simplify(M_xy.subs({y: u*x}))
                    N_uy = simplify(N_xy.subs({y: u*x}))
                    steps.append(f"$ ({latex(M_ux)}) dx + ({latex(N_uy)}) (xdu + udx) = 0.$")
                    steps.append(f"$ ({latex(M_ux)}) dx + ({latex(N_uy*x)}) du + ({latex(N_uy*u)}) dx = 0.$")
                    steps.append(f"$ ({latex(M_ux + u*N_uy)}) dx + ({latex(N_uy*x)}) du = 0$")
                    cool = simplify(M_ux + u*N_uy)
                    steps.append(f"$ ({latex(cool)}) dx + ({latex(N_uy*x)}) du = 0$")
                    steps.append(f"$\\text{{and the latter differential equation is separable!}}$")
                    phi_u = simplify(-(M_ux + u*N_uy) / N_uy)
                    eq = Eq(du/dx, phi_u / x)
                    steps.append(f"$\\text{{Simplify, you will get that the new differential equation is: }} {latex(eq)}.$")
                    steps.append(f"$\\text{{Separate the equation! Put everything in terms of {latex(x)} on the right and everything in terms of {latex(u)} on the left.}}$")
                    eq = Eq(dx/x, phi_u)
                    steps.append(f"$\\text{{Your differential equation is now: }} {latex(eq)} du.$")
                    steps.append(f"$\\text{{Integrate both sides.}}$")
                    from sympy.assumptions import assuming
                    from sympy import Q
                    with assuming(Q.nonzero(x)):
                        G_u = simplify(integrate(phi_u,u,conds = 'none'))
                    steps.append(f"$\\int {latex(phi_u)} du =  {latex(G_u)}.$")
                    steps.append(f"$\\int \\frac{{{dx}}}{{x}} = {latex(log(x) + C)}.$")
                    eq = Eq(G_u, log(x) + C)
                    steps.append(f"$\\text{{So, we arrive at: }} {latex(eq)}.$")
                    lhs = G_u.subs({u: y/x})
                    eq = Eq(lhs, log(x) + C)
                    steps.append(f"$\\text{{Finally, replace u with }} \\frac{{{y}}}{{{x}}}  \\text{{ to get: }} {latex(eq)}.$")
                    return "\n".join(steps)
                else:
                    steps.append(f"$\\text{{It appears that the chosen method may not be applicable to this ODE.}}$")
                    return "\n".join(steps)

def bernoulli_solver(a_str,b_str,c_str,n):
    steps = []
    a_x = sympify(a_str)
    if a_x ==0 : 
        steps.append(f"$\\text{{Error: a(x) cannot be zero.}}$")
        return "\n".join(steps)
    n = sympify(n)
    if n == 0 or n == 1:
        steps.append(f"$\\text{{Error: n has to be a real number which is different than 0 and 1.}}$")
        return "\n".join(steps)
    
    b_x = sympify(b_str)
    c_x = sympify(c_str)
    eq = Eq(a_x*(y_prime) + b_x*y, c_x*y**n)
    steps.append(f"$\\text{{You are solving the differential equation: }} {latex(eq)}.$")
    u = symbols("u")
    eq = Eq(u, y**(1-n))
    steps.append(f"$\\text{{Solve this differential equaiton via the substituition: }} {latex(eq)}.$")
    steps.append(f"$\\text{{First, compute }} {latex(dy/dx)}.$")
    du = symbols("du")
    eq = Eq(du/dx, (1-n)*y**(-n)*y_prime)
    steps.append(f"$\\text{{Using the chain rule: }} {latex(eq)}.$")
    eq = Eq(y_prime, (1 / (1-n))*y**n)
    steps.append(f"$\\text{{Isolate }} {latex(y_prime)} \\text{{ to get: }} {latex(eq)} {latex(du/dx)}.$")
    u_prime = symbols("u'")
    eq = Eq((a_x / (1 - n))*y**n*u_prime + b_x*y, c_x*y**n)
    steps.append(f"$\\text{{Replace in the differential equation to get: }} {latex(eq)}.$")
    eq = Eq((a_x / (1 - n))*u_prime + b_x*y**(1-n), c_x)
    steps.append(f"$\\text{{Divide by }} {latex(y**n)} \\text{{ to get: }} {latex(eq)}.$")
    eq = Eq((a_x / (1 - n))*u_prime + b_x*u, c_x)
    steps.append(f"$\\text{{which reduces to: }} {latex(eq)}.$")
    steps.append(f"$\\text{{The latter ODE is linear!}}.$")
    a_x = a_x / (1 - n)
    P_x = b_x / a_x
    Q_x = c_x / a_x
    eq = Eq(u_prime + P_x*u, Q_x)
    if a_x != 1:
        steps.append(f"$\\text{{First make sure you divide by }} {latex(a_x)} \\text{{ to get the new equation: }} {latex(eq)}.$")
    steps.append(f"$\\text{{Proceed to compute the integrating factor: }}.$")
    int_P_x = integrate(P_x,x)
    steps.append(f"$\\text{{start off by computing }} \\int {latex(P_x)} dx = {latex(int_P_x)}.$")
    mu = simplify(exp(int_P_x))
    steps.append(f"$\\text{{Therefore, the integrating facotor is the exponential of the result we just obtained: }} \\mu =  {latex(mu)}.$")
    eq = Eq(mu*u_prime + mu*P_x*u, mu*Q_x)
    steps.append(f"$\\text{{From here multiply the integrating factor on both sides of the equation to get: }} {latex(eq)} $")
    d = symbols("d")
    steps.append(f"$\\text{{which you can automatically rewrite as: }} {latex(d/dx)} [ {latex(mu*u)} ] = {latex(mu*Q_x)}.$")
    rhs = simplify(mu*Q_x)
    steps.append(f"$\\text{{From here, integrate both sides to get: }} {latex(mu*y)} = \\int {latex(rhs)} dx.$")
    rhs = simplify(integrate(rhs,x))
    eq = Eq(mu*u, rhs + C)
    steps.append(f"$\\text{{Which reduces to: }} {latex(eq)}.$")
    rhs = simplify((rhs + C)/ mu)
    eq = Eq(u, rhs)
    steps.append(f"$\\text{{Therefore, solution is: }} {latex(eq)}.$")
    eq = Eq(y**(1-n), rhs)
    steps.append(f"$\\text{{Now replace u with what we took it to be: }} {latex(eq)}.$")
    rhs = simplify(rhs**(1/(1-n)))
    eq = Eq(y, rhs)
    steps.append(f"$\\text{{The overall solution is therefore: }} {latex(eq)}.$")
    return "\n".join(steps)

def reduction_to_separation_solver(f_str, A_str, B_str, C_str):
    steps = []
    B = sympify(B_str)
    if B == 0: 
        steps.append(f"$\\text{{This equation is separable!!}}$")
        return "\n".join(steps)
    A = sympify(A_str)
    C = sympify(C_str)
    f = sympify(f_str)
    f = f.subs({x: A*x + B*y + C})
    eq = Eq(y_prime, f)
    steps.append(f"$\\text{{You are solving the differential equation: }} {latex(eq)}.$")
    u = symbols("u")
    eq = Eq(u, A*x + B*y + C)
    steps.append(f"$\\text{{Start off by making the substitution }} {latex(eq)}.$")
    u_prime = symbols("u'")
    eq = Eq(u_prime, A + B*y_prime)
    steps.append(f"$\\text{{Then }} {latex(eq)}.$")
    eq = Eq(y_prime, (1/B)*u_prime - A/B)
    steps.append(f"$\\text{{Isolate {y_prime} to get: }} {latex(eq)}.$")
    f = f.subs({A*x + B*y + C: u})
    eq = Eq((1/B)*u_prime - A/B, f)
    steps.append(f"$\\text{{Which gives us the separable differential equation: }} {latex(eq)}.$")
    du = symbols("du")
    lhs = simplify((1 / ((A/B) + f)))
    steps.append(f"$\\text{{Isolate everything in terms of u on the left and in terms of x on the right to get }} {latex(lhs)} du = dx.$")
    lhs = integrate(lhs, u)
    c = symbols("c")
    eq = Eq(lhs, x + c)
    steps.append(f"$\\text{{Integrate both sides to get: }} {latex(eq)}.$")
    lhs = lhs.subs({u: A*x + B*y + C})
    eq = Eq(lhs, x+c)
    steps.append(f"$\\text{{Repalce u with what it is to get the overall solution: }} {latex(eq)}.$")
    return "\n".join(steps)

y = symbols("y")
y_double_prime = symbols("y''")
c_1 = symbols("c_1")
c_2 = symbols("c_2")
y_1 = symbols("y_1")
y_2 = symbols("y_2")
y_c_1 = symbols("y_c_1")
y_c_2 = symbols("y_c_2")
y_c = symbols("y_c")
y_p = symbols("y_p")

def homogeneous_reduction_of_order_solver(a_str,b_str,c_str,y1_str):
    steps = []
    a_x = sympify(a_str)
    if a_x == 0: 
        steps.append(f"$\\text{{Error:}} a(x) \\text{{cannot be zero.}} $")
        return "\n".join(steps)
    b_x = sympify(b_str)
    c_x = sympify(c_str)
    y_1 = sympify(y1_str)
    eq = Eq(a_x*y_double_prime + b_x*y_prime + c_x*y, 0)
    steps.append(f"$\\text{{You are using reduction of order to find a linearly independent solution }} {latex(y_2)} \\text{{ of the differential equation }}$")
    steps.append(f"${latex(eq)} \\text{{  given your solution  }} {latex(y_1)}.$")
    P_x = b_x
    Q_x = c_x
    if a_x != 1:
        P_x = simplify(b_x / a_x)
        Q_x = simplify(c_x / a_x)
        steps.append(f"$\\text{{First, make sure you divide by }} {latex(a_x)}.$")
        eq = Eq(y_double_prime + P_x*y_prime+Q_x*y, 0)
        steps.append(f"$\\text{{Your new differential equation is now: }} {latex(eq)}.$")
    int_P_x = simplify(integrate(P_x,x))
    steps.append(f"$\\text{{Now, start off by computing}} \\int {latex(P_x)} dx = {latex(int_P_x)}.$")
    y1_squared = y_1*y_1
    steps.append(f"$\\text{{From here, compute the following integral: }} \\int \\frac{{{latex(exp(-int_P_x))}}}{{{latex(y1_squared)}}} dx.$")
    simplify1 = simplify(exp(-int_P_x))
    simplify2 = simplify(simplify1 / y_1**2)
    steps.append(f"$\\text{{Which reduces to: }} \\int {latex(simplify2)} dx.$")
    simplify3 = simplify(integrate(simplify2,x))
    steps.append(f"$\\text{{Which reduces to: }} {latex(simplify3)} .$")
    overall_result = simplify(y_1*simplify3)
    steps.append(f"$\\text{{Therefore, the second linearly independent solution  }} {latex(y_2)} \\text{{  is: }} \\left( {latex(simplify3)} \\right) \\left( {latex(y_1)} \\right) = {latex(overall_result)}.$")
    return "\n".join(steps)

def homogeneous_constant_coefficients(a_str, b_str, c_str):
    steps = []
    a = sympify(a_str)
    if a == 0:
        steps.append(f"$\\text{{Error: a cannot be zero!}}$")
        return "\n".join(steps)
    b = sympify(b_str)
    c = sympify(c_str)
    if not a.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{a}} must be a constant.}}$")
        return "\n".join(steps)
    if not b.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{b}} must be a constant.}}$")
        return "\n".join(steps)
    if not c.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{c}} must be a constant.}}$")
        return "\n".join(steps)
    eq = Eq(a*y_double_prime + b*y_prime + c*y, 0)
    steps.append(f"$\\text{{You are solving the differential equaiton: }} {latex(eq)}.$")
    delta = b*b - 4*a*c 
    steps.append(f"$\\text{{Start off by computing }} \\Delta =  {latex(b**2)} - 4({latex(a)})({latex(c)}) = {delta}.$")
    if delta > 0: 
        m_1 = (-b + sqrt(delta)) / (2*a)
        m_2 = (-b - sqrt(delta)) / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta > 0 \\text{{, which means that the roots are:  }} m_1 = {latex(m_1)}, m_2 = {latex(m_2)}$")
        eq = Eq(y, c_1*exp(m_1*x) + c_2*exp(m_2*x))
    
    elif delta == 0: 
        m = -b / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta = 0, \\text{{, which means that there is only one root:}} {m}.$")
        eq = Eq(y_1, exp(m*x))
        steps.append(f"$\\text{{Thus, we have one solution: }} {latex(eq)}.$")
        steps.append(f"$\\text{{We still need to find }} {latex(y_2)}\\text{{ which is linearly independent to }} {latex(y_1)}.$")
        eq = Eq(y_2, x*y_1)
        steps.append(f"$\\text{{Apply reduction of order! It will always be the case that }} {latex(eq)}.$")
        steps.append(f"$\\text{{(Verify this using the reduction of order calculator)}}.$")
        eq = Eq(y_2, x*y_1)
        steps.append(f"$\\text{{Hence, the second solution is: }} {latex(eq)}.$")
        eq = Eq(y, c_1*exp(m*x) + c_2*x*exp(m*x))
    
    else:
        steps.append(f"$\\text{{In this case }} \\Delta < 0, \\text{{ which means that the roots are of the form }} \\alpha \\pm \\beta i.$")
        alpha = -b / (2*a)
        beta = sqrt(-delta) / 2*a
        steps.append(f"$\\text{{Calculate }} \\alpha \\text{{ and }} \\beta \\text{{ to get that: }} \\alpha = {latex(alpha)} \\text{{ and }} \\beta = {latex(beta)}.$")
        eq = Eq(y, x**alpha*(c_1*cos(beta*x) + c_2*sin(beta*x)))
    
    steps.append(f"$\\text{{Your overall solution is: }} {latex(eq)}.$")
    return "\n".join(steps)

def homogeneous_Cauchy_Euler(a_str, b_str, c_str):
    steps = []
    a = sympify(a_str)
    if a == 0:
        steps.append(f"$\\text{{Error: a cannot be zero!}}$")
        return "\n".join(steps)
    b = sympify(b_str)
    c = sympify(c_str)
    if not a.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{a}} must be a constant.}}$")
        return "\n".join(steps)
    if not b.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{b}} must be a constant.}}$")
        return "\n".join(steps)
    if not c.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{c}} must be a constant.}}$")
        return "\n".join(steps)
    eq = Eq(a*x**2*y_double_prime + b*x*y_prime  +c*y, 0)
    m = symbols("m")
    steps.append(f"$\\text{{You are solving the differential equaiton: }} {latex(eq)}.$")
    eq = Eq(y, x**m)
    steps.append(f"$\\text{{Start off by making the substitution }} {latex(eq)}.$")
    t = m-1
    s = m-2
    eq = Eq(a*x**2*m*(m-1) + b*x*m*x**t + c*x**m, 0)
    steps.append(f"${latex(eq)}.$")
    eq = Eq(a*m*(m-1)*x**m + b*m*x**m  +c*x**m, 0)
    steps.append(f"${latex(eq)}.$")
    eq = Eq(a*m*(m-1) + b*m + c, 0)
    steps.append(f"$\\text{{Cancel }} {latex(x**m)} \\text{{  provided }} x \\neq 0. \\text{{We get the new equation: }} {latex(eq)}. $")
    eq = Eq(a*m**2 + (b-a)*m + c, 0)
    steps.append(f"$\\text{{Which reduces to: }} {latex(eq)}.$")
    delta = (b - a)*(b - a) - 4*a*c
    steps.append(f"$\\text{{From here proceed as follows: }} \\Delta =  ({latex((b-a)**2)}) - 4({latex(a)})({latex(c)}) = {delta}.$")
    if delta > 0: 
        m_1 = (-(b-a) + sqrt(delta)) / (2*a)
        m_2 = (-(b-a) - sqrt(delta)) / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta > 0 \\text{{,which means that the roots are:  }} m_1 = {latex(m_1)}, m_2 = {latex(m_2)}$")
        eq = Eq(y, c_1*x**m_1 + c_2*x**m_2)
    elif delta == 0: 
        m = -b / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta = 0, \\text{{, which means that there is only one root:}} {m}.$")
        eq = Eq(y_1, x**m)
        steps.append(f"$\\text{{Thus, we have one solution: }} {latex(eq)}.$")
        steps.append(f"$\\text{{We still need to find }} {latex(y_2)} \\text{{ which is linearly independent to }} {latex(y_1)}.$")
        eq = Eq(y_2, log(x)*y_1)
        steps.append(f"$\\text{{Apply reduction of order! It will always be the case that }} {latex(eq)}.$")
        y_1 = x**m
        steps.append(f"$\\text{{(Verify this using the reduction of order calculator)}}.$")
        eq = Eq(y_2, y_1*log(x))
        steps.append(f"$\\text{{Hence, the second solution is: }} {latex(eq)}.$")
        y_2 = log(x)*y_1
        eq = Eq(y, c_1*y_1 + c_2*y_2)    
    else:
        steps.append(f"$\\text{{In this case }} \\Delta < 0, \\text{{ which means that the roots are of the form }} \\alpha \\pm \\beta i.$")
        alpha = -b / (2*a)
        beta = sqrt(-delta) / 2*a
        steps.append(f"$\\text{{Calculate }} \\alpha \\text{{ and }} \\beta \\text{{ to get that: }} \\alpha = {latex(alpha)} \\text{{ and }} \\beta = {latex(beta)}.$")
        eq = Eq(y, x**alpha*(c_1*cos(beta*log(x)) + c_2*sin(beta*log(x))))
    
    steps.append(f"$\\text{{The overall solution is therefore: }} {latex(eq)} $")
    return "\n".join(steps)

def variation_of_parameters(f_x, y1_x, y2_x, steps):
    y1_x_prime = diff(y1_x)
    y2_x_prime = diff(y2_x)
    W = Matrix([[y1_x, y2_x], [y1_x_prime, y2_x_prime]])
    W_1 = Matrix([[0, y2_x], [f_x, y2_x_prime]])
    W_2 = Matrix([[y1_x, 0], [y1_x_prime, f_x]])
    steps.append(f"$\\text{{Compute the determinant of each of the following matrices: }}.$")
    steps.append(f"$W = {latex(W)}, W_1 = {latex(W_1)}, W_2 = {latex(W_2)} $")
    detW = simplify(y1_x*y2_x_prime - y1_x_prime*y2_x)
    detW_1 = simplify(-f_x*y2_x)
    detW_2 = simplify(y1_x*f_x)
    steps.append(f"$\\text{{det}} W = ({latex(y1_x)})({latex(y2_x_prime)}) - ({latex(y1_x_prime)})({latex(y2_x)}) = {latex(detW)}.$")
    steps.append(f"$\\text{{det}} W_1 = (0)({latex(y2_x_prime)}) - ({latex(f_x)})({latex(y2_x)}) = {latex(detW_1)}.$")
    steps.append(f"$\\text{{det}} W_2 = ({latex(y1_x)})({latex(f_x)}) - ({latex(y1_x_prime)})({latex(0)}) = {latex(detW_2)}.$")
    u_1_prime = simplify((detW_1) / (detW))
    steps.append(f"$u_1' = \\frac{{det W_1}}{{det W}} = {latex(u_1_prime)}.$")
    u_2_prime = simplify((detW_2) / (detW))
    steps.append(f"$u_2' = \\frac{{det W_2}}{{det W}} = {latex(u_2_prime)}.$")
    u1 = simplify(integrate(u_1_prime,x))
    u2 = simplify(integrate(u_2_prime,x))
    steps.append(f"$\\text{{From here, integrate to get: }}$")
    steps.append(f"$u_1 = \\int {latex(u_1_prime)} dx = {latex(u1)}.$")
    steps.append(f"$u_2 = \\int {latex(u_2_prime)} dx = {latex(u2)}.$")
    eq = Eq(y_p, u1*y1_x + u2*y2_x)
    steps.append(f"$\\text{{The particular solution is then: }} {latex(eq)}.$")
    y_c = symbols("y_c")
    c_1 = symbols("c_1")
    c_2 = symbols("c_2")
    eq = Eq(y_c + y_p, c_1*y1_x + c_2*y2_x + u1*y1_x + u2*y2_x)
    steps.append(f"$\\text{{The overall solution is then: }} y = {latex(eq)}.$")

def NonHomogenous_constant_coefficient(a_str,b_str,c_str,f_str):
    steps = []
    a = sympify(a_str)
    if a == 0:
        steps.append(f"$\\text{{Error: a cannot be zero!}}$")
        return "\n".join(steps)
    b = sympify(b_str)
    c = sympify(c_str)
    f_x = sympify(f_str)
    if not a.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{a}} must be a constant.}}$")
        return "\n".join(steps)
    if not b.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{b}} must be a constant.}}$")
        return "\n".join(steps)
    if not c.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{c}} must be a constant.}}$")
        return "\n".join(steps)
    eq = Eq(a*y_double_prime + b*y_prime + c*y, f_x)
    steps.append(f"$\\text{{You are solving the differential equation: }} {latex(eq)}$")
    eq = Eq(a*y_double_prime + b*y_prime + c*y, 0)
    steps.append(f"$\\text{{The first step is to solve the homogeneous version of your differential equation: }} {latex(eq)} $")
    delta = b*b - 4*a*c 
    steps.append(f"$\\text{{Start off by computing }} \\Delta =  ({latex(b)})({latex(b)}) - 4({latex(a)})({latex(c)}) = {delta}.$")
    if delta > 0: 
        m_1 = (-b + sqrt(delta)) / (2*a)
        m_2 = (-b - sqrt(delta)) / (2*a)
        y_c_1 = exp(m_1*x)
        y_c_2 = exp(m_2*x)
        steps.append(f"$\\text{{In this case }} \\Delta > 0 \\text{{,which means that the roots are:  }} m_1 = {latex(m_1)}, m_2 = {latex(m_2)}$")
        eq = Eq(y_c, c_1*y_c_1 + c_2*y_c_2)
    elif delta == 0: 
        m = -b / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta = 0, \\text{{ which means that there is only one root:}} {m}.$")
        y_c_1 = exp(m*x)
        eq = Eq(y_1, y_c_1)
        steps.append(f"$\\text{{Thus, we have one solution: }} {latex(eq)}.$")
        steps.append(f"$\\text{{We still need to find }} {latex(y_2)} \\text{{ which is linearly independent to }} {latex(y_1)}.$")
        eq = Eq(y_2, x*y_1)
        steps.append(f"$\\text{{Apply reduction of order! It will always be the case that }} {latex(eq)}.$")
        steps.append(f"$\\text{{(Verify this using the reduction of order calculator)}}.$")
        y_c_2 = simplify(x*y_c_1)
        eq = Eq(y_2, y_c_2)
        steps.append(f"$\\text{{Hence, the second solution is: }} {latex(eq)}.$")
        eq = Eq(y_c, c_1*y_c_1 + c_2*y_c_2)
    else:
        steps.append(f"$\\text{{In this case }} \\Delta < 0, \\text{{ which means that the roots are of the form }} \\alpha \\pm \\beta i.$")
        alpha = -b / (2*a)
        beta = sqrt(-delta) / 2*a
        steps.append(f"$\\text{{Calculate }} \\alpha \\text{{ and }} \\beta \\text{{ to get that: }} \\alpha = {latex(alpha)} \\text{{ and }} \\beta = {latex(beta)}.$")
        y_c_1 = cos(beta*x)
        y_c_2 = sin(beta*x)
        eq = Eq(y_c, exp(alpha*x)*c_1*y_c_1 + c_2*y_c_2)
    steps.append(f"$\\text{{The solution is the homogeneous version of your differential equation is: }} {latex(eq)}.$")
    eq = Eq(a*y_double_prime + b*y_prime + c*y, f_x)
    steps.append(f"$\\text{{Proceed now to find}} {latex(y_p)} \\text{{ for the differential equation: }} {latex(eq)}$")
    if a != 1: 
            P = simplify(b / a)
            Q = simplify(c / a)
            f_x = simplify(f_x / a)
            eq = Eq(y_double_prime + P*y_prime + Q*y, 0)
            steps.append(f"$\\text{{Divide by {latex(a)} to get: }} {latex(eq)}.$")
    
    variation_of_parameters(f_x,y_c_1,y_c_2,steps)

    return "\n".join(steps)

def NonHomogeneous_Cauchy_Euler(a_str,b_str,c_str,f_str):
    steps = []
    a = sympify(a_str)
    if a == 0:
        steps.append(f"$\\text{{Error: a cannot be zero!}}$")
        return "\n".join(steps)
    b = sympify(b_str)
    c = sympify(c_str)
    f_x = sympify(f_str)
    if not a.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{a}} must be a constant.}}$")
        return "\n".join(steps)
    if not b.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{b}} must be a constant.}}$")
        return "\n".join(steps)
    if not c.is_constant():
        steps.append(f"$\\text{{Error: \\textbf{{c}} must be a constant.}}$")
        return "\n".join(steps)
    if f_x == 0:
        steps.append(f"$\\text{{Your equation is homogeneous, use the homogeneous calculator it would make it easier for me!.}}$")
        return "\n".join(steps)
    eq = Eq(a*x**2*y_double_prime + b*x*y_prime + c*y ,f_x)
    steps.append(f"$\\text{{You are solving the differential equaiton: }} {latex(eq)}.$")
    eq = Eq(a*x**2*y_double_prime + b*x*y_prime + c*y ,0)
    steps.append(f"$\\text{{The first step in solving your differential equation is solving the homogeneous version of it: }} {latex(eq)}.$")
    m = symbols("m")
    eq = Eq(y, x**m)
    steps.append(f"$\\text{{Start off by making the substitution }} {latex(eq)}.$")
    t = m-1
    s = m-2
    eq = Eq(a*x**2*m*(m-1)*x**s + b*x*m*x**t + c*x**m, 0)
    steps.append(f"${latex(eq)}$")
    eq = Eq(a*m*(m-1)*x**m + b*m*x**m + c*x**m, 0)
    steps.append(f"${latex(eq)}.$")
    eq = Eq(a*m*(m-1) + b*m + c, 0)
    steps.append(f"$\\text{{Cancel }} {latex(x**m)} \\text{{  provided }} x \\neq 0. \\text{{We get the new equation: }} {latex(eq)}. $")
    eq = Eq(a*m**2 + b*m - a*m + c, 0)
    steps.append(f"$\\text{{Which reduces to: }} {latex(eq)} $")
    delta = (b - a)*(b - a) - 4*a*c
    steps.append(f"$\\text{{From here proceed as follows: }} \\Delta =  {latex((b-a)**2)} - 4({latex(a)})({latex(c)}) = {delta}.$")
    if delta > 0: 
        m_1 = (-(b-a) + sqrt(delta)) / (2*a)
        m_2 = (-(b-a) - sqrt(delta)) / (2*a)
        steps.append(f"$\\text{{In this case }} \\Delta > 0 \\text{{,which means that the roots are:  }} m_1 = {latex(m_1)}, m_2 = {latex(m_2)}.$")
        y_c_1 = x**m_1
        y_c_2 = x**m_2
        eq = Eq(y_c,c_1*y_c_1 + c_2*y_c_2)
    elif delta == 0: 
        root = -b / (2*a)
        eq = Eq(m, root)
        steps.append(f"$\\text{{In this case }} \\Delta = 0 \\text{{, which means that there is only one root: }} {latex(eq)}.$")
        y_c_1 = x**root
        eq = Eq(y_1, y_c_1)
        steps.append(f"$\\text{{Thus, we have one solution: }} {latex(eq)}.$")
        steps.append(f"$\\text{{We still need to find }} {latex(y_2)} \\text{{ which is linearly independent to }} {latex(y_1)}.$")
        eq = Eq(y_2, log(x)*y_1)
        steps.append(f"$\\text{{Apply reduction of order! It will always be the case that }} {latex(eq)}.$")
        steps.append(f"$\\text{{(Verify this using the reduction of order calculator)}}.$")
        y_c_2 = simplify(log(x)*y_c_1)
        eq = Eq(y_2, y_c_2)
        steps.append(f"$\\text{{Hence, the second solution is: }} {latex(eq)}.$")
        eq = Eq(y_c, c_1*y_c_1+c_2*y_c_2)
    else:
        steps.append(f"$\\text{{In this case }} \\Delta < 0, \\text{{ which means that the roots are of the form }} \\alpha \\pm \\beta i.$")
        alpha = -b / (2*a)
        beta = sqrt(-delta) / 2*a
        steps.append(f"$\\text{{Calculate }} \\alpha \\text{{ and }} \\beta \\text{{ to get that: }} \\alpha = {latex(alpha)} \\text{{ and }} \\beta = {latex(beta)}.$")
        y_c_1 = cos(beta*log(x))
        y_c_2 = sin(beta*log(x))
        eq = Eq(y_c, c_1*x**alpha*y_c_1  +c_2*x**alpha*y_c_2)
    steps.append(f"$\\text{{Therefore, the solution to the homogeneous version of your differential equation is: }} {latex(eq)} $")
    eq = Eq(a*x**2*y_double_prime + b*x*y_prime + c*y, f_x)
    steps.append(f"$\\text{{Proceed now to find }} y_p \\text{{ for the differential equation: }} {latex(eq)}.$")
    avoid = a*x**2
    P = simplify(b / avoid)
    Q = simplify(c / avoid)
    f_x = simplify(f_x / avoid)
    eq = Eq(y_double_prime + P*y_prime + Q, f_x)
    steps.append(f"$\\text{{Divide by }} {latex(avoid)}   \\text{{ to get the new differential equation: }} {latex(eq)}.$")
    steps.append(f"$\\text{{Make sure to exclude zero from the domain of your solution.}}$")
    variation_of_parameters(f_x,y_c_1,y_c_2,steps)
    return "\n".join(steps)

def NonHomogeneous_Variation_of_Parameters(a_str,b_str,c_str,f_str,y_1_str,y_2_str):
    steps = []
    a_x = sympify(a_str)
    if a_x == 0: 
        steps.append(f"$\\text{{Error: a(x) cannot be zero.}}$")
        return "\n".join(steps)
    b_x = sympify(b_str)
    c_x = sympify(c_str)
    f_x = sympify(f_str)
    y1_x = sympify(y_1_str)
    y2_x = sympify(y_2_str)
    y_c = y1_x + y2_x
    eq = Eq(a_x*y_double_prime + b_x*y_prime + c_x*y, f_x)
    steps.append(f"$\\text{{You are solving the differential equation: }} {latex(eq)}. $")
    eq = Eq(a_x*y_double_prime + b_x*y_prime + c_x*y, 0)
    steps.append(f"$\\text{{The first step is to solve the homongenous version of your ODE: }} {latex(eq)}. $")
    eq = Eq(y_1, y1_x)
    steps.append(f"$\\text{{ which has two linearly independent solutions: }}$")
    steps.append(f"${latex(eq)}$")
    eq = Eq(y_2, y2_x)
    steps.append(f"${latex(eq)}$")
    P_x = b_x 
    Q_x = c_x 
    if a_x != 1:
        P_x = simplify(b_x / a_x)
        Q_x = simplify(c_x / a_x )
        f_x = simplify(f_x / a_x)
        eq = Eq(y_double_prime  +P_x*y_prime + Q_x*y, f_x)
        steps.append(f"$\\text{{First, divide by {latex(a_x)} to get: }} {latex(eq)}.$")
    variation_of_parameters(f_x,y1_x,y2_x,steps)
    return "\n".join(steps)
# --- /solve Endpoint ---
@app.route("/solve", methods=["POST"])
def solve():
    global history_records
    try:
        data = request.get_json()
        method = data.get("method", "")
        order  = data.get("order", "")
        result = None

        if order == "1":
            if method == "Separable":
                f_str = data.get("f","").strip()
                g_str = data.get("g","").strip()
                result = separable_solver(f_str, g_str)
                

            elif method == "Linear":
                a_str = data.get("a","").strip()
                b_str = data.get("b","").strip()
                c_str = data.get("c","").strip()
                result = linear_solver(a_str, b_str, c_str)
                

            elif method == "Exact / Integrating Factor / Homogeneous":
                M_str = data.get("M","").strip()
                N_str = data.get("N","").strip()
                result = exact_integratingFactor_Homogenous_solver(M_str, N_str)

            elif method == "Bernoulli":
                a_str = data.get("a","").strip()
                b_str = data.get("b","").strip()
                c_str = data.get("c","").strip()
                n = data.get("n", None)
                result = bernoulli_solver(a_str, b_str, c_str, n)

            elif method == "Reduction to Separation of Variables":
                    f_str = data.get("f","").strip()
                    A_str = data.get("A","").strip()
                    B_str = data.get("B","").strip()
                    C_str = data.get("C","").strip()
                    result = reduction_to_separation_solver(f_str, A_str, B_str, C_str)

            else:
                result = "This first-order method is not implemented."

        elif order == "2":
            a = data.get("a", "").strip()
            b = data.get("b", "").strip()
            c = data.get("c", "").strip()

            if method == "Homogeneous - Reduction of Order":
                y1 = data.get("y1", "").strip()
                result = homogeneous_reduction_of_order_solver(a, b, c, y1)

            elif method == "Homogeneous - Constant Coefficients":
                result = homogeneous_constant_coefficients(a, b, c)

            elif method == "Homogeneous - Cauchy-Euler":
                f = data.get("f","").strip()
                result = homogeneous_Cauchy_Euler(a, b, c,f)

            elif method == "Non-Homogeneous - Constant Coefficients":
                f = data.get("f", "").strip()
                result = NonHomogenous_constant_coefficient(a, b, c, f)

            elif method == "Non-Homogeneous - Cauchy-Euler":
                f = data.get("f", "").strip()
                result = NonHomogeneous_Cauchy_Euler(a, b, c, f)
            
            elif method == "Non-Homogeneous - Variation of Parameters":
                f_str  = data.get("f",  "").strip()
                y1_str = data.get("y1", "").strip()
                y2_str = data.get("y2", "").strip()
                result = NonHomogeneous_Variation_of_Parameters(a, b, c, f_str, y1_str, y2_str)

            else:
                result = "This second‑order method is not implemented."

        else:
            result = "Error: order must be '1' or '2'."

        # if helper returned a raw string, wrap it
        if isinstance(result, str):
            result = {"steps": result, "solution": ""}
        

        return jsonify(result)

    except Exception:
        tb = traceback.format_exc()
        print("❌ solve() exception:\n", tb)
        return jsonify({"steps": f"Backend Error:\n{tb}", "solution": ""})


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
