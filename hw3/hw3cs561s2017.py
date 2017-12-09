"""
AI Homework #3: Decision Network
Author: Wei-Chi Chen (Vic), uscid: 8206528808
"""
import copy
import time

DBG = False  # Debug_Flag
DBG2 = False
DBG3 = False
DBG4 = False  # Input Check
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
D_NODE = "decision"
S_LINE = "******"
N_LINE = "***"
T_PROB = 1.0
F_PROB = 0.0
NODE_D = 'D'
NODE_P = 'P'
NODE_U = 'U'


class DecisionNetwork:

    mRequestType = []
    mRequestQuery = []
    mRequestEvidence = []
    mDecisionNode = []

    def __init__(self, bn):
        self.bn = bn
        self.initialStatus()

    def initialStatus(self):
        input_file = open(INPUT_FILE, "r")

        self.parseQuery(input_file)
        self.parseNode(input_file)
        if DBG4: print "Decision nodes: %s" % self.mDecisionNode
        self.parseUtility(input_file)

        input_file.close()

    def parseQuery(self, input_file):
        tmpStr = input_file.readline().rstrip('\r\n')

        while tmpStr:
            if tmpStr == S_LINE:
                break
            if DBG4: print "--------"
            tmplist = tmpStr.split('(')
            self.mRequestType.append(tmplist[0])
            if DBG4: print tmplist
            tmpQE = tmplist[1].split(')')  # leave tmpQE[0]: Q | E
            tmpQE = tmpQE[0].split(' | ')   # tmpQE[0]: Q, tmpQE[1]: E
            if DBG4: print tmpQE[0]
            # input query children
            self.mRequestQuery.append(tmpQE[0].split(', '))
            # input query parents
            if len(tmpQE) == 2:
                evi = tmpQE[1].split(', ')
                if DBG4: print evi
                self.mRequestEvidence.append(evi)
            else:
                self.mRequestEvidence.append([])
            tmpStr = input_file.readline().rstrip('\r\n')

        if DBG4:
            print "Query:%s" % self.mRequestType
            print self.mRequestQuery
            print self.mRequestEvidence

    def parseNode(self, input_file):
        if DBG4: print "Nodes:"
        tmpStr = input_file.readline().rstrip('\r\n')
        while tmpStr:
            if tmpStr == S_LINE:
                break
            if DBG4: print "--------"
            # node header
            header = tmpStr.split(" | ")
            if len(header) == 1:
                # P(x) doesn't have parents or D(x)
                tmpStr = input_file.readline().rstrip('\r\n')
                if tmpStr == D_NODE:
                    # set d node
                    if DBG4: print "node: %s, %s" % (header[0], tmpStr)
                    cpt = {(): 0.5}  # tmp set decision node = 0.5
                    node_type = NODE_D
                    self.mDecisionNode.append(header[0])
                else:
                    # set p node
                    if DBG4: print "node: %s, %s" % (header[0], tmpStr)
                    cpt = {(): float(tmpStr)}
                    node_type = NODE_P

                if DBG4: print cpt
                self.setNode(header[0], [], cpt, node_type)

                tmpStr = input_file.readline().rstrip('\r\n')
                if tmpStr == N_LINE:
                    tmpStr = input_file.readline().rstrip('\r\n')
                    continue

                # re-start loop to next node

            else:
                # set p node with parent
                if DBG4: print "Node: %s" % tmpStr
                parents = header[1].split()
                if DBG4: print "parents: %s" % parents

                tmpStr = input_file.readline().rstrip('\r\n')
                cpt = {}

            while tmpStr:
                # deal with the probability info
                info = tmpStr.split()
                prob = float(info[0])
                parentState = info[1:]
                parentState = tuple(parentState)
                # build cpt
                cpt[parentState] = prob

                if DBG4: print prob, parentState

                # next line
                tmpStr = input_file.readline().rstrip('\r\n')
                if tmpStr == N_LINE:
                    if DBG4: print "cpt: %s" % cpt
                    self.setNode(header[0], parents, cpt)
                    break
                if tmpStr == S_LINE or not tmpStr:
                    if DBG4: print "cpt: %s" % cpt
                    self.setNode(header[0], parents, cpt)
                    # end of parseNode
                    return

            # next node
            tmpStr = input_file.readline().rstrip('\r\n')

    def parseUtility(self, input_file):
        tmpStr = input_file.readline().rstrip('\r\n')
        if not tmpStr: return
        if DBG4: print "--------"
        if DBG4: print tmpStr
        header = tmpStr.split(" | ")
        parents = header[1].split()
        tmpStr = input_file.readline().rstrip('\r\n')
        cpt = {}

        while tmpStr:
            row = tmpStr.split()
            value = row[0]
            parentsState = row[1:]
            parentsState = tuple(parentsState)
            if DBG4: print "%s:%s" % (value, parentsState)

            # build cpt
            cpt[parentsState] = value

            tmpStr = input_file.readline().rstrip('\r\n')

        node_specs = []
        node_type = NODE_U
        node_specs.append(header[0])
        node_specs.append(parents)
        node_specs.append(cpt)
        node_specs.append(node_type)
        self.bn.setUtility(node_specs)

        if DBG4: print "Utility: %s" % self.bn.mUnode

        return

    def setNode(self, var, parents, cpt, node_type='P'):
        """Pack variables to node_spec, than add it to BN"""
        node_spec = []
        node_spec.append(var)
        node_spec.append(parents)
        node_spec.append(cpt)
        node_spec.append(node_type)
        self.bn.add(node_spec)
        return

    def solveQuery(self):
        output_file = open(OUTPUT_FILE, "w")
        while not len(self.mRequestType) == 0:
            if DBG: print "Solve: %s(%s | %s)" % \
                           (self.mRequestType[0], self.mRequestQuery[0], self.mRequestEvidence[0])

            if self.mRequestType[0] == 'P':
                """ Solve P """
                x = {}
                xv = []
                events = {}
                for q in self.mRequestQuery[0]:
                    tmp = q.split(" = ")
                    x[tmp[0]] = tmp[1]
                    xv.append(tmp[0])
                if DBG3: print "x: %s\nxv: %s" % (x, xv)

                for e in self.mRequestEvidence[0]:
                    tmp = e.split(" = ")
                    events[tmp[0]] = tmp[1]
                if DBG3: print "events: %s" % events

                # set decision nodes
                for i in self.mDecisionNode:
                    node = self.bn.variable_node(i)
                    if i in x:
                        if x[i] == '+':
                            node.cpt = {(): T_PROB}
                        else:
                            node.cpt = {(): F_PROB}
                    if i in events:
                        if events[i] == '+':
                            node.cpt = {(): T_PROB}
                        else:
                            node.cpt = {(): F_PROB}

                    if DBG3: print "set decision node(%s), cpt = %s" % (i, node.cpt)

                # deal with pre_list
                pre_list = pre_ask(xv, x, events, self.bn)

                answer = enumeration_ask(x, events, bn, pre_list, 'P')
                w_str = "%.2f\n" % round(answer+0.0000001, 2)

                if DBG3: print "========"
                # end of P

            elif self.mRequestType[0] == 'EU':
                """ Solve EU()
                Deal with Decision nodes first """
                x = {}
                xv = []
                events = {}

                for q in self.mRequestQuery[0]:
                    tmp = q.split(" = ")
                    x[tmp[0]] = tmp[1]
                    xv.append(tmp[0])
                if DBG3: print "x: %s\nxv: %s" % (x, xv)

                for e in self.mRequestEvidence[0]:
                    tmp = e.split(" = ")
                    events[tmp[0]] = tmp[1]
                if DBG3: print "events: %s" % events

                # Check U node's parents are in query or not
                unode = self.bn.mUnode[0]
                if DBG3: print "unode: %s, %s" % (unode, unode.parents)
                for ps in unode.parents:
                    if ps not in xv:
                        xv.append(ps)
                        x[ps] = '+'  # tmp set to +, we need to deal with + and - in pre_list

                # move decision nodes from query to events
                for d in self.mDecisionNode:
                    if d in xv:
                        events[d] = x[d]
                        xv.remove(d)
                        del(x[d])

                if DBG3: print "new querys: %s\nnew events: %s" % (x, events)

                # set decision nodes
                for i in self.mDecisionNode:
                    node = self.bn.variable_node(i)
                    if i in x:
                        if x[i] == '+':
                            node.cpt = {(): T_PROB}
                        else:
                            node.cpt = {(): F_PROB}
                    if i in events:
                        if events[i] == '+':
                            node.cpt = {(): T_PROB}
                        else:
                            node.cpt = {(): F_PROB}

                # deal with pre_list
                pre_list = pre_ask(xv, x, events, self.bn)

                answer = enumeration_ask(x, events, bn, pre_list, 'EU')
                answer = int(round(answer, 0))
                w_str = "%s\n" % answer
                if DBG3: print "========"
                # end of EU

            elif self.mRequestType[0] == 'MEU':
                """"""
                x = {}
                xv = []
                events = {}
                eu_list = []  # store dict
                eu_value = []

                for q in self.mRequestQuery[0]:
                    tmp = q.split(" = ")
                    xv.append(tmp[0])
                if DBG3: print "xv: %s" % (xv)
                nested_extend({}, xv, eu_list)  # eu_list is EU action candidates
                if DBG3: print "eu_list: %s" % eu_list

                for eu_candidate in eu_list:
                    if DBG3: print "Deal with candidate: %s" % eu_candidate
                    for k in eu_candidate.keys():
                        x[k] = eu_candidate[k] # temp set to '+'
                    if DBG3: print "x: %s\nxv: %s" % (x, xv)

                    for e in self.mRequestEvidence[0]:
                        tmp = e.split(" = ")
                        events[tmp[0]] = tmp[1]
                    if DBG3: print "events: %s" % events

                    copy_x = copy.deepcopy(x)
                    copy_xv = copy.deepcopy(xv)
                    copy_events = copy.deepcopy(events)

                    # Check U node's parents are in query or not
                    unode = self.bn.mUnode[0]
                    if DBG3: print "unode: %s, %s" % (unode, unode.parents)
                    for ps in unode.parents:
                        if ps not in xv:
                            copy_xv.append(ps)
                            copy_x[ps] = '+'  # tmp set to +, we need to deal with + and - in pre_list

                    # move decision nodes from query to events
                    for d in self.mDecisionNode:
                        if d in copy_xv:
                            copy_events[d] = x[d]
                            copy_xv.remove(d)
                            del(copy_x[d])

                    if DBG3: print "new querys: %s\nnew events: %s" % (copy_x, copy_events)

                    # set decision nodes
                    for i in self.mDecisionNode:
                        node = self.bn.variable_node(i)
                        if i in x:
                            if x[i] == '+':
                                node.cpt = {(): T_PROB}
                            else:
                                node.cpt = {(): F_PROB}
                        if i in events:
                            if events[i] == '+':
                                node.cpt = {(): T_PROB}
                            else:
                                node.cpt = {(): F_PROB}

                    # deal with pre_list
                    pre_list = pre_ask(copy_xv, copy_x, copy_events, self.bn)

                    answer = enumeration_ask(copy_x, copy_events, bn, pre_list, 'EU')
                    eu_value.append(answer)

                meu = eu_value[0]
                for i in range(len(eu_value)):
                    if DBG3: print "action:%s (%s)" % (eu_list[i], eu_value[i])
                    meu = max(meu, eu_value[i])

                # act = eu_value.index(meu)
                act_dict = eu_list[eu_value.index(meu)]

                meu = int(round(meu, 0))
                w_str = ""
                for v in act_dict.values():
                    w_str += v
                    w_str += " "

                w_str += str(meu)
                if DBG3: print "Best action: %s" % w_str
                w_str += "\n"
                if DBG3: print "========"
                # end of MEU


            output_file.write(w_str)

            del(self.mRequestType[0])
            del(self.mRequestQuery[0])
            del(self.mRequestEvidence[0])

        # end of query, close the file
        output_file.close()


