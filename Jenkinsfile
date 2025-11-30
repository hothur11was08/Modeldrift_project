pipeline {
    agent any

    environment {
        DB_URL = credentials('db-credentials-id')         // Secret text: postgres://credit_user:credit_pass@localhost:5433/credit
        DOCKERHUB = credentials('dockerhub-creds-id')     // Username/Password
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code...'
                checkout scm
            }
        }

        stage('Docker login') {
            steps {
                echo '🔑 Logging into DockerHub...'
                sh '''
                  echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
                '''
            }
        }

        stage('Build API Image') {
            steps {
                echo '🔨 Building Docker image for API...'
                sh 'docker compose build api'
            }
        }

        stage('Deploy Stack') {
            steps {
                echo '🚀 Deploying stack...'
                sh """
                  docker compose down || true
                  export DB_URL='$DB_URL'
                  docker compose up -d
                """
            }
        }

        stage('Smoke Test') {
            steps {
                echo '🧪 Running smoke tests...'
                sh '''
                  set -e
                  echo "Waiting for API to be ready..."
                  for i in $(seq 1 30); do
                    code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo 000)
                    if [ "$code" = "200" ]; then
                      echo "Health check: 200"
                      exit 0
                    fi
                    sleep 2
                  done
                  echo "API did not become healthy in time"
                  exit 1
                '''
                sh '''
                  curl -s -o /dev/null -w "Predict check: %{http_code}\\n" \
                    -H "Content-Type: application/json" \
                    -d '{"data": [1,2,3]}' \
                    http://localhost:8000/predict || true
                '''
            }
        }

        stage('Drift Monitoring') {
            steps {
                echo '📊 Running drift monitoring inside API container...'
                sh """
                  docker exec credit_project_api \
                    bash -lc 'DB_URL="$DB_URL" python src/routes/monitor.py' || true
                """
            }
        }
    }

    post {
        always {
            script {
                echo '🧹 Cleaning up containers...'
                try {
                    sh 'docker compose down || true'
                    sh 'docker logout || true'
                } catch (err) {
                    echo "Cleanup skipped: ${err}"
                }
            }
        }
    }
}

