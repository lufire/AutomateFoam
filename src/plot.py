import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter)
import math


mpl.rcParams['font.size'] = 6
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8


def plot_profiles(meas_data, sim_data):

    fig = plt.figure(dpi=200)
    major_locator = MultipleLocator(2.5)
    major_formatter = FormatStrFormatter('%4.1f')
    minor_locator = MultipleLocator(0.5)
    plot_num = len(meas_data.x_position)
    plot_num += math.ceil(len(meas_data.x_position) % 2)

    for j, xpos in enumerate(meas_data.x_position):
        m_to_mm = 1000.0

        ax = fig.add_subplot(plot_num/2 + 1, 2, j + 1)
        ax.set_title("x = " + str(xpos * m_to_mm) + " mm")

        plt.plot(meas_data.y_grid * m_to_mm, meas_data.x_vel_prof[j] * m_to_mm, 'k-', label="Measurement")
        plt.plot(sim_data.y_grid * m_to_mm, sim_data.x_vel_prof[j] * m_to_mm, 'r-', label="Simulation")

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
        plt.legend(loc=0)
    return fig


def add_info(fig, in_dict):
    info = ''
    for key in in_dict:
        info += str(key) + ': ' + '%.2E' % in_dict[key] + '\n'
    fig.text(0.1, 0.001, info, horizontalalignment='left', fontsize='8.0')

    return fig
