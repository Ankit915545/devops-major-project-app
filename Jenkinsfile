
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        AWS_REGION   = 'ap-south-1'
        ECR_REGISTRY = '133210447219.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPO     = 'devops-major-project'
        IMAGE_TAG    = "${BUILD_NUMBER}"

        AWS_CREDS    = 'aws-ecr-credentials'
        SSH_CREDS    = 'ec2-deploy-ssh-key'
        EC2_HOST     = '13.204.246.218'
        CONTAINER_NAME = 'devops-major-project'
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                echo 'Fetching source code from GitHub...'
                checkout scm
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Creating Python virtual environment and running pytest...'
                sh '''
                    set -e
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest --verbose test_app.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_TAG}"
                sh '''
                    set -e
                    docker build \
                      -t ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} .

                    docker tag \
                      ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} \
                      ${ECR_REGISTRY}/${ECR_REPO}:latest
                '''
            }
        }

        stage('Authenticate & Push to AWS ECR') {
            steps {
                echo 'Authenticating and pushing images to AWS ECR...'

                withCredentials([usernamePassword(
                    credentialsId: "${AWS_CREDS}",
                    usernameVariable: 'AWS_ACCESS_KEY_ID',
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh '''
                        set -e

                        export AWS_DEFAULT_REGION="$AWS_REGION"

                        aws sts get-caller-identity

                        aws ecr get-login-password \
                          --region "$AWS_REGION" |
                          docker login \
                          --username AWS \
                          --password-stdin "$ECR_REGISTRY"

                        docker push "$ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"
                        docker push "$ECR_REGISTRY/$ECR_REPO:latest"
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying Flask application to EC2...'

                sshagent(credentials: ["${SSH_CREDS}"]) {
                    sh '''
                        set -e

                        ssh -o BatchMode=yes \
                            -o StrictHostKeyChecking=accept-new \
                            ubuntu@${EC2_HOST} \
                            "AWS_REGION='${AWS_REGION}' ECR_REGISTRY='${ECR_REGISTRY}' ECR_REPO='${ECR_REPO}' IMAGE_TAG='${IMAGE_TAG}' CONTAINER_NAME='${CONTAINER_NAME}' bash -s" <<'REMOTE'

                        set -e

                        echo "Logging in to AWS ECR using EC2 IAM role..."

                        aws ecr get-login-password \
                          --region "$AWS_REGION" |
                          docker login \
                          --username AWS \
                          --password-stdin "$ECR_REGISTRY"

                        echo "Pulling new Docker image..."
                        docker pull "$ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"

                        echo "Stopping previous application container..."
                        if docker ps -a --format '{{.Names}}' |
                           grep -Fxq "$CONTAINER_NAME"; then
                            docker stop "$CONTAINER_NAME"
                            docker rm "$CONTAINER_NAME"
                        fi

                        echo "Starting new application container..."
                        docker run -d \
                          --name "$CONTAINER_NAME" \
                          --restart unless-stopped \
                          -p 80:5000 \
                          "$ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"

                        echo "Checking application health..."
                        sleep 5
                        curl -fsS http://localhost/health

                        echo "EC2 deployment successful!"

REMOTE
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up Jenkins workspace and Docker images...'
            sh '''
                docker rmi "${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}" || true
                docker rmi "${ECR_REGISTRY}/${ECR_REPO}:latest" || true
                rm -rf venv
            '''
        }

        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the Jenkins Console Output.'
        }
    }
}
