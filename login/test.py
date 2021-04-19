a = {'a':'1','b':'','c':None}
print(a.get('a',None))
print(a.get('b',None))

if a.get('a',None):
    print('------'+a.get('a',None))
if a.get('b',None):
    print('-------b')
else:
    print('-------b2')
if a.get('c',None):
    print('-------c1')
else:
    print('-------c2')
