pipeline {
    agent any

    environment {
        DB_URL = "postgresql://credit_user:credit_pass@postgres:5432/credit"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling latest code...'
                checkout scm
            }
        }

        stage('Docker login') {
            steps {
                echo 'Logging into DockerHub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                }
            }
        }

        stage('Build API Image') {
            steps {
                echo 'Building Docker image for API...'
                sh 'docker-compose build api'
            }
        }

        stage('Deploy Stack') {
            steps {
                echo 'Deploying stack...'
                sh """
                  docker-compose down || true
                  docker-compose up -d
                """
            }
        }

        stage('Smoke Test') {
            steps {
                echo 'Running smoke tests...'
                sh '''
                  set -e
                  echo "Waiting for API to be ready..."
                  for i in $(seq 1 30); do
                    code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8010/health || echo 000)
                    if [ "$code" = "200" ]; then
                      echo "Health check: 200"
                      break
                    fi
                    sleep 2
                  done
                '''
                sh '''
                  curl -s -o /dev/null -w "Predict check: %{http_code}\\n" \
                    -H "Content-Type: application/json" \
                    -d '{"purpose":"car","housing":"own","job":"skilled","age":35,"credit_amount":5000,"duration":24}' \
                    http://localhost:8010/v1/predict
                '''
            }
        }

        stage('Drift Monitoring') {
            steps {
                echo 'Running drift monitoring inside API container...'
                sh """
                  docker-compose exec api bash -lc 'DB_URL="$DB_URL" python src/routes/monitor.py' || true
                """
            }
        }
    }

    post {
        always {
            echo 'Cleaning up containers...'
            sh 'docker-compose down'
            sh 'docker logout'
        }
    }
}

