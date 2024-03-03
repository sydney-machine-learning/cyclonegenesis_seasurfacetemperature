import numpy as np
from scipy.stats import norm


noise = np.random.standard_normal(1000)
xs = np.linspace(-5,5, 1000)
ys = -2 * xs + noise

betas = np.linspace(-5, 5, 1000) 
log_sigmas = np.linspace(-10, 10, 1000)

## create a 1000 x 1000 array of heights
logls = np.zeros((1000, 1000))
# loop through rows - 
for i in range(1000):
    logls[i] = norm.logpdf(ys, 1)



## simple linear model:
## y = a + bx
# 
# 
## plot for different values of sigma and beta_1 