#!/bin/bash

echo -e "Will start from git clone contiki-ng and will patch and prepare your tree for the lopos!"
echo -e "Author Bart Jooris"
echo -e "Date 26/12/2019"
echo -e "Please store your git credentials before moving on!"
echo -e "One option is using 'git config --global credential.helper store'"
echo -e "Or more secure visit https://stackoverflow.com/questions/36585496/error-when-using-git-credential-helper-with-gnome-keyring-as-sudo/40312117#40312117\n"
echo -e "Hit enter to exit. Or r + enter to run the script"
#read input
#if [ "$input" != "r" ]; then
#	exit
#fi

release="release/v4.4"

if [ -e taiscMgt ]; then
	rm -rf taiscMgt
fi

git clone http://vps2.lopos.be:52080/firmware/taisc.git taiscMgt
cd taiscMgt
git checkout master
git remote rm origin
git filter-branch --subdirectory-filter patches -- --all
chmod u+x check_git*.sh
chmod u+x fixgitmodules
chmod u+x build_engine.sh
chmod u+x 2*.sh
cd -
ln -fs taiscMgt/build_engine.sh .
ln -fs taiscMgt/2*.sh .

if [ -e contiki-ng ]; then
	rm -rf contiki-ng
fi

git clone https://github.com/contiki-ng/contiki-ng.git
cd contiki-ng
git pull
git checkout tags/$release
git restore-mtime
if [ ! -e ../taiscMgt/contiki-ng/$release/lopos_rev4.patch ]; then
	echo "not able to find patch $release/lopos_rev4.patch"
	exit
fi
patchresult=`git apply ../taiscMgt/contiki-ng/$release/lopos_rev4.patch 2>&1`
if [ ! -z "`echo $patchresult | grep -i 'error'`" ]; then
	echo "Patching failed $release	"
	echo "$patchresult"
	echo "Patching failed $release"
	exit
fi
../taiscMgt/fixgitmodules
../taiscMgt/check_pull_needed.sh .

touch os/net/mac/taisc/Makefile.TAISC_UPPERMACS

cd -


ln -fs contiki-ng/os/net/mac/taisc/patches/build_engine.sh .
ln -fs contiki-ng/os/net/mac/taisc/patches/2*.sh .
mv bootstrap_taisc.sh bootstrap_taisc_orig.sh
ln -fs contiki-ng/os/net/mac/taisc/patches/bootstrap_taisc.sh .

echo "please run:"
echo "./build_engine.sh"
