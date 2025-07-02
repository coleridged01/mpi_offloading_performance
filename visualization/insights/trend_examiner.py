import pandas as pd

def path(node, np, lib, off_mode, coll):
    return f"../../offloading_modes/benchmarks/osu/{node}{str(np)}-dist/{lib}/{off_mode}/{coll}.txt"

def compute_scalability_trend(coll, libs, off_modes, nodes, nprocs):
    nprocs = list(zip(nprocs, nprocs[1:]))
    df = pd.DataFrame(columns=[f"{l} -> {r}" for l, r in nprocs])
    ind = []
    for lib in libs:
        for off_mode in off_modes:
            if off_mode == 'dpu' and lib != 'ucc':
                continue
            val = []
            try:
                for l, r in nprocs:
                    prefix = "" if nodes == 2 else f"{str(nodes)}-"
                    lpath = path(prefix, l, lib, off_mode, coll)
                    rpath = path(prefix, r, lib, off_mode, coll)

                    lnorm = normalize_osu_blocking_benchmark(lpath)
                    rnorm = normalize_osu_blocking_benchmark(rpath)

                    relinc = (rnorm - lnorm) / lnorm  # relative increase/decrease
                    val.append(relinc)

                df.loc[len(df)] = val
                ind += [f"{lib} - {off_mode}"]

            except FileNotFoundError:
                continue

    df.index = ind
    return df


def compute_redistribution_trend(coll, libs, off_modes, nodes, nprocs):
    nodes = list(zip(nodes, nodes[1:]))
    df = pd.DataFrame(columns=[f"({np}) {l} -> {r}" for l, r in nodes for np in nprocs])
    ind = []
    for off_mode in off_modes:
        for lib in libs:
            if off_mode == 'dpu' and lib != 'ucc':
                continue
            try:
                val = []
                for np in nprocs:
                    for l, r in nodes:
                        lprefix = "" if l == 2 else f"{str(l)}-"
                        rprefix = "" if r == 2 else f"{str(r)}-"
                        lpath = path(lprefix, np, lib, off_mode, coll)
                        rpath = path(rprefix, np, lib, off_mode, coll)

                        lnorm = normalize_osu_blocking_benchmark(lpath)
                        rnorm = normalize_osu_blocking_benchmark(rpath)

                        relinc = (rnorm - lnorm) / lnorm #relative increase/decrease
                        val.append(relinc)

            except FileNotFoundError:
                continue

            df.loc[len(df)] = val
            ind += [f"{lib} - {off_mode}"]

    df.index = ind
    return df



def normalize_osu_blocking_benchmark(b_path):
    data = pd.read_csv(b_path, sep='\s+', comment='#', header=None, skiprows=2,
                       engine='python')
    data.columns = ['Size', 'AvgLatency(us)']

    return data['AvgLatency(us)'].sum() / data['Size'].sum()