def pre_ask(vars, querys, events, bn):
    pre_list = []  # final use

    nested_extend(events, vars, pre_list)

    if DBG3: print "pre_list: %s item(s)\n%s" % (len(pre_list), pre_list)

    return pre_list


def nested_extend(e, vars, pre_list):
    if len(vars) == 0:
        pre_list.append(e)
        return

    x, rest = vars[0], vars[1:]
    for v in ['+','-']:
        newdict = e.copy()
        newdict[x] = v
        nested_extend(newdict, rest, pre_list)


def enumeration_ask(target_dic, e, bn, pre_list, query_type):

    Q = ProbDist(str(target_dic))
    for xi in pre_list:
        if DBG: print "-------\ndo: %s" % xi
        Q[str(xi)] = enumerate_all(bn.variables, xi, bn)

    Q.normalize()
    goal = dict(e.items() + target_dic.items())
    if DBG3:
        for q in Q.prob:
            print q, Q.prob[q]
    if DBG: print "\nanswer: %.2f\n" % round(Q[str(goal)], 2)

    if query_type == 'P':
        return Q[str(goal)]
    if query_type == 'EU':
        if DBG3: print "calculate EU: %s\nevents: %s" % (target_dic.keys(), e)
        uti_table = bn.mUnode[0].cpt
        if DBG3: print "utility: %s\n%s" % (bn.mUnode[0].parents, uti_table)
        eu_value = 0.0

        for xi in pre_list:
            # find U(xi)
            u_search = []
            for u_col in bn.mUnode[0].parents:
                u_col_value = xi[u_col]
                u_search.append(u_col_value)
            u_search = tuple(u_search)
            if DBG3: print "xi: %s\nu_search: %s, %s" % (xi, u_search, bn.mUnode[0].cpt[u_search])
            eu_value += Q[str(xi)] * (int(bn.mUnode[0].cpt[u_search]))

        # eu_value = int(round(eu_value, 0))
        if DBG3: print "\neu_value: %s" % (int(round(eu_value, 0)))

        """ Return EU """
        return eu_value

    return Q[str(goal)]


