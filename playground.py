import numpy as np

# Given values
magnSigma2 = 0.1
lengthScale = 0.1

# Calculate Pinf
Pinf = np.array([[magnSigma2, 0],
                 [0, 3 * magnSigma2 / lengthScale**2]])
print(Pinf)
