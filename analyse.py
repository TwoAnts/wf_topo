#!/usr/bin/python

import sys

ranges = [
(0, 100, 10),
(100,600, 100),
(600, 5600, 1000),
(5600, 65600, 20000),
(65600, 665600, 200000),
(665600, 2665600, 2000000)]

ranges2 = [
(0, 10, 10),
(10,60, 50),
(60, 560, 500),
(560, 6560, 6000),
(6560, 66560, 60000)]



analyse_list = []

def init_analyse_list(analyse_list, ranges):
    for one_range in ranges:
        for i in range(*one_range):
            _dict = {'range' : i+one_range[2],
                     'bytes' : 0,
                     'fct1' : 0,
                     'fct2' : 0, 
                     'sub' : 0}
            analyse_list.append(_dict)

def append_to_analyse_list(analyse_list, content):
    tmp = content.split()
    if len(tmp) < 6:
        return
    #print tmp
    size, req_h, resp_h, fct1, fct2, sub = tmp
    size = int(size)
    for e in analyse_list:
        if size <= e['range']:
            e['bytes'] = size + e['bytes']
            e['fct1'] = int(fct1) + e['fct1']
            e['fct2'] = int(fct2) + e['fct2']
            e['sub'] = int(sub) + e['sub']
            break
        
if __name__ == '__main__':
    if len(sys.argv[1:]) < 2:
        print 'require 2 args!'
        exit()

    i_f = open(sys.argv[1], 'r')

    init_analyse_list(analyse_list, ranges)

    for line in i_f:
        append_to_analyse_list(analyse_list, line)

    i_f.close()


    o_f = open(sys.argv[2], 'w')
    start = 0
    for e in analyse_list:
        r = '%s\t%s\t%s\t%s\t%s\t%s\n' %(start, e['range'],\
                    e['bytes'], e['fct1'], e['fct2'],\
                    e['sub'])
        start = e['range']
        o_f.write(r)

    o_f.close()

    print 'Done!'

    

        
