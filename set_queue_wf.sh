#!/bin/bash

#cfg_qos='other-config:max-rate=100000000'
#cfg_q0='other-config:min-rate=5000000 other-config:priority=1'
#cfg_q1='other-config:min-rate=10000000 other-config:priority=2'
#cfg_q2='other-config:min-rate=20000000 other-config:priority=4'

#cfgp_qos='other-config:max-rate=300000000'
#cfgp_q0='other-config:min-rate=15000000 other-config:priority=1'
#cfgp_q1='other-config:min-rate=30000000 other-config:priority=2'
#cfgp_q2='other-config:min-rate=60000000 other-config:priority=4'

cfg_qos='other-config:max-rate=100000000'
cfg_q0='other-config:priority=1'
cfg_q1='other-config:priority=2'
cfg_q2='other-config:priority=4'

cfgp_qos='other-config:max-rate=300000000'
cfgp_q0='other-config:priority=1'
cfgp_q1='other-config:priority=2'
cfgp_q2='other-config:priority=4'


ovs-vsctl --all destroy qos
ovs-vsctl --all destroy queue

set_queue(){
    ovs-vsctl -- set port $1 qos=@newqos \
    -- --id=@newqos create qos type=linux-htb $2 \
    queues=0=@q0,1=@q1,2=@q2 \
    -- --id=@q0 create queue $3 \
    -- --id=@q1 create queue $4 \
    -- --id=@q2 create queue $5
}

set_queue_p(){
    ovs-vsctl -- set port $1 qos=@newqos \
    -- --id=@newqos create qos type=linux-htb $cfgp_qos \
    queues=0=@q0,1=@q1,2=@q2 \
    -- --id=@q0 create queue $cfgp_q0 \
    -- --id=@q1 create queue $cfgp_q1 \
    -- --id=@q2 create queue $cfgp_q2
}

set_queue_c(){
    ovs-vsctl -- set port $1 qos=@newqos \
    -- --id=@newqos create qos type=linux-htb $cfg_qos \
    queues=0=@q0,1=@q1,2=@q2 \
    -- --id=@q0 create queue $cfg_q0 \
    -- --id=@q1 create queue $cfg_q1 \
    -- --id=@q2 create queue $cfg_q2
}

set_queue_p s1-eth1 
set_queue_p s1-eth2
set_queue_p s2-eth1
set_queue_p s3-eth1

for i in {2..3}
do
    for j in {2..4}
    do
        set_queue_c s$i-eth$j
    done
done