def enumerate_all(variables, e, bn):
    """14.2 """
    if DBG3: print "enumerate_all: %s" % variables
    if not variables:
        return 1.0
    Y, rest = variables[0], variables[1:]
    Ynode = bn.variable_node(Y)
    if Y in e:
        answer = Ynode.p(e[Y], e) * enumerate_all(rest, e, bn)
        if DBG3: print "Y in e, answer: %s" % answer
        return answer
    else:
        answer = sum(Ynode.p(y, e) * enumerate_all(rest, extend(e, Y, y), bn)
                     for y in bn.variable_values(Y))
        if DBG3: print "Y not in e, extend Y to e, sum of answers: %s" % answer
        return answer


# Reference and modifications
class BayesNet:

    def __init__(self, node_specs=[]):
        self.nodes = []  # record nodes; list of BayesNode
        self.variables = []  # record how many node "variables" we have
        self.mUnode = []
        for node_spec in node_specs:  # for initialization, but can be empty
            self.add(node_spec)

    def add(self, node_spec):
        """Add a node to the net.
        means parse the node_spec list to different variables
        node_spec[0], node_spec[1], node_spec[2]   -> X, parents, cpt."""
        node = BayesNode(*node_spec)  # means parse the node_spec list to different variables
        self.nodes.append(node)
        self.variables.append(node.variable)

    def setUtility(self, node_spec):
        node = BayesNode(*node_spec)
        self.mUnode.append(node)

    def variable_node(self, var):
        """ Get the node to operate """
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception("No such variable: {}".format(var))

    def variable_values(self, var):
        return ['+', '-']

    def __repr__(self):
        return 'BayesNet({0!r})'.format(self.nodes)


