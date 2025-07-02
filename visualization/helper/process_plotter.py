import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
import matplotlib as mpl

block_coll = ['allgather', 'allreduce', 'alltoall', 'bcast', 'gather', 'reduce', 'reduce_scatter', 'scatter', 'allgatherv', 'alltoallv']
non_block_coll = ['iallgather', 'ialltoall', 'ibcast', 'igather', 'iscatter', 'iallgatherv', 'ialltoallv']

libs = [
    ('ucc', '#D1786F') ,
    # ('han', '#8F7DC1'),
    ('hcoll', '#B4CB8E')
]
offloading_modes = [('no-offloading', 'o', '//'), ('tm', '^', '\\\\'), ('dpu', 'X', '--')]

def plot_overlap_ratios(plot, color, hatch, df, label, i, n):
    bar_width = 0.8 / n

    message_sizes = df['Size'].values.tolist()

    x_positions = np.arange(len(message_sizes))
    plot.bar(x_positions + i * bar_width - (n / 2) * bar_width + bar_width / 2,
        df['Overlap'],
        bar_width,
        label=label,
        color=color,
        hatch=hatch,
        edgecolor='black',
        linewidth=1
    )


def format_size(sizes):
    return [
        f"{float(size / 1024) if size < 1024 else int(size / 1024)}"
        for size in sizes
    ]

