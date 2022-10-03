#/bin/bash

first_json_entry="yes"
result=


while getopts i:o:j: option
do
	case "${option}"
	in
		i) GIT_DIR=${OPTARG};;
		o) OUTPUT_FILE=${OPTARG};;
		j) json=${OPTARG};;
	esac
done

if [ -z "$GIT_DIR" ]
then
    echo "Pass the GIT directory to this script"
    exit 1
fi


function parse_git_dir()
{
    local CUR_GIT_DIR=$1
    local CUR_PREFIX=$2

    BRANCH=`git -C $CUR_GIT_DIR rev-parse --abbrev-ref HEAD`
    URL=`git -C $CUR_GIT_DIR config --get remote.origin.url`
    COMMIT_ID=`git -C $CUR_GIT_DIR rev-parse HEAD`

    if [ -z "$json" ]; then
        result+="$CUR_PREFIX,$URL,$BRANCH,$COMMIT_ID"
    else
        if [ ! -z "$first_json_entry" ]; then
            first_json_entry=
        else
            result+=", "
        fi
        result+="{"
        result+="\"dir\": \"$CUR_PREFIX\""
        result+=", "
        result+="\"url\": \"$URL\""
        result+=", "
        result+="\"branch\": \"$BRANCH\""
        result+=", "
        result+="\"commit_hash\": \"$COMMIT_ID\""
        result+="}"
    fi

    if [ -f "$CUR_GIT_DIR/.gitmodules" ]; then
        for SUBMODULE in `git -C $CUR_GIT_DIR config --file .gitmodules --get-regexp path | awk '{ print $2 }'`; do
            parse_git_dir $CUR_GIT_DIR/$SUBMODULE "$CUR_PREFIX/$SUBMODULE"
        done
    fi
}


# Parse the subrepo tree:
parse_git_dir $GIT_DIR "."


if [ ! -z "$json" ]; then
    result="[$result]"
fi

if [ -z "$OUTPUT_FILE" ]
then
    echo "$result"
else
    echo "$result" > $OUTPUT_FILE
fi
