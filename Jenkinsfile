pipeline {
    agent any

    stages {
        stage('Git Pull & Build Containers') {
            steps {
                script {
                    sh 'git pull'
                    
                    sh 'docker-compose down -v'
                    sh 'docker-compose build'
                }
            }
        }

        stage('Start Containers & Run Tests') {
            steps {
                script {
                    sh 'docker-compose up mariadb -d'
                    sh 'docker-compose up flask -d'
                    sh 'docker-compose up test -d'

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
                    sh 'docker-compose up mariadb -d'
                    sh 'docker-compose up flask -d'
                    sh 'docker-compose up test -d'
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
