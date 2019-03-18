import os
import numpy as np
import scipy as sp
import pickle as pickle
from scipy import interpolate
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


class MeasurementData:

    def __init__(self, meas_path, x_pos_profiles, bounds):
        try:
            # full_meas_data = np.load(meas_path)
            full_meas_data = pickle.load(open(meas_path, 'rb'))
            x_grid = np.nan_to_num(full_meas_data['ygrid'][:, 0])
            y_grid = np.nan_to_num(full_meas_data['xgrid'][0, :])
            x_vel_grid = np.nan_to_num(full_meas_data['v_y'])

            # Strip grid from data outside of the bounds
            bound_id = [[np.argmin(abs(x_grid - bounds[0][0])),
                         np.argmin(abs(x_grid - bounds[0][1]))],
                        [np.argmin(abs(y_grid - bounds[1][0])),
                         np.argmin(abs(y_grid - bounds[1][1]))]]

            self.x_grid = x_grid[bound_id[0][0]:bound_id[0][1]]
            self.y_grid = y_grid[bound_id[1][0]:bound_id[1][1]]
            self.x_vel_grid = x_vel_grid[bound_id[0][0]:bound_id[0][1], bound_id[1][0]:bound_id[1][1]]
            # self.x_vel_grid = x_vel_grid[:][:]
            self.x_vel_prof = []
            self.x_position = []
            for xpos in x_pos_profiles:
                pos_id = np.argmin(abs(self.x_grid - xpos))
                self.x_position.append(xpos)
                self.x_vel_prof.append(np.nan_to_num(self.x_vel_grid[pos_id]))

        except IOError:
            print "File containing measurement data not found"


class SimulationData:

    def __init__(self, case_path, meas_data):
        control_dict = ParsedParameterFile(os.path.join(case_path, 'system/controlDict'))
        end_time = str(control_dict['endTime'])
        y_bounds = [0.0, 15e-3]
        self.y_grid = meas_data.y_grid
        self.x_grid = meas_data.x_grid
        self.x_vel_prof = []
        for i in range(len(meas_data.x_position)):
            graph_dir = os.path.join(case_path, 'postProcessing/graph' + str(i + 1) + '/')
            # graph_list = [int(i) for i in os.listdir(graph_dir)]
            # max_iter_nr = max(graph_list)
            graph_file = graph_dir + end_time + '/line_U.xy'
            try:
                x_vel = np.loadtxt(graph_file, usecols=2)
                y = np.linspace(y_bounds[0], y_bounds[1], len(x_vel), endpoint=True)
                x_vel = np.nan_to_num(sp.interpolate.griddata(y, x_vel, meas_data.y_grid))
                self.x_vel_prof.append(x_vel)

            except IOError:
                print "File containing simulation profiles was not found"
