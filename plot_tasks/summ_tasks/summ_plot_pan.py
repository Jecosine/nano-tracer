from utils.tools import chkdir
from utils.summ_plot import summ_plot, SL
from plot_tasks.ns_plots.ns_pan_plot import ns_pan_plot
import os.path

def special_tasks(axs, data, task_list):
    conf_suffix, dims_ls, conc_list, temp_list, arm_num_list = data
    # special tasks
    # 1. a horizontal dashed line at 109.5° for the 4 arm
    axs[0,0].plot((15,55), (109.5,109.5),c='#1AA555',ls=':')
    # 2. one at 90° for the 6 arm patch angle plot. 
    axs[0,2].plot((15,55), (90,90),c='#1AA555',ls=':')
    # 4. a solid horizontal black line at skew=0° in the bottom row of plots.
    for i in range(len(arm_num_list)):
        axs[2,i].plot((15,55), (0,0),c='#000000')
    # special tasks ends
    axs[0,len(arm_num_list)-1].legend()
    return axs


def summ_plot_pan(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list):
    '''
    Summary plot (design fixed) of orthogonal patch angle.
    Set varname and plot confs.
    Define special tasks to customize the plot.
    '''
    assert len(conc_list) == len(color_list) == len(marker_list)
    varname = 'pan'
    #### plot confs ####    
    xlim = (15,55)
    ylim_avg = (60, 170)
    ylim_std = (0, 110)
    ylim_skw = (-1.3, 1.3)
    y_var = rf'Patch Angles (False) ($^\circ$)'
    #### conf ends ####
    plot_confs = (xlim, ylim_avg, ylim_std, ylim_skw, y_var)
    data = conf_suffix, dims_ls, conc_list, temp_list, arm_num_list
    # load data
    summary_dic, savepath = SL(ns_pan_plot, data, varname)
    # plot
    plt = summ_plot(summary_dic, plot_confs, data, task_list, color_list, marker_list, special_tasks)
    chkdir(os.path.dirname(f'{savepath}-{varname}.png'))
    plt.savefig(f'{savepath}-{varname}.png',dpi=500)
    plt.clf()
    return True
