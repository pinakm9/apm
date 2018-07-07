import numpy as np
from scipy.special import erf 
import matplotlib.pyplot as plt

def C(x, y, z, Q = 1, u = 5, L = 3000, K = 1.5):
	r = K*x/u
	rr = np.sqrt(r)
	cy = erf((y + L/2)/rr) -  erf((y - L/2)/rr)
	cz = np.exp(-z**2/(4*r))
	return Q*cy*cz/(2*u*rr*np.sqrt(np.pi))


x = np.arange(0.1, 5, 0.1)
y = np.arange(-5, 5, 0.1)
x, y  = np.meshgrid(x, y)
c = C(x, y, 5)
plt.figure()
cp = plt.contourf(x, y, c)
plt.colorbar(cp)
plt.contour(x, y, c)

plt.show()