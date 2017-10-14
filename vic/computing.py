def searchDivisor(p, interval):
    for d in range(interval[0], interval[1]+1):
        if p % d == 0:
            return 'COMPOSITE' #TODO return divisor
    return 'UNKNOWN'
