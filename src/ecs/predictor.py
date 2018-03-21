import time
import datetime
import copy

def predict_vm(ecs_lines, input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result

    flavorName = []
    createTime = []
    for i in range(len(ecs_lines)):
        values = ecs_lines[i].split(" ")
        createTime.append(time.strptime(values[2] + ' ' + values[3][:-1], "%Y-%m-%d %H:%M:%S"))

    startDate = datetime.datetime(createTime[0][0], createTime[0][1], createTime[0][2])
    endDate = datetime.datetime(createTime[-1][0], createTime[-1][1], createTime[-1][2])
    totalTrainTime = (endDate - startDate).days

    for i in range(totalTrainTime + 1):
        flavorName.append([])

    for i in range(len(ecs_lines)):
        values = ecs_lines[i].split(" ")
        temptime = time.strptime(values[2] + ' ' + values[3][:-1], "%Y-%m-%d %H:%M:%S")
        tempDate = datetime.datetime(temptime[0], temptime[1], temptime[2])
        tempindex = (tempDate - startDate).days
        flavorName[tempindex].append(values[1])

    fSpeciesNum = int(input_lines[2][:-1])
    fSpeciesList = []
    for i in range(fSpeciesNum):
        fSpeciesList.append([0] * (totalTrainTime + 1))

    fList = []
    fCPUData = []
    fMEMData = []
    FSP = time.strptime(input_lines[-2][:-1], "%Y-%m-%d %H:%M:%S")
    FSPdate = datetime.datetime(FSP[0], FSP[1], FSP[2])
    FEP = time.strptime(input_lines[-1][:-1], "%Y-%m-%d %H:%M:%S")
    FEPdate = datetime.datetime(FEP[0], FEP[1], FEP[2])
    FSPdateCurs = (FSPdate - startDate).days + 1
    FEPdateCurs = (FEPdate - startDate).days + 1
    FPCursDiff = FEPdateCurs - FSPdateCurs

    for i in range(fSpeciesNum):
        fList.append(input_lines[3 + i].split(" ")[0])
        fCPUData.append(int(input_lines[3 + i].split(" ")[1]))
        fMEMData.append(int(input_lines[3 + i].split(" ")[2][:-1]))

    for ifn in range(len(flavorName)):
        for idly in flavorName[ifn]:
            for ifsn in range(fSpeciesNum):
                if fList[ifsn] == idly:
                    fSpeciesList[ifsn][ifn] += 1

    fDataList = copy.copy(fSpeciesList)
    for i in range(len(fDataList)):
        for j in range(1, len(fDataList[i])):
            fDataList[i][j] += fDataList[i][j - 1]

    predict_y = []
    for i in range(len(fDataList)):
        sumdif = 0
        for j in range(totalTrainTime - FPCursDiff + 1):
            tempdif = fDataList[i][j + FPCursDiff] - fDataList[i][j]
            sumdif += tempdif
        avgdif = sumdif/(totalTrainTime - FPCursDiff + 1)
        predict_y.append(int(round(avgdif)))

    CPUperHost = int(input_lines[0].split(" ")[0])
    MEMperHost = int(input_lines[0].split(" ")[1]) * 1024
    pstable = []
    pperHost = [0] * fSpeciesNum
    p_y = copy.copy(predict_y)
    if input_lines[-4][:-1] == 'CPU':
        n = fSpeciesNum - 1
        tempcrest = CPUperHost
        while (n >= 0):
            if tempcrest / fCPUData[n] >= p_y[n]:
                tempcrest -= p_y[n] * fCPUData[n]
                pperHost[n] += p_y[n]
                p_y[n] = 0
                n -= 1
            else:
                p_y[n] -= tempcrest / fCPUData[n]
                pperHost[n] += tempcrest / fCPUData[n]
                tempcrest = tempcrest % fCPUData[n]
                i = n - 1
                while i >= 0:
                    if tempcrest >= fCPUData[i] and p_y[i] > 0:
                        tempcrest -= fCPUData[i]
                        p_y[i] -= 1
                        pperHost[i] += 1
                        if tempcrest == 0:
                            break
                    i -= 1
                pstable.append(copy.copy(pperHost))
                pperHost = [0] * fSpeciesNum
                tempcrest = CPUperHost
        pstable.append(copy.copy(pperHost))

    if input_lines[-4][:-1] == 'MEM':
        n = fSpeciesNum - 1
        tempmrest = MEMperHost
        while (n >= 0):
            if tempmrest / fMEMData[n] >= p_y[n]:
                tempmrest -= p_y[n] * fMEMData[n]
                pperHost[n] += p_y[n]
                p_y[n] = 0
                n -= 1
            else:
                p_y[n] -= tempmrest / fMEMData[n]
                pperHost[n] += tempmrest / fMEMData[n]
                tempmrest = tempmrest % fMEMData[n]
                i = n - 1
                while i >= 0:
                    if tempmrest >= fMEMData[i] and p_y[i] > 0:
                        tempmrest -= fMEMData[i]
                        p_y[i] -= 1
                        pperHost[i] += 1
                        if tempmrest == 0:
                            break
                    i -= 1
                pstable.append(copy.copy(pperHost))
                pperHost = [0] * fSpeciesNum
                tempmrest = MEMperHost
        pstable.append(copy.copy(pperHost))

    result.append(str(sum(predict_y)))
    for i in range(fSpeciesNum):
        result.append(fList[i] + ' ' + str(predict_y[i]))
    result.append('')
    result.append(str(len(pstable)))
    for i in range(len(pstable)):
        tempstr = str(i + 1)
        for j in range(len(pstable[i])):
            if pstable[i][j]:
                tempstr += (' ' + fList[j] + ' ' + str(pstable[i][j]))
        result.append(tempstr)

    # for itemTrain in flavorName:
    #	for itemf in fList:
    #		if itemf == itemTrain:
    #			fSpeciesList[fList.index(itemf)]+=1
    # for item in input_lines:
    #   print "index of input data"

    return result
