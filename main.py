from plot_tasks.summ_tasks import summ_plot_pa, summ_plot_k2, summ_plot_as, summ_plot_pj, summ_plot_kj, summ_plot_rj, summ_plot_js, summ_plot_pan, summ_plot_pjn
from plot_tasks.summ_tasks_juns import summ_plot_pa_jun, summ_plot_k2_jun, summ_plot_as_jun, summ_plot_pj_jun, summ_plot_kj_jun, summ_plot_rj_jun, summ_plot_js_jun, summ_plot_pan_jun, summ_plot_pjn_jun
# import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
import pickle


def data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix = ''):
    '''
    For debug.
    Extract the desired data of a given design of nanostar at a given condition.
    '''
    dims_ls = [20,2,7]
    label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
    loose_lbl = f'{temp}C-{conc}M-GPU{sp_suffix}'
    savepath = f'data/composed_traj/{arms}arms{conf_suffix}/{loose_lbl}/{label}.{varname}'
    import pickle
    result = pickle.load(open(savepath,'rb'))
    return result

def calc_data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix = ''):
    '''
    For debug.
    Extract the calculated results of measurements of a given design at a given condition
    '''
    varname = varname+'tp'
    result = data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix)
    return result

def datapoint_location(tg_value, result):
    '''
    For debug.
    Locate the desired value in a timestamp~value tuple list
    '''
    import numpy as np
    result_val = [tp[1] for tp in result]
    r_arr = np.array(result_val)
    r_tg_loc = np.argmin(np.abs(r_arr-tg_value))
    t_stamp, r_tg = result[r_tg_loc]
    return t_stamp, r_tg

def calc_value_obtain():
    '''
    For debug.
    '''
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    varname = 'rj'
    result = calc_data_extraction(varname, arms, temp, conc, conf_suffix)
    target = 7.0
    t_stamp, r_tg = datapoint_location(target, result)
    print(f'{arms}arm @ {temp}C and {conc}M with {conf_suffix} , the desired {varname} value: {target} locates at {t_stamp} : true value {r_tg} .')
    return True

def dist(t1, t2):
    return np.sqrt(np.sum(np.square(np.array(t1) - np.array(t2))))

def debug_ns_arm_examine():
    '''
    For debug.
    Print out the pairing of a nanostar.
    '''
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    varname = 'ns'
    ns_tm = data_extraction(varname, arms, temp, conc, conf_suffix)
    ns = ns_tm.time_capsule[ns_tm.timeseries[0]]
    arm = ns.arms[0]
    b_pairs_dic = arm.base_pairs
    import numpy as np
    for i in range(len(b_pairs_dic)):
        b1, b2 = b_pairs_dic[i+1]
        dist = np.sqrt(np.sum(np.square(np.array(b1.position) - np.array(b2.position))))
        print(f'Bpair {i+1}, dist: {dist:.3f}, ID1: {b1.base_id}, ID2: {b2.base_id}')
    return True

def single_pairing_all(sys):
    '''
    For debug.
    Pair the bases in a strand system only by finding the closest base.
    '''
    # id_pairs = []
    # strands_ls = [list(strand.base_sequence.values()) for strand in sys.values()]
    # l = len(strands_ls[0])
    # for i in range(l):
    
    pool_b = []
    for strand in sys.values():
        pool_b.extend(list(strand.base_sequence.values()))
    pool_pos = [base.position for base in pool_b]
    base_number = len(pool_pos)
    d_2darr = np.zeros((base_number, base_number))
    for i in range(base_number):
        for j in range(base_number):
            if pool_b[i].strand_id == pool_b[j].strand_id:
                d_2darr[i][j] = 100000
            else:
                d_2darr[i][j] = dist(pool_pos[i], pool_pos[j])
    min_indices = np.argmin(d_2darr,0)
    id_pairs = []
    for i in range(base_number):
        print(dist(pool_b[i].position, pool_b[min_indices[i]].position))
        id_pairs.append((pool_b[i].base_id, pool_b[min_indices[i]].base_id))
    return id_pairs

def debug_pairing():
    '''
    For debug.
    '''
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    sys_tm = data_extraction('sys', arms, temp, conc, conf_suffix)
    sys = sys_tm.time_capsule[sys_tm.timeseries[0]]
    ns_tm = data_extraction('ns', arms, temp, conc, conf_suffix)
    assert sys_tm.timeseries[0] == ns_tm.timeseries[0]
    ns = ns_tm.time_capsule[ns_tm.timeseries[0]]
    id_pairs = single_pairing_all(sys)
    for arm in ns.arms.values():
        for idx, (b1, b2) in arm.base_pairs.items():
            print(f'{(b1.base_id, b2.base_id) in id_pairs}')
    return True


