from flask import Flask, render_template, redirect, url_for,request
from flask import make_response, jsonify
from flask_cors import CORS
from data_manager import create_datasets
from flow_integrator import FlowIntegrator
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
        x = float(data['x'])
        y = float(data['y'])

        flowline_d = np.array(flow_integrator.integrate(x, y, resolution = 2., threshold = 5.))
        flowline_u = np.array(flow_integrator.integrate(x, y, resolution = 2., threshold = 5., x_scale = -1., y_scale = -1.))
        flowline = np.concatenate((flowline_u[::-1][:,::-1], flowline_d[:,::-1]))
        
        ys = flowline[:,0]
        xs = flowline[:,1]

        B = datasets['bed'].interp(xs, ys, grid = False)
        S = datasets['surface'].interp(xs, ys, grid = False)
        segment_lens = np.sqrt((xs[1:] - xs[:-1])**2 + (ys[1:] - ys[:-1])**2)
        Ls = np.insert(segment_lens.cumsum(), 0, 0.)

        B_return = pd.DataFrame(np.c_[Ls, B], columns=['x', 'y'])
        S_return = pd.DataFrame(np.c_[Ls, S], columns=['x', 'y'])
        
        return_data = {'flowline_coords' : flowline.tolist(),
                       'B' : B_return.to_dict(orient = 'records'),
                       'S' : S_return.to_dict(orient = 'records')
        }
        #print(data)
        return return_data



@app.route('/get_data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        data = request.json
        print(data)
        return 
    

if __name__ == "__main__":
    datasets = create_datasets()
    flow_integrator = FlowIntegrator(datasets['VX'], datasets['VY'])
    app.run(debug = True)
