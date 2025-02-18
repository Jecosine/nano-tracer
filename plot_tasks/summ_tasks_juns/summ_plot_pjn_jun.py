from utils.tools import chkdir
from utils.summ_plot import summ_plot_jun, SL_jun
from plot_tasks.ns_plots.ns_pjn_plot import ns_pjn_plot
import os.path


def special_tasks(axs, data, task_list):
    jun_list, dims_ls, temp_list, arm_num_list = data
    # 1. a horizontal dashed line at 109.5° for the 4 arm
    axs[0,0].plot((-1,11), (109.5,109.5),c='#1AA555',ls=':')
    # 2. one at 90° for the 6 arm patch angle plot. 
    axs[0,2].plot((-1,11), (90,90),c='#1AA555',ls=':')
    # 4. a solid horizontal black line at skew=0° in the bottom row of plots.
    for i in range(len(arm_num_list)):
        axs[2,i].plot((-1,11), (0,0),c='#000000')
    return axs


def summ_plot_pjn_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list):
    '''
    Summary plot (#unpaired at junction varied) of orthogonal patch angle of junction.
    Set varname and plot confs.
    Define special tasks to customize the plot.
    '''
    assert len(color_list) == len(marker_list) == len(temp_list)
    varname = 'pjn'
    #### plot confs ####
    xlim = (-1, 11)
    ylim_avg = (60, 170)
    ylim_std = (0, 110)
    ylim_skw = (-1.3, 1.3)
    y_var = rf'Patch Angles (False) of Junction ($^\circ$)'
    plot_confs = (xlim, ylim_avg, ylim_std, ylim_skw, y_var)
    #### conf ends ####
    # packing
    data = (jun_list, dims_ls, temp_list, arm_num_list)
    plot_confs = (xlim, ylim_avg, ylim_std, ylim_skw, y_var)
    # load
    jun_summ_dic, savepath = SL_jun(ns_pjn_plot, data, conc_list, varname)
    #### Plot Summaries ####
    # plot: conc ~ {x: jun_nums, y: summaries, series: temperature}
    # data: conc ~ temperature ~ (jun~summ)
    for conc in conc_list:
        plt = summ_plot_jun(jun_summ_dic, plot_confs, data, conc, task_list, color_list, marker_list, special_tasks)
        chkdir(os.path.dirname(f'{savepath}-{varname}-jun{jun_list}-{conc}M.png'))
        plt.savefig(f'{savepath}-{varname}-jun{jun_list}-{conc}M.png',dpi=500)
        plt.clf()
    return True