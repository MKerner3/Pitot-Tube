import numpy as np
from scipy.linalg import expm
from scipy.linalg import solve_discrete_are


def gp_solve(w, x, y, k, xt, return_likelihood=True):
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
    if xt is not None and return_likelihood is False:
        # Make additional covariance matrices
        K22 = k(np.subtract.outer(xt, xt), param[1:])
        K21 = k(np.subtract.outer(xt, x), param[1:])

        # Solve the mean
        Eft = K21 @ alpha

        # Solve the variance
        v = np.linalg.solve(L, K21.T)
        Varft = np.diag(K22) - np.sum(v**2, axis=0)

        # Solve the full covariance matrix
        Covft = K22 - np.dot(v.T, v)

        # Return 95% interval
        conf_interval = 1.96  # 95% confidence interval
        lb = Eft - conf_interval * np.sqrt(Varft)
        ub = Eft + conf_interval * np.sqrt(Varft)

        return (Eft, Varft, Covft, lb, ub)  # , (alpha, vv, L))
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
            # print('VALUES OF DK')
            # print(dk)

            # Allocate spaceS
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

            # Return: TODO figure if it is necessary or better to output/use eg
            return e  # (e, eg)
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
    # print(lambd)

    # Feedback matrix
    F = np.array([[0, 1], [-lambd**2, -2*lambd]])

    # Noise effect matrix
    L = np.array([[0], [1]])

    # Spectral density
    Qc = 12*np.sqrt(3)/lengthScale**3 * magnSigma2

    # Observation model
    H = np.array([[1, 0]])

    # Stationary Covariance

    # Calculate Pinf
    Pinf = np.array([[magnSigma2, 0],
                     [0, 3 * magnSigma2 / lengthScale**2]])

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

    # TODO check if params is needed anywhere
    return (F, L, Qc, H, Pinf, dF, dQc, dPinf)  # params


