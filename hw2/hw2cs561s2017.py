"""
AI Homework #2: Wedding Seating Arrangement
Author: Wei-Chi Chen (Vic), uscid: 8206528808
"""
import copy
import random
import time
DBG = True  # Debug_Flag
DBG2 = True
DBG3 = False
DBG4 = False
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
POSSIBILITY = 0.5
MAX_FLIP = 100000
REDUCED_RULE = False
LIMITED_PL = True
LIMITED_C = 1000
ASSUME_G1 = False
SKIP_PL = True


# start of class WeddingSeatingArrangement
class WeddingSeatingArrangement:

    # Params of Walk_SAT
    poss = POSSIBILITY
    max_flips = MAX_FLIP

    # KB
    mGuestNum = 0
    mTableNum = 0
    mIsSatisfied = True
    mIsInputValid = True
    mTruthTable = []  # [man+1][table+1] which is easy to map to symbols
    KB = []  # list of lists, collect clauses

    def __init__(self):
        self.initialStatus()
        if self.mIsInputValid:
            self.initialTruthTable()

    def initialStatus(self):
        input_file = open(INPUT_FILE, "r")
        tmp = input_file.readline()
        tmp = tmp.split()
        self.mGuestNum = int(tmp[0])
        self.mTableNum = int(tmp[1])
        if DBG: print "Guests:%s Tables:%s" % (self.mGuestNum, self.mTableNum)
        if self.mGuestNum < 1 or self.mTableNum < 1:
            self.mIsInputValid = False
            return

        tmp = input_file.readline()
        while tmp:
            tmp = tmp.split()
            guest1 = tmp[0]
            guest2 = tmp[1]
            relation = tmp[2]
            if DBG:
                print "g1: %s, g2: %s, relation:%s" % (guest1, guest2, relation)
            if tmp[2] == "F":
                # rule2
                self.buildRuleF(guest1, guest2)
            elif tmp[2] == "E":
                # rule3
                self.buildRuleE(guest1, guest2)
            # next loop
            tmp = input_file.readline()

        # rule1, set the rule1 and symbols to KB
        self.buildRuleI()
        input_file.close()
        if DBG:
            self.dumpKB()
        return

    def initialTruthTable(self):
        for i in range(0, self.mGuestNum+1, 1):
            self.mTruthTable.append([])
            for j in range(0, self.mTableNum+1, 1):
                self.mTruthTable[i].append(False)
        return

    def outputResult(self):
        # output board
        output_file = open(OUTPUT_FILE, "w")

        if self.mIsSatisfied or DBG4:
            output_file.write("yes\n")
            # print result set
            seat = self.getSeatAssignment()
            for i in range(1, self.mGuestNum+1, 1):
                w_str = str(i) + " " + str(seat[i]) + "\n"
                output_file.write(w_str)
        else:
            output_file.write("no\n")

        output_file.close()
        return

    def pl_resolution(self):
        tmpClauses = copy.deepcopy(self.KB)
        tmpClauses = self.discardRepeatSentences(tmpClauses)
        clauses = copy.deepcopy(tmpClauses)
        new = []
        count = 1
        while True:
            if DBG3: print "loop: %s, clauses num:%s" % (str(count), len(clauses))
            if LIMITED_PL and len(clauses) > LIMITED_C:
                if DBG3: print "Over limited clauses number, guess it's satisfied!"
                self.mIsSatisfied = True
                return self.mIsSatisfied
            count += 1
            start_time = time.time()

            # Resolute and generate new clauses
            for i in range(0, len(clauses), 1):
                for j in range(i+1, len(clauses), 1):
                    resolvents = self.pl_resolve(clauses[i], clauses[j])
                    if ["empty"] in resolvents:
                        self.mIsSatisfied = False
                        return self.mIsSatisfied
                    if len(resolvents):
                        new.extend(resolvents)

            new.sort()
            tmpClauses = self.discardRepeatSentences(new)

            if DBG3: print "after pl, reduce_new:%s, new:%s, clauses:%s" % (str(len(tmpClauses)), str(len(new)), str(len(clauses)))
            new = copy.deepcopy(tmpClauses)  # restore reduced_new

            # Check if new is subset of clauses
            if len(new) <= len(clauses):
                if self.checkIncludeSet(new, clauses):
                    self.mIsSatisfied = True
                    return self.mIsSatisfied
            clauses.extend(new)
            if DBG:
                print "Union KB and new"
                print clauses
            tmpClauses = self.discardRepeatSentences(clauses)
            if DBG3: print "after reduce union, reduced_union:%s, orig_clauses:%s" % (str(len(tmpClauses)), str(len(clauses)))

            # reduce
            if REDUCED_RULE:
                tmpClauses = self.reduceUnitRule(tmpClauses)
                if ["empty"] in tmpClauses:
                    if DBG3: print "reduce a empty clause!"
                    if DBG: print tmpClauses
                    self.mIsSatisfied = False
                    return self.mIsSatisfied

            clauses = copy.deepcopy(tmpClauses)
            clauses.sort()
            new = []
            if DBG3: print "loop end, len(KB):%s" % (str(len(clauses)))
            if DBG: print clauses
            spend_time = time.time() - start_time
            if DBG3: print "spend_time: %s" % str(spend_time)

    def pl_resolve(self, c1, c2):
        resolvents = []
        if DBG2:
            print "pl-resolve"
            print "c1" + str(c1)
            print "c2" + str(c2)
        for literal in c1:
            objc1 = copy.deepcopy(c1)
            objc2 = copy.deepcopy(c2)
            # if DBG: print "symbol:" + literal, type(literal) is str
            if literal[0] == "+":
                searchComplementary = "-" + literal[1:len(literal)]
            else:
                searchComplementary = "+" + literal[1:len(literal)]
            if DBG2: print "symbol:" + literal + "comp:" + searchComplementary
            if searchComplementary in c2:
                objc1.remove(literal)
                objc2.remove(searchComplementary)
                if DBG2:
                    print "after remove comp."
                    print objc1
                    print objc2
                res = []
                if len(objc1) == 0 and len(objc2) == 0:
                    res.append("empty")
                    if DBG3:
                        print c1
                        print c2
                    if DBG3:
                        print "!!!find empty clause!!!"
                    resolvents.append(res)
                    return resolvents
                else:
                    res.extend(objc1)
                    res.extend(objc2)
                if DBG2:
                    print "new clause:" + str(res)
                res = self.discardTautology(res)
                if not res == []:
                    res.sort()
                    resolvents.append(res)
                    # return resolvents  # only one resolvent could be derived

        if DBG2 and len(resolvents) != 0:
            print "resolvents:"
            print resolvents

        return resolvents

    def discardTautology(self, clause):
        refineClause = []
        for literal in clause:
            # if DBG2: print "symbol:" + literal
            if literal[0] == "+":
                searchComplementary = "-" + literal[1:len(literal)]
            else:
                searchComplementary = "+" + literal[1:len(literal)]
            if searchComplementary in clause:
                # if there are complementary, return [] because it's always true, discard
                refineClause = []
                return refineClause

            if (searchComplementary not in clause) and (literal not in refineClause):
                # if there are no comp., discard the repeat symbol
                refineClause.append(literal)

        return refineClause

    def discardRepeatSentences(self, clauses):
        tmpClauses = copy.deepcopy(clauses)
        refineClauses = []
        while not len(tmpClauses) == 0:
            clause = tmpClauses.pop()
            if clause not in refineClauses:
                refineClauses.append(clause)

        # refineClauses = self.reduceUnitRule(refineClauses)

        return refineClauses

    def reduceUnitRule(self, clauses):
        if DBG: print "reduceUnitRule"
        tmpClauses = copy.deepcopy(clauses)
        refineClauses = []
        newClauses = []
        unitClauses = []
        compClauses = []
        # find Unit symbol
        for findUnit in tmpClauses:
            if len(findUnit) == 1:  # find unit symbol
                findUnitStr = findUnit[0]

                if findUnitStr[0] == "+":
                    compUnitStr = "-" + findUnitStr[1:]
                else:
                    compUnitStr = "+" + findUnitStr[1:]

                compUnit = []
                compUnit.append(compUnitStr)
                if compUnit in tmpClauses:
                    # Could be empty set!
                    if DBG2: print "There may be empty set!"
                    refineClauses.append(["empty"])
                    return refineClauses

                unitClauses.append(findUnit)
                compClauses.append(compUnit)

        if DBG:
            print "unit clauses:" + str(unitClauses)
            print "comp clauses:" + str(compClauses)


        # Unit Rule
        for chk_clause in tmpClauses:
            if DBG:
                print "chk_clause:" + str(chk_clause)
            thisClause = copy.deepcopy(chk_clause)
            ignore = False
            for i in range(len(unitClauses)):
                findUnit = unitClauses[i]
                compUnit = compClauses[i]
                findUnitStr = str(findUnit[0])
                compUnitStr = str(compUnit[0])
                if DBG:
                    print "check unit:" + findUnitStr + " | check compUnit:" + compUnitStr

                if findUnitStr in chk_clause:
                    # The clause must be true
                    if DBG: print "remove clause:" + str(chk_clause)
                    ignore = True
                    break
                elif compUnitStr in chk_clause:
                    print chk_clause
                    print thisClause
                    print compUnitStr
                    thisClause.remove(compUnitStr)

                    if DBG:
                        print "reduce comp:" + str(chk_clause)
                    if thisClause == []:  # contradiction
                        if DBG: print "There may be empty set!"
                        thisClause.append('empty')

            if not ignore:
                newClauses.append(thisClause)

            if DBG:
                print "after check unit:"
                print tmpClauses
                print newClauses

            refineClauses = copy.deepcopy(newClauses)

        return refineClauses

    def checkIncludeSet(self, new, old):
        for item in new:
            if item not in old:
                if DBG: print "new not in clauses"
                return False

        return True

    def walk_sat(self):
        clauses = self.KB
        poss = self.poss
        max_flips = self.max_flips
        self.randomInitialGuess()


        for count in range(max_flips):
            # Check Model
            unsatisfiedClauses = self.checkClausesSatisfaction(clauses)
            if unsatisfiedClauses == []:
                # Satisfy!
                if DBG3: print "Model is correct!"
                return

            random_clause = self.randomChooseClauses(unsatisfiedClauses)

            if random.random() < poss:
                # random flip in clause
                select_index = random.randint(0, len(random_clause) - 1)
                random_literal = random_clause[select_index]
                self.flipSymbolBool(random_literal)
            else:
                # maximize the satisfaction
                self.flipSymbolInClauseMaximizesNumberSatisfiedClauses(random_clause, clauses)

        if DBG3: print "Running out the count! Answer may not exist"
        self.mIsSatisfied = False;

        return

    def getSeatAssignment(self):
        seatAssignment = [0]*(self.mGuestNum+1)

        for i in range(1, self.mGuestNum+1, 1):
            try:
                seatAssignment[i] = self.mTruthTable[i].index(True)
            except:
                seatAssignment[i] = 0

        if DBG3: print seatAssignment

        return seatAssignment

    def randomInitialGuess(self):
        """
        truth_table[m+1][n+1]
        """
        for i in range(1, self.mGuestNum+1, 1):
            set_table = random.randint(1, self.mTableNum)
            self.mTruthTable[i][set_table] = True

        if DBG: print self.mTruthTable
        return

    def randomChooseClauses(self, clauses):
        select_index = random.randint(0, len(clauses)-1)
        clause = clauses[select_index]

        if DBG3:
            print clauses
            print select_index
            print clause

        return clause

    def checkSymbolBool(self, symbol):
        """
        Be careful the input
        :param symbol: str
        :return: the symbol's True/False
        """
        sign = symbol[0]
        sub_symbol = symbol[2:]
        sub_symbol = sub_symbol.split(".")
        guest = int(sub_symbol[0])
        table = int(sub_symbol[1])
        if DBG2: print "%s %s" % (str(guest), str(table))
        if guest > self.mGuestNum or table > self.mTableNum:
            return False

        if sign == "+":
            return self.mTruthTable[guest][table]
        else:
            return (not self.mTruthTable[guest][table])

    def flipSymbolBool(self, symbol):
        sub_symbol = symbol[2:]
        sub_symbol = sub_symbol.split(".")
        guest = int(sub_symbol[0])
        table = int(sub_symbol[1])
        if DBG2: print "%s %s" % (str(guest), str(table))
        self.mTruthTable[guest][table] = not self.mTruthTable[guest][table]
        return

    def checkClausesSatisfaction(self, clauses):
        """
        Help the check the satisfaction of clauses
        :param clauses: clauses, e.g. KB
        :return: the unsatisfied clauses, if the unsatisfiedClauses = [], it means all satisfied
        """
        unsatisfiedClauses = []
        if DBG: print "before check:" + str(clauses)

        for clause in clauses:
            isStf = False
            if DBG2: print clause
            for literal in clause:
                if DBG2: print literal
                if self.checkSymbolBool(literal):
                    isStf = True
                    break

            if not isStf:
                unsatisfiedClauses.append(clause)

        if DBG: print "After check:" + str(unsatisfiedClauses)

        return unsatisfiedClauses

    def flipSymbolInClauseMaximizesNumberSatisfiedClauses(self, clause, clauses):
        # holdModel = copy.deepcopy(self.mTruthTable)
        minimumSatisfiedClausesCount = len(clauses)

        for literal in clause:
            self.flipSymbolBool(literal)

            unsatisfiedClauses = self.checkClausesSatisfaction(clauses)
            if len(unsatisfiedClauses) < minimumSatisfiedClausesCount:
                minimumSatisfiedClausesCount = len(unsatisfiedClauses)
                if minimumSatisfiedClausesCount == 0:
                    # all is satisfied!
                    break
            else:
                self.flipSymbolBool(literal)  # flip back

        return

    def buildRuleI(self):
        # everyone could sit only one table
        # symbols ->  X11  -> "+X1.1"
        #            ~X11  -> "-X1.1"

        # rule1.2
        # & [~Xai | ~ Xaj]
        for i in range(1, self.mGuestNum+1, 1):
            for j in range(1, self.mTableNum+1, 1):
                for k in range(j+1, self.mTableNum+1, 1):
                    clause = []
                    symbol = "-X" + str(i) + "." + str(j)
                    clause.append(symbol)
                    symbol = "-X" + str(i) + "." + str(k)
                    clause.append(symbol)
                    clause.sort()
                    self.KB.append(clause)

        # rule1.1
        # | Xai
        for i in range(1, self.mGuestNum+1, 1):
            clause = []
            for j in range(1, self.mTableNum+1, 1):
                symbol = "+X" + str(i) + "." + str(j)
                clause.append(symbol)
            clause.sort()
            self.KB.append(clause)
        # if DBG: self.dumpKB()
        if ASSUME_G1:
            self.KB.append(["+X1.1"])
        return

    def buildRuleF(self, g1, g2):
        # relationship: friend
        for i in range(1, self.mTableNum+1, 1):
            clause = []
            symbol = "-X" + str(g1) + "." + str(i)
            clause.append(symbol)
            symbol = "+X" + str(g2) + "." + str(i)
            clause.append(symbol)
            clause.sort()
            self.KB.append(clause)
            clause = []
            symbol = "+X" + str(g1) + "." + str(i)
            clause.append(symbol)
            symbol = "-X" + str(g2) + "." + str(i)
            clause.append(symbol)
            clause.sort()
            self.KB.append(clause)
        return

    def buildRuleE(self, g1, g2):
        # relationship: enemy
        for i in range(1, self.mTableNum+1, 1):
            clause = []
            symbol = "-X" + str(g1) + "." + str(i)
            clause.append(symbol)
            symbol = "-X" + str(g2) + "." + str(i)
            clause.append(symbol)
            clause.sort()
            self.KB.append(clause)
        return

    def dumpKB(self):
        # dumpKnowledgeBase
        for sentence in self.KB:
            print sentence
        return
