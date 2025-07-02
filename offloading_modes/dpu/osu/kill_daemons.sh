
# change user and dpu hostnames
ssh user@dpu1 "kill $(pgrep job_persi)"
ssh user@dpu2 "kill $(pgrep job_persi)"
ssh user@dpu3 "kill $(pgrep job_persi)"
ssh user@dpu4 "kill $(pgrep job_persi)"

