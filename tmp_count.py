#!/usr/bin/python
import sys

if __name__ == '__main__':
    fin = sys.argv[1]
    
    size_all = 0
    s = 0
    d = 0
    f = open(fin, 'r')
    for line in f:
        tmp = line.split()
        size, dist = int(tmp[0]), float(tmp[1])
        print '+ size:%s %s  dist:%s %s' %(size, (size - s)/2.0, dist, dist - d) 
        size, s = (size - s)/2.0, size
        dist, d = (dist - d), dist
        size_all = size * dist
   
    f.close()
    print size_all
        
