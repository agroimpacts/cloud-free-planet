#! /usr/bin/python

testData = [('SA1','geom1a'),('SA2','geom2'),('SA1','geom1b')]
testHash = {} # creates a dict (aka hash)

for polygon in testData:
    name, geom = polygon
    if name not in testHash:
        testHash[name] = [geom]
    else:
        testHash[name].append(geom)

print testHash

print("testHash has %s distinct names" % len(testHash))
for name in testHash:
    print("Name %s has %s polygon(s)" % (name, len(testHash[name])))
    if len(testHash[name]) == 1:
        print("Do normal processing here: only one polygon:")
        print(testHash[name][0])
    else:
        print("Do reassembly processing here: %s polygons:" % len(testHash[name]))
        for polygon in testHash[name]:
            print(polygon)
