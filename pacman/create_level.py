import json
def readlevel(filename="pacman_points.json"):
    return json.loads(open(filename,'r'))

def writelevel(name,dictionary):
    open(name,'w').write(json.dumps(dictionary))
    return json.dumps(dictionary)

def convert_fromstring(x,long):
    count = -1
    row = -1
    outcome = []
    for i in x:
        try:
            i = int(i)
            count += 1
            if count%long == 0:
                row += 1
                outcome.append([i])
                continue
            outcome[row] += [i]
        except:
            pass
    return outcome

def write_down(x,start_ghost=[],wanted=[],walls=0,empty=1,road=2):
    switch = {walls:"walls",empty:"empty",road:"road",}
    outcome = {"walls":[],"empty":[],"road":[],"start_ghost":start_ghost,"wanted":wanted}
    pos = [-1,-1]
    for i in x:
        pos[0] += 1
        pos[1] = -1
        for j in i:
            pos[1] += 1
            outcome[switch[j]] += [pos[:]]
    return outcome

if __name__ == "__main__":
    print(
        writelevel(
            "small.json",
            write_down(
                convert_fromstring(
                    """

                    """,4
                ),[[3,3],[0,2]],[[1,0],[2,1]]
            )
        )
    )