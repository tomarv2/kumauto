# Monitoring automation project for Prometheus and ecosystem (in-progress)

One of the main problem that we face with microservices deployment is how to configure monitoring.
With deployment being so dynamic its hard to make changes.

In this project we are trying to offload the management of monitoring. When a new project is added, 
user adds `user_input.yaml` and it will be picked up by CICD (in our case Jenkins).

###

<p align="center">
  <img width="600" height="370" src="https://files.gitter.im/tomarv2/hhdj/Screen-Shot-2020-04-23-at-8.48.17-AM.png">
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

