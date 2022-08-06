from time import time, sleep
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from scipy.signal import medfilt


def smoothing_factor(t_e, cutoff):
    r = 2 * np.pi * cutoff * t_e
    return r / (r + 1)


def exponential_smoothing(a, x, x_prev):
    return a * x + (1 - a) * x_prev


class OneEuroFilter:

    def __init__(self,
                 x0,
                 dx0=0.0,
                 min_cutoff=1.7,
                 beta=0.3,
                 d_cutoff=30.0,
                 fps=None):
        self.data_shape = x0.shape
        self.min_cutoff = np.full(x0.shape, min_cutoff)
        self.beta = np.full(x0.shape, beta)
        self.d_cutoff = np.full(x0.shape, d_cutoff)
        self.x_prev = x0.astype(np.float32)
        self.dx_prev = np.full(x0.shape, dx0)
        self.mask_prev = np.ma.masked_where(x0 <= 0, x0)
        self.realtime = True
        if fps is None:
            self.t_e = None
            self.skip_frame_factor = d_cutoff
            self.fps = d_cutoff
        else:
            self.realtime = False
            self.fps = float(fps)
            self.d_cutoff = np.full(x0.shape, self.fps)

        self.t_prev = time()

    def __call__(self, x, t_e=1.0):


        t = 0
        if self.realtime:
            t = time()
            t_e = (t - self.t_prev) * self.skip_frame_factor
        t_e = np.full(x.shape, t_e)

        mask = np.ma.masked_where(x <= 0, x)

        a_d = smoothing_factor(t_e / self.fps, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        a = smoothing_factor(t_e / self.fps, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)

        np.copyto(np.array(x_hat), -10, where=mask.mask)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        self.mask_prev = mask

        return x_hat


class GaussianFilter:

    def __init__(self, window_size: int = 5, sigma: float = 4.0):
        self.window_size = window_size
        self.sigma = sigma

    def __call__(self, x: np.ndarray):
        T = x.shape[0]
        if T < self.window_size:
            pad_width = [(self.window_size - T, 0), (0, 0), (0, 0)]
            x = np.pad(x, pad_width, mode='edge')
        smoothed = medfilt(x, (self.window_size, 1, 1))

        smoothed = gaussian_filter1d(smoothed, self.sigma, axis=0)
        return smoothed[-T:]