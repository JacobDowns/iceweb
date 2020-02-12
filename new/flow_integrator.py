from scipy.integrate import ode
import numpy as np


'''
Class: FlowIntegrator
Integration class developed my Jake Downs. 


Dependencies: scipy ode
Creator: Jake Downs
Date created: Unknown
Last edited: 3/2/18
'''

class FlowIntegrator:
    def __init__(self, vx, vy):

        # Velocity components
        self.vx_data = vx
        self.vy_data = vy
        self.x_scale = 1.
        self.y_scale = 1.
        self.perpendicular = False
        
        # Velocity right hand side function
        def rhs(t, u):
            x = u[0]
            y = u[1]
            d = u[2]

            vx = self.x_scale * self.vx_data.interp(x, y, grid = False)
            vy = self.y_scale * self.vy_data.interp(x, y, grid = False)
            v_mag = np.sqrt(vx**2 + vy**2)
            #if (self.perpendicular):
            #    vx, vy = vy, vx

            return np.array([vx / v_mag,  vy / v_mag, v_mag])

        # ODE integrator
        self.integrator = ode(rhs).set_integrator('vode', method = 'adams')

        
    # Flowline integration
    def integrate(self, x0, y0, resolution, threshold, x_scale = 1., y_scale = 1., perpendicular = False):

        self.perpendicular = perpendicular
        self.x_scale = x_scale
        self.y_scale = y_scale

        flowline = []
        v_mags = []
        u0 = np.array([x0, y0, 0.])
        self.integrator.set_initial_value(u0, 0.0)

        vx = self.vx_data.interp(x0, y0, grid = False)
        vy = self.vy_data.interp(x0, y0, grid = False)
        v_mag = np.sqrt(vx**2 + vy**2)
        print("vx", vx, vy)
        print(v_mag)
        print()

        while self.integrator.successful() and v_mag > threshold:
            u = self.integrator.integrate(self.integrator.t + resolution)
            x, y  = u[0], u[1]
            vx = self.vx_data.interp(x, y, grid = False)
            vy = self.vx_data.interp(x, y, grid = False)
            v_mag = np.sqrt(vx**2 + vy**2)
            flowline.append([x, y])
            v_mags.append(v_mag)

        return flowline
