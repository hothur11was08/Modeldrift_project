pipeline {
    agent any

    environment {
        DB_URL = credentials('db-credentials-id')   // Securely stored in Jenkins
        TF_SERVING_URL = "http://tfserving:8501/v1/models/credit_model:predict"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📥 Pulling latest code..."
                checkout scm
            }
        }

        stage('Build API Image') {
            steps {
                echo "🔨 Building Docker image for API..."
                sh 'docker compose build api'
            }
        }

        stage('Deploy Stack') {
            steps {
                echo "🚀 Starting containers (API, Postgres, TF Serving)..."
                sh 'docker compose up -d'
            }
        }

        stage('Smoke Test Prediction') {
            steps {
                echo "🧪 Running a test prediction..."
                script {
                    def response = sh(
                        script: """curl -s -X POST http://127.0.0.1:8000/v1/predict \
                          -H 'Content-Type: application/json' \
                          -d '{"age":35,"credit_amount":2500,"duration":12,"purpose":"A43","housing":"A152","job":"A173"}'""",
                        returnStdout: true
                    ).trim()
                    echo "Prediction response: ${response}"
                }
            }
        }

        stage('Drift Monitoring') {
            steps {
                script {
                    echo "📊 Checking drift metrics..."
                    def drift = sh(
                        script: "curl -s http://127.0.0.1:8000/v1/monitor/drift",
                        returnStdout: true
                    ).trim()
                    echo "Drift result: ${drift}"

                    def psi = drift.replaceAll(/.*\"psi\":([0-9\\.]+).*/, '$1').toFloat()
                    def ks_pval = drift.replaceAll(/.*\"ks_pval\":([0-9\\.]+).*/, '$1').toFloat()

                    if (psi > 0.2 || ks_pval < 0.05) {
                        error "🚨 Drift detected! PSI=${psi}, KS_pval=${ks_pval}"
                    } else {
                        echo "✅ Drift within acceptable limits"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up containers..."
            sh 'docker compose down'
        }
    }
}

