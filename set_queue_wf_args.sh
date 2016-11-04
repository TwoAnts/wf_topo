#!/bin/bash

DEPTH=$1
FANOUT=$2
HOST_MAX_RATE=$3
HOST_NUM_PER_SWITCH=$4


child_port_rate(){
    depth=$1
    fanout=$FANOUT
    unit_rate=$HOST_MAX_RATE
    per_host_num=$HOST_NUM_PER_SWITCH
    if [ $depth -eq 1 ]; then
        child_rate=$unit_rate
    else
        child_rate=$[($fanout**($depth-2)*$per_host_num) * $unit_rate] 
    fi
}

parent_port_rate(){
    depth=$1
    fanout=$FANOUT
    unit_rate=$HOST_MAX_RATE
    per_host_num=$HOST_NUM_PER_SWITCH
    parent_rate=$[($fanout**($depth-1)*$per_host_num) * $unit_rate]
}

min_rate(){
    max_rate=$1
    min_rate_result=$[$max_rate * 0.05]
}

cfg_qos_='other-config:max-rate='
cfg_q0='other-config:priority=1'
cfg_q1='other-config:priority=2'
cfg_q2='other-config:priority=4'



ovs-vsctl --all destroy qos
ovs-vsctl --all destroy queue

set_queue(){
    ovs-vsctl -- set port $1 qos=@newqos \
    -- --id=@newqos create qos type=linux-htb ${cfg_qos_}${2} \
    queues=0=@q0,1=@q1,2=@q2 \
    -- --id=@q0 create queue $cfg_q0 \
    -- --id=@q1 create queue $cfg_q1 \
    -- --id=@q2 create queue $cfg_q2
}

parent_port_rate $DEPTH
for((port=1; port <= $FANOUT; port++))
do
    set_queue s0-eth$port "$parent_rate"
    echo s0-eth$port-$parent_rate
done

for((i=$DEPTH; i > 0; i--))
do
    j=$[$DEPTH - $i]
    node_num=$[$FANOUT**($j+1)]
    node_start=$[$FANOUT*$j+1]
    node_end=$[$node_start + $node_num - 1]
    child_port_rate $i
    parent_port_rate $i
    child_num=$FANOUT
    if [ $i -eq 1 ];then
        child_num=$HOST_NUM_PER_SWITCH
    fi
    for((node=$node_start; node<=$node_end; node++))
    do
        set_queue s$node-eth1 "$parent_rate"
        echo s$node-eth1-$parent_rate
        for((port=2; port<=$[$child_num+1]; port++))
        do
            set_queue s$node-eth$port "$child_rate"	    
            echo s$node-eth$port-$child_rate
        done
    done
done

