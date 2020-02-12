from flask import Flask, render_template, redirect, url_for,request
from flask import make_response, jsonify
from flask_cors import CORS
from data_manager import create_datasets
from flowline_data_manager import *
from flow_integrator import FlowIntegrator
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
from pyproj import Proj
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
            coords = flow_integrator.integrate_flowline(x, y, resolution = 2.5)
            return_data[i] = coords[:,::-1].tolist()
     
        return return_data


@app.route('/plot_flowline', methods=['POST'])
def plot_flowline():
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


        #flow_frame = pd.DataFrame(data)
        #print(flow_frame)
        
        for k in range(3):
            df = pd.DataFrame(data['flowline_coords'][str(k)])
            xs = df['lng'].to_numpy()[::-1]
            ys = df['lat'].to_numpy()[::-1]
            Ls = get_Ls(xs, ys)
            print(xs)
            print(ys)
            print(Ls)
            print()
            print()

            if k == 0:
                extend_frame = pd.DataFrame(data['extension_coords'])
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
    

@app.route('/load_flowline', methods=['POST'])
def load_flowline():
    if request.method == 'POST':

        data = request.json
        coords = len(data['file']['xy_coords'])

        return ''
    
        coords[:,0] += 637.925
        coords[:,1] += 3348.675
        xs = coords[:,0]
        ys = coords[:,1]
        
        S_ends = datasets['surface'].interp(xs[[0,-1]], ys[[0,-1]], grid = False)
        d_index = S_ends.argmin()
        u_index = S_ends.argmax()

        coords_d = np.array([[]])
        coords_u = np.array([[]])

        if data['extend_down']:
            coords_d = flow_integrator.integrate(xs[[0,-1]][d_index], ys[[0,-1]][d_index],
                                             resolution = 2.,
                                             threshold = 10.)
            coords = np.concatenate((coords_d, coords[1:]))

        if data['extend_up']:
            coords_u = flow_integrator.integrate(xs[[0,-1]][u_index], ys[[0,-1]][u_index],
                                             x_scale = -1.,
                                             y_scale = -1.,
                                             resolution = 2.,
                                             threshold = 10.)
            coords = np.concatenate((coords, coords_u[1:]))

        return_data = {}
        return_data[0] = coords[::-1,::-1].tolist()
        return return_data



@app.route('/download_flowline', methods=['POST'])
def download_flowline():
    if request.method == 'POST':
        data = request.json
        return get_data(data)

