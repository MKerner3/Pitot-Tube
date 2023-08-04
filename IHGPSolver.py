# This code does GP regression from a sinc function and
# produces the results in Fig. 1 in the IHGP paper.

# ***Run full GP and infinite-horizon***

# Dependencies
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import gp_methods as gp

# ***Simulate Data***
np.random.seed(0)
sigma2 = 0.1
x = np.linspace(0, 6, num=100)
y = np.sin(6 - x) + np.sqrt(sigma2) * np.random.randn(len(x))
# y = np.sin(2*np.pi*x) + np.sqrt(sigma2)*np.random.randn(len(x))

# **Initial model parameters**

# Initial model parameters (sigma2, magnSigma2, lengthScale)
param = np.array([.1, .1, .1])


# **Set up full model**

# Covariance function (Matern, nu=3/2)
def k(r, p):
    return p[0]*(1+np.sqrt(3)*abs(r)/p[1]) * np.exp(-np.sqrt(3)*np.abs(r)/p[1])


# Derivatives of covariance function (Matern, nu=3/2)
dk = [
    lambda r, p: (1 + np.sqrt(3) * np.abs(r) / p[1]) *
    np.exp(-np.sqrt(3) * np.abs(r) / p[1]),
    lambda r, p: p[0] * 3 * r**2 / p[1]**3 *
    np.exp(-np.sqrt(3) * np.abs(r) / p[1])
]

# **Optimize hyperparameters and predict: Full GP**


# Optimization options

# Set the options using the 'options' parameter
# MATLAB version: options = {'GradpObj', 'on', 'display', 'iter'}
opts = {'disp': True, 'gtol': 1e-6}

# Initial guess for the optimization
initial_guess = np.log(param)

# Optimize hyperparameters w.r.t. log marginal likelihood
result = minimize(gp.gp_solve, initial_guess, args=(x, y, k, dk),
                  method='BFGS', options=opts)
w1 = result.x
ll = result.fun

# Solve
xt = x.tolist()
Eft1, Varft1, Covft1, lb1, ub1 = gp.gp_solve(w1, x, y, k, xt,
                                             return_likelihood=False)

# **Set up equivalent state space model**


# State space model
def ss(x, p):
    return gp.cf_matern32_to_ss(p[0], p[1])

# **Optimize hyperparameters and predict: IHGP**


# Objective function for optimization
def objective_function(w, x, y, ss):
    ihgpr_result = gp.ihgpr(w, x, y, ss)
    if all(value is not None for value in ihgpr_result):
        negated_result = tuple(-value for value in ihgpr_result)
        return negated_result
    else:
        return (-1e6,)


# Optimization options
# MATLAB version: options = {'GradpObj', 'on', 'display', 'iter'}
opts1 = {'disp': True, 'gtol': 1e-6}

# initial guess
initial_guess = np.log(param)

# Optimize hyperparameters w.r.t. log marginal likelihood
result = minimize(objective_function, initial_guess, args=(x, y, ss),
                  method='BFGS', options=opts1)
w2 = result.x
ll = -result.fun

# Solve Inifinite-Horizon GP regression problem
(Eft2, Varft2, Covft2, lb2, ub2, out) = gp.ihgpr(w2, x, y, ss, x)


# ***Visualize results***

# Create a new figure
plt.figure(2)
plt.clf()
plt.grid(True)

# Plot the IHGP mean and 95% confidence intervals
plt.fill_between(x, ub2, lb2, color='blue', edgecolor='blue',
                 label='95% quantiles')
plt.plot(x, Eft2, '-k', label='IHGP mean')

# Plot the full GP mean and confidence intervals (if available)
if Eft1 is not None:
    plt.plot(x, Eft1, '--', color='red', label='Full GP')
    plt.plot(x, lb1, '--', color='red')
    plt.plot(x, ub1, '--', color='red')

# Plot the true observations
plt.plot(x, y, '+k', markersize=3, label='Observations')

# Set plot labels and limits
plt.xlabel('Input, t')
plt.ylabel('Output, y')
plt.ylim(-1, 1.2)

# Add legend and grid
plt.legend(loc='upper right')
plt.grid(True)

# Show the plot
plt.show()
