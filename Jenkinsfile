pipeline {
  agent any

  environment {
    DB_URL = "postgresql://credit_user:credit_pass@postgres:5432/credit"
  }

  stages {
    stage('Checkout') {
      steps {
        echo '📥 Pulling latest code...'
        git branch: 'main', url: 'https://github.com/hothur11was08/Modeldrift_project.git'
      }
    }

    stage('Docker login') {
      steps {
        echo '🔑 Logging into DockerHub...'
        withCredentials([usernamePassword(credentialsId: 'Docker_id', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
        }
      }
    }

    stage('Setup Python env') {
      steps {
        sh '''
        apt-get update && apt-get install -y python3-venv python3-pip || true
        python3 -m venv .venv
        . .venv/bin/activate
        python -m ensurepip --upgrade
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
        '''
      }
    }

    stage('Train model') {
      steps {
        sh '. .venv/bin/activate && python scripts/train.py'
      }
    }

    stage('Build API Image') {
      steps {
        echo '🔨 Building Docker image for API...'
        sh 'docker-compose build api'
      }
    }

    stage('Deploy Stack') {
      steps {
        echo '🚀 Deploying stack...'
        sh '''
        docker-compose down || true
        docker-compose up -d
        '''
      }
    }

    stage('Smoke Test') {
      steps {
        echo '🩺 Running smoke tests...'
        sh '''
        set -e
        for i in $(seq 1 30); do
          code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
          if [ "$code" = "200" ]; then
            echo "API health OK"
            break
          fi
          sleep 2
        done
        . .venv/bin/activate && python scripts/smoke_tests.py
        '''
      }
    }

    stage('Drift monitor') {
      steps {
        sh '. .venv/bin/activate && python scripts/drift_monitor.py'
      }
    }

    stage('Bias monitor') {
      steps {
        sh '. .venv/bin/activate && python scripts/bias_monitor.py'
      }
    }

    stage('Archive artifacts') {
      steps {
        sh 'mkdir -p artifacts/logs artifacts/reports models'
        sh 'docker ps > artifacts/logs/containers.txt'
        archiveArtifacts artifacts: 'artifacts/**, models/**', fingerprint: true
      }
    }
  }

  post {
    always {
      sh 'docker-compose down --remove-orphans || true'
      sh 'docker logout || true'
    }
  }
}

