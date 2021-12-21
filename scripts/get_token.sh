#!/bin/sh
set -e

output=$(kubectl $1 -n kubernetes-dashboard get secret $(kubectl $1 -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}")

printf "%s\n" $output
