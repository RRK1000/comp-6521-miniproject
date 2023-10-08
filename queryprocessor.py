class QProcessor:
    project = []
    clauses = []
    relationList = []
    relationInfo = {}

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

        for relation in query.split("from")[1].split("where")[0].split(","):
            self.relationList.append(relation.strip(" "))
        return

    def processJoin(self, conn, relation1, relation2):
        result = []
        cursor = conn.cursor()

        # first relation
        query = """select * from """
        cursor.execute(query + relation1)
        relation1data = cursor.fetchall()
        relation1colData = {
            ele: pos for pos, ele in enumerate([desc[0] for desc in cursor.description])
        }
        self.relationInfo[relation1] = relation1colData

        # second relation
        query = """select * from """
        cursor.execute(query + relation2)
        relation2data = cursor.fetchall()
        relation2colData = {
            ele: pos for pos, ele in enumerate([desc[0] for desc in cursor.description])
        }
        self.relationInfo[relation2] = relation2colData

        for item1 in relation1data:
            for item2 in relation2data:
                result.append(item1 + item2)

        return result

    def processSelectQuery(self, conn, query):
        self.tokenizeQuery(query)

        # processing relation join
        joinResult = []
        if len(self.relationList) > 1:
            joinResult = self.processJoin(
                conn, self.relationList[0], self.relationList[1]
            )

        # for row in joinResult:
        #     print(row)

        # processing where clauses
        whereResult = []
        whereResult = self.processWhere(
            joinResult, self.relationList[0], self.relationList[1], self.clauses
        )

        # processing projections

        return

    def processWhere(self, joinResult, relation1, relation2, clauses):
        # clauses = ['product', '=', 'products.product_id']
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']
        i = 0
        conditionList = []
        while i + 3 <= len(clauses):
            if clauses[i] == "and" or clauses[i] == "or":
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
        print("Condition List:" + " ".join(conditionList))

        whereResult = []
        for tuple in joinResult:
            for condition in conditionList:
                # print("Tuple: ", tuple)
                # print("Condition: ", condition)
                lidx = self.relationInfo[condition.split("=")[0].split(".")[0]][
                    condition.split("=")[0].split(".")[1]
                ]
                ridx = -1
                if "." in condition.split("=")[1]:
                    ridx = len(self.relationInfo[condition.split("=")[0].split(".")[0]])
                    +self.relationInfo[condition.split("=")[1].split(".")[0]][
                        condition.split("=")[1].split(".")[1]
                    ]
                # print("lidx: ", lidx, " ridx: ", ridx)
                # print("Checking: ", tuple[lidx], " = ", condition.split("=")[1] if ridx == -1 else tuple[ridx])
                if tuple[lidx] == (
                    condition.split("=")[1] if ridx == -1 else tuple[ridx]
                ):
                    whereResult.append(tuple)
                    print(tuple)
            # print()
            # print()
        return

    def processWhereWithAnd(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id', 'and', 'region_from', '=', '1']

        return

    def processWhereWithOr(self, joinResult, clauses):
        # clauses = ['product', '=', 'products.product_id', 'or', 'region_from', '=', '1']

        return
