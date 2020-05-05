# Monitoring Automation project

One of the main problem that we face with microservices deployment is how to add monitoring.
With deployment being so dynamic its hard to track what to monitor and adjust to changes.

In this project we are trying to offload the management of monitoring. When a new project is to added, 
user just needs to update the `user_input.yaml` and it will be picked up by CICD (in our case Jenkins).

If a project needs to add a pagerduty information or update the contact person for a project, 
they can ust update the user information and it be taken car of by CICD.

Where we can add Project to:

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