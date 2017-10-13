# Jobernetes

## Purpose
This is a very simple job runner for Kubernetes. You can not create job
dependencies in Kubernetes. For example if you have 2 jobs a and b and be depends on the
result of a, b should wait until a is finished. There is (at least for now) no native way to do this in Kubernetes.
This project should solve that problem.

## How it  works
Let's say you have 4 jobs, A, B, C and D. A sets some settings, B and C download some data from the internet and
D generates a report. So  B and C are depened on A en D is depenend on B and C. More graphically
```
     /-- B --\
A --          -- D
     \-- C --/
```
For this you need a `yaml` file. In this `yaml` file example, we use sleeps jobs. This hand for testing the job structure. 
The file should look like:
```yaml
---
jobernetes_config:
  cleanup: true
jobernetes:
  - phase_name: start_sleep
    jobs:
      - name: sleep_one
        job_path: test-dir/0-prepare/phase-one-sleep-5.yaml

  - phase_name: mid_sleep
    jobs:
      - name: dream_a
        job_path: test-dir/1-gather/phase-two-sleep-15b.yaml
      - name: dream_b
        job_path:  test-dir/1-gather/phase-two-sleep-7b.yaml

  - phase_name: end_sleep
    jobs:
      - name: wakeup
        type: directory
        job_path: test-dir/2-finalize
```
The scheduler will first run all jobs in the first phase (start_sleep) and wait until they are finished. Then it will run (in parallel)
run the jobs's in the second phase (source_systems) and wait until there are finished and then will run the jobs in the third phase (end_sleep).
You will also notice that the third phase has a job with `type` directory. This means that it will run all jobs which are in that directory.

### More advanced scheduling
The have a more complex example, with 6 jobs. Here we want this tree.
```
     /-- B -- D --\
A --               -- F
     \-- C -- E --/
```
We want this because job B long and job D depends on B, but is short. Job C is short and job E depends on C but is long.
Your git repo directory structure should look like this
```yaml
---
jobernetes_config:
  cleanup: true
jobernetes:
  - phase_name: start_sleep
    jobs:
      - name: sleep_one
        job_path: test-dir/0-prepare/phase-one-sleep-5.yaml

  - phase_name: mid_sleep
    jobs:
      - name: dream_a
        job_path: test-dir/1-gather/phase-two-sleep-15b.yaml
      - name: sleep_hickup_a
        job_path: test-dir/1-gather/phase-two-sleep-5a.yaml
        depends_on:
          - dream_a
      - name: dream_b
        job_path:  test-dir/1-gather/phase-two-sleep-7b.yaml
      - name: sleep_hickup_b
        job_path: test-dir/1-gather/phase-two-sleep-10a.yaml
        depends_on:
          - dream_b

  - phase_name: end_sleep
    jobs:
      - name: wakeup
        type: directory
        job_path: test-dir/2-finalize
```
There is a new element `depends_on` which cointains a array of dependencies. These dependencies should be within
the same phase.

#### Additional features
* Cleanup jobs after finished
* Revert jobs if job has failed (to do)

## Use cases
* A ETL (Extract Transform Load) job
* A Build/test jog
* Download and import a database during a kubernetes deployment
* A calculation with multipe steps running parallel on your kube cluster


# Running
First configure `jobermodel.yaml` to your prefered model. You also need access to a kubernetes cluster

#### From CLI
You need access to a good `kubectl` config. Make sure you have in you `jobermodel` the setting `incluster`
set to `False` Then just run `./jobernetes.py`

#### From a inside a kubernetes cluster
Make sure you have setting `incluster:True`
```shell
kubectl run jobernetes --image=atzdevries/jobernetes:v0.0.2
```
#### From a container
You need access to a good `kubectl` config. Make sure you have in you `jobermodel` the setting `incluster`
set to `False` 
```shell
docker run \
    -v $(pwd)/jobermodel.yaml:/jobernetes/jobermodel.yaml \
    -v /path/to/your/kube/config/.kube:/root/.kube \
    atzedevries/jobernetes:v0.0.2
```
*note* that links in your kubeconfig should also be available in the container.


### Config options
Currently the options are limited. You can config a job in the `jobernetes_config` section
```yaml
jobernetes_config:
  cleanup: True #cleanup jobs after all is finished
  ssl_insecure_warnings: True #If you are using kubernetes with a self signed certificate this might be handy to set to False
  refresh_time: 5 #The amount of secons between each check update/check of your jobs
  kubernetes_namespace: 'default' #The namespace in which the jobs will be running
  incluster: True #Set this to true if you want to use this project from a kubernetes pod
```
### Known issues
* Does not (yet) check for circle depenencies
* Does not validate if a `yaml`/`json` is really a kubernetes job


