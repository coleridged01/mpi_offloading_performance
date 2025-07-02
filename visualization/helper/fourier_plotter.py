import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

libs = [('ucc', '#D1786F') , ('hcoll', '#B4CB8E')]
offloading_modes = [('no-offloading','//'), ('tm', '\\\\'), ('dpu', '--'), ('dpu-rndv@16KiB', 'X')]
nproc = [4, 8, 16, 32]

def plot_best_times(plot, color, hatch, df, label, i, n):
    bar_width = 0.8 / n

    processes = np.hstack(df['N.Proc.']).tolist()
    x_positions = np.arange(len(processes))
    bars = plot.bar(x_positions + i * bar_width - (n / 2) * bar_width + bar_width / 2,
        df['Best Time'],
        bar_width,
        color=color,
        hatch=hatch,
        label=label,
        edgecolor='black',
        linewidth=1
    )

    plot.bar_label(
        bars,
        labels=df['Grid'],
        fontsize=13,
        fontweight='bold',
        padding=3,
        rotation=70,
        label_type='edge'
    )

def plot_fourier_comparison(off_modes, nodes):
    n = "" if nodes == 2 else str(nodes) + "-"

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({'font.size': 20})
    btplot, btax = plt.subplots(figsize=(10, 8), dpi=300)

    i = 0
    for lib in libs:
        for off_mode in offloading_modes:
            if off_mode[0] not in off_modes:
                continue

            if 'dpu' in off_mode[0] and lib[0] != 'ucc':
                continue

            #l = lib[0] if off_mode[0] != 'dpu' else '.'
            grids = []
            btimes = []
            for npr in nproc:
                if 'dpu' in off_mode[0] and np == 64:
                    continue

                thresh = 'thresh' if off_mode[0] == 'dpu-rndv@16KiB' else '.'
                off = 'dpu' if off_mode[0] == 'dpu-rndv@16KiB' else off_mode[0]

                path = f"../../offloading_modes/benchmarks/fourier/{n}{npr}-dist/{lib[0]}/{off}/{thresh}/fourier.txt"

                with open(path, 'r') as file:
                    lines = file.readlines()
                    summary = lines[-1].strip()
                    grid, btime = summary.split(', ')
                    grid = grid.split(' ')[2]
                    btime = float(btime.split(' ')[1])
                    grids.append(grid)
                    btimes.append(btime)



            df = pd.DataFrame({"N.Proc.": nproc, "Grid": grids, "Best Time": btimes})
            plot_best_times(btax, lib[1], off_mode[1], df, f'{lib[0]} - {off_mode[0]}', i, 8)
            i+=1



    btax.grid(True, linestyle='--', alpha=0.5)
    btax.set_xlabel('Number of Equally Distributed Processes')
    btax.set_ylabel('Best Time(ms)')
    btax.set_xticks(np.arange(len(nproc)))
    btax.set_xticklabels(nproc, fontsize=12, fontweight='bold')
    btax.legend()
    #btax.set_title(f'P3DFFT++ C2C Benchmark - Best Time (ms) {nodes} nodes over IB')