def get_data(data):

    resolution = 1.
    # Returned dictionary
    return_data = {}
    
    # Along flow coords.
    def get_L(xs, ys):
        segment_lens = np.sqrt((xs[1:] - xs[:-1])**2 + (ys[1:] - ys[:-1])**2)
        return np.insert(segment_lens.cumsum(), 0, 0.)

    # Dicitonary containing coordinates and data for each flowline
    flowline_data = {}
    fields = ['coords', 'coords_xy', 'L', 'x', 'y', 'bed', 'surface', 'thickness', 'indicator']
    
    for field in fields:
        flowline_data[field] = []
    for field in ['coords', 'L']:
        return_data[field] = []
    return_data['coords_y_x'] = []
        
    
    num_flowlines = len(data['flowline_coords'].keys())
        

    ### Get data for each flowline
    ##################################################################

    L0 = None
    for i, key in zip(range(num_flowlines), data['flowline_coords'].keys()):
        df = pd.DataFrame(data['flowline_coords'][str(i)])
        x = df['lng'].to_numpy()[::-1]
        y = df['lat'].to_numpy()[::-1]

        # Along flow coordinate system 
        L = get_L(x, y)
        
        if i == 0:
            extend_frame = pd.DataFrame(data['extension_coords'])
            x_extend = extend_frame['lng'].to_numpy()
            y_extend = extend_frame['lat'].to_numpy()
            
            if len(x_extend) > 1:
                L_extend = get_L(x_extend, y_extend)
                L = np.concatenate((-L_extend, L))
                x = np.concatenate((x_extend, x))
                y = np.concatenate((y_extend, y))

            L0 = L
            
        flow_len = L.max() - L.min()
        L_res = np.linspace(L.min(), L.max(), int(flow_len / resolution), endpoint = True)
        x_res = interp1d(L, x)(L_res)
        y_res = interp1d(L, y)(L_res)

        
        # Along flow coords
        flowline_data['L'].append(L_res)
        return_data['L'].append(L_res.tolist())
        # Custom map xy coords
        coords_xy = np.c_[x_res, y_res]
        flowline_data['coords_xy'].append(coords_xy)
        return_data['coords_y_x'].append(coords_xy[:,::-1].tolist())
        # epsg:3413 map coords
        map_xs = (x_res - 637.925)*1e3
        map_ys = (y_res - 3348.675)*1e3
        coords = np.c_[map_xs, map_ys]
        flowline_data['coords'].append(coords)
        return_data['coords'].append(coords.tolist())
        
        
        ### Interpolated flowline data
        ##############################################################
        
        L_interp = np.concatenate(([-10e3, L_res.min() - 1e-10], L_res, [L_res.max() + 1e-10, 10e3]))
        for field in ['bed', 'surface', 'thickness', 'indicator', 'x', 'y']:
            if field == 'indicator':
                field_data = np.ones_like(x_res)
            elif field == 'x':
                field_data = x_res
            elif field == 'y':
                field_data = y_res
            else :
                field_data = datasets[field].interp(x_res, y_res, grid = False)
                
            data_interp = np.concatenate(([0.,0.], field_data, [0.,0.]))
            flowline_data[field].append(interp1d(L_interp, data_interp)(L0))

            
    ### Width average
    ###################################################################

    avg_data = {}
    indicator = np.array(flowline_data['indicator']).sum(axis = 0)

    width = np.sqrt((flowline_data['x'][1] - flowline_data['x'][2])**2 +
                    (flowline_data['y'][1] - flowline_data['y'][2])**2)

    width[indicator < 3.] = 0.
    return_data['width'] = width.tolist()
    
    
    for field in ['bed', 'surface', 'thickness']:
        return_data[field] = (np.array(flowline_data[field]).sum(axis = 0) / indicator).tolist()


    #print(return_data)
    return return_data


"""
    L_avg = flowline_data['center']['L_coords']
    flowline_avg = {}
    indicator = np.zeros_like(L_avg)
    for field in fields:
        flowline_avg[field] = np.zeros_like(L_avg)


    for flowline in flowline_data:
        Ls = flowline_data[flowline]['L_coords']
        indicator_data = np.concatenate(([0.,0.], np.ones_like(Ls), [0.,0.]))
        Ls = np.concatenate(([-10e3, Ls.min() - 1e-10], Ls, [Ls.max() + 1e-10, 10e3]))
        indicator_interp = interp1d(Ls, indicator_data)(L_avg)
        indicator += indicator_interp
        
        for field in ['bed', 'surface', 'thickness']:
            
            field_data = flowline_data[flowline][field]
            field_data = np.concatenate(([0.,0.], field_data, [0.,0.]))
            field_interp = interp1d(Ls, field_data)(L_avg)
            flowline_avg[field] += field_interp
                                                

    for field in fields:
        flowline_avg[field] /= indicator
    flowline_avg['bhat'] = flowline_avg['surface'] - flowline_avg['thickness']
    flowline_data['avg'] = flowline_avg

    df = pd.DataFrame(flowline_data)
    print(df.to_dict())
    
    return ''
"""


@app.route('/get_flowline_data', methods=['POST'])
def get_flowline_data():
    if request.method == 'POST':
        data = request.json
        return_data = flowline_data_manager.get_flowline_data(data)

        return return_data
        

if __name__ == "__main__":
    datasets = create_datasets()
    flowline_data_manager = FlowlineDataManager(datasets)
    flow_integrator = FlowIntegrator(datasets['VX'], datasets['VY'])
    app.run(debug = True)
