from collections import namedtuple

import numpy as np

class KalmanFilter:
    def __init__(self, A, B, H, x, P, Q, R):
        self.A = A        # State transition matrix
        self.B = B        # Control matrix
        self.H = H        # Observation matrix
        self.x = x        # state variable (i.v.)
        self.P = P        # covariance (i.v.)
        self.Q = Q        # Estimated error in process
        self.R = R        # Estimated error in measurements

    def get_current_state(self):
        return self.x

    def step(self, u, z):
        # Prediction
        x_predicted = self.A * self.x + self.B * u
        P_predicted = self.A * self.P * np.transpose(self.A) + self.Q
        # Observation
        x_delta = z - self.H * x_predicted
        P_delta = self.H * P_predicted * np.transpose(self.H) + self.R
        # Update
        K = P_predicted * np.transpose(self.H) * np.linalg.inv(P_delta)
        self.x = x_predicted + K * x_delta

        I = np.eye(self.x.shape[0])
        self.P = (I - K * self.H) * P_predicted

class KalmanFilterPair:
    def __init__(self, A, B, H, x, P, Q, R):
        self.A = A        # State transition matrix         2x2
        self.B = B        # Control matrix                  2x2
        self.H = H        # Observation matrix - price A    1x2
        self.x = x        # state variable (i.v.)           2x1
        self.P = P        # covariance (i.v.)               2*2
        self.Q = Q        # Estimated error in process      2*2
        self.R = R        # Estimated error in measurements 1

    def get_current_state(self):
        return self.x

    def step(self, z, H_update):
        u = np.matrix([[0],[0]])
        # overwrite Price of Stock A
        self.H = H_update                                               # 1x2
        # Prediction
        x_predicted = self.A * self.x + self.B * u                      # 2x1
        P_predicted = self.A * self.P * np.transpose(self.A) + self.Q   # 2x2
        # Observation
        x_delta = z - self.H * x_predicted                              # 1
        P_delta = self.H * P_predicted * np.transpose(self.H) + self.R  # 1
        # Update
        K = P_predicted * np.transpose(self.H) * np.linalg.inv(P_delta) # 2x1
        self.x = x_predicted + K * x_delta                              # 2x1

        I = np.eye(self.x.shape[0])
        self.P = (I - K * self.H) * P_predicted                         # 2x2
        # return spread
        return x_delta, P_delta

StepRtnVal = namedtuple('StepRtnVal',('err','sig','sd'))


class KalmanFilterPair2:
    def __init__(self, A, B, H, x, P, Q, R):
        self.A = A        # State transition matrix         2x2
        self.B = B        # Control matrix                  2x2
        self.H = H        # Observation matrix - price A    1x2
        self.x = x        # state variable (i.v.)           2x1
        self.P = P        # covariance (i.v.)               2*2
        self.Q = Q        # Estimated error in process      2*2
        self.R = R        # Estimated error in measurements 1

    def get_current_state(self):
        return self.x

    def get_x0(self):
        return self.x[0][0,0]

    def get_x1(self):
        return self.x[1][0,0]

    def get_hedge_ratio(self):
        return -1.0 / self.get_x0()

    def step(self, z_scalar, h0, h1 = 1.0):
        z = np.matrix(z_scalar)
        u = np.matrix([[0],[0]])
        # overwrite Price of Stock A
        self.H = np.matrix([h0, h1])                                    # 1x2
        # Prediction
        x_predicted = self.A * self.x + self.B * u                      # 2x1
        P_predicted = self.A * self.P * np.transpose(self.A) + self.Q   # 2x2
        # Observation
        x_delta = z - self.H * x_predicted                              # 1
        P_delta = self.H * P_predicted * np.transpose(self.H) + self.R  # 1
        # Update
        K = P_predicted * np.transpose(self.H) * np.linalg.inv(P_delta) # 2x1
        self.x = x_predicted + K * x_delta                              # 2x1

        I = np.eye(self.x.shape[0])
        self.P = (I - K * self.H) * P_predicted                         # 2x2
        # return spread
        return StepRtnVal(x_delta[0,0], P_delta[0,0], np.sqrt(np.abs(P_delta[0,0])))
