pipeline {
  agent any

  environment {
    DB_URL = "postgresql://credit_user:credit_pass@postgres:5432/credit"
  }

  stages {
    stage('Checkout') {
      steps {
        echo '📥 Pulling latest code...'
        git url: 'https://github.com/hothur11was08/Modeldrift_project.git', branch: 'main'
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
        docker network connect credit_project_default $(cat /etc/hostname) || true
        '''
      }
    }

    stage('Smoke Test') {
      steps {
        echo '🩺 Running smoke tests...'
        sh '''
        curl -s http://api:8000/health || exit 1
        curl -s http://tfserving:8501/v1/models/credit_model || exit 1
        '''
      }
    }

    stage('Drift Detection') {
      steps {
        echo '📊 Running drift detection...'
        sh '. .venv/bin/activate && python scripts/drift_check.py --db $DB_URL --out drift_reports/drift_report.json'
      }
    }

    stage('Accuracy Evaluation') {
      steps {
        echo '🎯 Evaluating accuracy...'
        sh '. .venv/bin/activate && python scripts/accuracy_eval.py --data data/german_credit.csv --model models/credit_model --out drift_reports/accuracy_report.json'
      }
    }

    stage('Bias/Fairness Check') {
      steps {
        echo '⚖️ Checking bias/fairness...'
        sh '. .venv/bin/activate && python scripts/bias_check.py --data data/german_credit.csv --out drift_reports/bias_report.json'
      }
    }

    stage('Archive Reports') {
      steps {
        echo '📦 Archiving reports...'
        archiveArtifacts artifacts: 'drift_reports/*.json', fingerprint: true
      }
    }
  }
}

