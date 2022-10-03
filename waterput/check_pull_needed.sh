#/bin/bash


if [ "$#" == "1" ]; then
    GIT_DIR=$1
    echo "Performing git check on" $1
else
    echo "Pass the GIT directory to this script"
    exit 1
fi

function parse_git_dir()
{
    local CUR_DIR=`pwd`
    local CUR_GIT_DIR=$1
    local CUR_PREFIX=$2

    cd $CUR_GIT_DIR
    echo $CUR_PREFIX $CUR_DIR/$CUR_GIT_DIR
    git remote update
    STATUS_OUTPUT=`git status -uno`
    if [[ $STATUS_OUTPUT == *"Your branch is up to date"* ]]; then
        echo "Up to date!"
    else
        echo "Pull needed"
    fi

    CUR_PREFIX="-$CUR_PREFIX"
    if [ -f ".gitmodules" ]; then
        for SUBMODULE in `git config --file .gitmodules --get-regexp path | awk '{ print $2 }'`; do
            parse_git_dir $SUBMODULE $CUR_PREFIX
        done
    fi
    cd $CUR_DIR
}

parse_git_dir $GIT_DIR "->"