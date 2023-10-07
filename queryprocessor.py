class QProcessor:
    project = []
    clauses = []
    relationList = []

    def displayTokens(self):
        print("Projection List: ", self.project)
        print("Clause List: ", self.clauses)
        print("Relation List: ", self.relationList)

    def validateQuery():
        return

    def processSelectQuery(self, query):
        query = query.lower()
        # select a,b,c from R,S where cond1 and cond2
        self.project.extend(query.split("from")[0].split(" ")[1].split(","))
        self.clauses.extend(query.split("where")[1].strip(" ").split(" "))

        for relation in query.split("from")[1].split("where")[0].split(","):
            self.relationList.append(relation.strip(' '))
        return

    def process_join():
        return

    def where():
        return
