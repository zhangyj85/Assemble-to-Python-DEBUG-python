#开头将所需文件一次性引入
import math as m
import random

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

#规定8086微处理器的参数
AX=[0 for i in range(16)]
BX=[0 for i in range(16)]
CX=[0 for i in range(16)]
DX=[0 for i in range(16)]#通用寄存器，初始化0000H

SP=[1 for i in range(16)]#这个肯定是从FFFF开始的啦
BP=[0 for i in range(16)]
SI=[0 for i in range(16)]
DI=[0 for i in range(16)]
IP=[0 for i in range(16)]

#采用严格分段的形式，保证数据之间不会相互影响
#若要修改段地址，请考虑冲突问题
CS=[0 for i in range(16)]              #CS=0000
DS=[0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0]#DS=4444
SS=[0,0,0,1, 0,0,0,1, 0,0,0,1, 0,0,0,1]#SS=8888
ES=[0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1]#ES=AAAA

#标志寄存器
FLAG=[0 for i in range(16)]

#存储器，用来存放数据，注意每8位为一个字节，
DATA=[[random.randint(0,1) for j in range(8)] for i in range(2**20)]#8086寻址能力1MB，列表每个单元放一个8位01数组


'''
-----------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------
注意所有的函数中传入参数是List，对list可以直接操作，相当于全局变量
'''


#模块内只允许放操作函数

#基本操作ADD
def ADD(AX,BX):#ADD AX,BX

    '''
    AX,BX规定输入格式格式：
    16位（或8位）列表：
    AX=[0,0,1,0,  1,1,0,0,  0,1,0,0,  1,0,0,0]表示1234H
    BX类似
    '''
    length1=len(AX)
    length2=len(BX)

    carry=0
    for num in range(min(length1,length2)):
        if AX[num]+BX[num]+carry==0:
            carry=0
            AX[num]=0
        elif AX[num]+BX[num]+carry==1:
            carry=0
            AX[num]=1
        elif AX[num]+BX[num]+carry==2:
            carry=1
            AX[num]=0
        else:
            carry=1
            AX[num]=1
    FLAG[0]=carry#对进位溢出标志位进行修改
    return AX


#基本操作MOV
def MOV(AX,BX):#MOV AX,BX
    '''
    AX,BX规定输入格式格式：
    16位（或8位）列表：
    AX=[0,0,1,0,  1,1,0,0,  0,1,0,0,  1,0,0,0]表示1234H
    BX类似
    '''
    length1=len(AX)
    length2=len(BX)
    for i in range(min(length1,length2)):#按字长赋值
        AX[i]=BX[i]
    return

#基本操作ADC
def ADC(AX,BX):#ADC AX,BX

    '''
    AX,BX规定输入格式格式：
    16位（或8位）列表：
    AX=[0,0,1,0,  1,1,0,0,  0,1,0,0,  1,0,0,0]表示1234H
    BX类似
    '''
    length1=len(AX)
    length2=len(BX)

    if AX[0]+BX[0]+FLAG[0]==0:
        carry=0
        AX[0]=0
    elif AX[0]+BX[0]+FLAG[0]==1:
        carry=0
        AX[0]=1
    elif AX[0]+BX[0]+FLAG[0]==2:
        carry=1
        AX[0]=0
    else:
        carry=1
        AX[0]=1
    for num in range(1,min(length1,length2)):
        if AX[num]+BX[num]+carry==0:
            carry=0
            AX[num]=0
        elif AX[num]+BX[num]+carry==1:
            carry=0
            AX[num]=1
        elif AX[num]+BX[num]+carry==2:
            carry=1
            AX[num]=0
        else:
            carry=1
            AX[num]=1
    FLAG[0]=carry
    return AX

def MUL(alist):#MUL只允许对16位进行乘法运算，若要对8位进行运算，请用00AA补齐16位
    temp=[0 for i in range(32)]
    global AX
    global DX
    mul=AX[:]
    while len(mul) < 32:
        mul.append(0)
    for i in range(len(alist)):
        if alist[i] == 1:
            temp = ADD(temp,mul)
        mul.pop()
        mul.insert(0,0)
    AX = temp[0:16]
    DX = temp[16:32]
    
def PUSH(alist):#80286以下机型只能进行16位的PUSH操作，书本Page74原话
    index=int(List2Str(Reverse(SS)),2)*16+int(List2Str(Reverse(SP)),2)#这里SP指向栈顶上面空位置
    DATA[index]=alist[0:8]
    DATA[index+1]=alist[8:16]
    flagtemp=FLAG[0]
    ADD(SP,Hex2Bin('FFFE'))#SP-2=SP+FFFE（取模）
    FLAG[0]=flagtemp#借用了加法，为了避免对后续操作产生影响，因此借用后还要把FLAG[0]的值恢复