def ihgpr(w, x, y, ss, opt=None, w0=None, xt=None, filteronly=None):
    # *Check defaults*

    # is there test data
    if xt is None or filteronly is None or opt is None or w0 is None:
        xt = []

    # if nargs < 6
    if filteronly is None:
        filteronly = False

    if xt is not None and filteronly is not None and w0 is not None \
            and opt is not None:
        w0[opt] = w
        w = w0
    else:
        opt = np.ones_like(w, dtype=bool)

    # Figure out the correct way of dealing with the data
    xall = np.concatenate((x, xt))

    # Create an array of nan values with the same length as xt
    nan_array = np.full_like(xt, np.nan)

    # Vertically concatenate y and nan_array arrays
    yall = np.concatenate((y, nan_array))

    # Make sure the points are unique and in ascending order
    sort_ind = np.argsort(xall, kind='mergesort')
    xall = xall[sort_ind]
    yall = yall[sort_ind]

    # Only return test indices
    return_ind = sort_ind[-len(xt):]

    # Check
    if np.std(np.diff(xall)) > 1e-12:
        raise ValueError('This function only accepts \
                         equidistant inputs for now.')

    # *Set up model*

    # Log transformed parameters
    param = np.exp(w)

    # Extract values
    d = np.size(x)
    sigma2 = param[1]

    # print(x)
    # print(param[1:])
    # Form the state space model
    try:
        F, L, Qc, H, Pinf, dF, dQc, dPinf = ss(x, param[1:])
    except Exception:
        if xt is None:
            varargout = (np.nan, np.nan*param)
            return varargout
        else:
            raise ValueError('Problems with state space model.')

    # Concatenate derivatives
    dF = np.expand_dims(np.zeros_like(dF), axis=2)
    dF = np.concatenate((dF, dF), axis=2)

    dQc = np.expand_dims(np.zeros_like(dQc), axis=2)
    dQc = np.concatenate((dQc, dQc), axis=2)

    dPinf = np.expand_dims(np.zeros_like(dPinf), axis=2)
    dPinf = np.concatenate((dPinf, dPinf), axis=2)
    dR = np.zeros((1, 1, len(param)))
    dR[0, 0, 0] = 1

    # *Do the stationary stuff*

    # Parameters (this assumes the prior covariance function)
    # print(Pinf)

    dt = xall[1] - xall[0]
    A = expm(F * dt)
    Q = Pinf - A*Pinf*A.T
    Q = (Q+Q.T)/2
    # print(Q)
    R = sigma2

    # Solve the Riccatti equation for the predictive state covariance
    try:
        PP = solve_discrete_are(A.T, H.T, Q, R)
    except Exception:
        if xt is None:
            varargout = (np.nan, np.nan*param)
            return varargout
        else:
            raise ValueError('Unstable DARE solution!')

    # Test eigenvalues. Should they be less than and not equal to 1?
    eigP = np.linalg.eigvals(PP)
    eigA = np.linalg.eigvals(A)
    eigQ = np.linalg.eigvals(Q)
    # eigR = np.linalg.eigvals(R)
    # eigH = np.linalg.eigvals(H)
    # print('EIGENVALUES OF P, A, Q, R, H')
    # print(eigP)
    # print(eigA)
    # print(eigQ)
    # print(eigR)
    # print(eigH)

    # FIXME find a better method to check for unstable DARE solutions
    # https://github.com/AaltoML/IHGP/blob/master/matlab/ihgpr.m
    # Equivalent to line 149, (if report = -1)
    # Is there a better way to check for stability of the solution P? report
    # is not a return variable like in the matlab implementation.

    # Check the riccatti result
    # if np.any(np.abs
    #          (np.linalg.eigvals(A.T @ PP @ A - PP @ H.T @
    #                             np.linalg.solve
    #                             (R + H @ PP @ H.T, H @ PP @ A) + Q)) >= 1):
    #    raise ValueError('The Symplectic matrix has \
    #                     eigenvalues on the unit circle')

    # Innovation variance
    S = H @ PP @ H.T+R

    # Stationary gain
    K = PP @ H.T @ np.linalg.inv(S)

    # Precalculate
    AKHA = A-K @ H @ A

    # *Prediction of test inputs (filtering and smoothing)*

    # Check that we are predicting
    if xt is not None:
        # Set initial state
        m = np.zeros((F.shape[0], 1))
        PF = PP - K*H*PP

        # Allocate space for results
        MS = MS = np.zeros((m.shape[0], yall.shape[0]))
        PS = np.zeros((m.shape[0], m.shape[0], yall.shape[0]))

        # *Forward filter*

        # The filter recursion
        for k in range(yall.shape[0]):
            if not np.isnan(yall[k]):
                # The stationary filter recursion

                m = A @ (K @ (H @ (A @ (m + K * yall[k]))))  # O(m^2)

                # Store estimate
                MS[:, k] = m.flatten()
                PS[:, :, k] = PF  # This is the same for all points
            else:
                m = A @ m
                MS[:, k] = m
                PS[:, :, k] = Pinf

        # *Backward smoother*

        GS = None

        # Should we run the smoother?
        if not filteronly:
            # The gain and covariance
            (L, notpositivedefinite) = np.linalg.cholesky(PP).T, False
            G = PF @ A.T @ np.linalg.inv(L.T) @ np.linalg.inv(L)

            # Solve the Riccati equation
            QQ = PF - G @ PP @ G.T
            QQ = (QQ + QQ.T)/2

            RR = np.eye(QQ.shape[0])  # Identity matrix of the same size as QQ
            P = solve_discrete_are(G.T, np.zeros_like(G), QQ, RR)
            PS[:, :, -1] = P

            # Allocate space for storing the smoother gain matrix
            GS = np.zeros((F.shape[0], F.shape[1], yall.shape[0]))

            # print(MS[:, k].shape)
            # print(m.shape)
            # Rauch-Tung-Striebel smoother
            for k in range(MS.shape[1]-2, -1, -1):
                # Backward iteration
                m = MS[:, k].reshape(-1, 1) + \
                    G @ (m - A @ MS[:, k].reshape(-1, 1))  # O(m^2)

                # Store estimate
                MS[:, k] = m.flatten()
                PS[:, :, k] = P
                GS[:, :, k] = G

        # Output debug information
        # Define the Python dictionary
        out = {
            'K': K,
            'G': G,
            'S': S,
            'P': P,
            'PP': PP
        }

        # These indices will remain to be returned
        MS = MS[:, return_ind]
        PS = PS[:, :, return_ind]

        # Return mean
        Eft = H @ MS

        # Return variance
        Varft = np.zeros((H.shape[0], H.shape[0], MS.shape[1]))
        for k in range(MS.shape[1]):
            Varft[:, :, k] = H @ PS[:, :, k] @ H.T

        # Upper/lower 95% confidence
        # The bounds
        lb = Eft - 1.96 * np.sqrt(Varft)
        ub = Eft + 1.96 * np.sqrt(Varft)

        # return values
        Eft_flat = Eft.flatten()
        Varft_flat = Varft.flatten()
        lb_flat = lb.flatten()
        ub_flat = ub.flatten()

        # Wil not estimate the joint covariance matrix
        Covft = None

        varargout = (Eft_flat, Varft_flat, Covft, lb_flat, ub_flat, out)

    # *Evaluate negative log marginal likelihood and its gradient*
    if xt is None:
        # Size of inputs
        d = F.shape[0]
        nparam = len(param)

        # Allocate space for derivative matrices
        dA = np.zeros((d, d, nparam))
        dPP = np.zeros((d, d, nparam))
        dAKHA = np.zeros((d, d, nparam))
        dK = np.zeros((d, 1, nparam))
        dS = np.zeros((1, 1, nparam))
        HdA = np.zeros((d, nparam))

        # Precalculate Z and B
        Z = np.zeros(d)
        B = A @ K  # A @ PP @ H.T * np.linalg.inv(H @ PP @ H.T + R)

        for j in range(len(param)):
            # The first matrix for the matrix factor decomposition
            FF = np.array([F, Z],
                          [dF[:, :, j], F])

            # Solve the matrix exponential
            AA = expm(FF*dt)
            dA[:, :, j] = AA[d:, :d]
            dQ = dPinf[:, :, j] - dA[:, :, j] @ Pinf @ A.T - \
                A @ dPinf[:, :, j] @ A.T - A @ Pinf @ dA[:, :, j].T
            dQ = (dQ + dQ.T)/2

            # Precalculate C
            C = dA[:, :, j] @ PP @ A.T + A @ PP @ dA[:, :, j].T - \
                dA[:, :, j] @ PP @ H.T @ B.T - B @ H @ PP @ dA[:, :, j].T + \
                B @ dR[:, :, j] @ B.T + dQ
            C = (C+C.T)/2

            # Solve dPP
            try:
                dPP[:, :, j] = solve_discrete_are
                ((A-B*H).T, np.zeros((d, d)), C)
            except np.linalg.LinalgError:
                varargout = (np.nan, np.nan*param)
                return varargout

            # Evaluate dS and dK
            dS[:, :, j] = H @ dPP[:, :, j] @ H.T + dR[:, :, j]

            dK[:, :, j] = dPP[:, :, j] @ H.T @ \
                np.linalg.inv(S) - PP @ H.T @ np.linalg.inv(S) @ \
                (H @ dPP[:, :, j] @ H.T + dR[:, :, j]) @ np.linalg.inv(S)

            dAKHA[:, :, j] = dA[:, :, j] - \
                dK[:, :, j] @ H @ A - K @ H @ dA[:, :, j]

            HdA[:, j] = (H @ dA[:, :, j]).T

        # Reshape for vectorization
        dAKHAp = np.reshape(np.transpose(dAKHA, (0, 2, 1)), (-1, d))
        dKp = np.reshape(dK, (-1, nparam))

        # Size of inputs
        steps = len(yall)
        m = np.zeros(d, 1)
        dm = np.zeros(d, nparam)

        edata = 0.5 * np.log(2 * np.pi) * steps + 0.5 * \
            np.log(np.linalg.det(S)) * len(x)
        gdata = 0.5 * steps * np.sum(dS / S)

        for k in range(1, steps + 1):
            if y[k] is np.nan:
                # Innovation mean
                v = y[k] - H @ A @ m

                # Marginal likelihood (approximation)
                edata = edata + 0.5 * v**2 / S  # 0.5*np.sum(v/cS)**2

                # The same as above without the loop
                dv = -m @ HdA - H @ A @ dm
                gdata = gdata + v * dv / S - 0.5 * v**2 * dS / S**2
                dm = AKHA @ dm + dKp @ y[k]
                dm += dAKHAp @ m

                # The stationary filter recursion
                AKHA @ m + K @ y[k]

            else:
                for j in range(nparam):
                    dm[:, j] = A @ dm[:, j] + dA[:, :, j] @ m
                m = A @ m

        # Account for log-scale
        gdata = gdata * np.exp(w)

        # Return correct number of parameters
        gdata = gdata[opt]

        # Return negative log marginal likelihood and gradient
        varargout = (edata, gdata)
    return varargout
