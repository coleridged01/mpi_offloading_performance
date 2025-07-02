#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

#define EPSILON 1e-6
#define MAX_SIZE 1008

int main(int argc, char **argv) {
	int rank, size;

	if (argc < 3) {
		printf("Insufficient arguments: <N> <max_iter> \n");
		exit(1);
	}

	const char* a = argv[1];
	const int N = atoi(a);

	if ((N & N - 1) != 0 || N < 4) {
    	printf("N must be power of 2 and greater than 3!\n");
		exit(1);
	}

	const double MAX_ITER = atoi(argv[2]);
   	
	MPI_Init(&argc, &argv);
    
   	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
	
	char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    
	MPI_Get_processor_name(processor_name, &name_len);

	double **A =  malloc(N * sizeof(double*));

	if (!A) {
          printf("Out of memory\n");
          exit(1);
	}

	double *b = malloc(N * sizeof(double));

    if (!b) {
		printf("Out of memory\n");
		exit(1);
    }

    for (int i = 0; i < N; i++) {
    	A[i] = (double *) malloc(N * sizeof(double));
        if (!A[i]) {
			printf("Out of memory\n");
			exit(1);
        }
    }

    //Print stats:
    if (rank == 0) {
		printf(
    		"%-30s %-30s %-30s %-30s %-30s %-30s\n",
			"Matrix Dim. N",
			"Norm",
			"Converged at:",
			"Avg. Comp. Time(us) p. it.",
			"Avg. Comm. Time(us) p. it.",
			"Avg. Total Time(us) p. it."
		);
    }

	double overall_time;
	double compute_time;
	double communication_time;

	double overall_execution_time;
	double overall_communication_time;
	double overall_compute_time;

	double overall_time_start;

	double comm_start;
	double comm_end;

    for (int n = size; n <= N; n = n << 1) {
    	overall_time = 0.0;
    	compute_time = 0.0;
    	communication_time = 0.0;

    	overall_execution_time = 0.0;
    	overall_communication_time = 0.0;
    	overall_compute_time = 0.0;

    	comm_start = 0.0;
    	comm_end = 0.0;

    	// Matrix assignment (optimized for fast convergence)
	    double x[n];
	    double x_new[n];
		const int local_start = rank * (n / size);
	    const int local_end = rank == size - 1 ? n : (rank + 1) * (n / size);
	    int iter;
	    double diff, global_diff;
		const int m = local_end - local_start;


	    for (int i = 0; i < n; i++) {
	        b[i] = 2 * n + i;
	        for (int j = 0; j < n; j++) {
	            A[i][j] = 1;
				if (i == j) {
					A[i][j]= n * n;
	            } else {
            		A[i][j]= n + 1;
	            }
			}
	    }

	    for (int i = 0; i < n; i++) {
    		x[i] = 0;
	    }

    	// Commence benchmark
    	overall_time_start = MPI_Wtime();
		for (iter = 0; iter < MAX_ITER; iter++) {
			for (int i = local_start; i < local_end; i++) {
	            x_new[i] = b[i];

	            for (int j = 0; j < n; j++) {
		        	if (j != i) {
						x_new[i] -= A[i][j] * x[j];
            		}
		        }
		        x_new[i] /= A[i][i];
            }

			comm_start += MPI_Wtime();
			MPI_Allgather(x_new + local_start, m, MPI_DOUBLE, x_new, m, MPI_DOUBLE, MPI_COMM_WORLD);
			comm_end += MPI_Wtime();

			diff = 0;
	        for (int i = local_start; i < local_end; i++) {
				diff += fabs((x_new[i] - x[i]) * (x_new[i] - x[i]));
	  		}

			diff = sqrt(diff);

			for (int i = 0; i < n; i++) {
				x[i] = x_new[i];
	        }

			comm_start += MPI_Wtime();
			MPI_Allreduce(&diff, &global_diff, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			comm_end += MPI_Wtime();

       		if (global_diff < EPSILON) {
				break;
      		}
		}

    	communication_time = comm_end - comm_start;

        overall_time = MPI_Wtime() - overall_time_start;
    	compute_time = overall_time - communication_time;

    	MPI_Reduce(&compute_time, &overall_compute_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
		MPI_Reduce(&communication_time, &overall_communication_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
		MPI_Reduce(&overall_time, &overall_execution_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);


		if (rank == 0) {
        	const double comp_time = 1e6 * overall_compute_time / (size * iter);
            const double comm_time = 1e6 *  overall_communication_time / (iter * size);
            const double total_time = 1e6 * overall_execution_time / (size * iter);

			printf("%-30d %-30f %-30d %-30f %-30f %-30f\n",
                n, global_diff, iter, comp_time, comm_time, total_time
            );
	    }
    }

	for (int i = 0; i < N; i++) {
		free(A[i]);
	}

	free(b);
	free(A);

	MPI_Finalize();

    return 0;
}

