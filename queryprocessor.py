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

    def processSelectQuery(self, conn, query) -> list:
        t0 = pc()

        query = query.replace("\n", "")

        self.tokenizeQuery(query)
        joinResult = self.processJoin(conn, self.relationList, query)

        merged_data = {}

        for item in joinResult:
            key = tuple(item[:-1])
            value = item[-1]
            if key in merged_data:
                merged_data[key] += " + " + value
            else:
                merged_data[key] = value

        joinResult = [list(key) + [values] for key, values in merged_data.items()]

        self.selectQueryTime = pc() - t0
        return joinResult
