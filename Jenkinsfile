#!/usr/bin/env groovy

pipeline {

    agent { label 'devops' } // jenkins slave for this job
    options {
        timeout(time: 1, unit: 'HOURS') // timeout
        disableConcurrentBuilds() // can multiple jobs run at same time
        buildDiscarder(logRotator(numToKeepStr: '50')) // log history
    }
    parameters {
        string(name: 'artifactId', defaultValue: '0', description: 'artifactId')
        string(name: 'requirements_file', defaultValue: '0', description: 'raw url of requirements.yaml file')
        string(name: 'branchName', defaultValue: 'master', description: 'branch for requirements.yaml file')
    }
    stages {
        stage('Prepare Build') {
            steps {
                deleteDir() // start with a clean working directory
                cleanWs() // clean jenkins workspace, each jenkins job runs in a workspace

                // need the LocalBranch extension for the maven release plugin to work correctly
                checkout([
                        $class           : 'GitSCM',
                        branches         : scm.branches,
                        extensions       : scm.extensions + [[$class: 'LocalBranch']],
                        userRemoteConfigs: scm.userRemoteConfigs
                ])
            script {
                    sh "echo '----------------------------------'"
                    workspace = pwd()  // get the working directory
                    env.serviceName = params.artifactId // use artifactId as a ServiceName
                    echo params.artifactId
                    echo params.requirements_file
                    sh "echo '----------------------------------'"
                    //sh "git clone ${params.requirements_file} ${env.workspace}/project"
                    //sh "cd ${env.workspace}/project; git checkout ${params.branchName}"
                    env.imageTag = 'v18'
                    git branch: 'master', url: params.requirements_file
                    sh "pwd"
                    sh "ls -l"
                }
            }
        }
        stage('run test and create configmap') {
            when {
                anyOf {
                    branch "development"
                    branch "devops"
                    branch "master"
                }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                        sh "wget http://git.demo.com:7990/projects/DOPS/repos/automation/raw/tests/unit/conftest.py -O conftest.py"
                        sh "wget http://git.demo.com:7990/projects/DOPS/repos/automation/raw/tests/unit/config_test.py -O config_test.py"
                        //sh "pytest config_test.py --filename ./_kube/requirements.yaml"
                        sh "kubectl create configmap ${env.serviceName}-config --from-file=./_kube/requirements.yaml --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                    }
                }
            }
        }
        // Run below stage in parallel
        // Reason: Setting up monitoring and cleanup can run at the sametime
        stage("parallel") {
            when {
                anyOf {
                    branch "development"
                    branch "devops"
                    branch "master"
                }
            }
            steps {
                parallel (
                    'monitoring': {script {
                        withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                            sh "wget http://git.demo.com:7990/projects/DOPS/repos/automation/raw/deployment/monitoring.yaml -O monitoring.yaml"
                            sh "sed -i 's/BASE/${env.serviceName}/g' monitoring.yaml"
                            sh "sed -i -e 's|image: aws.dkr.ecr.us-west-2.amazonaws.com/devlabs/devops/.*\$|image: aws.dkr.ecr.us-west-2.amazonaws.com/devlabs/devops/automation-base:${env.imageTag}|' monitoring.yaml"
                            sh "sed -i -e 's|python /automation/change_on_user_repo/main.py.*\$|python /automation/change_on_user_repo/main.py ONPREM-QA;|' monitoring.yaml"
                            sh "echo '======= monitoring.yaml =========='"
                            sh "cat monitoring.yaml"
                            sh "echo '======== monitoring.yaml after =========================='"
                            sh "kubectl create -f monitoring.yaml --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                            sh "sleep 300"
                            sh "kubectl delete -f monitoring.yaml --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                            }
                         }
                    },
                    'cleanup': {script {
                        withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                            sh "wget http://git.demo.com:7990/projects/DOPS/repos/automation/raw/deployment/cleanup.yaml -O cleanup.yaml"
                            sh "sed -i 's/BASE/${env.serviceName}/g' cleanup.yaml"
                            sh "sed -i -e 's|image: aws.dkr.ecr.us-west-2.amazonaws.com/devlabs/devops/.*\$|image: aws.dkr.ecr.us-west-2.amazonaws.com/devlabs/devops/automation-base:${env.imageTag}|' cleanup.yaml"
                            sh "echo '======= cleanup.yaml =========='"
                            sh "cat cleanup.yaml"
                            sh "echo '======== cleanup.yaml after======================='"
                            sh "kubectl create -f cleanup.yaml --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                            sh "sleep 300"
                            sh "kubectl delete -f cleanup.yaml --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                            }
                        }
                    }
                )
            }
        }
        // If the branch name is:
        // development
        // devops
        // master
        // we are deleting the configmap
        stage('cleanup: configmap') {
            when {
                anyOf {
                    branch "development"
                    branch "devops"
                    branch "master"
                }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                        sh "kubectl delete configmap ${env.serviceName}-config --namespace=sharedservices --server='https://qak8s-master.onpremtest.devlabs.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true"
                    }
                }
            }
        }
    }
}


@NonCPS
def static cleanBranchName(String branchName) {
    return branchName.replaceAll("/", "-")
}

@NonCPS
def getChangeString() {
    MAX_MSG_LEN = 100
    def changeString = ""

    echo "Gathering SCM changes"
    def changeLogSets = currentBuild.changeSets
    for (int i = 0; i < changeLogSets.size(); i++) {
        def entries = changeLogSets[i].items
        for (int j = 0; j < entries.length; j++) {
            def entry = entries[j]
            truncated_msg = entry.msg.take(MAX_MSG_LEN)
            changeString += " - ${truncated_msg} [${entry.author}]\n"
        }
    }

    if (!changeString) {
        changeString = " - No new changes"
    }
    return changeString
}
