pipeline {
    agent { label 'docker-builder' }

    environment {
        REGISTRY = 'kregistry.siwko.org:5000'
        IMAGE = "${REGISTRY}/mqtt-reader"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                sh "docker build --provenance=false --sbom=false -f Dockerfile -t ${IMAGE}:${IMAGE_TAG} -t ${IMAGE}:latest ."
            }
        }
        stage('Push') {
            steps {
                sh "docker push ${IMAGE}:${IMAGE_TAG}"
                sh "docker push ${IMAGE}:latest"
            }
        }
        stage('Deploy') {
            steps {
                sh "kubectl apply -f k8s/mosquitto.yaml"
                sh "kubectl apply -f k8s/mqtt-reader-deployment.yaml"
                sh "kubectl rollout restart deployment/mqtt-reader"
            }
        }
    }
}
