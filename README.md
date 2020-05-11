# Monitoring automation project for Prometheus and ecosystem (in-progress)

One of the main problem that we face with microservices deployment is how to configure monitoring.
With deployment being so dynamic its hard to make changes.

In this project we are trying to offload the management of monitoring. When a new project is added, 
user adds `user_input.yaml` and it will be picked up by CICD (in our case Jenkins).

Where will the monitoring be configured:

- Prometheus
- Blackbox
- Elastalert
- Pushgateway
- Pagerduty
- Email
- Slack


**How to use this:**

Pre-reqs:

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

To create dummy data for testing:

verify if static-files directory exists:

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