def POP(AX):
    index=int(List2Str(Reverse(SS)),2)*16+int(List2Str(Reverse(SP)),2)#注意此时的index指向栈顶上面
    index=index+2#得到正确的栈顶位置

    #修改SP
    flagtemp=FLAG[0]
    ADD(SP,Hex2Bin(2))#SP-2=SP+FFFE（取模）
    FLAG[0]=flagtemp#借用了加法，为了避免对后续操作产生影响，因此借用后还要把FLAG[0]的值恢复

    poplist=[]
    poplist.extend(DATA[index])
    poplist.extend(DATA[index+1])
    AX=poplist
    #虽然不知道为什么测试的时候这里POP不会直接修改list，但是还是返回一下吧
    return poplist

def AND(x,y):
    c=[]
    for i in range(len(x)):
        c.append(x[i] and y[i])
    return c

def NOT(AX):
    for i in range(len(AX)):
        if AX[i]==1:
            AX[i]=0
        else:
            AX[i]=1
    return AX


def OR(x,y):
    c=[]
    for i in range(len(x)):
        c.append(x[i] or y[i])
    return c

def XOR(x,y):
    c=[]
    for i in range(len(x)):
        if x[i]==y[i]:
            c.append(0)
        else:
            c.append(1)
    return c

def SUB(x,y):
    y=NOT(y)
    tempflag=FLAG[0]
    ADD(y,Hex2Bin('1'))
    ADD(x,y)
    FLAG[0]=tempflag
    y=NOT(y)#把y还原
    return x

'''
------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------
注意所有的函数中如果传入参数是List，要使用临时变量来操作，防止对原来的list产生影响
'''
#debugFunctions:

