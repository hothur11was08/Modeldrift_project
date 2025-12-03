pipeline {
  agent any

  environment {
    // Adjust these to your stack needs
    COMPOSE_FILE = 'docker-compose.yml'
    DOCKER_REGISTRY = ''
  }

  stages {
    stage('Declarative: Checkout SCM') {
      steps {
        checkout scm
      }
    }

    stage('Checkout') {
      steps {
        echo '📥 Pulling latest code...'
        git url: 'https://github.com/hothur11was08/Modeldrift_project.git',
            branch: 'main',
            credentialsId: 'GitHub_id'
      }
    }

    stage('Docker login') {
      steps {
        echo '🔑 Logging into DockerHub...'
        withCredentials([usernamePassword(credentialsId: 'Docker_id',
                                          usernameVariable: 'DOCKER_USER',
                                          passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
          '''
        }
      }
    }

    stage('Setup Python env') {
      steps {
        sh '''
          set -eux
          apt-get update
          apt-get install -y python3-venv python3-pip
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
        '''
      }
    }

    stage('Train model') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/train.py
        '''
      }
    }

    stage('Build API Image') {
      steps {
        sh '''
          set -eux
          docker-compose -f ${COMPOSE_FILE} build api
        '''
      }
    }

    stage('Deploy Stack') {
      steps {
        sh '''
          set -eux
          docker-compose -f ${COMPOSE_FILE} up -d
        '''
      }
    }

    stage('Smoke Test') {
      steps {
        sh '''
          set -eux
          curl -sSf http://localhost:8000/health
          # If using TF Serving:
          curl -sSf http://localhost:8501/v1/models/your_model
        '''
      }
    }

    stage('Drift Detection') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/drift_detection.py --out reports/drift_report.json
        '''
      }
    }

    stage('Accuracy Evaluation') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/accuracy_eval.py --out reports/accuracy_report.json
        '''
      }
    }

    stage('Bias/Fairness Check') {
      steps {
        sh '''
          set -eux
          . .venv/bin/activate
          python scripts/bias_check.py --out reports/bias_report.json
        '''
      }
    }

    stage('Archive Reports') {
      steps {
        archiveArtifacts artifacts: 'reports/*.json', fingerprint: true, onlyIfSuccessful: false
      }
    }
  }

  post {
    always {
      echo '🧹 Pipeline finished.'
    }
    failure {
      echo '❌ Pipeline failed.'
    }
    success {
      echo '✅ Pipeline succeeded.'
    }
  }
}