def plot_fixed_process_count(nprocs: int, off_modes, nodes, save=False, title=True, save_list=None, savepath=None):
    nod = "" if nodes == 2 else str(nodes) + "-"
    skiprows = 0

    if nprocs < 2 or nprocs > 1048576 or not np.log2(nprocs).is_integer():
        print('Process count is not a power of 2.')
        exit(1)

    os.makedirs("plots", exist_ok=True)

    mpl.rcParams['axes.formatter.useoffset'] = False
    mpl.rcParams['axes.formatter.limits'] = (-5, 5)
    plt.rcParams.update({'font.size': 24})

    for bc in block_coll:
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(10, 8), dpi=300)
        for lib in libs:
            for off_mode in offloading_modes:
                if off_mode[0] not in off_modes:
                    continue

                if off_mode[0] == 'dpu' and nprocs > 32:
                    continue

                if off_mode[0] == 'dpu' and lib[0] != 'ucc':
                    continue

                path = f'../../offloading_modes/benchmarks/osu/{nod}{str(nprocs)}-dist/{lib[0]}/{off_mode[0]}/{bc}.txt'
                if not os.path.exists(path):
                    continue

                data = pd.read_csv(path, sep='\s+', comment='#', header=None, skiprows=skiprows, skipfooter=skiprows, engine='python')
                data.columns =  ['Size', 'AvgLatency(ms)']

                data['Size'] = data['Size'] / 1000
                data['AvgLatency(ms)'] = data['AvgLatency(ms)'] / 1000

                plt.plot(data['Size'], data['AvgLatency(ms)'], color=lib[1],  label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])


        # PLOT
        plt.ticklabel_format(style='plain', axis='x')
        if title:
            plt.title(f'{bc} - Benchmark {str(nprocs)} processes over {nodes} nodes - InfiniBand')
        plt.xlabel('Message Size (KB)')
        plt.ylabel('Avg. Latency (ms)')
        plt.legend()
        plt.grid(True)

        if save or savepath:
            postfix = f'{bc}_{nodes}_{nprocs}.png'

            if savepath and (not save_list or postfix in save_list):
                plt.savefig(f'{savepath}/{postfix}')

            plt.savefig(f"plots/{postfix}", dpi=300, bbox_inches='tight')
            plt.close('all')
        else:
            plt.show()

    for nbc in non_block_coll:

        oplot, oax = plt.subplots(figsize=(10, 8), dpi=300)
        cplot, cax = plt.subplots(figsize=(10, 8), dpi=300)
        pplot, pax = plt.subplots(figsize=(10, 8), dpi=300)
        ovplot, ovax = plt.subplots(figsize=(10, 8), dpi=300)

        message_sizes = 0

        n = 2 * len(libs) + (1 if 'dpu' in off_modes else 0)

        i = 0
        for lib in libs:
            for off_mode in offloading_modes:
                if off_mode[0] not in off_modes:
                    continue

                if off_mode[0] == 'dpu' and nprocs == 64:
                    continue

                if off_mode[0] == 'dpu' and lib[0] != 'ucc':
                    continue

                path = f'../../offloading_modes/benchmarks/osu/{nod}{str(nprocs)}-dist/{lib[0]}/{off_mode[0]}/{nbc}.txt'
                if not os.path.exists(path):
                    continue
                data = pd.read_csv(path, sep='\s+', comment='#', header=None, skiprows=skiprows, skipfooter=skiprows, engine='python')
                data.columns = ['Size', 'Overall', 'Compute', 'PureComm.', 'Overlap']

                data['Size'] = data['Size'] / 1000
                data['Overall'] = data['Overall'] / 1000
                data['Compute'] = data['Compute'] / 1000
                data['PureComm.'] = data['PureComm.'] / 1000

                oax.plot(data['Size'], data['Overall'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])
                cax.plot(data['Size'], data['Compute'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])
                pax.plot(data['Size'], data['PureComm.'], color=lib[1], label=f'{lib[0]} - {off_mode[0]}', marker=off_mode[1])

                data = data[data['Size'] >= 512]
                message_sizes = data['Size'].to_list()
                plot_overlap_ratios(ovax, color=lib[1], hatch=off_mode[2], df=data, label=f'{lib[0]} - {off_mode[0]}', i=i, n=n)
                i += 1

        oax.set_xlabel('Message Size (KB)')
        oax.set_ylabel('Overall Latency (ms)')

        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(False)
        formatter.set_powerlimits((0, 0))
        oax.xaxis.set_major_formatter(formatter)
        oax.xaxis.get_offset_text().set_visible(False)
        oax.legend()
        if title:
            oax.set_title(f'Overall Time - {nbc} Benchmark {str(nprocs)} processes over {nodes} nodes InfiniBand')

        cax.set_xlabel('Message Size (KB)')
        cax.set_ylabel('Compute time (ms)')

        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(False)
        formatter.set_powerlimits((0, 0))
        cax.xaxis.set_major_formatter(formatter)
        cax.xaxis.get_offset_text().set_visible(False)
        cax.legend()
        if title:
            cax.set_title(f'Compute Time - {nbc} Benchmark over {str(nprocs)} processes over {nodes} nodes InfiniBand')


        pax.set_xlabel('Message Size (KB)')
        pax.set_ylabel('Pure Communication Time (ms)')

        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(False)
        formatter.set_powerlimits((0, 0))
        pax.xaxis.set_major_formatter(formatter)
        pax.xaxis.get_offset_text().set_visible(False)
        pax.legend()
        if title:
            pax.set_title(f'Pure Communication Time - {nbc} Benchmark over {str(nprocs)} processes over {nodes} nodes InfiniBand')

        x_positions = np.arange(len(message_sizes))
        ovax.set_xlabel('Message Size (KiB)')
        ovax.set_ylabel('Overlap (%)')
        ovax.set_xticks(x_positions)
        ovax.set_xticklabels(format_size(message_sizes), fontsize=16)
        ovax.legend(fontsize=14)
        if title:
            ovax.set_title(f'Overlap Ratio - {nbc} Benchmark over {str(nprocs)} processes over {nodes} nodes InfiniBand')

        if save or savepath:
            postfix_ov = f'{nbc}_{nodes}_{nprocs}_overlap.png'
            postfix_p = f'{nbc}_{nodes}_{nprocs}_comm.png'
            postfix_c = f'{nbc}_{nodes}_{nprocs}_comp.png'
            postfix_o = f'{nbc}_{nodes}_{nprocs}_overall.png'
            if savepath and (not save_list or postfix_ov in save_list):
                ovplot.savefig(f"{savepath}/{postfix_ov}", dpi=300, bbox_inches='tight')

            if savepath and (not save_list or postfix_ov in save_list):
                pplot.savefig(f"{savepath}/{postfix_p}", dpi=300, bbox_inches='tight')

            if savepath and (not save_list or postfix_ov in save_list):
                cplot.savefig(f"{savepath}/{postfix_c}", dpi=300, bbox_inches='tight')

            if savepath and (not save_list or postfix_ov in save_list):
                oplot.savefig(f"{savepath}/{postfix_o}", dpi=300, bbox_inches='tight')

            ovplot.savefig(f"plots/{postfix_ov}", dpi=300, bbox_inches='tight')
            pplot.savefig(f"plots/{postfix_p}", dpi=300, bbox_inches='tight')
            cplot.savefig(f"plots/{postfix_c}", dpi=300, bbox_inches='tight')
            oplot.savefig(f"plots/{postfix_o}", dpi=300, bbox_inches='tight')
            plt.close('all')
        else:
            plt.show()