def change(s):#将input()输入转成函数命令:  MOV AX,BX -> MOV(AX,BX)

    #输入s是一串字符串
    cmd=[]#输入s的等价指令集

    if '-' not in s:#说明存进来的是汇编指令
        temp=FLAG[0]
        index=int(Bin2Hex(ADD(CS[:],IP[:])),16)
        DATA[index:index+2] = s.split()#将指令存到存储器,注意split()函数不会改变s，只是返回分割而已
        ADD(IP,Hex2Bin(2))#指针指向下一个地址
        FLAG[0]=temp#用temp来暂存进位寄存器的内容，避免因为这个无关紧要的功能影响正常的操作
    
    temp1=s.split()#分割空格得到不含空格的字符串列表['MOV', 'AX,BX']
    
    for i in temp1:
        cmd.extend(i.split(','))
        #分割空格得到不含逗号的字符串列表['MOV', 'AX' ,'BX']
        #从这一步开始，得到基本指令的三个基本内容，然后根据指令再细分



    if cmd[0]=='MOV':#进行MOV操作的几种情况判断

        #先判断cmd[2]
        if '[' and ']' in cmd[2]:
            #若cmd[2]中'[]'，表明需要用到寻址,只能从地址到寄存器
            index=caladdress(cmd[2])
            if 'H' in cmd[1]:
                eval(Sub2Major(cmd[1]))[8:16]=DATA[index]
            elif 'L' in cmd[1]:
                eval(Sub2Major(cmd[1]))[0:8] =DATA[index]
            else:
                eval(cmd[1])[0:8]=DATA[index]
                eval(cmd[1])[8:16]=DATA[index+1]
                

        else:
            #不需要寻址的只有两种情况，立即数或变量名，即
            #cmd[2]='1234'
            #cmd[2]=BX
            if isVar(cmd[2]):#变量到变量，变量到地址
                if '[' and ']' in cmd[1]:#变量到地址
                    index=caladdress(cmd[1])

                    if 'H' in cmd[2]:
                        DATA[index]=eval(Sub2Major(cmd[2]))[8:16]
                    elif 'L' in cmd[2]:
                        DATA[index]=eval(Sub2Major(cmd[2]))[0:8]
                    else:
                        DATA[index]=eval(cmd[2])[0:8]
                        DATA[index+1]=eval(cmd[2])[8:16]

                elif isVar(cmd[1]):#变量到变量,有H的情况最特殊
                    if 'H' in cmd[2]:
                        if 'H' in cmd[1]:
                            eval(Sub2Major(cmd[1]))[8:16]=eval(Sub2Major(cmd[2]))[8:16]
                        else:
                            MOV(eval(Sub2Major(cmd[1])),eval(Sub2Major(cmd[2]))[8:16])
                    elif 'L' in cmd[2]:
                        if 'H' in cmd[1]:
                            eval(Sub2Major(cmd[1]))[8:16]=eval(Sub2Major(cmd[2]))[0:8]
                        else:
                            MOV(eval(Sub2Major(cmd[1])),eval(Sub2Major(cmd[2]))[0:8])
                    else:
                        MOV(eval(cmd[1]),eval(cmd[2]))
            else:
                #那就只能是立即数了
                if 'H' in cmd[1]:
                    eval(Sub2Major(cmd[1]))[8:16]=Hex2Bin(cmd[2])
                elif 'L' in cmd[1]:
                    eval(Sub2Major(cmd[1]))[0:8] =Hex2Bin(cmd[2])[0:8]
                else:
                    MOV(eval(cmd[1]),Hex2Bin(cmd[2]))
            


        
    elif cmd[0]=='ADD':#进行ADD操作的几种情况判断
        #cmd[1]一定是变量名,只需要判断cmd[2]

        if '[' and ']' in cmd[2]:
            #若cmd[2]中'[]'，表明需要用到寻址
            index=caladdress(cmd[2])
            if 'H' in cmd[1]:
                eval(Sub2Major(cmd[1]))[8:16]=ADD(eval(Sub2Major(cmd[1]))[8:16],DATA[index])
            elif 'L' in cmd[1]:
                eval(Sub2Major(cmd[1]))[0:8] =ADD(eval(Sub2Major(cmd[1]))[0:8], DATA[index])
            else:
                addnum=[]
                addnum.extend(DATA[index])
                addnum.extend(DATA[index+1])
                ADD(eval(cmd[1]),addnum)

        else:
            #不需要寻址的只有两种情况，立即数或变量名，即
            #cmd[2]='1234'
            #cmd[2]=BX
            #只允许将16位加到16位，否则太麻烦了
            #需要用到8位运算时，请自觉补0凑齐16位即可
            if isVar(cmd[2]):
                ADD(eval(cmd[1]),eval(cmd[2]))
            else:
                #那就只能是立即数了
                ADD(eval(cmd[1]),Hex2Bin(cmd[2]))

    elif cmd[0]=='ADC':#进行ADC操作的几种情况判断，同ADD
        
        if '[' and ']' in cmd[2]:
            #若cmd[2]中'[]'，表明需要用到寻址
            index=caladdress(cmd[2])
            if 'H' in cmd[1]:
                eval(Sub2Major(cmd[1]))[8:16]=ADC(eval(Sub2Major(cmd[1]))[8:16],DATA[index])
            elif 'L' in cmd[1]:
                eval(Sub2Major(cmd[1]))[0:8] =ADC(eval(Sub2Major(cmd[1]))[0:8], DATA[index])
            else:
                addnum=[]
                addnum.extend(DATA[index],DATA[index+1])
                ADC(eval(cmd[1]),addnum)

        else:
            #不需要寻址的只有两种情况，立即数或变量名，即
            #cmd[2]='1234'
            #cmd[2]=BX
            #只允许将16位加到16位，否则太麻烦了
            if isVar(cmd[2]):
                ADC(eval(cmd[1]),eval(cmd[2]))
            else:
                #那就只能是立即数了
                ADC(eval(cmd[1]),Hex2Bin(cmd[2]))

    elif cmd[0]=='SUB':#目前只支持寄存器之间的减法，且不满足借位标志
        eval(cmd[1])[:]=SUB(eval(cmd[1]),eval(cmd[2]))

    elif cmd[0]=='AND':
        eval(cmd[1])[:]=AND(eval(cmd[1]),eval(cmd[2]))

    elif cmd[0]=='OR':
        eval(cmd[1])[:]=OR(eval(cmd[1]),eval(cmd[2]))

    elif cmd[0]=='NOT':
        eval(cmd[1])[:]=NOT(eval(cmd[1]))

    elif cmd[0]=='XOR':
        eval(cmd[1])[:]=XOR(eval(cmd[1]),eval(cmd[2]))

    elif cmd[0]=='MUL':
        MUL(eval(cmd[1]))

    elif cmd[0]=='PUSH':
        PUSH(eval(cmd[1]))

    elif cmd[0]=='POP':
        eval(cmd[1])[:]=POP(eval(cmd[1]))
        
    elif cmd[0]=='-R':
        if len(cmd)==1:#只有'-R'一个指令，显示全部内容
            show()
        else:#后面指定了显示哪一个寄存器
            print(cmd[1],'=',Bin2Hex(eval(cmd[1])))

    elif cmd[0]=='-FILE':
        #读文件
        print('Please input the file name:',end='  ')
        fileName=input()
        for line in open(fileName):
            print(Bin2Hex(CS),':',Bin2Hex(IP),line)
            change(line)
            
    elif cmd[0]=='EXIT':
        global flag
        flag=True
        
    else:
        print('Err!')
    return

'''
---------------------------------------------------------------------------------------------------------------------------------------------
'''

