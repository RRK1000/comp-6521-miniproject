import itertools
from time import perf_counter as pc


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
        return result
    
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


    def processSelectQuery(self, conn, query) -> list:
        t0 = pc()

        self.tokenizeQuery(query)

        # processing relation join
        joinResult = []
        if len(self.relationList) > 1:
            joinResult = self.processJoin(conn, self.relationList)
        self.displayTokens()

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
            tuple = []
            for idx in idxList:
                tuple.append(row[idx])
            tuple.append(str(row[len(row) - 1]))
            projectionResult.append(tuple)

        self.selectQueryTime = pc() - t0
        return projectionResult

    