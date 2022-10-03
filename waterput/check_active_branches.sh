#/bin/bash


if [ "$#" == "1" ]; then
    GIT_DIR=$1
    echo "Getting all active branches of " $1
    echo ""
else
    echo "Pass the GIT directory to this script"
    exit 1
fi


function parse_git_dir()
{
    local CUR_DIR=`pwd`
    local CUR_GIT_DIR=$1

    cd $CUR_GIT_DIR
    RELATIVE_DIR=${CUR_DIR:${#MAIN_DIR} + 1:${#CUR_DIR}-${#MAIN_DIR}}
    if [ ${#RELATIVE_DIR} == 0 ]; then
        RELATIVE_DIR=$CUR_GIT_DIR
    else
        RELATIVE_DIR=$RELATIVE_DIR/$CUR_GIT_DIR
    fi
    
    printf "cd %s; git checkout %s; %s; cd -;\n" $RELATIVE_DIR `git branch | grep \* | cut -d ' ' -f2` `git rev-parse HEAD`

    if [ -f ".gitmodules" ]; then
        for SUBMODULE in `git config --file .gitmodules --get-regexp path | awk '{ print $2 }'`; do
            parse_git_dir $SUBMODULE $CUR_PREFIX
        done
    fi
    cd $CUR_DIR
}

cd $GIT_DIR
MAIN_DIR=`pwd`
parse_git_dir "."