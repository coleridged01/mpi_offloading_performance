import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from visualization.helper.process_plotter import format_size

block_coll = ['allgather', 'allreduce', 'alltoall', 'bcast', 'gather', 'reduce', 'reduce_scatter', 'scatter']
non_block_coll = ['iallgather', 'ialltoall', 'ibcast', 'igather', 'iscatter']

libs = ['ucc', 'han', 'hcoll']
offloading_modes = ['no-offloading', 'tm']

scale = [4, 8, 16, 32]

def plot_overlap_ratios(plot, df, label, i, n):
    bar_width = 0.8 / n

    message_sizes = np.hstack(df['NumProc']).tolist()
    x_positions = np.arange(len(message_sizes))
    plot.bar(x_positions + i * bar_width - (n / 2) * bar_width + bar_width / 2,
            df['Overlap'],
            bar_width,
            label=label)

def plot_proc_scale(msg_size):
    for bc in block_coll:
        plt.figure(figsize=(10, 8))
        for lib in libs:
            for off_mode in offloading_modes:
                comp = pd.DataFrame()

                for s in scale:
                    path = f'../../offloading_modes/{off_mode}/osu/{str(s)}-dist/{lib}/{str(s)}/collective/{bc}.txt'
                    data = pd.read_csv(path, sep='\s+', comment='#', header=None)
                    data.columns =  ['Size', 'AvgLatency']
                    data['NumProc'] = s
                    data = data[data['Size'] == msg_size]
                    comp = pd.concat([comp, data], ignore_index=True)


                plt.plot(comp['NumProc'], comp['AvgLatency'], label=f'{lib} - {off_mode}', marker='o')

        plt.title(f'{bc} Benchmark on {msg_size} B - scaling processes')
        plt.xlabel('Number of processes')
        plt.ylabel('Avg Latency(us)')
        plt.legend()
        plt.grid(True)
        plt.show()

    for nbc in non_block_coll:
        oplot, oax = plt.subplots()
        cplot, cax = plt.subplots()
        pplot, pax = plt.subplots()
        ovplot, ovax = plt.subplots()

        oplot.set_size_inches(10, 8)
        cplot.set_size_inches(10, 8)
        pplot.set_size_inches(10, 8)
        ovplot.set_size_inches(10, 8)

        procs = 0
        x_positions = []

        i = 0
        for lib in libs:
            for off_mode in offloading_modes:
                comp = pd.DataFrame()

                for s in scale:
                    path = f'../../offloading_modes/{off_mode}/osu/{str(s)}-dist/{lib}/{str(s)}/collective/{nbc}.txt'
                    data = pd.read_csv(path, sep='\s+', comment='#', header=None)
                    data.columns = ['Size', 'Overall', 'Compute', 'PureComm.', 'Overlap']
                    data['NumProc'] = s
                    data = data[data['Size'] == msg_size]
                    comp = pd.concat([comp, data], ignore_index=True)


                oax.plot(comp['NumProc'], comp['Overall'], label=f'{lib} - {off_mode}', marker='o')
                cax.plot(comp['NumProc'], comp['Compute'], label=f'{lib} - {off_mode}', marker='o')
                pax.plot(comp['NumProc'], comp['PureComm.'], label=f'{lib} - {off_mode}', marker='o')
                procs = np.hstack(comp['NumProc']).tolist()
                x_positions = np.arange(len(procs))
                plot_overlap_ratios(ovax, comp, f'{lib} - {off_mode}', i, len(offloading_modes) * len(libs))
                i += 1

        oax.set_xlabel('Number of processes')
        oax.set_ylabel('Overall Latency(us)')
        oax.legend()
        oax.set_title(f'Overall Time - {nbc} Scaling Process Benchmark on {msg_size} B processes over IB')

        cax.set_xlabel('Number of processes')
        cax.set_ylabel('Compute time(us)')
        cax.legend()
        cax.set_title(f'Compute Time - {nbc} Scaling Process over {msg_size} B processes over IB')

        pax.set_xlabel('Number of processes')
        pax.set_ylabel('Pure Communication Time(us)')
        pax.legend()
        pax.set_title(f'Pure Communication Time - {nbc} Scaling Process Benchmark over {msg_size} B processes over IB')

        ovax.set_xlabel('Number of processes')
        ovax.set_ylabel('Overlap (%)')
        ovax.set_xticks(x_positions)
        ovax.set_xticklabels(format_size(procs))
        ovax.legend()
        ovax.set_title(f'Overlap Ratio - {nbc} Scaling Process Benchmark over {msg_size} B processes over IB')

        plt.show()
