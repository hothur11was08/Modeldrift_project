pipeline {
    agent any

    environment {
        DB_URL = "postgresql://credit_user:credit_pass@postgres:5432/credit"
    }

    stages {
        stage('Pull latest code from GitHub repository') {
            steps {
                echo 'Checking out the most recent commit from GitHub...'
                checkout scm
            }
        }

        stage('Authenticate Jenkins to DockerHub for image build/push') {
            steps {
                echo 'Logging into DockerHub using stored Jenkins credentials...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                }
            }
        }

        stage('Build FastAPI container with dependencies and source code') {
            steps {
                echo 'Building Docker image for the FastAPI service...'
                sh 'docker-compose build api'
            }
        }

        stage('Start Postgres, TF Serving, API, and pgAdmin via docker-compose') {
            steps {
                echo 'Deploying the full stack (database, model server, API, pgAdmin)...'
                sh """
                  docker-compose down || true
                  docker-compose up -d
                """
            }
        }

        stage('Run health check and prediction test against API') {
            steps {
                echo 'Running smoke tests to validate API readiness and prediction endpoint...'
                sh '''
                  set -e
                  echo "Waiting for API to be ready..."
                  for i in $(seq 1 30); do
                    code=$(curl -s -o /dev/null -w "%{http_code}" http://api:8000/health || echo 000)
                    if [ "$code" = "200" ]; then
                      echo "Health check passed: 200 OK"
                      break
                    fi
                    sleep 2
                  done
                '''
                sh '''
                  curl -s -o /dev/null -w "Prediction endpoint check: %{http_code}\\n" \
                    -H "Content-Type: application/json" \
                    -d '{"purpose":"car","housing":"own","job":"skilled","age":35,"credit_amount":5000,"duration":24}' \
                    http://api:8000/v1/predict
                '''
            }
        }

        stage('Execute drift detection script on prediction logs in Postgres') {
            steps {
                echo 'Running drift monitoring to compare live predictions against training baseline...'
                sh '''
                  docker-compose run --rm api bash -lc "DB_URL=\\"$DB_URL\\" python src/routes/monitor.py" > drift_report.txt || true
                '''
                archiveArtifacts artifacts: 'drift_report.txt', fingerprint: true
            }
        }

        stage('Clean up containers and logout from DockerHub') {
            steps {
                echo 'Tearing down containers and logging out of DockerHub...'
                sh '''
                  docker-compose down
                  docker logout
                '''
            }
        }
    }
}

