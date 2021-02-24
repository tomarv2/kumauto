<p align="center">
    <a href="https://www.apache.org/licenses/LICENSE-2.0" alt="license">
        <img src="https://img.shields.io/github/license/tomarv2/mauto" /></a>
    <a href="https://github.com/tomarv2/mauto/tags" alt="GitHub tag">
        <img src="https://img.shields.io/github/v/tag/tomarv2/mauto" /></a>
    <a href="https://stackoverflow.com/users/6679867/tomarv2" alt="Stack Exchange reputation">
        <img src="https://img.shields.io/stackexchange/stackoverflow/r/6679867"></a>
    <a href="https://discord.gg/XH975bzN" alt="chat on Discord">
        <img src="https://img.shields.io/discord/813961944443912223?logo=discord"></a>
    <a href="https://twitter.com/intent/follow?screen_name=varuntomar2019" alt="follow on Twitter">
        <img src="https://img.shields.io/twitter/follow/varuntomar2019?style=social&logo=twitter"></a>
</p>

# Monitoring automation using Prometheus and ecosystem (in-progress)

One of the main problem that we face with microservices deployment is how to configure monitoring.
With deployment being so dynamic its hard to make changes.

As you can see in the blog: https://medium.com/@tomarv2/jenkins-shared-libraries-ab64f7acac68. I discussed how can 
repos can be arranged and how monitoring jobs at scale can be configured. Most of the work of adding projects to monitoring and alerting was manual.

In this project we are trying to offload the management of monitoring and alerting. When a new project is added, 
user adds/updates `user_input.yaml` and it will be picked up by CICD (in this case Jenkins).


###

<p align="center">
  <img width="600" height="370" src="https://miro.medium.com/max/1400/1*Tp1kUoGHRPmB4wik1kKHkA.png">
</p>

###
Where will the monitoring be configured:

- Prometheus
- Blackbox
- Elastalert
- Pushgateway
- Pagerduty
- Email
- Slack

**Pre-reqs:**

 - Running Elastalert
 - Running Alertmanager
 - Running Prometheus Monitoring
 - Running Pushgateway
 - Pagerduty account
 - Slack account
 - Kafka/Zookeper (when we wrote this project, we had a requirement to cleanup Kafka/Zookeeper)
    
**Note:**
  
  - Docker image should have ssh keys to connect to git.

***

### How to begin:

To create dummy data for testing:

verify if `static-files` directory exists:

```
DIR_NAME=demo1
BASE_PATH='/Users/varun.tomar/Documents/personal_github'

mkdir -p $BASE_PATH/mauto/$DIR_NAME/demo-data/monitoring/static-files
```

verify if alertmanager config file exists:

```
mkdir -p $BASE_PATH/mauto/$DIR_NAME/demo-data/alertmanager
cp $BASE_PATH/mauto/data/demo-data/alertmanager/config.yaml $BASE_PATH/mauto/$DIR_NAME/demo-data/alertmanager/config.yaml
```

verify if prometheus config file exists:

```
mkdir -p $BASE_PATH/mauto/junk/demo-data/monitoring/
cp $BASE_PATH/mauto/data/demo-data/monitoring/config.yaml $BASE_PATH/mauto/junk/demo-data/monitoring/
```

verify .env file exists:

Copy the `example.env` and create a .env file

Update `src/automation/config.yaml`

### How to use?

- run `pip install mauto`
- run `muato` for available options

### Note: 

1. Trying to make it modular or plug and play type so new components can be added easily.

2. I am using `click` to create python cli.

3. Python 3.6 and above is required

