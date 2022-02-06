pipeline {
    agent any
    options {
        disableConcurrentBuilds()
    }
    environment {
        AWS_ACCOUNT_ID = "537006042321"
        AWS_DEFAULT_REGION = "eu-central-1"
        testImageName = "swfrontend:test-${env.BUILD_ID}"
        IMAGE_REPO_NAME = "swfrontend"
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
    }
    stages{
        stage('Build test container and run tests') {
            environment {
                dockerfile = "Dockerfile.test"
            }
            steps {
               dir("swfrontend") {
                script {
                    docker.build(testImageName, "-f ${dockerfile} .")
                }
               }
            }
        }
        stage('Run tests') {
            agent {
                docker {
                    image testImageName
                    reuseNode true
                    label "test-image"
                }
            }
            steps {
                sh "python3 -m pytest -o cache_dir=/tmp /app/tests/unit/test_frontend.py"
            }
        }
        stage('Build prod image') {
            when { buildingTag() }
            steps {
                dir("swfrontend") {
                    script {
                        dockerImage = docker.build "${IMAGE_REPO_NAME}:${env.TAG_NAME}"
                    }
                }
            }
        }
        stage('Push image to registry') {
            when { buildingTag() }
            steps {
                script {
                    sh "aws ecr get-login-password — region ${AWS_DEFAULT_REGION} | docker login — username AWS — password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
                    sh "docker tag ${IMAGE_REPO_NAME}:${env.TAG_NAME} ${REPOSITORY_URI}:${env.TAG_NAME}"
                    sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${IMAGE_REPO_NAME}:${env.TAG_NAME}"
                }
            }
        }
    }
    post {
        always {
            sh "docker rmi ${testImageName}"
            step([$class: "WsCleanup"])
            cleanWs()
        }
    }
}