import threading
import random
import collections

class Abm:
    data_segment = {}
    memoryBus = False   #shows if the memory is in use
    printing = False    #shows if one core is generating output
    cacheSize = 2       #number of cache blocks

    def __init__(self):
        self.name = ""
        self.code = {}
        self.functions = {}
        self.end = False
        self.pc = 0
        self.stack = []
        self.previous_frames = []
        self.current_frame = {}
        self.call_type = "normal"
        self.returnAdd = []
        self.write_to_file = ""
        self.pointers = {}  #indicates what variable points to what memory

        self.cache = collections.defaultdict(dict)  #initialize as dictionary of dictionaries
        self.cacheUsed = 0  #number of cache blocks occupied

    def read_file(self, file):
        self.name = file 
        f = open(self.name, 'r')

        for i, j in enumerate(f):
            if j.strip().partition(' ')[0] == ".int":
                for x in j.strip().split(' ', 1)[1].split(" "):

                    while self.memoryBus:
                        pass

                    self.memoryBus = True
                    self.data_segment[x] = 0    #if instruction begins with .int, create variables in the data segment
                    self.memoryBus = False
            else:
                if not(j.strip().partition(' ')[0] == ".data" or j.strip().partition(' ')[0] == ".text"):   #ignore .data and .text keywords
                    self.code[i] = j.strip()    #store instruction
                    if self.code[i].partition(' ')[0] == "label":
                        self.functions[self.code[i].partition(' ')[2]] = i  #store label

        self.pc = list(self.code.keys())[0]     #set program counter to the line number of the first instruction after .text

    def classify(self, i):
        if (i == "push" or i == "rvalue" or i == "lvalue" or i == "pop" or i == ":=" or i == "copy" or i == ":&"):
            return 0

        if (i == "goto" or i == "gofalse" or i == "gotrue" or i == "halt"):
            return 1

        if (i == "+" or i == "-" or i == "*" or i == "/" or i == "div"):
            return 2

        if (i == "&" or i == "!" or i == "!"):
            return 2

        if (i == "<>" or i == "<=" or i == ">=" or i == "<" or i == ">" or i == "="):
            return 2

        if (i == "print" or i == "show"):
            return 3

        if (i == "begin" or i == "end" or i == "return" or i == "call"):
            return 4

    def loop(self):
        while(not(self.end)):
            opcode = self.classify(self.code[self.pc].partition(' ')[0])
            if opcode == 0:
                self.stack_manipulation(self.code[self.pc])
            if opcode == 1:
                self.control(self.code[self.pc])
            if opcode == 2:
                self.calculations(self.code[self.pc].partition(' ')[0])
            if opcode == 3:
                self.output(self.code[self.pc])
            if opcode == 4:
                self.subprogram(self.code[self.pc])
                
            self.pc = self.pc + 1


        while self.memoryBus:
            pass

        self.memoryBus = True

        for key in self.cache.keys():
            if self.cache[key]["modified"] == 1 and not(self.cache[key]["invalid"] == 1):   #at the end, write back modified and valid cache blocks
                self.data_segment[key] = self.cache[key]["value"]
        
        self.memoryBus = False

        while self.printing:    #if another core is printing, wait
            pass

        self.printing = True

        print(self.write_to_file)
        f = open(self.name[:-4] + ".out", "w")  #open file in write mode
        f.write(self.write_to_file)

        self.printing = False

    def stack_manipulation(self, i):
        funct = i.partition(' ')[0]
        if funct == "push":
            self.stack.append(i.partition(' ')[2])

        if funct == "rvalue":
            if i.partition(' ')[2] in self.cache.keys() and self.cache[i.partition(' ')[2]]["invalid"] == 0:    #if variable is in cache and valid
                self.stack.append(self.cache[i.partition(' ')[2]]["value"])     #fetch from cache

            elif i.partition(' ')[2] in self.data_segment.keys():     #if the variable exists in the data segment, fetch value from there
                while self.memoryBus:   #if memory is in use, wait
                    pass
                
                self.memoryBus = True   #mark the memory bus as busy
                self.stack.append(self.data_segment[i.partition(' ')[2]])

                if self.cacheUsed >= self.cacheSize and not(i.partition(' ')[2] in self.cache.keys()):    #if cache is full, remove a random block
                    random_block = random.choice(list(self.cache.keys()))
                    if self.cache[random_block]["modified"] == 1:   #if that block has modified flag on, write back
                        self.data_segment[random_block] = self.cache[random_block]["value"]

                    del(self.cache[random_block])   #delete block
                    self.cacheUsed -= 1     #update cache size

                self.cache[i.partition(' ')[2]]["value"] =  self.data_segment[i.partition(' ')[2]]  #add block to cache
                self.cache[i.partition(' ')[2]]["modified"] = 0
                self.cache[i.partition(' ')[2]]["shared"] = 0   #will always be 0 since cache is read-write in both cores
                self.cache[i.partition(' ')[2]]["invalid"] = 0

                self.cacheUsed += 1     #set cache size

                self.memoryBus = False

            elif i.partition(' ')[2] in self.pointers.keys():       #if the variable is a pointer, get the variable name it points to
               self.stack.append(self.pointers[i.partition(' ')[2]])

            else:
                temp = {}
                if self.call_type == "begin":
                    temp = self.current_frame
                    self.current_frame = self.previous_frames[-1]   #move to previous frame

                if i.partition(' ')[2] not in self.current_frame:
                    self.current_frame[i.partition(' ')[2]] = 0

                self.stack.append(self.current_frame[i.partition(' ')[2]])

                if self.call_type == "begin":
                    self.current_frame = temp   #restore frame

        if funct == "lvalue":
            self.stack.append(i.partition(' ')[2])
            
        if funct == "pop":
            self.stack.pop()

        if funct == ":=":           #if not in mem set invalid
            val = self.stack.pop()
            var = self.stack.pop()

            if var in self.data_segment.keys():     #if variable is global, initialize value there
                while self.memoryBus:
                    pass

                self.memoryBus = True

                if var in self.cache:
                    self.cache[var]["value"] = val      #if variable is in cache, update value and set modified flag
                    self.cache[var]["modified"] = 1
                else:
                    self.data_segment[var] = val        #else update in memory

                self.memoryBus = False

            else:
                temp = {}
                if self.call_type == "return":
                    temp = self.current_frame
                    self.current_frame = self.previous_frames[-1]   #move to previous frame
                
                if var in self.cache:
                    self.cache[var]["value"] = val
                    self.cache[var]["modified"] = 1 
                else:
                    self.current_frame[var] = val

                if self.call_type == "return":
                    self.current_frame = temp   #restore frame


            if not(var in self.cache):      #if variable is not in cache and there is space in the cache, create an instance of the variable
                if self.cacheUsed < self.cacheSize:
                    self.cache[var]["value"] =  0
                    self.cache[var]["modified"] = 0
                    self.cache[var]["shared"] = 0
                    self.cache[var]["invalid"] = 1
                    self.cacheUsed += 1

        if funct == "copy":
            self.stack.append(self.stack[-1])

        if funct == ":&":
            globl = self.stack.pop()
            local = self.stack.pop()

            self.pointers[local] = globl    #set local variable to the address of global variable

    def calculations(self, i):
        if i == "!":
            self.stack.append(int(not(self.stack.pop())))

        else:
            op1 = int(self.stack.pop())
            op2 = self.stack.pop()

            if i == "+":
                if op2.isnumeric():
                    self.stack.append(op1 + int(op2))
                else:       #if operand is a variable name i.e. address
                    self.stack.append(list(self.data_segment)[(list(self.data_segment.keys()).index(op2)+op1)])     #find index of variable and increment it, find the name of the variable at the new index

            if i == "-":
                if op2.isnumeric():
                    self.stack.append(int(op2) - op1)
                else:
                    self.stack.append(list(self.data_segment)[(list(self.data_segment.keys()).index(op2)-op1)])

            if op2.isnumeric():
                op2 = int(op2)      #if operand 2 is numeric, cast to int
                if i == "*":
                    self.stack.append(op1 * op2)
                if i == "/":
                    self.stack.append(int(op2 / op1))
                if i == "div":
                    self.stack.append(op2 % op1)
                if i == "&":
                    self.stack.append(op1 & op2)
                if i == "|":
                    self.stack.append(op1 | op2)
                if i == "<>":
                    self.stack.append(int(op1 != op2))
                if i == "<=":
                    self.stack.append(int(op2 <= op1))
                if i == ">=":
                    self.stack.append(int(op2 >= op1))
                if i == "<":
                    self.stack.append(int(op2 < op1))
                if i == ">":
                    self.stack.append(int(op2 > op1))
                if i == "=":
                    self.stack.append(int(op1 == op2))

    def output(self, i):
        if i.partition(' ')[0] == "print":
            self.write_to_file += str(self.stack[-1])   #concatenate output string

        if i.partition(' ')[0] == "show":
            self.write_to_file += i.partition(" ")[2].lstrip()

        self.write_to_file += "\n"  #embed newlines

    def control(self, i):
        if i.partition(' ')[0] == "goto":
            self.pc = self.functions[i.partition(' ')[2]]

        if i.partition(' ')[0] == "gotrue":
            if self.stack[-1] == 1: #check top value of stack
                self.pc = self.functions[i.partition(' ')[2]]

        if i.partition(' ')[0] == "gofalse":
            if self.stack[-1] == 0:
                self.pc = self.functions[i.partition(' ')[2]]

        if i.partition(' ')[0] == "halt":
            self.end = True

    def subprogram(self, i):
        if i.partition(' ')[0] == "begin":
            self.call_type = "begin" 
            self.previous_frames.append(self.current_frame) #save existing frame
            self.current_frame = {} #create new frame

        if i.partition(' ')[0] == "end":
            self.call_type = "normal"
            self.current_frame = self.previous_frames.pop() #delete frame

        if i.partition(' ')[0] == "return":
            self.call_type = "return"
            self.pc = self.returnAdd.pop()  #return to calling function

        if i.partition(' ')[0] == "call":
            self.call_type = "normal"
            self.returnAdd.append(self.pc)  #save return address
            self.pc = self.functions[i.partition(' ')[2]]   #jumo to function

a = Abm()
a1 = Abm()
a.read_file("test1forP2.abm")
a1.read_file("test1forP2.abm")

t1 = threading.Thread(target=a.loop)
t2 = threading.Thread(target=a1.loop)
 
t1.start()
t2.start()
 
t1.join()
t2.join()

#print(a.data_segment)
#a.data_segment["d1"] = 5       #test to show shared memory
#print(a1.data_segment)