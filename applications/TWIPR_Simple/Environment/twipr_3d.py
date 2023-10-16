class Twipr3D:
    model: TwiprModel

    def __init__(self, model, Ts, x0=None):
        self.Ts = Ts
        self.model = model

        self.n = 6
        self.p = 2
        self.q = 1

        if not (x0 is None):
            self.x0 = x0
        else:
            self.x0 = np.zeros(self.n)

        self.state = self.x0
        self.state_names = ['x', 'x_dot', 'theta', 'theta_dot', 'psi', 'psi_dot']
        self.K_cont = np.zeros((1, self.n))  # continous-time state controller
        self.K_disc = np.zeros((1, self.n))  # discrete-time state controller

        # get the linear continious model matrixes
        self.A, self.B, self.C, self.D = self.linear_model()
        # generate a linear continious model
        self.sys_cont = control.StateSpace(self.A, self.B, self.C, self.D, remove_useless=False)
        # convert the continious-time model to discrete-time
        self.sys_disc = control.c2d(self.sys_cont, self.Ts)
        self.A_d = np.asarray(self.sys_disc.A)
        self.B_d = np.asarray(self.sys_disc.B)
        self.C_d = np.asarray(self.sys_disc.C)
        self.D_d = np.asarray(self.sys_disc.D)

        self.A_hat = self.A
        self.A_hat_d = self.A_d

        self.ref_ctrl_is_set = False
        self.ref_ctrl_1 = lib_control.PidController(0, 0, 0, self.Ts)
        self.ref_ctrl_2 = lib_control.PidController(0, 0, 0, self.Ts)
        self.ref_ctrl_1_state_num = 0
        self.ref_ctrl_2_state_num = 0

    def linear_model(self):
        g = 9.81
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w
        D_33 = self.model.d_w / (2 * self.model.r_w ** 2) * self.model.c_alpha
        V_2 = self.model.I_z + 2 * self.model.I_w2 + (
                self.model.m_w + self.model.I_w / self.model.r_w ** 2) * self.model.d_w ** 2 / 2

        A = [[0, 1, 0, 0, 0, 0],
             [0, -D_11 / V_1, -C_11 * g / V_1, D_12 / V_1, 0, 0],
             [0, 0, 0, 1, 0, 0],
             [0, D_21 / V_1, C_21 * g / V_1, -D_22 / V_1, 0, 0],
             [0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, -D_33 / V_2]]

        B_1 = (self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l
        B_2 = self.model.m_b * self.model.l / self.model.r_w + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
        B_3 = self.model.d_w / (2 * self.model.r_w)

        B = [[0, 0],
             [B_1 / V_1, B_1 / V_1],
             [0, 0],
             [-B_2 / V_1, -B_2 / V_1],
             [0, 0],
             [-B_3 / V_2, B_3 / V_2]]

        C = [[0, 0, 1, 0, 0, 0]]

        D = [0, 0]

        return np.asarray(A), np.asarray(B), np.asarray(C), np.asarray(D)

    def set_eigenstructure(self, poles, eigenvectors):
        poles = np.asarray(poles)
        self.K_cont = lib_control.eigenstructure_assignment(self.A, self.B, poles, eigenvectors)
        self.K_disc = lib_control.eigenstructure_assignment(self.A_d, self.B_d, np.exp(poles * self.Ts), eigenvectors)

    def nonlinear_model(self, u):
        g = 9.81

        x = self.state[0]
        x_dot = self.state[1]
        theta = self.state[2]
        theta_dot = self.state[3]
        psi = self.state[4]
        psi_dot = self.state[5]

        C_12 = (self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l
        C_22 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2 * np.cos(
            theta) ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - 2 * self.model.m_b * self.model.l * np.cos(
            theta) * self.model.c_alpha / self.model.r_w
        B_2 = self.model.m_b * self.model.l / self.model.r_w * np.cos(
            theta) + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
        B_1 = (
                      self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta)
        C_31 = 2 * (self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta)
        C_32 = self.model.m_b * self.model.l
        D_33 = self.model.d_w ** 2 / (2 * self.model.r_w ** 2) * self.model.c_alpha
        V_2 = self.model.I_z + 2 * self.model.I_w2 + (
                self.model.m_w + self.model.I_w / self.model.r_w ** 2) * self.model.d_w ** 2 / 2 - (
                      self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.sin(theta) ** 2
        B_3 = self.model.d_w / (2 * self.model.r_w)
        C_13 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l + self.model.m_b * self.model.l * (
                       self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta) ** 2
        C_23 = (self.model.m_b ** 2 * self.model.l ** 2 + (
                self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                        self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2)) * np.cos(theta)

        state_dot = np.zeros(self.n)

        state_dot[0] = x_dot
        state_dot[1] = np.sin(theta) / V_1 * (
                -C_11 * g + C_12 * theta_dot ** 2 + C_13 * psi_dot ** 2) - D_11 / V_1 * x_dot + D_12 / V_1 * theta_dot + B_1 / V_1 * (
                               u[0] + u[1]) - self.model.tau_x * state_dot[0]
        state_dot[2] = theta_dot
        state_dot[3] = np.sin(theta) / V_1 * (
                C_21 * g - C_22 * theta ** 2 - C_23 * psi_dot ** 2) + D_21 / V_1 * x_dot - D_22 / V_1 * theta_dot - B_2 / V_1 * (
                               u[0] + u[1]) - self.model.tau_theta * state_dot[2]
        state_dot[4] = psi_dot
        state_dot[5] = np.sin(theta) / V_2 * (
                C_31 * theta_dot * psi_dot - C_32 * psi_dot * x_dot) - D_33 / V_2 * psi_dot - B_3 / V_2 * (
                               u[0] - u[1])

        return state_dot

    def set_reference_controller_pitch(self, P, I, D, state_num):
        self.ref_ctrl_is_set = True
        self.ref_ctrl_1_state_num = state_num
        self.ref_ctrl_1 = lib_control.PidController(P, I, D, self.Ts)

    def set_reference_controller_yaw(self, P, I, D, state_num):
        self.ref_ctrl_is_set = True
        self.ref_ctrl_2_state_num = state_num
        self.ref_ctrl_2 = lib_control.PidController(P, I, D, self.Ts)

    def __reference_controller(self, u):
        e_1 = u[0] - self.state[self.ref_ctrl_1_state_num]
        e_2 = u[1] - self.state[self.ref_ctrl_2_state_num]

        u_1 = self.ref_ctrl_1.calc(e_1)
        u_2 = self.ref_ctrl_2.calc(e_2)

        u = np.array([u_1 + u_2, u_1 - u_2])

        return u

    def __controller(self, u, mode):
        if self.ref_ctrl_is_set:
            u = self.__reference_controller(u)

        if mode == 'linear':
            u = u - self.K_disc @ self.state
        elif mode == 'nonlinear':
            u = u - self.K_cont @ self.state
        return u

    def __state_controller_linear(self, u):
        u = u - self.K_disc @ self.state
        return u

    def __state_controller_nonlinear(self, u):
        u = u - self.K_cont @ self.state
        return u

    def set_state(self, state):
        state = np.asarray(state, np.float)
        assert state.shape == (self.n,)
        self.state = state

    def simulate(self, u, mode, x0=None):
        # check the input and convert it to an array of appropriate size
        u = np.asarray(u)
        if len(u.shape) == 1:
            u = u[None, :]
        N = max(u.shape)
        if N < self.p:
            N = min(u.shape)
        u = u.reshape(self.p, N)

        # if an initial state is given, set the object state to the given state. If not, set the saved initial state
        if not (x0 is None):
            self.set_state(x0)
        else:
            self.set_state(self.x0)

        # reset the controllers and the saved input
        self.ref_ctrl_1.reset()
        self.ref_ctrl_2.reset()

        if mode == 'linear':
            [y_out, x_out] = self.__simulate_linear(u, N)
        elif mode == 'nonlinear':
            [y_out, x_out] = self.__simulate_nonlinear(u, N)
        else:
            raise Exception("Wrong type of simulation mode!")
        return y_out, x_out

    def simulate_step(self, u, mode):
        u = np.atleast_1d(np.asarray(u))  # convert the input to an ndarray
        assert u.shape == (self.p,) or u.shape == (self.p, 1)

        y_out = []
        x_out = []
        if mode == 'linear':
            [y_out, x_out] = self.__simulate_step_linear(u)
        elif mode == 'nonlinear':
            [y_out, x_out] = self.__simulate_step_nonlinear(u)
        return y_out, x_out

    def reset(self):
        self.state = self.x0
        self.ref_ctrl_1.reset()
        self.ref_ctrl_2.reset()

    def __simulate_linear(self, u, N):
        y_out = np.zeros((self.q, N))
        x_out = np.zeros((self.n, N))

        x_out[:, 0] = self.state
        y_out[:, 0] = self.C @ self.state

        for k in range(1, N):
            [y_out[:, k], x_out[:, k]] = self.__simulate_step_linear(u[:, k - 1])
        return y_out, x_out

    def __simulate_nonlinear(self, u, N):
        y_out = np.zeros((self.q, N))
        x_out = np.zeros((self.n, N))

        x_out[:, 0] = self.state
        y_out[:, 0] = self.C @ self.state

        for k in range(1, N):
            [y_out[:, k], x_out[:, k]] = self.__simulate_step_nonlinear(u[:, k - 1])
        return y_out, x_out

    def __simulate_step_linear(self, w):
        u = self.__controller(w, 'linear')
        self.state = self.A_d @ self.state + self.B_d @ u
        x_out = self.state
        y_out = self.C @ self.state

        return y_out, x_out

    def __simulate_step_nonlinear(self, w):
        u = self.__controller(w, 'nonlinear')
        x_dot = self.nonlinear_model(u)
        self.state = self.state + x_dot * self.Ts
        x_out = self.state
        y_out = self.C @ self.state
        return y_out, x_out