# jobs: arbitrary work batches; should be packed into tasks if reusable.
def summ_plot_main():
    '''
    Summary plot of nanostars with its design fixed. (default dimensions:[20,2,7])
    Summary plot: [tasks of] var vs temp [at different conc and arm_num]
    Set conditions in conc_list, temp_list, arm_num_list. Length must > 2
    The lengths of color_list and marker_list must  == len(conc_list)
    To change the dims, set both dims_ls (affect the interpretation of trajectory file) and conf_suffix (to read which trajectory)
    pa == patch angle, k2 == k2, as == arm stiffness, pj == atch angle of junction, kj == k2 of junction, rj == radius of gyration of junction, js == junction shift, pan == orthogonal patch angle, pjn == orthogonal patch angle of junction
    '''
    conf_suffix = '' # -jun_10
    dims_ls = [20, 2, 7]
    conc_list = [0.05, 0.1, 0.3, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 23, 27, 30, 40, 50] # 
    arm_num_list=[6] #3, 4, 5, 6
    task_list = ['Mean', 'ST Dev', 'Skewness'] # m1, std, m
    # summ_list = ['-Patch', '-k2']
    # customization of series ~ conc
    color_list = ['#4994FF','#E55050','#FCC555','#7AA77A'] # np.array((0.1, 0.2, 0.5)).reshape((1,3))  '#4994FF','#E55050','#FFF555','#7AA77A'
    marker_list = ['o','v','^','s'] # 'o','v','^','s'
    # if conf_suffix[:5] == '-jun_':
    #     dims_ls[1] = conf_suffix[-1]

    # summ_plot_pa(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_k2(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_as(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)    
    # summ_plot_pj(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_kj(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_rj(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_js(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_pan(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_pjn(conf_suffix, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    return True

def summ_plot_main_jun():
    '''
    Summary plot of nanostars with its design varied: currently varying the central unpaired bases at junction (default dimensions:[20,n,7])
    Summary plot: [tasks of] var #unpaired bases [at different temp, arm_num and conc]
    Set designs in jun_list. Length must > 2
    Set conditions in conc_list, temp_list, arm_num_list. Length must > 2
    The lengths of color_list and marker_list must  == len(temp_list)
    var conf_suffix is only for debug; var dims_ls is dummy now.
    '''
    conf_suffix = '' # -jun_10
    dims_ls = [20,2,7]
    conc_list = [0.1, 0.5]
    temp_list = [20, 30]
    arm_num_list=[6] #3,4,5,6
    task_list = ['Mean', 'ST Dev', 'Skewness'] # m1, std, m
    # summ_list = ['-Patch', '-k2']
    # customization of series ~ conc
    color_list = ['#4994FF','#E55050'] # np.array((0.1, 0.2, 0.5)).reshape((1,3))
    marker_list = ['o','v']

    jun_list = [0,1,2,5,10]

    summ_plot_pa_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)   
    # summ_plot_k2_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_as_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_pj_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_kj_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_rj_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_js_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    # summ_plot_pan_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)   
    # summ_plot_pjn_jun(jun_list, dims_ls, conc_list, temp_list, arm_num_list, task_list, color_list, marker_list)
    return True

def report_plot():
    '''
    Draw plots for report.
    '''
    conf_suffix = '' # -jun_10
    dims_ls = [20, 2, 7]
    conc_list = [0.05, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 50] # 20, 23, 27, 30, 40, 50
    arm_num_list=[3, 4, 5, 6] # 
    # task_list = ['Mean', 'ST Dev', 'Skewness'] # m1, std, m
    # summ_list = ['-Patch', '-k2']
    # customization of series ~ conc
    color_list = ['#4994FF','#E55050','#FFF555','#7AA77A'] # np.array((0.1, 0.2, 0.5)).reshape((1,3))  '#4994FF','#E55050','#FFF555','#7AA77A'
    marker_list = ['^','v','o','s'] # 'o','v','^','s'
    # from plot_tasks.report_tasks.report_plot_k2 import report_plot_k2
    # report_plot_k2(conf_suffix,dims_ls,conc_list,temp_list,arm_num_list,color_list,marker_list)
    # from plot_tasks.report_tasks.report_plot_js import report_plot_js
    # report_plot_js()
    from plot_tasks.report_tasks.report_plot_pa import report_plot_pa
    report_plot_pa()
    return True

def misc():
    plot_summ_dic = {}
    arm_list = [4]
    jun_list = [0, 1, 2, 5, 10]
    for arm in arm_list:
        for jun in jun_list:
            if jun == 2:
                conc_list = [0.05, 0.1, 0.3, 0.5] # 0.05, 0.1, 0.3, 0.5
                temp_list = [20, 23, 27, 30, 40, 50] # 20, 23, 27, 30, 40, 50
            else:
                conc_list = [0.1, 0.5] # 0.05, 0.1, 0.3, 0.5
                temp_list = [20, 30] # 20, 23, 27, 30, 40, 50
            for temp in temp_list:
                for conc in conc_list:
                    plot_summ_dic[(arm,jun,temp,conc)] = ns_time_summ_pa(arm, jun, temp, conc)
    stacking_scatter_plot(plot_summ_dic)
    return True

