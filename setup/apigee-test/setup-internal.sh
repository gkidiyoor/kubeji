kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/publisher_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/subscriber_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/cache_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/emmiter_rc.yaml

