pipeline {
  agent any

  environment {
    COMPOSE_FILE = 'docker-compose.yml'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/hothur11was08/Modeldrift_project.git', credentialsId: 'Gittoken'
      }
    }

    stage('Authenticate DockerHub') {
      steps {
        echo 'Logging into DockerHub using stored Jenkins credentials...'
        withCredentials([usernamePassword(credentialsId: 'Docker_id', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
        }
      }
    }

    stage('Setup Python env') {
      steps {
        sh '''
        python3 -m venv .venv
        . .venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        '''
      }
    }

    stage('Train model') {
      steps {
        sh '. .venv/bin/activate && python scripts/train.py'
      }
    }

    stage('Build FastAPI image') {
      steps {
        sh 'docker-compose build api'
      }
    }

    stage('Start services with docker-compose') {
      steps {
        sh 'docker-compose up -d'
      }
    }

    stage('Init Postgres schema') {
      steps {
        sh '''
        echo "Waiting for Postgres to be ready..."
        for i in $(seq 1 30); do
          cid=$(docker ps -q -f name=credit_project-postgres-1)
          if [ -n "$cid" ] && docker exec $cid pg_isready -U credit_user -d credit >/dev/null 2>&1; then
            echo "Postgres ready."
            break
          fi
          sleep 2
        done
        docker exec -i $(docker ps -q -f name=credit_project-postgres-1) psql -U credit_user -d credit < scripts/init_db.sql
        '''
      }
    }

    stage('Smoke tests') {
      steps {
        sh '''
        set -e
        echo "Checking API health..."
        for i in $(seq 1 30); do
          code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
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
        sh 'mkdir -p artifacts/logs artifacts/reports'
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