def stacking_scatter_plot(plot_summ_dic):
    fig, ax = plt.subplots()
    jun_list = [0, 1, 2, 5, 10]
    conc_list = [0.05, 0.1, 0.3, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 23, 27, 30, 40, 50] # 20, 23, 27, 30, 40, 50
    markers = ['v', 's',  '*', 'o', 'p', '8', 'h', 'H', 'D', 'd', 'P', 'X']
    plotting_stacking_type = {'with_stacking':('stacking', 'nonstacking', 'unlinked'), 'linked': ('stacking', 'nonstacking', 'no-stacking,linked')}
    # different stacking types?
    cm_sub = np.linspace(0.3, 1, 10)
    cmap = plt.get_cmap('hot')
    colors = [cmap(x) for x in cm_sub]
    for cond, vals in plot_summ_dic.items():
        arm,jun,temp,conc = cond
        prop_stacking = vals['prop_stacking']
        del vals['prop_stacking']
        for stacking_type, summ in vals.items():
            freq, m1, std, m3_s = summ
            n = sum(freq)
            if stacking_type in plotting_stacking_type['with_stacking']:
                lw = 0.6
            else:
                lw = 0.2
            if stacking_type in plotting_stacking_type['linked']:
                ax.scatter(m1, std, color=colors[temp_list.index(temp)], marker=markers[conc_list.index(conc)], s=5*(jun+1), linewidth=lw, edgecolor='#000000')
            else:
                ax.scatter(m1, std, color=colors[temp_list.index(temp)], marker=markers[conc_list.index(conc)], s=5*(jun+1), linewidth=lw, edgecolor=colors[temp_list.index(temp)], facecolors='none')
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\sigma$')
    ax.set_title('edgewidth: if stacking or not; markerfill: if linked or not')
    ax.set_xlim((70,170))
    ax.set_ylim((10,40))
    plt.savefig(f'tmp/2.jpg', dpi = 500)
    return True

def ns_time_summ_pa(arms, jun, temp, conc):
    ns_struc_4arm = {'linked_PA': [(0,1),(0,3),(1,2),(2,3)], 'unlinked_PA': [(0,2),(1,3)], 'pairing_linked':[((0,1),(2,3)),((0,3),(1,2))], 'pairing_unlinked':[((0,2),(1,3))]}
    stacking_options_ls = [('stacking', 'nonstacking', 'unlinked'),('no-stacking,unlinked','no-stacking,linked')] # 'stacking', 'nonstacking', 'unlinked', 'no-stacking,unlinked','no-stacking,linked', transiting?
    sp_suffix = ''
    conf_suffix = '' # -jun_10
    dims_ls = [20, 2, 7]
    if jun == 2:
        conf_suffix = ''
    else:
        conf_suffix = f'-jun_{jun}'
        dims_ls[1] = jun
    varname = 'pa'
    label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
    path = f'results/{arms}arms{conf_suffix}/{varname}/{varname}_vtime-{label}.png'
    with open(os.path.splitext(path)[0]+'.stack','rb') as f:
        stacking_vtime_dic, nonstacking_vtime_dic = pickle.load(f)
    # determine if the NS is stacking
    time_idx = stacking_vtime_dic[(0,1)]['t']
    stacking_state_arr = np.zeros(len(time_idx))
    for idx in ns_struc['linked_PA']:
        stacking_state_arr += np.array(stacking_vtime_dic[idx]['bool'], dtype=int)
    num_stacking = len(stacking_state_arr) - sum([1 if b == 0 else 0 for b in stacking_state_arr])
    num_double_stacking = sum([1 if b == 2 else 0 for b in stacking_state_arr])
    high_prop_stacking = True if num_stacking/len(stacking_state_arr) > 0.1 else False
    summ_dic = {'prop_stacking':high_prop_stacking} 
    if high_prop_stacking:
        for stacking_option in stacking_options_ls[0]:
            var_ls = create_var_ls(stacking_option,ns_struc,stacking_vtime_dic,nonstacking_vtime_dic)
            summ_dic[stacking_option] = tmp_summ(var_ls, 36) # n, m1, std, m3_s
    else:
        for stacking_option in stacking_options_ls[1]:
            var_ls = create_var_ls(stacking_option,ns_struc,stacking_vtime_dic,nonstacking_vtime_dic)
            summ_dic[stacking_option] = tmp_summ(var_ls, 36) # n, m1, std, m3_s
    return summ_dic

def create_var_ls(is_stacking,ns_struc,stacking_vtime_dic,nonstacking_vtime_dic):
    var_ls = []
    if is_stacking == 'unlinked':
        for iaidx in ns_struc['unlinked_PA']:
            var_ls.extend(stacking_vtime_dic[iaidx]['raw'])                        
    elif is_stacking == 'no-stacking,unlinked':
        for iaidx in ns_struc['unlinked_PA']:
            mask = ~(np.array(stacking_vtime_dic[iaidx]['bool']) + np.array(nonstacking_vtime_dic[iaidx]['bool']))
            pa_ls = np.array(stacking_vtime_dic[iaidx]['raw'],dtype=float) * mask.astype(int)
            var_ls.extend(pa_ls[pa_ls!=0])
    elif is_stacking == 'no-stacking,linked':
        for iaidx in ns_struc['linked_PA']:
            mask = ~(np.array(stacking_vtime_dic[iaidx]['bool']) + np.array(nonstacking_vtime_dic[iaidx]['bool']))
            pa_ls = np.array(stacking_vtime_dic[iaidx]['raw'],dtype=float) * mask.astype(int)
            var_ls.extend(pa_ls[pa_ls!=0])
    else:
        for iaidx in ns_struc['linked_PA']:
            if is_stacking == 'stacking':
                pa_ls = np.array(stacking_vtime_dic[iaidx]['raw'],dtype=float) * np.array(stacking_vtime_dic[iaidx]['bool'],dtype=int)
            elif is_stacking == 'nonstacking':
                pa_ls = np.array(nonstacking_vtime_dic[iaidx]['raw'],dtype=float) * np.array(nonstacking_vtime_dic[iaidx]['bool'],dtype=int)
            else:
                assert 0==1
            var_ls.extend(pa_ls[pa_ls!=0])
    return var_ls

