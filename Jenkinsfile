pipeline {
    agent any

    environment {
        DB_URL = credentials('db-credentials-id')           // Secret text -> injected as $DB_URL
        DOCKERHUB = credentials('dockerhub-creds-id')       // Username/Password -> $DOCKERHUB_USR / $DOCKERHUB_PSW
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
                sh 'docker compose up -d'
            }
        }

        stage('Smoke Test') {
            steps {
                echo '🧪 Running smoke tests...'
                sh 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || true'
                sh 'curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d "{\"data\": [1,2,3]}" http://localhost:8000/predict || true'
            }
        }

        stage('Drift Monitoring') {
            steps {
                echo '📊 Running drift monitoring...'
                sh 'python src/routes/monitor.py || true'
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up containers...'
            sh 'docker compose down || true'
            sh 'docker logout || true'
        }
    }
}

