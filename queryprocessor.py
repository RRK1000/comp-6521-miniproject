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
        query = query.lower().strip(";")
        self.project.extend([i.strip(" ") for i in query.split("from")[0].lstrip("select ").split(",")])
        self.clauses.extend([i.strip(" ") for i in query.split("where")[1].strip(" ").split(" ")])

        for relation in query.split("from")[1].split("where")[0].split(","):
            self.relationList.append(relation.strip(' '))
        return

    def process_join():
        return

    def where():
        return
