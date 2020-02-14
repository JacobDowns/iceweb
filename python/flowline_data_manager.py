from flow_integrator import FlowIntegrator
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
from pyproj import Proj


class FlowlineDataManager:

    def __init__(self, datasets):
        self.datasets = datasets


    def get_flowline_data(self, data):
        
        data_res = 1.
        if 'data_res' in data:
            data_res = data['data_res']

        return_data = {}
        fields = ['t2m', 'smb', 'bed', 'surface', 'thickness', 'indicator',
                  'x', 'y', 'coords_y_x', 'L']

        avg_data = {}
        avg_data['bed'] = []
        avg_data['thickness'] = []
        avg_data['surface'] = []
        avg_data['indicator'] = []
        avg_data['x'] = []
        avg_data['y'] = []
        avg_data['smb'] = []
        avg_data['t2m'] = []

        for field in fields:
            return_data[field] = []


        ### Get data for each flowline
        ###############################################################

        Lres0 = None
        for i in range(3):
            df = pd.DataFrame(data['coords'][str(i)])
            x = df['lng'].to_numpy()
            y = df['lat'].to_numpy()
            L =  self.get_L(x, y)

            flow_len = L.max() - L.min()
            L_res = np.linspace(L.min(), L.max(),
                                int(flow_len / data_res), endpoint = True)
            x_res = interp1d(L, x)(L_res)
            y_res = interp1d(L, y)(L_res)

            """
            Use the thickness to determine along flow distance. In 
            particular L=0 is the 0 thickness contour. 
            """
            ##########################################################

            field_data = self.datasets['thickness'].interp(x_res, y_res,
                                                           grid = False)

            index = -1
            indexes = np.argwhere(field_data <= 15.).flatten()
            if len(indexes) > 0:
                index = indexes.min()
            L0 = L_res[index]
            L_res -= L0

            return_data['thickness'].append(field_data.tolist())
            return_data['L'].append(L_res.tolist())
            return_data['coords_y_x'].append(np.c_[y_res, x_res].tolist())

            
            if i == 0:
                L_res0 = L_res
                
            L_interp = np.concatenate((
                [-1e12, L_res.min() - 1e-8],
                L_res,
                [L_res.max() + 1e-8, 1e12]
            ))
            data_interp = np.concatenate((
                [0.,0.],
                field_data,
                [0.,0.]
            ))
            
            avg_data['thickness'].append(interp1d(L_interp, data_interp)(L_res0).tolist())

            

            ### Interpolate the remaining data fields.
            ##########################################################
            
            for field in ['t2m', 'smb', 'bed', 'surface', 'indicator', 'x', 'y']:
                if field == 'indicator':
                    field_data = np.ones_like(x_res)
                elif field == 'x':
                    field_data = x_res
                elif field == 'y':
                    field_data = y_res
                else :
                    field_data = self.datasets[field].interp(x_res, y_res,
                                                             grid = False)

                return_data[field].append(field_data.tolist())
                data_interp = np.concatenate(([0.,0.], field_data, [0.,0.]))        
                avg_data[field].append(
                    interp1d(L_interp, data_interp)(L_res0).tolist()
                )


        ### Width average
        ###################################################################

        avg_data['L'] = L_res0.tolist()
        indicator = np.array(avg_data['indicator']).sum(axis = 0)
        avg_data['indicator'] = indicator.tolist()
        
        x1 = np.array(avg_data['x'][1])
        y1 = np.array(avg_data['y'][1])
        x2 = np.array(avg_data['x'][2])
        y2 = np.array(avg_data['y'][2])
        
        width = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        width[indicator < 3.] = 0.
        avg_data['width'] = width.tolist()


        for field in ['t2m', 'smb', 'bed', 'surface', 'thickness']:
            avg_data[field] = (np.array(avg_data[field]).sum(axis = 0)
                               / indicator).tolist()
            
        avg_data['bhat'] = (np.array(avg_data['surface']) -
                            np.array(avg_data['thickness'])).tolist()

        return_data['avg_data'] = avg_data
        return return_data


    # Get along flow coordinates
    def get_L(self, x, y):
        segment_lens = np.sqrt((x[1:] - x[:-1])**2 + (y[1:] - y[:-1])**2)
        return np.insert(segment_lens.cumsum(), 0, 0.)
