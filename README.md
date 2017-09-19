# Kubernetes Job Scheduler

## Purpose
This is a very simple scheduler for jobs in Kubernetes. You can not create job
dependencies in Kubernetes. For example if you have 2 jobs a and b and be depends on the
result of a, b should wait until a is finished. There is no native way to do this in Kubernets.
This project should solve that problem.

## How it  works
Let's say you have 4 jobs, A, B, C and D. A sets some settings, B and C download some data from the internet and
D generates a report. So  B and C are depened on A en D is depenend on B and C. More graphically
```
     /-- B --\
A --          -- D
     \-- C --/
```
For this you need a git repo with 3 directory's. The structure should look like:
```
0-prepare
  \ job-a.yaml
1-gather
  \ job-b.yaml
  \ job-c.yaml
2-report
  \ job-d.yaml
```
The scheduler will first run all jobs in `0` directory and wait until they are finished. Then it will run (in parallel)
run the jobs's in the `1` directory and wait until there are finished and then will run the jobs in the `2` directory.

### More advanced scheduling
The have a more complex example, with 6 jobs. Here we want this tree.
```
     /-- B -- D --\
A --               -- F
     \-- C -- E --/
```
We want this because job B long and job D depends on B, but is short. Job C is short and job E depends on C but is long.
Your git repo directory structure should look like this
```
0-prepare
  \ job-a.yaml
1.0-gather-animals
   \ job-b.yaml
1.1-gather-plants
   \ job-c.yaml
2.0-gather-animals
   \ job-d.yaml
2.1-gather-plants
   \ job-e.yaml
3-report
  \ job-f.yaml
```


#### Additional features
* Cleanup jobs after finished
* Revert jobs if job has failed

