# -*- mode: ruby -*-
# vi: set ft=ruby :

$PACKAGES = <<SCRIPT
  export LANGUAGE=en_US.UTF-8
  export LANG=en_US.UTF-8
  export LC_ALL=en_US.UTF-8
  locale-gen en_US.UTF-8
  dpkg-reconfigure locales

  aptitude update
  aptitude install -y autoconf \
		      automake \
		      build-essential \
		      bwm-ng \
		      debhelper \
		      emacs \
  	   	      fakeroot \
		      git \
		      graphviz \
		      htop \
		      libfreetype6-dev \
		      libssl-dev \
		      libtool \
		      libxft-dev \
		      openjdk-7-jdk \
  		      python-all \
		      python-dev \
		      python-pip \
		      python-paramiko \
		      python-qt4 \
  		      python-sphinx \
		      python-twisted-conch \
		      screen \
		      tmux \
		      vim 

  pip install alabaster \
      	      bitarray \
	      ipaddr \
	      netaddr \
	      networkx \
	      matplotlib \
	      yappi 
SCRIPT

$OVS = <<SCRIPT
  if command -v ovs-vswitchd; 
  then 
    echo "OpenVSwitch daemon already installed."
  else 
    echo "Installing OpenVSwitch..."
    curl http://openvswitch.org/releases/openvswitch-2.3.1.tar.gz | tar xz
    pushd openvswitch-2.3.1
    DEB_BUILD_OPTIONS='parallel=8 nocheck' fakeroot debian/rules binary
    popd
    sudo dpkg -i openvswitch-common*.deb \
       	         openvswitch-datapath-dkms*.deb \
	         python-openvswitch*.deb \
	         openvswitch-pki*.deb \
	         openvswitch-switch*.deb
    rm -rf *openvswitch*
  fi
SCRIPT

$MININET = <<SCRIPT
  if [ ! -d mininet ];
  then 
    echo "Installing mininet..."
    git clone https://github.com/mininet/mininet.git mininet
    cd mininet
      git checkout -b 2.2.1 2.2.1
      ./util/install.sh -fn
    cd ..
  else
    echo "Mininet already installed."
  fi 
SCRIPT

$PYRETIC = <<SCRIPT
  if [ ! -d pyretic ];
  then 
    echo "Installing pyretic..."
    git clone https://github.com/frenetic-lang/pyretic.git pyretic
  else
    echo "Pyretic already installed."
  fi
SCRIPT

$POX = <<SCRIPT
  if [ ! -d pox ];
  then
    echo "Installing pox..."
    git clone https://github.com/noxrepo/pox.git pox
  else
    echo "POX already installed."
  fi
SCRIPT

$SFLOW = <<SCRIPT
  if [ ! -d sflow-rt ];
  then
    echo "Installing sFlow-RT..."
    curl http://www.inmon.com/products/sFlow-RT/sflow-rt.tar.gz | tar xz
  else
    echo "sFlow-RT already installed."
  fi
SCRIPT

$KEY = <<SCRIPT
  mkdir -p /home/vagrant/.ssh
  chmod 700 /home/vagrant/.ssh
  ssh-keygen -q -t rsa -f /home/vagrant/.ssh/id_rsa -N "" -C vagrant@mininet
  cat /home/vagrant/.ssh/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys

  chmod 600 /home/vagrant/.ssh/authorized_keys
  chmod 600 /home/vagrant/.ssh/id_rsa
  chmod 644 /home/vagrant/.ssh/id_rsa.pub
  chown vagrant:vagrant /home/vagrant/.ssh/{authorized_keys,id_rsa,id_rsa.pub}

  if [ -f /home/vagrant/.ssh/id_rsa.pub ];
  then    
    echo "Creating a vagrant specific ssh key ... [OK]"
  else
    echo "Creating a vagrant specific ssh key ... [ERROR]"
  fi 
SCRIPT

$CLEAN = <<SCRIPT
  if [ -f /home/vagrant/.ssh/id_rsa.pub ];
  then 
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
    cp /home/vagrant/.ssh/{id_rsa,id_rsa.pub} /root/.ssh/ 
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

    chmod 600 /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/id_rsa
    chmod 644 /root/.ssh/id_rsa.pub
    chown root:root /root/.ssh/{authorized_keys,id_rsa,id_rsa.pub}

    echo "Inserted vagrant specific root key ... [OK]"
  fi

  aptitude clean
  rm -rf /tmp/*
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider "virtualbox" do |v|
      v.gui = false
      v.cpus = 4
      v.memory = 8000
      
      v.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
  end

  ## Guest config
  config.vm.hostname = "mininet"
  config.vm.synced_folder ".", "/vagrant/"
  config.vm.network :private_network, ip: "192.168.56.101" # hostonly network (vboxnet0) 192.168.56/24

  # ports forwarded for services
  #config.vm.network :forwarded_port, guest:6633, host:6633 # pox
  #config.vm.network :forwarded_port, guest:6634, host:6634 # pox
  config.vm.network :forwarded_port, guest:8008, host:8008 # sFlow-RT

  ## SSH config
  config.ssh.forward_x11 = true

  ## Provisioning
  config.vm.provision :shell, :inline => $PACKAGES

  config.vm.provision :shell, privileged: false, :inline => $KEY
  config.vm.provision :shell, privileged: false, :inline => $OVS
  config.vm.provision :shell, privileged: false, :inline => $MININET
  config.vm.provision :shell, privileged: false, :inline => $PYRETIC
  config.vm.provision :shell, privileged: false, :inline => $POX
  config.vm.provision :shell, privileged: false, :inline => $SFLOW

  config.vm.provision :shell, :inline => $CLEAN
end
