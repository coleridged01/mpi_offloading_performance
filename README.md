# MPI Collective Offloading Benchmarks

This repository contains the benchmark data and visualizations which are used for evaluating
collective performance across several MCA Coll modules (UCC, HCOLL, HAN) with varying offloading
modes, such as Hardware Tag Matching and DPU Collective offloads.
The Benchmarks were run on a 4-node environment, each with an NVIDIA Bluefield-2 Data Processing Unit (DPU).
The project contains the necessary bash scripts for reproducibility.
As this project's research was conducted on LRZ BEAST testbeds, the configuration has to be changed to
run on different equipment. More details below.

## Goals

This work’s primary objective is to conduct a performance-driven comparison of hardware-based collective offloading
techniques under various offloading modes, namely, results attained by leveraging UCC with the DPU offload SP and 
with HTM.

## Project Structure

```text
benchmarking-repo/
├── bmrkbackend/
│   ├── jacobi
│   │   └── jacobi.c              # MPI distributed Jacobi method source file
│   └── osu                       # OSU Benchmark binaries should go here
├── offloading_modes/
│   ├── benchmarks/               # Contains all benchmark results (Fourier, Jacobi, OSU)
│   ├── dpu/                      # Contains UCC-DPU benchmark automation scripts
│   ├── no-offloading/            # Contains benchmark automation scripts with no offloading applied
│   ├── tm/                       # Contains benchmark automation scripts with Hardware Tag Matching
│   └── run_benchmark.sh          # The script that initiates a benchmark run (Details on usage below)
├── setup/                        # Contains the host files corresponding to the various setups
├── visualization/
│   ├── helper/                   # Plotter helper files (Matplotlib)
│   ├── insights/                 # Plots for the Redistribution and Scalability measures
│   └── offloading_modes/         # Contains OSU, Jacobi and Fourier plots in figures and within Jupyter Notebook files
├── LICENSE
└── README.md    
```

## Benchmark Script Usage

This script runs the selected benchmark on various setups and process distributions.

```bash
./run_benchmark -b (benchmark)<osu|fourier|jacobi> -n (node_count)<2|4>
```

The script is not expected to work as-is, as it hardcodes setup details that need to be
reconfigured for the benchmarks to work. Moreover, the environment needs three separate MPI
installations for HCOLL, UCC DPU and UCC HTM.
The DPU scripts also expect the SP to be running on the DPUs, which requires additional setup.

Contributions that help generalize and improve the flexibility of this procedure for various setups are always welcome!
