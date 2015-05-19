from engg.kalman_filter import KalmanFilter

import numpy as np

import random

class Voltmeter:
    def __init__(self, v, n):
        self.v = v
        self.n = n

    def v_bar(self):
        return random.gauss(self.v, self.n)

if __name__ == '__main__':
    A = np.matrix([1])
    H = np.matrix([1])
    B = np.matrix([0])
    Q = np.matrix([0.00001])
    R = np.matrix([0.1])
    x = np.matrix([0])
    P = np.matrix([1])

    kalman_filter = KalmanFilter(A, B, H, x, P, Q, R)
    voltmeter = Voltmeter(1.33, 0.23)

    max_n = 180
    arr_m = []
    arr_v = []
    arr_k = []

    for i in range(max_n):
        measured = voltmeter.v_bar()
        arr_m.append(measured)
        arr_v.append(voltmeter.v)
        arr_k.append(kalman_filter.get_current_state()[0,0])
        kalman_filter.step(np.matrix([0]), np.matrix([measured]))

    import pylab
    pylab.plot(
            range(max_n), arr_m, 'b',
            range(max_n), arr_v, 'r',
            range(max_n), arr_k, 'g'
            )
    pylab.xlabel('Time')
    pylab.ylabel('Voltage')
    pylab.title('Kalman Filter Test')
    pylab.legend(('measured', 'true voltage', 'output'))
    pylab.show()
