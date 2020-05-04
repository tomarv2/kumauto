**How to use this project**

Pre-reqs:

 - Running Elastalert
 - Running Alertmanager
 - Running Prometheus Monitoring
 - Running Pushgateway
 - Pagerduty account
 - Kafka/Zookeper (when we wrote this project, we had a requirement to cleanup Kafka/Zookeeper)

Based on **user_input.yaml** (specified by user), this package will:

    - Update Elastalert
    - Update Alertmanager
    - Update Prometheus Monitoring
    - Update pushgateway
    - cleanup kafka/zk topics (DEV/QA only)
    

**Done:**

    - Prometheus: alertmanager/monitoring
    - Elastalert
    - Update multiple queries in elastalert
    - Update email/pagerduty
    - Allow user to change email and pagerduty ID
    - Part of deployment, push files to git repo - user side
    - Send logs to persitent storage
    - Part of deployment, push files to git repo - application side
    
**In progress:**

    - Setup up log rotation
    - Test cases
    - File locking
    - Enable checksum
    - Rearrange code

**How to use:**
    
Use **user_input.yaml** and **monitoring_change_on_user_repo_deploy.yaml** in this repo as the base files. 

- Update the env (available options: AWS-STG, AWS).
- Update the path to user_input.yaml in user repo.
- Copy monitoring_change_on_user_repo_deploy.yaml to your respective deployment directory.

**Note:**
  
  - Docker image should have ssh keys to connect to git.

