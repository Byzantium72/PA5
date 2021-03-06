from network_2 import Router, Host
from link_2 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)
    
    #create routers and routing tables for connected clients (subnets)
    #encap_tbl_D = {'H1': '1','H2': '2','H3': '3'}    # table used to encapsulate network packets into MPLS frames
    encap_tbl_D = {'H1': '1','H2': '2','H3': {'2': '4', '3': '3'}} 
    #Still need to be able to have source, to send to new route
    frwd_tbl_D = {'1': ['99', 'H1', 3], '2':['98','H2',2], '3':['4','RB',0], '4':['5','RC',1]}     # table used to forward MPLS frames
    decap_tbl_D = {'99':'H1','98':'H2'}    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA', 
                              intf_capacity_L=[500,500, 500, 500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    #H1 here is where you're sending it, and 11 is on what interface I think
    encap_tbl_D = {}
    #12 here is what it's coming in as, then 11 is what you're putting it in as next, destination, and the interface
    frwd_tbl_D = {'4': ['6', 'RB', 0], '7':['6','H1',1]}
    #If it's 11, decapsulate, and send it to H2
    decap_tbl_D = {}
    router_b = Router(name='RB', 
                              intf_capacity_L=[500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    encap_tbl_D = {}
    frwd_tbl_D = {'5': ['6', 'H3', 1],'6':['8','H2',0]}
    decap_tbl_D = {}
    router_c = Router(name='RC',
                              intf_capacity_L=[500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_c)

    #create routers and routing tables for connected clients (subnets)
    encap_tbl_D = {'H1': '1','H2': '2'}    # table used to encapsulate network packets into MPLS frames
    #Still need to be able to have source, to send to new route
    frwd_tbl_D = {'1': ['7', 'H1', 2], '2':['8','H2',1], '6':['97','H3',0]}     # table used to forward MPLS frames
    decap_tbl_D = {'97':'H3'}    # table used to decapsulate network packets from MPLS frames
    router_d = Router(name='RD',
                              intf_capacity_L=[500,500, 500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_d)



    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 3))
    link_layer.add_link(Link(host_2, 0, router_a, 2))

    link_layer.add_link(Link(router_a, 0, router_b, 1))
    link_layer.add_link(Link(router_a, 1, router_c, 0))

    link_layer.add_link(Link(router_d, 2, router_b, 0))
    link_layer.add_link(Link(router_d, 1, router_c, 1))

    link_layer.add_link(Link(host_3, 0, router_d, 0))

    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()

    #Currently, h1 and h2 will send through the same path, but h3 will send through different. Should be improved.
    host_1.udt_send('H2', 'MESSAGE_%d_FROM_H1' % 0, 0)
    host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % 1, 1)
    host_2.udt_send('H3', 'MESSAGE_%d_FROM_H2' % 0, 0)
    host_3.udt_send('H1', 'MESSAGE_%d_FROM_H3' % 0, 1)

    #create some send events    
    # for i in range(5):
    #     priority = i%2
    #     host_1.udt_send('H2', 'MESSAGE_%d_FROM_H1' % i, priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")
