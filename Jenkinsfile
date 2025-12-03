pipeline {
  agent any
  environment {
    COMPOSE_FILE = 'docker-compose.yml'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Install Docker CLI + Compose + Python') {
      steps {
        sh '''
          set -eux
          apt-get update
          apt-get install -y docker.io curl python3 python3-venv python3-pip
          curl -L "https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
          chmod +x /usr/local/bin/docker-compose
          docker --version
          docker-compose --version
        '''
      }
    }

    stage('Setup Python venv') {
      steps {
        sh '''
          set -eux
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
        '''
      }
    }

    stage('Build API image') {
      steps {
        sh '''
          set -eux
          docker-compose -f ${COMPOSE_FILE} build api
        '''
      }
    }

    stage('Deploy stack') {
      steps {
        sh '''
          set -eux
          docker-compose -f ${COMPOSE_FILE} up -d
          docker-compose -f ${COMPOSE_FILE} ps
        '''
      }
    }

    stage('Smoke tests (inside api container)') {
      steps {
        sh '''
          set -eux
          # Run curl inside the api service container so networking is correct
          docker-compose -f ${COMPOSE_FILE} exec -T api curl -sSf http://localhost:8000/health
          # TF Serving reachability
          docker-compose -f ${COMPOSE_FILE} exec -T api curl -sSf http://tfserving:8501/v1/models/${MODEL_NAME:-your_model} || true
        '''
      }
    }

    stage('Drift detection') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/drift_detection.py --out reports/drift_report.json
        '''
      }
    }

    stage('Accuracy evaluation') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/accuracy_eval.py --out reports/accuracy_report.json
        '''
      }
    }

    stage('Bias check') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/bias_check.py --out reports/bias_report.json
        '''
      }
    }

    stage('Archive reports') {
      steps {
        archiveArtifacts artifacts: 'reports/*.json', fingerprint: true, onlyIfSuccessful: false
      }
    }
  }
  post {
    always { echo 'Pipeline finished.' }
  }
}

