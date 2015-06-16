# ScienceDMZ

A collection of scripts to provision and test a ScienceDMZ using Mininet on a Vagrant box running Ubuntu 14.04.2 LTS (Trusty Tahr).

Includes:
- <a href="http://mininet.org/">Mininet</a> 2.2.1
- <a href="http://openvswitch.org/">OpenVSwitch</a> 2.3.1

Overview:
```
# install pre-requisites on the host
$ brew cask install virtualbox vagrant

# provision the vm
$ vagrant up

<<< wait a long time while the system initializes >>>

# log into the vm
$ vagrant ssh 
```
