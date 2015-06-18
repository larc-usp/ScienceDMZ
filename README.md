# ScienceDMZ

Collection of scripts to provision and test data transfer in a ScienceDMZ using Mininet on a Vagrant box running Ubuntu 14.04.2 LTS (Trusty Tahr).

Mac OS X:
- VirtualBox 4.3.28r100309
- Vagrant 1.7.2
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

# consider taking a snapshot of this clean install
$ vagrant halt
$ vagrant snapshot take default fresh

# log into the vm
$ vagrant up
$ vagrant ssh 

# start up the POX controller
$ pox/pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l2_learning
$ pox/pox.py log.level --DEBUG openflow.of_01 --port=6634 forwarding.l2_learning

# run the data transfer tests
$ sudo bash run.sh
```