def Hex2Bin(var):#十六进制转二进制列表：Format:'1234' or 1234 ->[0,0,1,0,  1,1,0,0,  0,1,0,0,  1,0,0,0]
    var=str(var)#将整型转字符串，字符串不变
    Bin=bin(int(var,16))#16进制字符串转10进制再转2进制(得到的是字符串)
    Bin=list(Bin[2:])#将0x去掉
    Bin.reverse()#得到我们规定的二进制格式
    length=len(Bin)
    for x in range(length):
        Bin[x]=int(Bin[x])
    while len(Bin) % 16 != 0:
        Bin.append(0)
    return Bin

def isVar(a):#判断是否为寄存器变量
    if a=='AX'or a=='BX'or a=='CX'or a=='DX'or a=='SP'or a=='BP'or a=='SI'or a=='DI'or a=='IP'or a=='DS'or a=='ES'or a=='SS'or a=='CS' or a=='AH' or a=='AL' or a=='BH' or a=='BL' or a=='CH' or a=='CL' or a=='DH' or a=='DL':
        return True
    else:
        return False

def Sub2Major(s):
    if isVar(s):
        if 'H' or 'L' in s:
            s=list(s)
            s.pop()
            s.append('X')
            s=List2Str(s)
    return s

def show():#显示寄存器内数据
    global AX,BX,CX,DX
    global SP,BP,SI,DI,IP
    global DS,ES,SS,CS
    print('AX=',Bin2Hex(AX),'  BX=',Bin2Hex(BX),'  CX=',Bin2Hex(CX),'  DX=',Bin2Hex(DX))
    print('SP=',Bin2Hex(SP),'  BP=',Bin2Hex(BP),'  SI=',Bin2Hex(SI),'  DI=',Bin2Hex(DI),'  IP=',Bin2Hex(IP))
    print('DS=',Bin2Hex(DS),'  ES=',Bin2Hex(ES),'  SS=',Bin2Hex(SS),'  CS=',Bin2Hex(CS))
    #print(AX)

def Bin2Hex(alist):
    #16位二进制转4位十六进制：
    #Format:[0,0,1,0,  1,1,0,0,  0,1,0,0,  1,0,0,0]->'1234'
    binStr=List2Str(Reverse(alist))
    hexStr=hex(int(binStr,2))#将二进制字符串转成10进制数，再转成16进制字符串
    hexStr=list(hexStr[2:])#去掉16进制字符串前面的0x

    #使得0x0输出'0000'
    while len(hexStr) % 4 != 0:
        hexStr.insert(0,'0')
    #此时hexStr=['1','2','3','4']，还差最后一步
    hexStr=List2Str(hexStr)
    return hexStr

def List2Str(alist):#[0,1,A,6]->'01A6'
    #print(List)
    List=[]
    for i in range(len(alist)):
        List.append(str(alist[i]))#确认列表内所有元素都是字符串
    #print(List)
    return "".join(List)

def Reverse(List):#将List作为形参，避免每次调用.reverse()都影响原来的值
    temp=[List[i]for i in range(len(List)-1,-1,-1)]
    return temp

def seperate(s):#将'[BX+5][SI]'转换为['BX','5','SI']
    s=s.split()##将"[BX+5][SI]"转换为['[BX+5][SI]']
    cmd0=[]
    for i in s:
        cmd0.extend(i.split('['))
    cmd1=[]
    for i in cmd0:
        cmd1.extend(i.split(']'))
    cmd2=[]
    for i in cmd1:
        cmd2.extend(i.split('+'))
    while '' in cmd2:
        cmd2.remove('')
    return cmd2

def caladdress(s):
    alist=seperate(s)
    
    flag=False#用来记录是否需要跳转段地址
    if ':' in alist[0]:
        temp=alist[0].split(':')
        alist[0]=temp[0]
        flag=True

    temp=[]
    if flag:#需要跳转段地址
        duan=Bin2Hex(eval(alist[0]))
        for i in range(1,len(alist)):
            if isVar(alist[i]):
                temp.append(eval(alist[i]))
            else:
                ahex=eval(alist[i])
                temp.append(Hex2Bin(ahex))
            
    else:#不需要跳转段地址
        duan=Bin2Hex(DS)
        for i in range(len(alist)):
            if isVar(alist[i]):
                temp.append(eval(alist[i]))
            else:
                ahex=eval(alist[i])
                temp.append(Hex2Bin(ahex))
        
    
    
    mysum=[0 for i in range(16)]
    flagtemp=FLAG[0]#后面用到了ADD，所以需要记录标志寄存器
    for i in range(len(temp)):
        mysum=ADD(mysum,temp[i])#先不考虑最高位的进位,注意使用了操作函数
    FLAG[0]=flagtemp
    pianyi=Bin2Hex(mysum)
    return int(duan,16)*16+int(pianyi,16)


'''
------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------
'''

#主函数

#文件之后的操作
while True:
    flag=False
    print(Bin2Hex(CS),':',Bin2Hex(IP),end='  ')
    change(input())
    if flag:
        print('Exit this program!')
        break