# end of class WeddingSeatingArrangement

# main flow started
wsa = WeddingSeatingArrangement()
start_time = time.time()
if wsa.mIsInputValid:
    if SKIP_PL or wsa.pl_resolution():
        if DBG3: print "yes"
        wsa.walk_sat()
    else:
        if DBG3: print "no"
else:
    wsa.mIsSatisfied = False

spend_time = time.time() - start_time
print "Total spend_time: %s" % str(spend_time)

wsa.outputResult()

"""
    def discardRepeatSentences(self, clauses):
        tmpClauses = copy.deepcopy(clauses)
        refineClauses = []
        while not len(tmpClauses) == 0:
            clause = tmpClauses.pop()
            if clause not in refineClauses:
                refineClauses.append(clause)

        return



    def discardRepeatSentences(self, clauses):
        tmpClauses = copy.deepcopy(clauses)
        refineClauses = []
        while not len(tmpClauses) == 0:
            ignore = False
            clause = tmpClauses.pop()
            set_clause = set(clause)
            for chk in tmpClauses:
                set_chk = set(chk)
                if set_clause.issubset(set_chk):
                    ignore = True
                    break
                if set_clause.issuperset(set_chk):
                    tmpClauses.remove(chk)

            if (not ignore) and (clause not in refineClauses):
                refineClauses.append(clause)

        return refineClauses
"""