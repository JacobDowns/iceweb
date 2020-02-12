from flask import Flask, render_template, redirect, url_for,request
from flask import make_response, jsonify
from flask_cors import CORS
from data_manager import create_datasets
from flow_integrator import FlowIntegrator
from scipy.interpolate import interp1d
#from scipy.interpolate 
import pandas as pd
import numpy as np
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "hi"
@app.route("/index")

@app.route('/get_flowline', methods=['POST'])
def get_flowline():
    if request.method == 'POST':

        data = request.json
       
        xs = data['x']
        ys = data['y']

        return_data = {}
        for i in range(len(xs)):
            x = float(xs[i])
            y = float(ys[i])
            coords = flow_integrator.integrate_flowline(x, y, resolution = 1.)
            return_data[i] = coords[:,::-1].tolist()
     
        return return_data


@app.route('/finish_flowline', methods=['POST'])
def finish_flowline():
    if request.method == 'POST':

        data = request.json
        
        max_len = 0
        X = []
        Y = []
        for k in data.keys():
            # Flowline coordinates
            data_frame = pd.DataFrame(data[k])
            xs = data_frame['lng'].to_numpy()
            print(len(xs))
            ys = data_frame['lat'].to_numpy()
            max_len = max(max_len, len(xs))
            X.append(xs)
            Y.append(ys)
                 
        print(max_len)


        flowline_data = {
                'bed' : np.zeros(max_len),
                'surface' : np.zeros(max_len),
                'thickness' : np.zeros(max_len),
                'bhat' : np.zeros(max_len)
        }

        for i in range(3):
            xs = X[i]
            ys = Y[i]
            for f in ['bed', 'surface', 'thickness']:
                flowline_data[f][0:len(xs)] += (1./3.)*datasets[f].interp(xs, ys, grid = False)

            
        flowline_data['bhat'] += (flowline_data['surface'] - flowline_data['thickness'])
        return_data = {}


        mid_len = len(X[1])
        Ls =  segment_lens = np.sqrt((X[1][1:] - X[1][:-1])**2 + (Y[1][1:] - Y[1][:-1])**2)
        Ls = np.insert(segment_lens.cumsum(), 0, 0.)
        
        
        for f in flowline_data:
            return_data[f] = pd.DataFrame(np.c_[Ls, flowline_data[f][0:mid_len]],
                                              columns = ['x', 'y'])
            return_data[f] = return_data[f].to_dict(orient = 'records')
                
            
            
        return return_data


@app.route('/get_flowline_data', methods=['POST'])
def get_flowline_data():
    if request.method == 'POST':
        data = request.json

        max_len = 0
        L = []
        X = []
        Y = []

        ### Build along flow coordinate system
        ##############################################################
        
        def get_Ls(xs, ys):
            segment_lens = np.sqrt((xs[1:] - xs[:-1])**2 + (ys[1:] - ys[:-1])**2)
            return np.insert(segment_lens.cumsum(), 0, 0.)

        for k in range(3):
            flow_frame = pd.DataFrame(data[k]['flowline_coords'])
            xs = flow_frame['lng'].to_numpy()[::-1]
            ys = flow_frame['lat'].to_numpy()[::-1]
            Ls = get_Ls(xs, ys)
            print(Ls)
            print()
            print()

            if k == 0:
                extend_frame = pd.DataFrame(data[k]['extension_coords'])
                xs_extend = extend_frame['lng'].to_numpy()[::-1]
                ys_extend = extend_frame['lat'].to_numpy()[::-1]

                if len(xs_extend) > 1:
                    Ls_extend = get_Ls(xs_extend, ys_extend)
                    Ls = np.concatenate((-Ls_extend[::-1], Ls))
                    xs = np.concatenate((xs_extend[::-1], xs))
                    ys = np.concatenate((ys_extend[::-1], ys))

            X.append(xs)
            Y.append(ys)
            L.append(np.concatenate(([-1e12, Ls[0] - 1e-10], Ls,
                                 [Ls[-1] + 1e-10, 1e12])))

        ### Get interpolated data 
        ##############################################################

        resolution = 1.

        L_max = np.array([L[0][-2], L[1][-2], L[2][-2]]).min() - 1.
        L_res = np.arange(L[0][2], L_max, resolution)
        
        averaged_data = {
            'bed' : np.zeros_like(L_res),
            'surface' : np.zeros_like(L_res),
            'thickness' : np.zeros_like(L_res)
        }

        
        for k in range(3):
            
            Ls = L[k]
            for field in ['bed', 'surface', 'thickness']:
                print(field)
                field_data = datasets[field].interp(X[k], Y[k], grid = False)
                field_data = np.concatenate(([0.,0.], field_data, [0.,0.]))
                field_interp = interp1d(Ls, field_data)(L_res)
                #indicator = np.ones_like(L_res)
                #print(L_res[40:60], field_interp[40:60])
                #print()
                indicator = np.ones_like(L_res)
                indicator[L_res > 0.] = 1./3.
                
                averaged_data[field] += field_interp

        
        averaged_data['bhat'] = averaged_data['surface'] - averaged_data['thickness']
        
        B_return = pd.DataFrame(np.c_[L_res, averaged_data['bed']], columns = ['x', 'y'])
        S_return = pd.DataFrame(np.c_[L_res, averaged_data['surface']], columns = ['x', 'y'])
        Bhat_return = pd.DataFrame(np.c_[L_res, averaged_data['bhat']], columns = ['x', 'y'])
                 
        return_data = {'B' : B_return.to_dict(orient = 'records'),
                       'S' : S_return.to_dict(orient = 'records'),
                       'Bhat' : Bhat_return.to_dict(orient = 'records')
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
