#!/usr/bin/python

import sys

def usage():
    print 'usage: cmp.py <file1> <file2> <file3>'
    print ' <file1> is normal trace file'
    print ' <file2> is flow scheduling trace file'
    print ' <file3> is output file'

if __name__ == '__main__':
    if len(sys.argv[1:]) < 3:
        usage()
        exit()

    o1 = open(sys.argv[1], 'r')
    o2 = open(sys.argv[2], 'r')
    o = open(sys.argv[3], 'w')

    sum1 = 0
    sum2 = 0
    i = 0
    for line in o1:
        line2 = o2.readline()
        tmp1 = line.split()
        tmp2 = line2.split()
        if ' '.join(tmp1[:-2]) != ' '.join(tmp2[:-2]):
            print 'error: line %d not same' %i
            exit()
        if int(tmp1[-1]) == -1 or int(tmp2[-1]) == -1:
            print 'line %s timeout, ignore' %(i+1)
            continue
        sub = int(tmp1[-1]) - int(tmp2[-1])
        sum1 += int(tmp1[-1])
        sum2 += int(tmp2[-1])
        tmp1.append(tmp2[-1])
        tmp1.append(str(sub))
        r = '\t'.join(tmp1)
        o.write(r + '\n')

        i += 1

    o.write('sum1:%s\n' %sum1)
    o.write('sum2:%s\n' %sum2)
    effect = (sum1 - sum2) * 1.0 / sum1
    o.write('%.2f\n' %effect)
    o.close()
    o1.close()
    o2.close()
    print 'Done!'