def tmp_summ(var_ls, bin_num):
    x_lim = (0,180)
    y_lim = (0,0.2)
    n,bin_edges = np.histogram(var_ls,bins = bin_num, range = x_lim)
    n, m1, std, m3_s = moments_calc(n, var_ls)
    return n, m1, std, m3_s


def moments_calc(n, var_ls):
    '''
    Calculate the 0th raw, 1st raw, 2nd central, and 3rd standardized moment of a given distribution.
    '''
    n = np.array(n)
    m0 = np.sum(n) # 0th unitless raw moment: integration
    m1 = np.sum(var_ls)/m0
    m2_c = stats.moment(var_ls, moment=2) # 2nd central moment: variance
    std = m2_c**0.5 # standard deviation
    m3_c = stats.moment(var_ls, moment=3) # 3rd central moment
    m3_s = m3_c / (std**3) # 3rd standardized moment: skewness
    return n, m1, std, m3_s
# jobs end

if __name__ == '__main__':
    # summ_plot_main()
    # summ_plot_main_jun()
    misc()
    # calc_value_obtain()
    # debug_ns_arm_examine()
    # debug_pairing()
    # report_plot()
    print('DONE')


'''
01-30 Propensity-plot
def misc():
    conc_list = [0.1, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 30] # 20, 23, 27, 30, 40, 50
    jun_list = [5,10]
    ns_stacking_state_plotting(conc_list, temp_list, jun_list)
    return True

def ns_stacking_state_plotting(conc_list, temp_list, jun_list):
    import pickle
    ns_struc_4arm = {'linked_PA': [(0,1),(0,3),(1,2),(2,3)], 'unlinked_PA': [(0,2),(1,3)], 'pairing_linked':[((0,1),(2,3)),((0,3),(1,2))], 'pairing_unlinked':[((0,2),(1,3))]}
    sp_suffix = ''
    conf_suffix = '' # -jun_10
    dims_ls = [20, 2, 7]
    conc_list = [0.05, 0.1, 0.3, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 23, 27, 30, 40, 50] # 20, 23, 27, 30, 40, 50
    arm_num_list=[4] #3, 4, 5, 6
    jun_list = [2]
    varname = 'pa'
    # loop through conditions, link all values together
    for arms in arm_num_list:
        for jun in jun_list:
            if jun == 2:
                conf_suffix = ''
            else:
                conf_suffix = f'-jun_{jun}'
                dims_ls[1] = jun
            for conc in conc_list:
                for temp in temp_list:
                    label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
                    path = f'results/{arms}arms{conf_suffix}/{varname}/{varname}_vtime-{label}.png'
                    with open(os.path.splitext(path)[0]+'.stack','rb') as f:
                        stacking_vtime_dic, nonstacking_vtime_dic = pickle.load(f)
                    time_idx = stacking_vtime_dic[(0,1)]['t']
                    stacking_state_ls = []
                    for i in range(len(time_idx)):
                        stacking_state_ls.append(sum([stacking_vtime_dic[idx]['bool'][i] for idx in ns_struc['linked_PA']]))
                    # plot
                    plotpath = os.path.splitext(path)[0]+'-state-chart.png'
                    fig, ax = plt.subplots()
                    num_stacking = len(stacking_state_ls) - sum([1 if b == 0 else 0 for b in stacking_state_ls])
                    num_double_stacking = sum([1 if b == 2 else 0 for b in stacking_state_ls])
                    ax.plot(time_idx,stacking_state_ls,label = f'#Stacking: {num_stacking} , Stacking%: {num_stacking/len(stacking_state_ls):.2f} \n#2-stacking: {num_double_stacking} , 2-stacking%: {num_double_stacking/len(stacking_state_ls):.2f}')
                    ax.legend()
                    plt.savefig(plotpath)
                    plt.close()
    return True

01-30 pooling histogram
def data_process_func(p_ang_ls_res, data, vtime = False): # should be trimmed.
    from collections import OrderedDict
    import numpy as np
    p_angs_dic, arms_idx = p_ang_ls_res
    # tracing of specific p-angles setup
    angle_dic = OrderedDict() # {(ia1, ia2):{t_stamp:angle}} 
    for idx_1, ia1 in enumerate(arms_idx):
        for idx_2 in range(idx_1+1, len(arms_idx)):
            ia2 = arms_idx[idx_2]
            angle_dic[(ia1, ia2)] = OrderedDict()
    # hist of p-angle
    drop_t_ls = []
    for t_stamp, ang_ls in p_angs_dic.items():
        ## sanity chk: because of old pairing method. TODO: look into the dropped frames
        s = [1 for i in ang_ls if i[1] == True]
        if len(s) != len(arms_idx): # n arms should yield n angles.
            print(t_stamp)
            drop_t_ls.append(t_stamp)
            continue
        ## chk ends
        for ang, is_sharing, ia_tp in ang_ls:
            # {(ia1, ia2):{t_stamp:angle, 'is_sharing':is_sharing}}
            angle_dic[ia_tp][t_stamp] = [ang] # tracing of specific p-angles
            if 'is_sharing' not in angle_dic[ia_tp].keys():
                angle_dic[ia_tp]['is_sharing'] = is_sharing
    print(f'Total time steps dropped: {len(drop_t_ls)}')
    t_ls = [t for t in angle_dic[(0,1)] if type(t) == int]
    ang_ls = [t_dic[t][0] for t_dic in angle_dic.values() if t_dic['is_sharing']==True for t in t_ls] # pooled for is_sharing
    if vtime == False:
        return ang_ls
    else:
        return angle_dic

def draw_ns_pooling():
    is_stacking_ls = ['no-stacking,unlinked','no-stacking,linked'] # 'stacking', 'nonstacking', 'unlinked', 'no-stacking,unlinked','no-stacking,linked', transiting?
    conc_list = [0.1, 0.5] # 0.05, 0.1, 0.3, 0.5
    temp_list = [20, 30] # 20, 23, 27, 30, 40, 50
    jun_list = [5,10]
    for is_stacking in is_stacking_ls:
        for conc in conc_list:
            for temp in temp_list:
                for jun in jun_list:
                    ns_time_pool_pa(is_stacking,[conc],[temp],[jun])
        for conc in conc_list:
            ns_time_pool_pa(is_stacking,[conc],temp_list,jun_list)
        for temp in temp_list:
            ns_time_pool_pa(is_stacking,conc_list,[temp],jun_list)
        for jun in jun_list:
            ns_time_pool_pa(is_stacking,conc_list,temp_list,[jun])
    # ns_time_pool_pa()
    return True

def ns_time_pool_pa(is_stacking,conc_list,temp_list, jun_list):
    import pickle
    ns_struc_4arm = {'linked_PA': [(0,1),(0,3),(1,2),(2,3)], 'unlinked_PA': [(0,2),(1,3)], 'pairing_linked':[((0,1),(2,3)),((0,3),(1,2))], 'pairing_unlinked':[((0,2),(1,3))]}
    # is_stacking = 'stacking' # 'stacking', 'nonstacking', 'unlinked', 'no-stacking,unlinked','no-stacking,linked', transiting?
    sp_suffix = ''
    conf_suffix = '' # -jun_10
    dims_ls = [20, 2, 7]
    # conc_list = [0.1] # 0.05, 0.1, 0.3, 0.5
    # temp_list = [20] # 20, 23, 27, 30, 40, 50
    arm_num_list=[4] #3, 4, 5, 6
    # jun_list = [2]
    # loop through conditions, link all values together
    var_ls = []
    for arms in arm_num_list:
        for jun in jun_list:
            if jun == 2:
                conf_suffix = ''
            else:
                conf_suffix = f'-jun_{jun}'
                dims_ls[1] = jun
            for conc in conc_list:
                for temp in temp_list:
                    varname = 'pj'
                    label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
                    pj_path = f'results/{arms}arms{conf_suffix}/{varname}/{varname}_vtime-{label}.png'
                    with open(os.path.splitext(pj_path)[0]+'.stack','rb') as f:
                        stacking_vtime_dic, nonstacking_vtime_dic = pickle.load(f)
                    varname = 'pa'
                    loose_lbl = f'{temp}C-{conc}M-GPU{sp_suffix}'
                    savepath = f'data/composed_traj/{arms}arms{conf_suffix}/{loose_lbl}/{label}'
                    var_path = f'{savepath}.{varname}tp'
                    with open(var_path,'rb') as f:
                        pa_raw_dic = pickle.load(f)
                    pa_vtime_dic = data_process_func(pa_raw_dic, None, vtime = True)
                    # create var_ls according to is_stacking options
                    if is_stacking == 'unlinked':
                        for iaidx in ns_struc['unlinked_PA']:
                            t_ls = stacking_vtime_dic[iaidx]['t']
                            pa_ls = [pa_vtime_dic[iaidx][t][0] for t in t_ls]
                            var_ls.extend(pa_ls)                        
                    elif is_stacking == 'no-stacking,unlinked':
                        for iaidx in ns_struc['unlinked_PA']:
                            t_ls = stacking_vtime_dic[iaidx]['t']
                            pa_ls = [pa_vtime_dic[iaidx][t][0] for t in t_ls]
                            var_ls.extend(pa_ls)                        
                    elif is_stacking == 'no-stacking,linked':
                        for iaidx in ns_struc['linked_PA']:
                            t_ls = stacking_vtime_dic[iaidx]['t']
                            pa_ls = [pa_vtime_dic[iaidx][t][0] for t in t_ls]
                            var_ls.extend(pa_ls)                        
                    else:
                        for iaidx in ns_struc['linked_PA']:
                            t_ls = stacking_vtime_dic[iaidx]['t']
                            if is_stacking == 'stacking':
                                bool_ls = stacking_vtime_dic[iaidx]['bool']
                                t_ls = list(filter(None,[t_ls[i] if bool_ls[i] else None for i in range(len(bool_ls))]))
                            elif is_stacking == 'nonstacking':
                                bool_ls = nonstacking_vtime_dic[iaidx]['bool']
                                t_ls = list(filter(None,[t_ls[i] if bool_ls[i] else None for i in range(len(bool_ls))]))
                            else:
                                assert 0==1
                            pa_ls = [pa_vtime_dic[iaidx][t][0] for t in t_ls]
                            var_ls.extend(pa_ls)
    # draw histogram
    bin_num = 36
    plt = tmp_plot(var_ls, bin_num, is_stacking)
    plt.title(f'PA-pool,{arm_num_list}arm,{temp_list}C,{conc_list}M,jxn:{jun_list}')
    plt.savefig(f'tmp/PA-pool,{is_stacking},{arm_num_list}arm,{temp_list}C,{conc_list}M,{jun_list}jxn.png',dpi=400)
    plt.close()
    return True

def tmp_plot(var_ls, bin_num, is_stacking):
    x_lim = (0,180)
    y_lim = (0,0.2)
    n,bin_edges = np.histogram(var_ls,bins = bin_num, range = x_lim)
    bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
    # moments
    n, m1, std, m3_s = moments_calc(n, var_ls)
    ax = plt.axes()
    n_sum = np.sum(n)
    plt.bar(bin_centers,np.divide(np.array(n),n_sum),width=180/bin_num, color='#4994FF',label=rf'{is_stacking}, $N={np.sum(n):.2f}$, $\mu={m1:.2f}$, $\sigma={std:.2f}$, $\gamma={m3_s:.2f}$')
    plt.errorbar(bin_centers,np.divide(np.array(n),n_sum),yerr = np.divide(np.sqrt(np.array(n)),n_sum),marker = '.',markersize=2,drawstyle = 'steps-mid',c='#f7aed0',linewidth=0.7,ecolor='#f7aed0')
    # customization
    txt = (
        rf'$N={np.sum(n):.2f}$'
        '\n'
        rf'$\mu={m1:.2f}$'
        '\n'
        rf'$\sigma={std:.2f}$'
        '\n'
        rf'$\gamma={m3_s:.2f}$'
    )
    text_x, text_y = (0,0)
    plt.text(text_x, text_y, txt, c='#4994FF')
    plt.ylim(y_lim)
    plt.legend()
    # customization ends
    return plt


01-14 sloan plots
def sloan_hist_plot():
    # ns_pa_plot(single=True,arms=5,temp=23,conc=0.3)
    # for conc in conc_list:
    #     ns_k2_plot(single=True,arms=4,temp=30,conc=conc)

    # dims_ls = [20,1,7]
    # arms = 6
    # temp = 30
    # conc = 0.3
    # conf_suffix = '-jun_1' #-jun_1
    # sp_suffix = ''
    # label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
    # loose_lbl = f'{temp}C-{conc}M-GPU{sp_suffix}'
    # p = f'data/composed_traj/{arms}arms{conf_suffix}/{loose_lbl}/{label}.k2tp'
    # # finding_extreme_k2_vals(p) # deprecated. saved in DNA3
    # top_path = f'../../ox-sync/simul-inputs-{arms}arms{conf_suffix}/{arms}arm-rods-clustered{conf_suffix}.top'
    # traj_path = f'../../ox-sync/simul-inputs-{arms}arms{conf_suffix}/{loose_lbl}/trajectory.dat'
    # from calc_tasks.patch_angle_calc import patch_angle_calc as pa
    # pa(top_path,traj_path,arms,dims_ls)

    f = open('data\composed_traj\\4arms\\20C-0.1M-GPU\\4arms@(20C,0.1M).patp','rb')
    import pickle
    patp = pickle.load(f)
    f.close()

    pa_v_t = patp[0]
    # t_ls = np.arange(50100000,150000000,100000)
    # t_ls = np.arange(20100000,60200000,100000)
    t_ls = np.arange(65000000,80000000,100000)
    # pool_idx = [[(0,1),(2,3)],[(0,2),(1,3)],[(0,3),(1,2)]]
    pool_idx = [(0,1),(2,3),(0,2),(1,3),(0,3),(1,2)]
    # pool_idx = [[(0,2),(1,3)],[(0,1),(2,3),(0,3),(1,2)]]
    ang_dic = {}
    for i in range(6):
        idx = pa_v_t[50100000][i][2]
        # idx = pa_v_t[20100000][i][2]
        ang_dic[idx] = [pa_v_t[t][i][0] for t in t_ls]
    for idx_ls in pool_idx:
        if type(idx_ls) is list:
            idx1 = idx_ls[0]
            var_ls = ang_dic[idx1]
            for i in range(len(idx_ls)-1):
                idx2 = idx_ls[i+1]
                var_ls.extend(ang_dic[idx2])
        else:
            idx1 = idx_ls
            var_ls = ang_dic[idx1]
        x_lim = (0,180)
        bin_num = 36
        n,bin_edges = np.histogram(var_ls,bins = bin_num, range = x_lim)
        bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])

        # moments
        n, m1, std, m3_s = moments_calc(n, var_ls)

        ax = plt.axes()
        n_sum = np.sum(n)
        # plt.bar(bin_centers,np.divide(np.array(n),n_sum),width=180/bin_num, color='#4994FF',label=f'{idx1} joining {idx2}')
        plt.bar(bin_centers,np.divide(np.array(n),n_sum),width=180/bin_num, color='#4994FF',label=f'{idx1}')
        plt.errorbar(bin_centers,np.divide(np.array(n),n_sum),yerr = np.divide(np.sqrt(np.array(n)),n_sum),marker = '.',markersize=2,drawstyle = 'steps-mid',c='#f7aed0',linewidth=0.7,ecolor='#f7aed0')
        # customization
        txt = (
            rf'$N={np.sum(n):.2f}$'
            '\n'
            rf'$\mu={m1:.2f}$'
            '\n'
            rf'$\sigma={std:.2f}$'
            '\n'
            rf'$\gamma={m3_s:.2f}$'
        )
        text_x, text_y = (20800000,160)
        plt.text(text_x, text_y, txt, c='#4994FF') # 28%
        plt.ylim((0,0.15))
        plt.legend()
        # customization ends
        # plt.savefig(f'tmp/pa_v_t-Arm{idx1}~{idx2}-t[20100000,60200000].jpg',dpi=400)
        plt.savefig(f'tmp/pa_v_t-Arm{idx1}-t[20100000,60200000].jpg',dpi=400)
        # plt.show()
        plt.close()
        plt.clf()
        print(f'PA: {idx1} , mean: {m1} , std: {std} , skewness: {m3_s}')
        # print(f'PA: {idx1} joining {idx2} , mean: {m1} , std: {std} , skewness: {m3_s}')
    # print(stats.ks_2samp(ang_dic[(0,1)],ang_dic[(2,3)]))
    # print(stats.ks_2samp(ang_dic[(0,2)],ang_dic[(1,3)]))
    # print(stats.ks_2samp(ang_dic[(0,3)],ang_dic[(1,2)]))
    return True

10-02 debug: s1.reverse(): arm not generated correctly.
def data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix = ''):
    dims_ls = [20,2,7]
    label = f'{arms}arms@({temp}C,{conc}M){conf_suffix}{sp_suffix}'
    loose_lbl = f'{temp}C-{conc}M-GPU{sp_suffix}'
    savepath = f'data/composed_traj/{arms}arms{conf_suffix}/{loose_lbl}/{label}.{varname}'
    import pickle
    result = pickle.load(open(savepath,'rb'))
    return result

def calc_data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix = ''):
    varname = varname+'tp'
    result = data_extraction(varname, arms, temp, conc, conf_suffix, sp_suffix)
    return result

def datapoint_location(tg_value, result):
    import numpy as np
    result_val = [tp[1] for tp in result]
    r_arr = np.array(result_val)
    r_tg_loc = np.argmin(np.abs(r_arr-tg_value))
    t_stamp, r_tg = result[r_tg_loc]
    return t_stamp, r_tg

def calc_value_obtain():
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    varname = 'rj'
    result = calc_data_extraction(varname, arms, temp, conc, conf_suffix)
    target = 7.0
    t_stamp, r_tg = datapoint_location(target, result)
    print(f'{arms}arm @ {temp}C and {conc}M with {conf_suffix} , the desired {varname} value: {target} locates at {t_stamp} : true value {r_tg} .')
    return True

def dist(t1, t2):
    return np.sqrt(np.sum(np.square(np.array(t1) - np.array(t2))))

def debug_ns_arm_examine():
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    varname = 'ns'
    ns_tm = data_extraction(varname, arms, temp, conc, conf_suffix)
    ns = ns_tm.time_capsule[ns_tm.timeseries[0]]
    arm = ns.arms[0]
    b_pairs_dic = arm.base_pairs
    import numpy as np
    for i in range(len(b_pairs_dic)):
        b1, b2 = b_pairs_dic[i+1]
        dist = np.sqrt(np.sum(np.square(np.array(b1.position) - np.array(b2.position))))
        print(f'Bpair {i+1}, dist: {dist}')
    return True

def single_pairing_all(sys):
    
    # id_pairs = []
    # strands_ls = [list(strand.base_sequence.values()) for strand in sys.values()]
    # l = len(strands_ls[0])
    # for i in range(l):
    
    pool_b = []
    for strand in sys.values():
        pool_b.extend(list(strand.base_sequence.values()))
    pool_pos = [base.position for base in pool_b]
    base_number = len(pool_pos)
    d_2darr = np.zeros((base_number, base_number))
    for i in range(base_number):
        for j in range(base_number):
            if pool_b[i].strand_id == pool_b[j].strand_id:
                d_2darr[i][j] = 100000
            else:
                d_2darr[i][j] = dist(pool_pos[i], pool_pos[j])
    min_indices = np.argmin(d_2darr,0)
    id_pairs = []
    for i in range(base_number):
        print(dist(pool_b[i].position, pool_b[min_indices[i]].position))
        id_pairs.append((pool_b[i].base_id, pool_b[min_indices[i]].base_id))
    return id_pairs

def debug_pairing():
    arms = 3
    temp = 30
    conc = 0.5
    conf_suffix = '' # -jun_10
    sp_suffix = ''
    sys_tm = data_extraction('sys', arms, temp, conc, conf_suffix)
    sys = sys_tm.time_capsule[sys_tm.timeseries[0]]
    ns_tm = data_extraction('ns', arms, temp, conc, conf_suffix)
    assert sys_tm.timeseries[0] == ns_tm.timeseries[0]
    ns = ns_tm.time_capsule[ns_tm.timeseries[0]]
    id_pairs = single_pairing_all(sys)
    for arm in ns.arms.values():
        for idx, (b1, b2) in arm.base_pairs.items():
            print(f'{(b1.base_id, b2.base_id) in id_pairs}')
    return True











def dump():
    stacking_dic = {
        (4,2,20,0.05):False,
        (4,2,20,0.1):True,
        (4,2,20,0.3):True,
        (4,2,20,0.5):True,
        (4,2,23,0.05):False,
        (4,2,23,0.1):True,
        (4,2,23,0.3):True,
        (4,2,23,0.5):True,
        (4,2,27,0.05):False,
        (4,2,27,0.1):True,
        (4,2,27,0.3):True,
        (4,2,27,0.5):True,
        (4,2,30,0.05):False,
        (4,2,30,0.1):True,
        (4,2,30,0.3):True,
        (4,2,30,0.5):True,
        (4,2,40,0.05):False,
        (4,2,40,0.1):True,
        (4,2,40,0.3):True,
        (4,2,40,0.5):True,
        (4,2,50,0.05):False,
        (4,2,50,0.1):True,
        (4,2,50,0.3):True,
        (4,2,50,0.5):True,

        (4,2,20,0.05):False,
        (4,2,20,0.1):True,
        (4,2,20,0.3):True,
        (4,2,20,0.5):True,
        (4,2,23,0.05):False,
        (4,2,23,0.1):True,
        (4,2,23,0.3):True,
        (4,2,23,0.5):True,
        (4,2,27,0.05):False,
        (4,2,27,0.1):True,
        (4,2,27,0.3):True,
        (4,2,27,0.5):True,
        (4,2,30,0.05):False,
        (4,2,30,0.1):True,
        (4,2,30,0.3):True,
        (4,2,30,0.5):True,
        (4,2,40,0.05):False,
        (4,2,40,0.1):True,
        (4,2,40,0.3):True,
        (4,2,40,0.5):True,
        (4,2,50,0.05):False,
        (4,2,50,0.1):True,
        (4,2,50,0.3):True,
        (4,2,50,0.5):True,

        (4,2,20,0.05):False,
        (4,2,20,0.1):True,
        (4,2,20,0.3):True,
        (4,2,20,0.5):True,
        (4,2,23,0.05):False,
        (4,2,23,0.1):True,
        (4,2,23,0.3):True,
        (4,2,23,0.5):True,
        (4,2,27,0.05):False,
        (4,2,27,0.1):True,
        (4,2,27,0.3):True,
        (4,2,27,0.5):True,
        (4,2,30,0.05):False,
        (4,2,30,0.1):True,
        (4,2,30,0.3):True,
        (4,2,30,0.5):True,
        (4,2,40,0.05):False,
        (4,2,40,0.1):True,
        (4,2,40,0.3):True,
        (4,2,40,0.5):True,
        (4,2,50,0.05):False,
        (4,2,50,0.1):True,
        (4,2,50,0.3):True,
        (4,2,50,0.5):True,

        (4,2,20,0.05):False,
        (4,2,20,0.1):True,
        (4,2,20,0.3):True,
        (4,2,20,0.5):True,
        (4,2,23,0.05):False,
        (4,2,23,0.1):True,
        (4,2,23,0.3):True,
        (4,2,23,0.5):True,
        (4,2,27,0.05):False,
        (4,2,27,0.1):True,
        (4,2,27,0.3):True,
        (4,2,27,0.5):True,
        (4,2,30,0.05):False,
        (4,2,30,0.1):True,
        (4,2,30,0.3):True,
        (4,2,30,0.5):True,
        (4,2,40,0.05):False,
        (4,2,40,0.1):True,
        (4,2,40,0.3):True,
        (4,2,40,0.5):True,
        (4,2,50,0.05):False,
        (4,2,50,0.1):True,
        (4,2,50,0.3):True,
        (4,2,50,0.5):True,

        (4,2,20,0.05):False,
        (4,2,20,0.1):True,
        (4,2,20,0.3):True,
        (4,2,20,0.5):True,
        (4,2,23,0.05):False,
        (4,2,23,0.1):True,
        (4,2,23,0.3):True,
        (4,2,23,0.5):True,
        (4,2,27,0.05):False,
        (4,2,27,0.1):True,
        (4,2,27,0.3):True,
        (4,2,27,0.5):True,
        (4,2,30,0.05):False,
        (4,2,30,0.1):True,
        (4,2,30,0.3):True,
        (4,2,30,0.5):True,
        (4,2,40,0.05):False,
        (4,2,40,0.1):True,
        (4,2,40,0.3):True,
        (4,2,40,0.5):True,
        (4,2,50,0.05):False,
        (4,2,50,0.1):True,
        (4,2,50,0.3):True,
        (4,2,50,0.5):True,
    }
    return True
'''