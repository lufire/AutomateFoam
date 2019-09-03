import os
import numpy as np
import scipy as sp
import pickle as pickle
from scipy import interpolate
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


class Data:

    def __init__(self):
        self.name = None
        self.x_grid = None
        self.y_grid = None
        self.plot_style = None


class MeasurementData(Data):

    def __init__(self, meas_path, x_pos_profiles, bounds):
        Data.__init__(self)
        self.name = 'Measurement'
        self.plot_style = 'k-'
        try:
            # full_meas_data = np.load(meas_path)
            full_meas_data = pickle.load(open(meas_path, 'rb'))
            x_grid = np.nan_to_num(full_meas_data['ygrid'][:, 0])
            y_grid = np.nan_to_num(full_meas_data['xgrid'][0, :])
            profile_grid = np.nan_to_num(full_meas_data['v_y'])

            # Strip grid from data outside of the bounds
            bound_id = [[np.argmin(abs(x_grid - bounds[0][0])),
                         np.argmin(abs(x_grid - bounds[0][1]))],
                        [np.argmin(abs(y_grid - bounds[1][0])),
                         np.argmin(abs(y_grid - bounds[1][1]))]]

            self.x_grid = x_grid[bound_id[0][0]:bound_id[0][1]]
            self.y_grid = y_grid[bound_id[1][0]:bound_id[1][1]]
            profile_bounded = profile_grid[bound_id[0][0]:bound_id[0][1],
                                           bound_id[1][0]:bound_id[1][1]]
            # self.x_vel_grid = x_vel_grid[:][:]
            self.profiles = []
            self.x_position = []
            for xpos in x_pos_profiles:
                pos_id = np.argmin(abs(self.x_grid - xpos))
                self.x_position.append(xpos)
                self.profiles.append(np.nan_to_num(profile_bounded[pos_id]))

        except IOError:
            raise IOError("File containing measurement data not found: ",
                          meas_path)


class SimulationData(Data):

    def __init__(self, case_path, meas_data, field_name, component):
        Data.__init__(self)
        self.name = 'Simulation - ' + field_name
        self.plot_style = 'r-'
        control_dict = \
            ParsedParameterFile(os.path.join(case_path, 'system/controlDict'))
        self.time = str(control_dict['endTime'])
        self.y_bounds = [0.0, 15e-3]
        self.y_grid = meas_data.y_grid
        self.x_grid = meas_data.x_grid
        self.profiles = self.read_profiles(case_path, meas_data.x_position,
                                           field_name, component)

    def read_profiles(self, case_path, x_positions, field_name, component):
        profiles = []
        for i in range(len(x_positions)):
            graph_dir = os.path.join(case_path,
                                     'postProcessing/graph' + str(i + 1))
            # graph_list = [int(i) for i in os.listdir(graph_dir)]
            # max_iter_nr = max(graph_list)
            self.time = self.read_time(graph_dir)
            graph_file = os.path.join(graph_dir, str(self.time),
                                      'line_' + field_name + '.xy')
            profiles.append(self.read_profile(graph_file, component))
        return profiles

    def read_profile(self, file_path, component):
        try:
            prof = np.loadtxt(file_path, usecols=component)
        except IOError:
            raise IOError("File containing simulation profiles not "
                          "found: ", file_path)
        y = np.linspace(self.y_bounds[0], self.y_bounds[1], len(prof),
                        endpoint=True)
        return np.nan_to_num(sp.interpolate.griddata(y, prof, self.y_grid))

    @staticmethod
    def read_time(path):
        times_str = os.listdir(path)
        times_float = [float(item) for item in times_str]
        return times_str[times_float.index(max(times_float))]




