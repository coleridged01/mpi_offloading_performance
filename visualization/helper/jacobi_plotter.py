import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

libs = [('ucc', '#D1786F') , ('hcoll', '#B4CB8E')]
offloading_modes = [('no-offloading', 'o'), ('tm', '^'), ('dpu', 'X'), ('dpu-rndv@16KiB', '*')]

def plot_jacobi(nprocs, off_modes, nodes, extended=False, title=True, save=False):
    n = "" if nodes == 2 else str(nodes) + "-"
    ext = "extended" if extended else "."

    if nprocs < 2 or nprocs > 1048576 or not np.log2(nprocs).is_integer():
        print('Process count is not a power of 2.')
        exit(1)

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({'font.size': 20})
    commplot, commax = plt.subplots(figsize=(10, 8), dpi=300)
    compplot, compax = plt.subplots(figsize=(10, 8), dpi=300)
    tplot, tax = plt.subplots(figsize=(10, 8), dpi=300)

    for lib in libs:
        for off_mode in offloading_modes:
            if off_mode[0] not in off_modes:
                continue

            if 'dpu' in off_mode[0] and lib[0] != 'ucc':
                continue

            thresh = 'thresh' if off_mode[0] == 'dpu-rndv@16KiB' else '.'
            off = 'dpu' if off_mode[0] == 'dpu-rndv@16KiB' else off_mode[0]

            path = f'../../offloading_modes/benchmarks/jacobi/{n}{str(nprocs)}-dist/{lib[0]}/{off}/{ext}/{thresh}/jacobi.txt'


            data = pd.read_csv(path, sep='\s+', skiprows=1, names=[
                "Matrix Dim. N", "Norm", "Convergence At", "Computation Time",
                "Communication Time", "Total Time"], header=None, engine='python')

            data['Computation Time'] = data['Computation Time'] / 1000
            data['Communication Time'] = data['Communication Time'] / 1000
            data['Total Time'] = data['Total Time'] / 1000

            compax.plot(data['Matrix Dim. N'], data['Computation Time'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])
            commax.plot(data['Matrix Dim. N'], data['Communication Time'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])
            tax.plot(data['Matrix Dim. N'], data['Total Time'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])


    commax.set_xlabel('Matrix Dim. N')
    commax.set_ylabel('Avg. Communication Time (ms) per iteration')
    commax.legend(fontsize=16)
    if title:
        commax.set_title(f'Avg. Jacobi Communication Time per iteration - equally distributed {str(nprocs)} processes over {nodes} nodes - '
                     f'IB')

    compax.set_xlabel('Matrix Dim. N')
    compax.set_ylabel('Avg. Computation Time (ms) per iteration ')
    compax.legend(fontsize=16)
    if title:
        compax.set_title(f'Avg. Jacobi Computation Time per iteration - equally distributed {nprocs} over {nodes} nodes - '
                     f' IB')

    tax.set_xlabel('Matrix Dim. N')
    tax.set_ylabel('Avg. Total Time per iteration (ms)')
    tax.legend(fontsize=16)
    if title:
        tax.set_title(f'Avg. Total Time per iteration - equally distributed {nprocs} over {nodes} nodes - '
                  f'IB')

    if save:
        ext = "_ext" if extended else ""
        postfix_comm = f"comm/comm_{nodes}_{nprocs}{ext}.png"
        postfix_comp = f"comp/comp_{nodes}_{nprocs}{ext}.png"
        postfix_total = f"total/total_{nodes}_{nprocs}{ext}.png"

        commplot.savefig(f"jacobi/{postfix_comm}", dpi=300, bbox_inches='tight')
        compplot.savefig(f"jacobi/{postfix_comp}", dpi=300, bbox_inches='tight')
        tplot.savefig(f"jacobi/{postfix_total}", dpi=300, bbox_inches='tight')
        plt.close('all')
    else:
        plt.show()
