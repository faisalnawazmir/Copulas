import numpy as np

from copulas.bivariate.base import Bivariate, CopulaTypes


class Clayton(Bivariate):
    """Class for clayton copula model."""

    copula_type = CopulaTypes.CLAYTON
    theta_interval = [-1, float('inf')]
    invalid_thetas = [0]

    def generator(self, t):
        r"""Compute the generator function for Clayton copula family.

        The generator is a function :math:`\psi: [0,1]\times\Theta \rightarrow [0, \infty)`
        that given an Archimedian copula fulills:

        .. math:: C(u,v) = \psi^{-1}(\psi(u) + \psi(v))

        Args:
            t (numpy.ndarray)

        Returns:
            numpy.ndarray

        """
        self.check_fit()

        return (1.0 / self.theta) * (np.power(t, -self.theta) - 1)

    def probability_density(self, X):
        r"""Compute probability density function for given copula family.

        The probability density(PDF) for the Clayton family of copulas correspond to the formula:

        .. math:: c(U,V) = \frac{\partial^2}{\partial v \partial u}C(u,v) =
            (\theta + 1)(uv)^{-\theta-1}(u^{-\theta} +
            v^{-\theta} - 1)^{-\frac{2\theta + 1}{\theta}}

        Args:
            X (numpy.ndarray)

        Returns:
            numpy.ndarray: Probability density for the input values.

        """
        self.check_fit()

        U, V = self.split_matrix(X)

        a = (self.theta + 1) * np.power(np.multiply(U, V), -(self.theta + 1))
        b = np.power(U, -self.theta) + np.power(V, -self.theta) - 1
        c = -(2 * self.theta + 1) / self.theta
        return a * np.power(b, c)

    def cumulative_distribution(self, X):
        """Compute the cumulative distribution function for the clayton copula.

        The cumulative density(cdf), or distribution function for the Clayton family of copulas
        correspond to the formula:

        .. math:: C(u,v) = max[(u^{-θ} + v^{-θ} - 1),0]^{-1/θ}

        Args:
            X (numpy.ndarray)

        Returns:
            numpy.ndarray: cumulative probability.

        """
        self.check_fit()

        U, V = self.split_matrix(X)

        if (V == 0).all() or (U == 0).all():
            return np.zeros(V.shape[0])

        else:
            cdfs = [
                np.power(
                    np.power(U[i], -self.theta) + np.power(V[i], -self.theta) - 1,
                    -1.0 / self.theta
                )
                if (U[i] > 0 and V[i] > 0) else 0
                for i in range(len(U))
            ]

            return np.array([max(x, 0) for x in cdfs])

    def percent_point(self, y, V):
        """Compute the inverse of conditional cumulative distribution :math:`C(u|v)^{-1}`.

        The percent point is the

        Args:
            y (numpy.ndarray): Value of :math:`C(u|v)`.
            v (numpy.ndarray): given value of v.
        """
        self.check_fit()

        if self.theta < 0:
            return V

        else:
            a = np.power(y, self.theta / (-1 - self.theta))
            b = np.power(V, self.theta)
            u = np.power((a + b - 1) / b, -1 / self.theta)
            return u

    def partial_derivative(self, X, y=0):
        r"""Compute partial derivative of cumulative distribution.

        The partial derivative of the copula(CDF) is the value of the conditional probability.

        .. math:: F(v|u) = \frac{\partial C(u,v)}{\partial u} =
            u^{- \theta - 1}(u^{-\theta} + v^{-\theta} - 1)^{-\frac{\theta+1}{\theta}}

        Args:
            X (np.ndarray)
            y (float)

        Returns:
            numpy.ndarray: Derivatives

        """
        self.check_fit()

        U, V = self.split_matrix(X)

        if self.theta == 0:
            return V

        else:
            A = np.power(V, -self.theta - 1)
            B = np.power(V, -self.theta) + np.power(U, -self.theta) - 1
            h = np.power(B, (-1 - self.theta) / self.theta)
            return np.multiply(A, h) - y

    def compute_theta(self):
        r"""Compute theta parameter using Kendall's tau.

        On Clayton copula this is

        .. math:: τ = θ/(θ + 2) \implies θ = 2τ/(1-τ)
        .. math:: θ ∈ (0, ∞)

        On the corner case of :math:`τ = 1`, a big enough number is returned instead of infinity.
        """
        if self.tau == 1:
            theta = 10000

        else:
            theta = 2 * self.tau / (1 - self.tau)

        return theta
