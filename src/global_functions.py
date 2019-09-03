import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter)
import subprocess
import math
import os
from scipy import ndimage

# =============================================================================
# Configure global plot settings
# =============================================================================

mpl.rcParams['font.size'] = 6
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8


def create_figure(meas_data, ylabel, ylabel2=None):
    n_plots = len(meas_data.x_position)
    n_plots += math.ceil(len(meas_data.x_position) % 2)
    n_cols = 2
    n_rows = int(math.floor(n_plots/2))  # + 1
    width = 7.0
    height = float(n_rows)/float(n_cols)*width*0.8
    fig, axs = plt.subplots(n_rows, n_cols, dpi=200, figsize=(width, height))
    axs = np.asarray(axs)
    major_locator = MultipleLocator(2.5)
    major_formatter = FormatStrFormatter('%4.1f')
    minor_locator = MultipleLocator(0.5)
    m_to_mm = 1000.0
    if ylabel2:
        axs_twin = []
    for i, ax in enumerate(axs.reshape(-1)):
        xpos = meas_data.x_position[i]
        ax.set_title("x = " + str(xpos * m_to_mm) + " mm")
        ax.set_xlabel("y-Position / $mm$", fontsize='8.0')
        ax.set_ylabel(ylabel, fontsize='8.0')
        if ylabel2:
            ax2 = ax.twinx()
            ax2.set_ylabel(ylabel2, fontsize='8.0')
            axs_twin.append(ax2)
        ax.grid()
        ax.xaxis.set_major_locator(major_locator)
        ax.xaxis.set_major_formatter(major_formatter)
        ax.xaxis.set_minor_locator(minor_locator)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25, top=1.1)
        #plt.legend(loc=0)
    axs_twin = np.asarray(axs_twin)
    return fig, axs, axs_twin


def add_plots(fig, axs, data, linestyle=None,
              scale=1., ylim=None, meas_res=None):
    for i, ax in enumerate(axs.reshape(-1)):
        if meas_res:
            y_grid = data.y_grid
            filt_size = \
                int(round(meas_res / abs(y_grid[-1] - y_grid[0]) * len(y_grid)))
            profile = \
                ndimage.uniform_filter1d(data.profiles[i], filt_size)
        else:
            profile = data.profiles[i]
        # xpos = meas_data.x_position[i]
        # ax.set_title("x = " + str(xpos * m_to_mm) + " mm")
        if not linestyle:
            linestyle = data.plot_style
        ax.plot(data.y_grid * 1000.0, profile * scale,
                linestyle, label=data.name)
        ax.set_ylim(ylim)
        # ax.set_xlabel("y-Position / $mm$", fontsize='8.0')
        # ax.set_ylabel("x-Velocity / $mm/s$", fontsize='8.0')
        # ax.grid()
        #
        # ax.xaxis.set_major_locator(major_locator)
        # ax.xaxis.set_major_formatter(major_formatter)
        # ax.xaxis.set_minor_locator(minor_locator)
        # plt.tight_layout()
        # # if n_plots % 2 == 0.0:
        # plt.subplots_adjust(bottom=0.17, top=1.1)
        # plt.legend(loc=0)
    return fig, axs


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

        plt.plot(meas_data.y_grid * m_to_mm, meas_data.profiles[j] * m_to_mm,
                 'k-', label="Measurement")
        plt.plot(sim_data.y_grid * m_to_mm, sim_data.profiles[j] * m_to_mm,
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


def calculate_error(meas_data, sim_data, meas_res):

    filt_size = 50
    y_grid = meas_data.y_grid
    y_grid_filt = ndimage.uniform_filter1d(y_grid, filt_size)

    y_bounds = [1e-3, 14e-3]
    idy = [np.argmin(abs(y_grid-y_bounds[0])),
           np.argmin(abs(y_grid-y_bounds[1]))]

    avg_vel = np.average(meas_data.profiles[-1])

    val_error = 0.0
    der_error = 0.0
    errors = []
    for i in range(len(meas_data.profiles)):
        filt_size_meas = \
            int(round(meas_res/abs(y_grid[-1]-y_grid[0]) * len(y_grid)))
        vel_sim_filt = \
            ndimage.uniform_filter1d(sim_data.profiles[i], filt_size_meas)
        vel_meas_filt = \
            ndimage.uniform_filter1d(meas_data.profiles[i], filt_size)
        vel_sim_double_filt = \
            ndimage.uniform_filter1d(sim_data.profiles[i], filt_size)

        der_meas = np.gradient(vel_meas_filt, y_grid_filt)
        der_sim = np.gradient(vel_sim_double_filt, y_grid_filt)
        der_error = np.nansum((der_meas - der_sim) ** 2)
        vel_meas = meas_data.profiles[i][idy[0]:idy[1]]
        #vel_sim = sim_data.profiles[i][idy[0]:idy[1]]
        vel_sim = vel_sim_filt[idy[0]:idy[1]]
        val_error += np.nansum(((vel_meas - vel_sim)/avg_vel) ** 2)
        errors.append(val_error + der_error)

    error = val_error + der_error
    return error, errors


def run_sim(case_dir):
    work_dir = os.getcwd()
    os.chdir(case_dir)
    # Run simulation
    allclean_bash = os.path.join(case_dir, 'Allclean')
    subprocess.call(allclean_bash, shell=True)
    allrun_bash = os.path.join(case_dir, 'Allrun')
    subprocess.call(allrun_bash, shell=True)
    os.chdir(work_dir)
