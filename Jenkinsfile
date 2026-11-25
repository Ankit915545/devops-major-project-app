pipeline {
     agent any

     options {
    skipDefaultCheckout(true)
}

 environment {
         AWS_REGION   = 'ap-south-1' 
         ECR_REGISTRY = '133210447219.dkr.ecr.ap-south-1.amazonaws.com'
         ECR_REPO     = 'devops-major-project'
         IMAGE_TAG    = "${env.BUILD_NUMBER}"    
         AWS_CREDS    = 'aws-ecr-credentials' // Match your Jenkins Credential ID  
   }

 stages {  
       stage('Checkout Source Code') { 
            steps {
                 echo "Fetching source code from repository..."
                 checkout scm
             }  
       }

       stage('Run Unit Tests') {
             steps {
                 echo "Initializing virtual environment and executing pytest suite..."
                 sh '''                     
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
                 echo "Building Docker image version: ${IMAGE_TAG}..." 
                sh '''                     
                  docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} .
                  docker tag ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:latest
               ''' 
            }       
       }

       
stage('Authenticate & Push to AWS ECR') {
    steps {
        echo "Authenticating Docker with AWS ECR in region ${AWS_REGION}..."

        withCredentials([usernamePassword(
            credentialsId: "${AWS_CREDS}",
            usernameVariable: 'AWS_ACCESS_KEY_ID',
            passwordVariable: 'AWS_SECRET_ACCESS_KEY'
        )]) {
            sh '''
                set -e

                echo "Checking AWS identity..."
                aws sts get-caller-identity

                echo "Logging in to AWS ECR..."
                aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

                echo "Pushing versioned image..."
                docker push "$ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"

                echo "Pushing latest image..."
                docker push "$ECR_REGISTRY/$ECR_REPO:latest"
            '''
          }
      }
   }
 }
      post { 
         always {  
             echo "Executing post-build cleanup to reclaim host disk space..." 
          sh '''
               docker rmi ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} || true 
               docker rmi ${ECR_REGISTRY}/${ECR_REPO}:latest || true 
               rm -rf venv
               echo "Cleanup completed." 
          '''
    }
      success {
            echo "Part A CI Pipeline completed successfully."
        }

        failure {
            echo "Part A CI Pipeline failed. Check Jenkins console output."
        }
  }
}   
