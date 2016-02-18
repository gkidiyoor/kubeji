kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/ui_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/ms_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/event_recorder_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/aggregator_rc.yaml
kubectl -s=http://kube-master-869596037.us-west-2.elb.amazonaws.com:8080 create -f ~/apigee/projects/aws-coreos-kubernetes/kube_app/purger_rc.yaml

