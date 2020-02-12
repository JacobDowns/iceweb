from flask import Flask, render_template, redirect, url_for,request
from flask import make_response, jsonify
from flask_cors import CORS
from data_manager import create_datasets
from flow_integrator import FlowIntegrator
#from scipy.interpolate 
import pandas as pd
import numpy as np
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "hi"
@app.route("/index")

@app.route('/map_click', methods=['POST'])
def map_click():
    if request.method == 'POST':

        data = request.json

        ### Get flowline coordinates
        ##############################################################

        # Selected points
        x = float(data['x'])
        y = float(data['y'])

        # Integrate upstream and downstream to form a full flowline
        flow_d = flow_integrator.integrate(x, y, resolution = 1.,
                                                    threshold = 4.)
        flow_u = flow_integrator.integrate(x, y, resolution = 1.,
                                                    threshold = 4.,
                                                    x_scale = -1.,
                                                    y_scale = -1.)
        flowline = np.concatenate((flow_u[::-1], [[x, y]], flow_d))
      

        # Along flow length 
        #segment_lens = np.sqrt((xs[1:] - xs[:-1])**2 + (ys[1:] - ys[:-1])**2)
        #Ls = np.insert(segment_lens.cumsum(), 0, 0.)


        ### Width average
        ##############################################################

        # Integrate perpendicular to flow
        start_index = -20
        start_x = flowline[start_index][0]
        start_y = flowline[start_index][1]
        
        
        flow_p1 = flow_integrator.integrate(start_x, start_y,
                                                      resolution = .5,
                                                      threshold = 1.,
                                                      max_dist = 20.,
                                                      perpendicular = True)
        flow_p2 = flow_integrator.integrate(start_x, start_y,
                                                      resolution = 1.,
                                                      threshold = 1.,
                                                      x_scale = -1.,
                                                      y_scale = -1.,
                                                      max_dist = 20.,
                                                      perpendicular = True)
        flow_p = np.concatenate((flow_p1[::-1], [[start_x, start_y]], flow_p2))


        # Get velocity along perpendicular
        perp_vel = datasets['velocity'].interp(flow_p[:,0], flow_p[:,1],
                                            grid = False)
        perp_vel = pd.DataFrame(np.c_[np.linspace(0.,1.,len(perp_vel)), perp_vel], columns = ['x', 'y'])

        print(perp_vel.to_dict(orient = 'records'))
        
        ### Return json data
        ##############################################################

        flowline = flowline[:, ::-1]
        flow_p = flow_p[:, ::-1]
        return_data = {'flow_coords' : flowline.tolist(),
                       'perp_coords' : flow_p.tolist(),
                       'perp_vel' : perp_vel.to_dict(orient = 'records')
        }
        
        return return_data



@app.route('/get_data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        data = request.json
        data_frame = pd.DataFrame(data)
        #print(dir(data_frame['lng'].to_list()))
        
        xs = data_frame['lng'].to_numpy()
        ys = data_frame['lat'].to_numpy()

        B = datasets['bed'].interp(xs, ys, grid = False)
        S = datasets['surface'].interp(xs, ys, grid = False)
        H = datasets['thickness'].interp(xs, ys, grid = False)
        Bhat = S - H
        
        segment_lens = np.sqrt((xs[1:] - xs[:-1])**2 + (ys[1:] - ys[:-1])**2)
        Ls = np.insert(segment_lens.cumsum(), 0, 0.)

        B_return = pd.DataFrame(np.c_[Ls, B], columns = ['x', 'y'])
        S_return = pd.DataFrame(np.c_[Ls, S], columns = ['x', 'y'])
        Bhat_return = pd.DataFrame(np.c_[Ls, Bhat], columns = ['x', 'y'])
        
        return_data = {'B' : B_return.to_dict(orient = 'records'),
                       'S' : S_return.to_dict(orient = 'records'),
                       'Bhat' : Bhat_return.to_dict(orient = 'records')
        }
        
        return return_data
    

if __name__ == "__main__":
    datasets = create_datasets()
    flow_integrator = FlowIntegrator(datasets['VX'], datasets['VY'])
    app.run(debug = True)
