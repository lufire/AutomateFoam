import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter)
import subprocess
import math
import os

# =============================================================================
# Configure global plot settings
# =============================================================================

mpl.rcParams['font.size'] = 6
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8


def plot_profiles(meas_data, sim_data):
    n_plots = len(meas_data.x_position)
    n_plots += math.ceil(len(meas_data.x_position) % 2)
    n_cols = 2
    n_rows = n_plots/2  # + 1
    width = 7.0
    height = float(n_rows)/float(n_cols)*width*0.7
    fig = plt.figure(dpi=200, figsize=(width, height))
    major_locator = MultipleLocator(2.5)
    major_formatter = FormatStrFormatter('%4.1f')
    minor_locator = MultipleLocator(0.5)

    for j, xpos in enumerate(meas_data.x_position):
        m_to_mm = 1000.0

        ax = fig.add_subplot(n_rows, n_cols, j + 1)
        ax.set_title("x = " + str(xpos * m_to_mm) + " mm")

        plt.plot(meas_data.y_grid * m_to_mm, meas_data.x_vel_prof[j] * m_to_mm,
                 'k-', label="Measurement")
        plt.plot(sim_data.y_grid * m_to_mm, sim_data.x_vel_prof[j] * m_to_mm,
                 'r-', label="Simulation")

        ax.set_xlabel("y-Position / $mm$", fontsize='8.0')
        ax.set_ylabel("x-Velocity / $mm/s$", fontsize='8.0')
        ax.grid()
        # ax.set_xlim(sim_data.y_grid[0] * m_to_mm, sim_data.y_grid[1] * m_to_mm)
        # ax.set_xticks(np.arange(y_plot_bounds[0]*1000,y_plot_bounds[1]*1000+2.5,step=2.5))
        # ax.set_ylim(0.0, 6.0)
        # ax.set_yticks(np.arange(0.0, 7.0, step=1.0))
        ax.xaxis.set_major_locator(major_locator)
        ax.xaxis.set_major_formatter(major_formatter)
        ax.xaxis.set_minor_locator(minor_locator)
        plt.tight_layout()
        # if n_plots % 2 == 0.0:
        plt.subplots_adjust(bottom=0.17, top=1.1)
        plt.legend(loc=0)
    return fig


def add_info(in_dict, info=''):
    for key in in_dict:
        if isinstance(in_dict[key], (float, int)):
            info += str(key) + ': ' + '%.3E' % in_dict[key] + '\n'
    # fig.text(0.1, 0.001, info, horizontalalignment='left', fontsize='8.0')
    return info


def calculate_error(meas_data, sim_data):

    y_grid = meas_data.y_grid

    y_bounds = [2e-3, 13e-3]
    idy = [np.argmin(abs(y_grid-y_bounds[0])),
           np.argmin(abs(y_grid-y_bounds[1]))]

    error = 0.0
    for i in range(len(meas_data.x_vel_prof)):
        vel_meas = meas_data.x_vel_prof[i][idy[0]:idy[1]]
        vel_sim = sim_data.x_vel_prof[i][idy[0]:idy[1]]
        error += np.sqrt(np.sum(((vel_meas - vel_sim)/vel_meas) ** 2))
    return error


def run_sim(case_dir):
    work_dir = os.getcwd()
    os.chdir(case_dir)
    # Run simulation
    allclean_bash = os.path.join(case_dir, 'Allclean')
    subprocess.call(allclean_bash, shell=True)
    allrun_bash = os.path.join(case_dir, 'Allrun')
    subprocess.call(allrun_bash, shell=True)
    os.chdir(work_dir)
