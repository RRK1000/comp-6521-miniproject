import itertools
import ast
from time import perf_counter as pc
import bitmap
import tracemalloc

class QProcessor:
    projectionList = []
    clauses = []
    relationList = []
    relationInfo = {}
    joinRelationInfo = {}
    selectQueryTime = 0

    # Displays Query Tokens (projections, clauses)
    def displayTokens(self):
        print("Projection List: ", self.projectionList)
        print("Clause List: ", self.clauses)
        print("Relation List: ", self.relationList)

    # finds the relation of the given column
    def findRelation(self, column) -> str:
        for i in self.relationInfo.keys():
            if column in self.relationInfo[i]:
                return i
        return ""

    # Splits the query into query tokens
    def tokenizeQuery(self, query):
        query = query.lower().strip(";")

        # projections
        self.projectionList.extend(
            [i.strip(" ") for i in query.split("from")[0].lstrip("select").split(",")]
        )

        # where clauses
        self.clauses.extend(
            [
                i.strip(" ")
                if i.strip(" ") not in ["and", "or", "in"]
                else " " + i + " "
                for i in query.split("where")[1].strip(" ").split(" ")
            ]
        )

        # relation list
        for relation in query.split("from")[1].split("where")[0].split(","):
            self.relationList.append(relation.strip(" "))

        return

    def generateConditionList(self, clauses):
        # clauses = ['product', '=', 'products.product_id']
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']
        i = 0
        conditionList = []
        while i + 3 <= len(clauses):
            if clauses[i] == " and " or clauses[i] == " or ":
                conditionList.append(clauses[i])
                i += 1
                continue

            # condition processing
            if "." not in clauses[i]:
                r = self.findRelation(clauses[i])
                if r != "":
                    clauses[i] = str(r) + "." + str(clauses[i])

            if "." not in clauses[i + 2]:
                r = self.findRelation(clauses[i + 2])
                if r != "":
                    clauses[i + 2] = str(r) + "." + str(clauses[i + 2])

            conditionList.append(
                str(clauses[i]) + str(clauses[i + 1]) + str(clauses[i + 2])
            )
            i += 3
        return conditionList

    def processJoinOnServer(self, conn, relationList, query: str) -> list:
        result = []
        cursor = conn.cursor()

        query_parts = query.lower().split(" from ")
        relationListAnn = ", '.', ".join([name + ".ann" for name in relationList])
        joinQuery = (
            query_parts[0] + f", concat({relationListAnn}) from " + query_parts[1]
        )

        cursor.execute(joinQuery)
        queryData = cursor.fetchall()

        result = [list(ele) for ele in queryData]

        return result

    def processJoin(self, conn, relationList) -> list:
        result = []
        relationDataDict = {}
        cursor = conn.cursor()
        # fetching data from postgresql
        for relation in relationList:
            query = """select * from """
            cursor.execute(query + relation)
            relationdata = cursor.fetchall()
            relationColData = {
                ele: pos
                for pos, ele in enumerate([desc[0] for desc in cursor.description])
            }
            self.relationInfo[relation] = relationColData
            relationDataDict[relation] = relationdata

        t0 = pc()

        idx = 0
        # updating self.joinRelationInfo
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + "." + column] = idx
                idx += 1
        # computing the cartesian product
        for tuple in itertools.product(*relationDataDict.values(), repeat=1):
            row = ""
            for item in tuple:
                row += str(item).replace("'", "")
            resultItem = row.replace(")(", ", ").lstrip("(").rstrip(")").split(", ")
            result.append(",".join(map(str, resultItem)))
        idxList = [
            self.joinRelationInfo[relation + ".ann"] for relation in self.relationList
        ]
        # computing the annotated bucket
        for i in range(len(result)):
            bucket = []
            for idx in idxList:
                bucket.append(result[i].split(",")[idx])

            result[i] = result[i] + "," + ".".join(map(str, bucket))
        print("Time taken for manual join: ", pc() - t0)

        return result

    def processSortJoin(self, conn, clauses, relationList) -> list:
        result = []
        relationDataDict = {}
        cursor = conn.cursor()

        # fetching data from postgresql
        for relation in relationList:
            query = """select * from """
            cursor.execute(query + relation)
            relationdata = cursor.fetchall()
            relationColData = {
                ele: pos
                for pos, ele in enumerate([desc[0] for desc in cursor.description])
            }
            self.relationInfo[relation] = relationColData
            relationDataDict[relation] = relationdata

        relationR = relationDataDict[relationList[0]]
        relationS = relationDataDict[relationList[1]]
        relationRName = relationList[0]
        relationSName = relationList[1]

        t0 = pc()
        idx = 0
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + "." + column] = idx
                idx += 1

        # sorting relations
        conditionList = self.generateConditionList(clauses)
        # print(conditionList)
        for cond in conditionList:
            if cond in [" and ", " or "]:
                continue

            tmpLhs = (
                cond.split("=")[0]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[0]
            )
            lhs = tmpLhs if "." in tmpLhs else None
            tmpRhs = (
                cond.split("=")[1]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[1]
            )
            rhs = tmpRhs if "." in tmpRhs else None

            if lhs.split(".")[0] != relationRName:
                tmpLhs, tmpRhs = tmpRhs, tmpLhs
                lhs, rhs = rhs, lhs

            lhsIdx = (
                self.relationInfo[lhs.split(".")[0]][lhs.split(".")[1]]
                if lhs != None
                else None
            )
            rhsIdx = (
                self.relationInfo[rhs.split(".")[0]][rhs.split(".")[1]]
                if rhs != None
                else None
            )

            relationR.sort(key=lambda x: x[lhsIdx]) if lhsIdx != None else None
            relationS.sort(key=lambda x: x[rhsIdx]) if rhsIdx != None else None

        # computing join after sort
        for tupleR in relationR:
            for tupleS in relationS:
                isValid = True
                for cond in conditionList:
                    if cond in [" and ", " or "]:
                        continue

                    tmpLhs = (
                        cond.split("=")[0]
                        if len(cond.split("=")) > 1
                        else cond.split(" in ")[0]
                    )
                    lhs = tmpLhs if "." in tmpLhs else None
                    tmpRhs = (
                        cond.split("=")[1]
                        if len(cond.split("=")) > 1
                        else cond.split(" in ")[1]
                    )
                    if tmpRhs[0] == "(":
                        tmpRhs = eval(tmpRhs)
                    rhs = tmpRhs if "." in tmpRhs else None

                    tmpTupleR = tupleR
                    tmpTupleS = tupleS
                    swapFlag = False
                    if lhs.split(".")[0] != relationRName:
                        tmpLhs, tmpRhs = tmpRhs, tmpLhs
                        lhs, rhs = rhs, lhs
                        tmpTupleR, tmpTupleS = tmpTupleS, tmpTupleR
                        swapFlag = True

                    lhsIdx = (
                        self.relationInfo[lhs.split(".")[0]][lhs.split(".")[1]]
                        if lhs != None
                        else None
                    )
                    # 0
                    rhsIdx = (
                        self.relationInfo[rhs.split(".")[0]][rhs.split(".")[1]]
                        if rhs != None
                        else None
                    )
                    if swapFlag:
                        lhsIdx, rhsIdx = rhsIdx, lhsIdx

                    if (
                        (
                            rhsIdx != None
                            and str(tmpTupleR[lhsIdx]) == str(tmpTupleS[rhsIdx])
                        )
                        or (swapFlag and str(tmpTupleR[lhsIdx]) == str(tmpLhs))
                        or (str(tmpTupleR[lhsIdx]) == str(tmpRhs))
                        or (type(tmpRhs) == tuple and int(tmpTupleR[lhsIdx]) in tmpRhs)
                        or (
                            swapFlag
                            and type(tmpLhs) == tuple
                            and int(tmpTupleR[lhsIdx]) in tmpLhs
                        )
                    ):
                        continue
                    else:
                        isValid = False
                        break
                if not isValid:
                    continue
                result.append(tupleR + tupleS)
        print("Time taken for sort based join: ", pc() - t0)

        idxList = [
            self.joinRelationInfo[relation + ".ann"] for relation in self.relationList
        ]

        # computing the annotated bucket
        for i in range(len(result)):
            bucket = []
            for idx in idxList:
                bucket.append(result[i][idx])
            result[i] = result[i] + tuple([".".join(map(str, bucket))])
            result[i] = ",".join(map(str, result[i]))

        return result

    def processBitmapJoin(self, conn, clauses, relationList) -> list:
        result=[]
        relationDataDict={}
        cursor=conn.cursor()

        # fetching data from postgresql
        for relation in relationList:
            query = """select * from """
            cursor.execute(query + relation)
            relationdata = cursor.fetchall()
            relationColData = {
                ele: pos
                for pos, ele in enumerate([desc[0] for desc in cursor.description])
            }
            self.relationInfo[relation] = relationColData
            relationDataDict[relation] = relationdata

        t0 = pc()

        idx = 0
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + "." + column] = idx
                idx += 1

        relationR = relationDataDict[relationList[0]]
        relationS = relationDataDict[relationList[1]]
        relationRName = relationList[0]

        # generate compressed bitmaps and save into csv files
        for key in self.joinRelationInfo:
            tableName = key.split(".")[0]
            attribute = key.split(".")[1]
            bitmap.generateBitmap(tableName, attribute, "i")

        idx = 0
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + "." + column] = idx
                idx += 1

        # extract bitmaps from csv files for the
        conditionList = self.generateConditionList(clauses)
        for cond in conditionList:
            if cond.lower() in [" and ", " or "]:
                continue

            tmpLhs = (
                cond.split("=")[0]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[0]
            )

            lhs = tmpLhs if "." in tmpLhs else tmpLhs
            tmpRhs = (
                cond.split("=")[1]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[1]
            )
            if "." in tmpRhs:
                rhs=tmpRhs

            elif "in" in tmpRhs:
                rhs="range"

            if rhs!="range":
                lhsBitmap = bitmap.extractBitmap("bitmap_index_"+lhs+".csv")
                rhsBitmap = bitmap.extractBitmap("bitmap_index_"+rhs+".csv")
                isSwap = False
                if len(lhs.split(".")) > 1 and (lhs.split(".")[0] == relationRName):
                    relationR, relationS = relationS, relationR
                    isSwap = True

                for key, bit1 in lhsBitmap.items():
                    if key in rhsBitmap.keys():

                        indexOf1R = ( [pos for pos, char in enumerate(bit1) if char == '1'])
                        indexOf1S = ( [pos for pos, char in enumerate(rhsBitmap.get(key)) if char == '1'])

                        for pos1R in indexOf1R:
                            for pos1S in indexOf1S:
                                tuple1=relationS[pos1R-1]
                                tuple2=relationR[pos1S-1]
                                result.append(tuple1 + tuple2 if isSwap else tuple2 + tuple1)

        idxList = [
            self.joinRelationInfo[relation + ".ann"] for relation in self.relationList
        ]

        for i in range(len(result)):
            bucket = []
            for idx in idxList:
                bucket.append(result[i][idx])
            result[i] = result[i] + tuple([".".join(map(str, bucket))])
            result[i] = ",".join(map(str, result[i]))
        print("Time taken for bitmap based join: ", pc() - t0)
        return result

    def andOnBitString(self, bit1, bit2):
        bitString=""

        minLen=min(len(bit1), len(bit2))

        while minLen!=0:
            if bit1[minLen-1] == "1" and bit2[minLen-1]=="1":
                bitString="1"+bitString
            else:
                bitString="0"+bitString

            minLen-=1

        return bitString

    def processWhere(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id']
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']
        i = 0
        conditionList = []
        while i + 3 <= len(clauses):
            if clauses[i] == " and " or clauses[i] == " or ":
                conditionList.append(clauses[i])
                i += 1
                continue

            # condition processing
            if "." not in clauses[i]:
                r = self.findRelation(clauses[i])
                if r != "":
                    clauses[i] = str(r) + "." + str(clauses[i])

            if "." not in clauses[i + 2]:
                r = self.findRelation(clauses[i + 2])
                if r != "":
                    clauses[i + 2] = str(r) + "." + str(clauses[i + 2])

            conditionList.append(
                str(clauses[i]) + str(clauses[i + 1]) + str(clauses[i + 2])
            )
            i += 3
        # print("Condition List:" + ",".join(conditionList))
        # print()

        whereResult = []
        operators = ["<", ">", "=", " in "]
        for tuple in joinResult:
            tuple = str(tuple).split(",")
            isTupleValid = []
            for i in range(len(conditionList)):
                cond = conditionList[i]
                if cond == " and " or cond == " or " or cond == " in ":
                    isTupleValid.append(cond)
                    continue

                for op in operators:
                    if len(cond.split(op)) > 1:
                        lhs = tuple[self.joinRelationInfo[cond.split(op)[0]]].lower()
                        rhs = (
                            tuple[self.joinRelationInfo[cond.split(op)[1]]].lower()
                            if "." in cond.split(op)[1]
                            else cond.split(op)[1].lower().strip("'")
                        )

                        if op == "<":
                            isTupleValid.append(str(lhs < rhs))
                        elif op == ">":
                            isTupleValid.append(str(lhs > rhs))
                        elif op == "=":
                            isTupleValid.append(str(lhs == rhs))
                        elif op == " in ":
                            rhs = rhs.lstrip("(").rstrip(")").split(",")
                            if lhs in rhs:
                                isTupleValid.append("True")
                            else:
                                isTupleValid.append("False")

            # Single condition case
            if len(isTupleValid) == 1:
                if isTupleValid[0] == "True":
                    whereResult.append(tuple)
                continue

            # multiple condition case
            isValid = False
            if isTupleValid[1] == " and ":
                isValid = eval(isTupleValid[0]) and eval(isTupleValid[2])
            elif isTupleValid[1] == " or ":
                isValid = eval(isTupleValid[0]) or eval(isTupleValid[2])

            for i in range(3, len(isTupleValid) - 1):
                if isTupleValid[i] == " and ":
                    isValid = isValid and eval(isTupleValid[i + 1])
                elif isTupleValid[i] == " or ":
                    isValid = isValid or eval(isTupleValid[i + 1])
            if isValid:
                whereResult.append(tuple)

        return whereResult

    def processSelectQuery(self, conn, query, jointype) -> list:
        t0 = pc()
        tracemalloc.start()


        query = query.replace("\n", "")

        self.tokenizeQuery(query)

        joinResult = []
        if len(self.relationList) > 1:
            if jointype == 2:
                joinResult = self.processSortJoin(conn, self.clauses, self.relationList)
            elif jointype == 3:
                joinResult = self.processOptimizedSortJoin(conn, self.clauses, self.relationList)
            elif jointype == 4:
                joinResult = list(set(self.processBitmapJoin(conn, self.clauses, self.relationList)))
            else:
                joinResult = self.processJoin(conn, self.relationList)


        # processing where clauses
        whereResult = []
        whereResult = self.processWhere(joinResult, self.clauses)

        # processing projections
        projectionResult = []
        idxList = []
        for column in self.projectionList:
            idxList.append(
                self.joinRelationInfo[self.findRelation(column) + "." + column]
            )
        for row in whereResult:
            tpl = []
            for idx in idxList:
                tpl.append(row[idx])
            tpl.append(str(row[len(row) - 1]))
            projectionResult.append(tpl)


        # Comment above code and uncomment below lines to execute processJoinOnServer

        # query = query.replace("\n", "")
        # self.tokenizeQuery(query)
        # projectionResult = self.processJoinOnServer(conn, self.relationList, query)

        merged_data = {}

        for item in projectionResult:
            key = tuple(item[:-1])
            value = item[-1]
            if key in merged_data:
                merged_data[key] += " + " + value
            else:
                merged_data[key] = value

        projectionResult = [list(key) + [values] for key, values in merged_data.items()]

        self.selectQueryTime = pc() - t0
        print("Peak memory [MB]: ", tracemalloc.get_traced_memory()[0]/(1024*1024))
        tracemalloc.stop()
        return projectionResult

    def processOptimizedSortJoin(self, conn, clauses, relationList) -> list:
        result = []
        relationDataDict = {}
        cursor = conn.cursor()

        # fetching data from postgresql
        for relation in relationList:
            query = """select * from """
            cursor.execute(query + relation)
            relationdata = cursor.fetchall()
            relationColData = {
                ele: pos
                for pos, ele in enumerate([desc[0] for desc in cursor.description])
            }
            self.relationInfo[relation] = relationColData
            relationDataDict[relation] = relationdata

        relationR = relationDataDict[relationList[0]]
        relationS = relationDataDict[relationList[1]]
        relationRName = relationList[0]
        relationSName = relationList[1]

        t0 = pc()
        idx = 0
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + "." + column] = idx
                idx += 1

        # sorting relations
        conditionList = self.generateConditionList(clauses)
        # print(conditionList)
        for cond in conditionList:
            if cond in [" and ", " or "]:
                continue

            tmpLhs = (
                cond.split("=")[0]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[0]
            )
            lhs = tmpLhs if "." in tmpLhs else None
            tmpRhs = (
                cond.split("=")[1]
                if len(cond.split("=")) > 1
                else cond.split(" in ")[1]
            )
            rhs = tmpRhs if "." in tmpRhs else None

            if lhs.split(".")[0] != relationRName:
                tmpLhs, tmpRhs = tmpRhs, tmpLhs
                lhs, rhs = rhs, lhs

            lhsIdx = (
                self.relationInfo[lhs.split(".")[0]][lhs.split(".")[1]]
                if lhs != None
                else None
            )
            rhsIdx = (
                self.relationInfo[rhs.split(".")[0]][rhs.split(".")[1]]
                if rhs != None
                else None
            )

            relationR.sort(key=lambda x: x[lhsIdx]) if lhsIdx != None else None
            relationS.sort(key=lambda x: x[rhsIdx]) if rhsIdx != None else None

        i = j = 0
        n = len(relationR)
        m = len(relationS)
        
        # computing join after sort
        while(i<n):
            j = 0
            while(j<m):
                isValid = True
                for cond in conditionList:
                    tupleR = relationR[i]
                    tupleS = relationS[j]

                    if cond in [" and ", " or "]:
                        continue

                    tmpLhs = (
                        cond.split("=")[0]
                        if len(cond.split("=")) > 1
                        else cond.split(" in ")[0]
                    )
                    lhs = tmpLhs if "." in tmpLhs else None
                    tmpRhs = (
                        cond.split("=")[1]
                        if len(cond.split("=")) > 1
                        else cond.split(" in ")[1]
                    )
                    if tmpRhs[0] == "(":
                        tmpRhs = eval(tmpRhs)
                    rhs = tmpRhs if "." in tmpRhs else None

                    tmpTupleR = tupleR
                    tmpTupleS = tupleS
                    swapFlag = False
                    if lhs.split(".")[0] != relationRName:
                        tmpLhs, tmpRhs = tmpRhs, tmpLhs
                        lhs, rhs = rhs, lhs
                        tmpTupleR, tmpTupleS = tmpTupleS, tmpTupleR
                        swapFlag = True

                    lhsIdx = (
                        self.relationInfo[lhs.split(".")[0]][lhs.split(".")[1]]
                        if lhs != None
                        else None
                    )
                    # 0
                    rhsIdx = (
                        self.relationInfo[rhs.split(".")[0]][rhs.split(".")[1]]
                        if rhs != None
                        else None
                    )
                    if swapFlag:
                        lhsIdx, rhsIdx = rhsIdx, lhsIdx

                    if (
                        (
                            rhsIdx != None
                            and str(tmpTupleR[lhsIdx]) == str(tmpTupleS[rhsIdx])
                        )
                        or (swapFlag and str(tmpTupleR[lhsIdx]) == str(tmpLhs))
                        or (str(tmpTupleR[lhsIdx]) == str(tmpRhs))
                        or (type(tmpRhs) == tuple and int(tmpTupleR[lhsIdx]) in tmpRhs)
                        or (
                            swapFlag
                            and type(tmpLhs) == tuple
                            and int(tmpTupleR[lhsIdx]) in tmpLhs
                        )
                    ):
                        j += 1
                        result.append(tupleR + tupleS)
                        continue
                    
                    
                    if ( not (
                            rhsIdx != None
                            and str(tmpTupleR[lhsIdx]) == str(tmpTupleS[rhsIdx])
                        )
                        or (swapFlag and str(tmpTupleR[lhsIdx]) == str(tmpLhs))
                        or (str(tmpTupleR[lhsIdx]) == str(tmpRhs))
                        or (type(tmpRhs) == tuple and int(tmpTupleR[lhsIdx]) in tmpRhs)
                        or (
                            swapFlag
                            and type(tmpLhs) == tuple
                            and int(tmpTupleR[lhsIdx]) in tmpLhs
                        )):
                        isValid = False
                        break
                if not isValid:
                    j += 1
                    continue
            i += 1
        

        idxList = [
            self.joinRelationInfo[relation + ".ann"] for relation in self.relationList
        ]

        # computing the annotated bucket
        for i in range(len(result)):
            bucket = []
            for idx in idxList:
                bucket.append(result[i][idx])
            result[i] = result[i] + tuple([".".join(map(str, bucket))])
            result[i] = ",".join(map(str, result[i]))

        print("Time taken for optimized sort based join: ", pc() - t0)
        return result