class ProbDist:

    def __init__(self, varname='?', freqs=None):
        self.prob = {}
        self.varname = varname
        self.values = []
        if freqs:
            for (v, p) in freqs.items():
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        """ P(value) """
        try:
            return self.prob[val]
        except KeyError:
            return 0

    def __setitem__(self, val, p):
        """ P(val) = p """
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        total = sum(self.prob.values())
        if DBG3: print "Normalize alpha: %s" % total
        if not isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] /= total
                if DBG3: print val, self.prob[val]
        return self

    def __repr__(self):
        return "P({})".format(self.varname)


class BayesNode:

    def __init__(self, X, parents, cpt, node_type='P'):

        # set type to check
        self.node_type = node_type

        if isinstance(parents, str):
            parents = parents.split()

        # We store the table always in the third form above.
        if isinstance(cpt, (float, int)):  # no parents, 0-tuple
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            # one parent, 1-tuple
            if cpt and isinstance(list(cpt.keys())[0], str):
                cpt = {(v,): p for v, p in cpt.items()}

        self.variable = X
        self.parents = parents
        self.cpt = cpt

    def p(self, value, event):
        pOfTrue = self.cpt[event_values(event, self.parents)]
        pOfTrue = pOfTrue if value == '+' else 1 - pOfTrue
        if DBG3: print "node: %s, p(%s):%s" % (self.variable, value, pOfTrue)
        return pOfTrue

    def __repr__(self):
        return repr((self.variable, ' '.join(self.parents)))


def event_values(e, vars):
    if DBG3: print "[event_values]\nevent %s\nparents: %s" % (e, vars)
    if isinstance(e, tuple) and len(e) == len(vars):
        return e
    else:
        return_value = tuple([e[var] for var in vars])
        if DBG3: print return_value
        return return_value


def extend(s, var, val):
    s1 = s.copy()
    s1[var] = val
    return s1


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
# end of reference

# main flow started
start_time = time.time()
bn = BayesNet()
dw = DecisionNetwork(bn)
if DBG3: print "\n%s\n" % dw.bn
dw.solveQuery()

spend_time = time.time() - start_time
print "Total spend_time: %s" % str(spend_time)