pipeline {
  agent {
    node {
      label 'base'
    }
 
  }
  stages {
    stage('拉取代码') {
      steps {
        container('base') {
          git(url: 'http://172.16.1.232:8443/git/shuhaojie/CFD.git', credentialsId: 'mark-git', branch: "$BRANCH_NAME", changelog: true, poll: false)
        }
 
      }
    }
 
    stage('初始化代码') {
      agent none
      steps {
        container('base') {
          sh '''pwd
ls -lart 
rm -rf .env'''
        }
 
      }
    }
 
    stage('build & push') {
      agent none
      steps {
        container('base') {
          withCredentials([usernamePassword(credentialsId : 'harbor' ,passwordVariable : 'DOCKER_PASS' ,usernameVariable : 'DOCKER_USER' ,)]) {
            sh 'echo "$DOCKER_PASS" | docker login $REGISTRY -u "$DOCKER_USER" --password-stdin'
            sh 'docker build -f Dockerfile -t $REGISTRY/$DOCKERHUB_NAMESPACE/$APP_NAME:dev_$BUILD_NUMBER  .'
            sh 'docker push $REGISTRY/$DOCKERHUB_NAMESPACE/$APP_NAME:dev_$BUILD_NUMBER '
          }
 
        }
 
      }
    }
 
    stage('deploy to  test') {
      agent none
      steps {
        container('base') {
          withCredentials([kubeconfigContent(credentialsId : 'k8s-test' ,variable : 'TEST_KUBECONFIG_CONTENT' ,)]) {
            sh '''mkdir ~/.kube
echo "$TEST_KUBECONFIG_CONTENT" > ~/.kube/config
envsubst <  cfd-api-dev.yaml | kubectl apply -f -'''
          }
 
        }
	 mail(to: 'shuhaojie@unionstrongtech.com', cc: 'songyanlong@unionstrongtech.com', subject: '研发环境后端构建完成！', body: """ALL;
                       CFD研发环境构建完成；
                       分支：$BRANCH_NAME
                       镜像：$REGISTRY/$DOCKERHUB_NAMESPACE/$APP_NAME:dev_$BUILD_NUMBER
                       服务：$APP_NAME
                       构建详情URL地址: ${BUILD_URL}
                  """)
      }
    }
 
 
  }
  environment {
    REGISTRY = '123.56.140.4:808'
    DOCKERHUB_NAMESPACE = 'cfd'
    APP_NAME = 'cfd-api'
    BRANCH_NAME = 'dev'
  }
}
