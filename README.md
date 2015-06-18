# ScienceDMZ

Collection of scripts to provision and test data transfer in a ScienceDMZ using Mininet on a Vagrant box running Ubuntu 14.04.2 LTS (Trusty Tahr).

Vagrant host:
- Vagrant 1.7.2
- VirtualBox 4.3.28r100309
- Ubuntu 14.04.2 LTS (Trusty Tahr)

Vagrant guest VM:
- <a href="http://mininet.org/">Mininet</a> 2.2.1
- <a href="http://openvswitch.org/">OpenVSwitch</a> 2.3.1
- POX
- Pyretic

Overview:
```
# install pre-requisites on the host
$ brew cask install virtualbox vagrant
$ vagrant plugin install vagrant-vbox-snapshot

# provision the vm
$ vagrant up

<<< wait a long time while the system initializes >>>

# log into the vm
$ vagrant ssh 

# run the data transfer tests
$ sudo bash run.sh
```
