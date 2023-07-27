import numpy as np


def gp_solve(w, x, y, k, xt):
    # Log transformed parameters
    param = np.exp(w)

    # Extract values
    n = np.size(x)
    sigma2 = param[0]

    # Compute the pairwise differences between points in x
    x_diff = np.subtract.outer(x, x)

    # Evaluate covariance matrix
    K11 = k(x_diff, param[1:]) + np.eye(len(x)) * sigma2

    # Solve Cholesky factor
    try:
        L = np.linalg.cholesky(K11)
        p = 0
    # Not psd
    except np.linalg.LinAlgError:
        # Add jitter and try again
        jitter = 1e-9 * np.diag(np.random.rand(n))
        try:
            L = np.linalg.cholesky(K11+jitter)
        except np.linalg.LinAlgError:
            # Still no luck
            return (np.nan, np.nan*w)

    # Evaluate quantities

    # Solve L * vv = y
    vv = np.linalg.solve(L, y)

    # Solve L' * alpha = vv
    alpha = np.linalg.solve(L.T, vv)

    # Do prediction
    if xt is not None and not isinstance(xt, list):
        # Make additional covariance matrices
        K22 = k(np.subtract.outer(xt, xt), param[1:])
        K21 = k(np.subtract.outer(xt, x), param[1:])

        # Solve the mean
        Eft = K21 * alpha

        # Solve the variance
        v = np.linalg.solve(L, K21.T)
        Varft = np.diag(K22) - np.sum(v**2, axis=0)

        # Solve the full covariance matrix
        Covft = K22 - np.dot(v.T, v)

        # Return 95% interval
        conf_interval = 1.96  # 95% confidence interval
        lb = Eft - conf_interval * np.sqrt(Varft)
        ub = Eft + conf_interval * np.sqrt(Varft)

        return (Eft, Varft, Covft, lb, ub, (alpha, vv, L))
    # Evaluate marginal likelihood
    else:

        # Solve beta
        beta1 = np.dot(vv.T, vv)

        # The negative log marginal likelihood
        e = n/2*np.log(2*np.pi) + np.sum(np.log(np.diag(L))) + 1/2*beta1

        # Calculate gradients
        if xt is not None:
            # Catch the derivatives
            dk = xt

            # Allocate space
            eg = np.zeros(len(param))

            # Derivative w.r.t. sigma2

            # Compute the inverse of invK
            L_invK = np.linalg.solve(L.T, np.eye(n))
            invK = np.linalg.solve(L, L_invK)

            eg[0] = 0.5 * np.trace(invK) - 0.5 * np.dot(alpha.T, alpha)

            # The rest of the params
            for j in range(len(param) - 1):
                # Compute dK using the derivative function dk{j}
                dK = dk[j](np.subtract.outer(x, x), param[1:])

                # Compute the elements of eg
                eg[j + 1] = 0.5 * np.sum(invK * dK) - \
                    0.5 * np.dot(alpha.T, np.dot(dK, alpha))

            # Return derivatives
            eg = eg * np.exp(w)

            # Return
            return {e, eg}
        else:
            return e


def cf_matern32_to_ss(magnSigma2, lengthScale):
    # Check if input args are none
    if magnSigma2 is None:
        magnSigma2 = 1
    if lengthScale is None:
        lengthScale = 1

    # Form state space model
    lambd = np.sqrt(3)/lengthScale

    # Feedback matrix
    F = np.array([0, 1],
                 [-lambd**2, -2*lambd])

    # Noise effect matrix
    L = np.array([0],
                 [1])

    # Spectral density
    Qc = 12*np.sqrt(3)/lengthScale**3 * magnSigma2

    # Observation model
    H = np.array([1, 0])

    # Stationary Covariance

    # Calculate Pinf
    Pinf = np.array([magnSigma2, 0],
                    0, 3*magnSigma2/lengthScale**2)

    # Calculate derivatives
    dFmagnSigma2 = np.array([[0, 0],
                            [0, 0]])

    dFlengthScale = np.array([[0, 0],
                             [6 / lengthScale**3, 2 * np.sqrt(3)
                             / lengthScale**2]])

    dQcmagnSigma2 = 12 * np.sqrt(3) / lengthScale**3

    dQclengthScale = -3 * 12 * np.sqrt(3) / lengthScale**4 * magnSigma2

    dPinfmagnSigma2 = np.array([[1, 0],
                               [0, 3 / lengthScale**2]])

    dPinflengthScale = np.array([[0, 0],
                                [0, -6 * magnSigma2 / lengthScale**3]])

    # Stack all derivatives into multi-dimensional arrays
    dF = np.dstack((dFmagnSigma2, dFlengthScale))
    dQc = np.array([[dQcmagnSigma2, dQclengthScale]])
    dPinf = np.dstack((dPinfmagnSigma2, dPinflengthScale))

    # Return parameter names
    stationary = True

    # Input parameter information
    params = {
        'stationary': stationary,
        'in': [
            {'name': 'magnSigma2', 'default': 1, 'opt': True},
            {'name': 'lengthScale', 'default': 1, 'opt': True}
        ]
    }

    return (F, L, Qc, H, Pinf, dF, dQc, dPinf, params)


def ihgpr(w, x, y, ss, xt, filteronly, opt, w0):

    return
