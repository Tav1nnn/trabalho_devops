pipeline {
    agent any

    stages {
        stage('Git Pull & Build Containers') {
            steps {
                script {
                    git branch: "main", url: "https://github.com/Tav1nnn/trabalho_devops.git"
                    
                    sh 'docker-compose down -v'
                    
                    sh 'docker-compose build'
                }
            }
        }

        stage('Start Containers & Run Tests') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test'

                    sh '''#!/bin/bash
                    until docker-compose exec mariadb mysqladmin --user=flask_user --password=flask_password --host mariadb --silent --wait=30 ping; do
                        echo "Esperando o MariaDB ficar disponível..."
                        sleep 5
                    done
                    echo "MariaDB está pronto!"
                    '''

                    try {
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Testes falharam. Pipeline interrompido."
                    }
                }
            }
        }

        stage('Keep Application Running') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down -v'
        }
    }
}
