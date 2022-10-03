#!/bin/bash
log="`pwd`/repo_log.txt"
date >$log #nw file

function repo_do()
{
    repo=$1
    cd $repo
    echo "---------------"  &>>$log
    pwd  &>>$log 
    echo "---------------"  &>>$log
    git pull  &>>$log
    git checkout devel  &>>$log 
    git pull  &>>$log
    git restore-mtime  &>>$log
    git tag -a cw_devel_v1.0 -m 'Release for cw devel v1.0 no connectivity' &>>$log
    git push origin cw_devel_v1.0 &>>$log
    cd -
}

cd contiki-ng
repo_do os/net/mac/taisc
repo_do  os/net/mac/taisc/tools/compiler
repo_do  os/lib/go2la
repo_do  examples/taisc_examples
repo_do  arch/platform/lopos
repo_do  arch/platform/lopos/sdk
repo_do  arch/platform/lopos/dev/soundgen
repo_do  arch/cpu/nrf52
repo_do  os/lib/serialstack
cd ..
repo_do sirin_code
