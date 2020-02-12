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
            if (self.perpendicular):
                vx, vy = vy, vx

            return np.array([vx / v_mag,  vy / v_mag, v_mag])

        # ODE integrator
        self.integrator = ode(rhs).set_integrator('dopri5')

        
    # Flowline integration
    def integrate(self, x0, y0, resolution, threshold, x_scale = 1., y_scale = 1., perpendicular = False, max_dist = 15e3):

        self.perpendicular = perpendicular
        self.x_scale = x_scale
        self.y_scale = y_scale

        flowline = []
        v_mags = []
        vx = self.vx_data.interp(x0, y0, grid = False)
        vy = self.vy_data.interp(x0, y0, grid = False)
        v_mag = np.sqrt(vx**2 + vy**2)
        u0 = np.array([x0, y0, 0.])
        dist = 0.
        
        flowline.append([x0, y0])

        if v_mag >= threshold:
            self.integrator.set_initial_value(u0, 0.0)
            

            while self.integrator.successful() and v_mag > threshold and dist <= max_dist:
                u = self.integrator.integrate(self.integrator.t + resolution)
                x, y  = u[0], u[1]
                vx = self.vx_data.interp(x, y, grid = False)
                vy = self.vx_data.interp(x, y, grid = False)
                v_mag = np.sqrt(vx**2 + vy**2)
                flowline.append([x, y])
                v_mags.append(v_mag)
                dist += resolution

        return flowline

    def integrate_flowline(self, x0, y0, resolution = 1., threshold = 7.5):

        # Integrate upstream 
        flow_d = self.integrate(x0, y0, resolution, threshold)
        # Integrate downstream 
        flow_u = self.integrate(x0, y0, resolution, threshold,
                                           x_scale = -1.,
                                           y_scale = -1.)
        # Return full flowline
        return np.concatenate((flow_u[::-1], flow_d[1:]))
        
