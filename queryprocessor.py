import itertools

class QProcessor:
    project = []
    clauses = []
    relationList = []
    relationInfo = {}
    joinRelationInfo = {}

    def displayTokens(self):
        print("Projection List: ", self.project)
        print("Clause List: ", self.clauses)
        print("Relation List: ", self.relationList)
        print("RelationInfo: ", self.relationInfo)

    def findRelation(self, column) -> str:
        for i in self.relationInfo.keys():
            if column in self.relationInfo[i]:
                return i
        return ""

    def validateQuery():
        return

    def tokenizeQuery(self, query):
        query = query.lower().strip(";")

        # projections
        self.project.extend(
            [i.strip(" ") for i in query.split("from")[0].lstrip("select ").split(",")]
        )

        # where clauses
        self.clauses.extend(
            [i.strip(" ") for i in query.split("where")[1].strip(" ").split(" ")]
        )

        # relation list
        for relation in query.split("from")[1].split("where")[0].split(","):
            self.relationList.append(relation.strip(" "))

        return

    def processJoin(self, conn, relationList):
        result = []
        relationDataDict = {}
        cursor = conn.cursor()

        # fetching data from postgresql
        for relation in relationList:
            query = """select * from """
            cursor.execute(query + relation)
            relationdata = cursor.fetchall()
            relationColData = {
                ele: pos for pos, ele in enumerate([desc[0] for desc in cursor.description])
            }
            self.relationInfo[relation] = relationColData
            relationDataDict[relation] = relationdata

        idx = 0
        # updating self.joinRelationInfo
        for relation, info in self.relationInfo.items():
            for column in info:
                self.joinRelationInfo[relation + '.' + column] = idx
                idx += 1

        # computing the cartesian product
        for tuple in itertools.product(*relationDataDict.values(), repeat=1):
            row = ""
            for item in tuple:
                row += str(item)
            result.append(row.replace(")(", ", "))
        self.displayTokens()
        print(len(result))
        return result

    def processSelectQuery(self, conn, query):
        self.tokenizeQuery(query)

        # processing relation join
        joinResult = []
        if len(self.relationList) > 1:
            joinResult = self.processJoin(conn, self.relationList)

        # processing where clauses
        whereResult = []
        whereResult = self.processWhere(joinResult, self.clauses)
        print(len(whereResult))


        projectionResult = []
        # processing projections
        idxList = []
        flag = True
        for column in self.project:
            idxList.append(
                self.relationInfo[self.findRelation(column)][column]
            ) if flag else idxList.append(
                6 + self.relationInfo[self.findRelation(column)][column]
            )
            flag = not flag
        for row in whereResult:
            tuple = []
            for idx in idxList:
                tuple.append(row[idx])
            projectionResult.append(tuple)
        return projectionResult

    def processWhere(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id']
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']
        i = 0
        conditionList = []
        while i + 3 <= len(clauses):
            if clauses[i] == "and" or clauses[i] == "or":
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
        print("Condition List:" + ",".join(conditionList))
        print("JoinInfo List:",  self.joinRelationInfo)
        print()

        whereResult = []
        operators = ['<', '>', '=']
        for tuple in joinResult:
            tuple = str(tuple).lstrip('(').rstrip(')').split(", ")
            isTupleValid = []
            for i in range(len(conditionList)):
                cond = conditionList[i]
                if cond == "and" or cond == "or":
                    isTupleValid.append(cond)
                    continue
                
                for op in operators:
                    if len(cond.split(op)) > 1:
                        lhs = tuple[self.joinRelationInfo[cond.split(op)[0]]].lower()
                        rhs = tuple[self.joinRelationInfo[cond.split(op)[1]]] if "." in cond.split(op)[1] else cond.split(op)[1].lower()
                        
                        if op == '<':
                            isTupleValid.append(str(lhs < rhs))
                        elif op == '>':
                            isTupleValid.append(str(lhs > rhs))
                        elif op == '=':
                            isTupleValid.append(str(lhs == rhs))
            
            # Single condition case
            if(len(isTupleValid) == 1 and isTupleValid[0] == "True"):
                whereResult.append(tuple)
                continue
            
            # multiple condition case
            isValid = False
            if(isTupleValid[1] == "and"):
                isValid = isTupleValid[0] and isTupleValid[2]
            else:
                isValid = isTupleValid[0] or isTupleValid[2]
            
            for i in range(3, len(isTupleValid)-1):
                if(isTupleValid[i] == "and"):
                    isValid = isValid and isTupleValid[i+1]
                elif(isTupleValid[i] == "or"):
                    isValid = isValid or isTupleValid[i+1]
            if(isValid):
                whereResult.append(tuple)
    
        return whereResult

    def processWhereWithAnd(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']

        return

    def processWhereWithOr(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']

        return
