import re
import sys


def replace_Text(Data, List_To_Replace):
    for Text in List_To_Replace:
        Data = re.sub(Text,"",Data)
    #print("\n","__"*100,"\n",Data)
    return Data

def check_for_other_conditions(Data):
    Client_Level_Detail = ""
    Employee_Level_Detail = ""
    Notes_Section = ""
    pos0 = Data.find('Quarter End Exception Report: Employee Detail')
    pos1 = Data.find('Quarter End Exception Report: QEER Notes')
    if pos0 != -1:
        Client_Level_Detail = Data[:pos0]
        if Client_Level_Detail.find("For Payrolls processed") == -1:
            if pos1 != -1:
                Employee_Level_Detail = Data[pos0:pos1]
                Notes_Section = Data[pos1:]
            else:
                Employee_Level_Detail = Data[pos0:]
            Client_Level_Detail = ""
        else:
            if pos1 != -1:
                Notes_Section = Data[pos1:]
                Employee_Level_Detail = Data[pos0:pos1]
            else:
                Employee_Level_Detail = Data[pos0:]
    elif pos1 != -1:
        Client_Level_Detail = Data[:pos1]
        if Client_Level_Detail.find("For Payrolls processed") == -1:
            Client_Level_Detail = ""
        Notes_Section = Data[pos1:]
    Client_Level_Detail = re.sub(r"For Payrolls processed.*\n.*\n.*","",Client_Level_Detail)
    Client_Level_Detail = re.sub(r"Quarter End Exception Report.*\n.*","",Client_Level_Detail)
    Client_Level_Detail = re.sub(r"QUARTER END EXCEPTION REPORT.*","",Client_Level_Detail)
    Employee_Level_Detail = re.sub(r"For Payrolls processed.*\n.*\n.*","",Employee_Level_Detail)
    Employee_Level_Detail = re.sub(r"Quarter End Exception Report.*\n.*","",Employee_Level_Detail)
    Employee_Level_Detail = re.sub(r"QUARTER END EXCEPTION REPORT.*","",Employee_Level_Detail)
    # Notes_Section = re.sub(r"For Payrolls processed.*\n.*\n.*","",Notes_Section)
    # Notes_Section = re.sub(r"Quarter End Exception Report.*\n.*","",Notes_Section)
    # Notes_Section = re.sub(r"QUARTER END EXCEPTION REPORT.*","",Notes_Section)
    Client_Level_Detail = Client_Level_Detail.strip()
    Employee_Level_Detail = Employee_Level_Detail.strip()
    if Client_Level_Detail == "" and Employee_Level_Detail == "":
        return False
    else:
        return True
    # Notes_Section = Notes_Section.strip()
    # print("__"*200,"\nClient_Level_Detail\n","__"*200,"\n",Client_Level_Detail)
    # print("__" * 200, "\nEmployee_Level_Detail\n","__"*200,"\n", Employee_Level_Detail)
    # print("__" * 200, "\nNotes_Section\n","__"*200,"\n", Notes_Section, "\n")


def ESL_FP(Data):
    List_Of_Match = []
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    Status = 'No Condition Match'
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    List_Of_Check = ['QTD','YTD']
    Is_Conditions_Match = True
    Is_Any_Con_Match = False
    for check in List_Of_Check:
        Match = re.search("(?<="+check+" SOC vs\. SOCER Exempt Wages\n)(.*\n)(.*)",Temp_Data)
        if Match != None:
            List_Of_Match.append(check + " SOC vs. SOCER Exempt Wages")
            List_Of_Match.append(Match.group(0))
            Status = 'Condition Match'
            Amount_Row = Match.group(2)
            Amount_Row = re.sub("\s+", " ", Amount_Row).strip().split(' ')
            Exempt_Wages = Amount_Row[len(Amount_Row)-1].strip().replace(',','')
            Match = re.search("(?<="+check+" SOC vs\. SOCER Taxable Wages\n)(.*\n)(.*)", Temp_Data)
            if Match != None:
                List_Of_Match.append(check+" SOC vs. SOCER Taxable Wages")
                List_Of_Match.append(Match.group(0))
                Amount_Row = Match.group(2)
                Amount_Row = re.sub("\s+", " ", Amount_Row).strip().split(' ')
                Taxable_Wages = Amount_Row[len(Amount_Row) - 1].strip().replace(',','')
                Result = float(Exempt_Wages)+float(Taxable_Wages)
                if(Result != 0):
                    Match = re.search("(?<=" + check + " SOC vs\. SOCER Excess Wages\n)(.*\n)(.*)", Temp_Data)
                    if Match != None:
                        List_Of_Match.append(check + " SOC vs. SOCER Excess Wages")
                        List_Of_Match.append(Match.group(0))
                        Amount_Row = Match.group(2)
                        Amount_Row = re.sub("\s+", " ", Amount_Row).strip().split(' ')
                        Excess_Wages = Amount_Row[len(Amount_Row) - 1].strip().replace(',', '')
                        Result = float(Exempt_Wages) + float(Taxable_Wages)+float(Excess_Wages)
                        if (Result != 0):
                            Is_Conditions_Match = False
                            break
                        else:
                            Is_Any_Con_Match = True
                    else:
                        Is_Conditions_Match = False
                        break
                else:
                    Is_Any_Con_Match = True
            else:
                Is_Conditions_Match = False
                break
    if Is_Conditions_Match and Is_Any_Con_Match:
        Has_Data = False
        while True:
            Match = re.search("(?<=Negative YTD Tax/Wages\n)(.*\n)*", Temp_Data)
            if Match != None:
                List_Of_Match.append("(?=Negative YTD Tax/Wages\n)(.*\n){2}")
                Has_Data = True
                Temp_Data = Match.group(0)
                Temp_Data1 = Temp_Data.split('\n')
                Res = False
                for loop_Count in range(1,len(Temp_Data1)):
                    Temp = Temp_Data1[loop_Count].strip()
                    Temp_Data1[loop_Count] = Temp_Data1[loop_Count].strip()
                    Temp_Data1[loop_Count] = re.sub('\s{2,}','\t',Temp_Data1[loop_Count])
                    if len(Temp_Data1[loop_Count].split('\t')) == 7:
                        List_Of_Match.append(Temp)
                        Res = True
                        Code = Temp_Data1[loop_Count].split('\t')[2].strip()
                        if Code != 'ZZESL':
                            return False,Status,[]
                    else:
                        if Res:
                            break
                        else:
                            return False,Status,[]
            else:
                if Has_Data:
                    return True,Status,List_Of_Match
                else:
                    break
    return False,Status,[]


def FUI_Finalized_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Match = re.search(r"Client FUI Setup\n\s*Code\n\s*FUI- Is Finalized",Temp_Data)
    if Match != None:
        Status = 'Condition Match'
        List_Of_Match.append(Match.group(0))
        return True,Status,List_Of_Match
    else:
        return False,Status,[]


def IN_County_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Is_Res_Found = False
    while True:
        Match = re.search(r".*IN County Tax Set Up\n\s*Emp No.*\n((.*\n)*)", Temp_Data)
        if Match != None:
            Status = 'Condition Match'
            List_Of_Match.append(".*IN County Tax Set Up\n\s*Emp No.*\n")
            Temp_Data = Match.group(1)
            Temp_List = Match.group(1).strip().split("\n")
            for Line in Temp_List:
                Line1 = str(Line).strip()
                if Line1 != "":
                    Line1 = Line1[0].isdigit()
                    if Line1:
                        Is_Res_Found = True
                        List_Of_Match.append(Line)
                    else:
                        break
                else:
                    break
        else:
            break
    if Is_Res_Found:
        return True, Status, List_Of_Match
    else:
        return False,Status,[]


def Taxes_On_Hold_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Is_Res_Found = False
    Match = re.search(r"(?<= Taxes On Hold).*\n(.*)", Temp_Data)
    if Match != None:
        Status = 'Condition Match'
        Columns = re.sub('\s\s+','\t',Match.group(1))
        Columns = Columns.strip().split('\t')
        if len(Columns) <= 3 and 'Difference' not in Columns:
            while True:
                Match = re.search(r"(?=Taxes On Hold).*\n(.*)((.*\n)*)", Temp_Data)
                if Match != None:
                    List_Of_Match.append("(?=Taxes On Hold).*\n.*")
                    # print(Match.group(2))
                    Temp_Data = Match.group(2)
                    Temp_List = Match.group(2).strip().split("\n")
                    for Line in Temp_List:
                        Line1 = str(Line).strip()
                        if Line1 != "":
                            Line1 = Line1[0].isdigit()
                            if Line1:
                                Is_Res_Found = True
                                List_Of_Match.append(Line)
                            else:
                                break
                        else:
                            break
                else:
                    break
    if Is_Res_Found:
        return True, Status, List_Of_Match
    else:
        return False,Status,[]


def Live_in_Locals_FP(Data):
    List_Of_Match = []
    #Edited .*
    Status = 'No Condition Match'
    List_Of_Check = ['QTD', 'YTD']
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    First_Condition = False
    for con in List_Of_Check:
        Match = re.search(r"(?<="+con+" Local Wage vs. W/H - Wages).*\n(.*\n.*)", Temp_Data)
        if Match != None:
            Status = 'Condition Match'
            Match = Match.group(1)
            Match = Match.strip().split('\n')
            if Match[0].find('Difference') != -1:
                Match = re.sub('\s\s+','\t',Match[1].strip())
                Match = Match.split('\t')
                Difference1 = Match[len(Match)-1].strip().replace(",","")
                if Difference1.find("(") != -1 or Difference1.find(")") != -1:
                    Difference1 = "-" + Difference1.replace("(", "").replace(")", "")
                if float(Difference1) < 0:
                    List_Of_Match.append("(?="+con+" Local Wage vs. W/H - Wages)(.*\n){3}")
                    First_Condition = True
                else:
                    return False, Status, []
    if First_Condition:
        pos1 = Data.find('Quarter End Exception Report: QEER Notes')
        if pos1 != -1:
            Temp_Data = Data[pos1:].upper()
            Match = re.search(r'(LIVE-IN|OVER ON LIVE-IN|LIVE IN|OVER ON LIVE IN)',Temp_Data)
            if Match != None:
                return True,Status,List_Of_Match
    return False,Status,[]


def Invalid_SSN_FP(Data):
    Employees_List = []
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    while True:
        Match = re.search(r"(?<=Invalid SSN, not allowed).*\n(.*\n)((.*\n)*)", Temp_Data)
        if Match != None:
            List_Of_Match.append("(?=Invalid SSN, not allowed).*\n.*")
            Temp_Data = Match.group(0)
            Temp_List = Match.group(2).strip().split("\n")
            for Line in Temp_List:
                Line1 = str(Line).strip()
                if Line1 != "":
                    Line1 = Line1[0].isdigit()
                    if Line1:
                        Is_Res_Found = True
                        replaced_Line = re.sub('\s\s+', '\t', Line.strip())
                        if len(replaced_Line.split("\t")) >= 2:
                            employee_name = replaced_Line.split("\t")[1]
                            Employees_List.append(employee_name)
                            List_Of_Match.append(Line.strip())
                        else:
                            break
                    else:
                        break
                else:
                    break
        else:
            break
    pos1 = Data.find('Quarter End Exception Report: QEER Notes')
    if pos1 != -1:
        Temp_Data = Data[pos1:]
        Match = re.search(r'Invalid SSN, not allowed((.*\n)*)',Temp_Data)
        if Match != None:
            if len(Employees_List) > 0:
                for employee in Employees_List:
                    if Match.group(0).find(employee) == -1:
                        break
                else:
                    return True,Status,List_Of_Match
    return False,Status,[]

def ZZERC_NEG_Tax_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Has_Data = False
    while True:
        Match = re.search(r'(?<=Negative YTD Tax/Wages).*\n(.*\n)*',Temp_Data)
        if Match != None:
            List_Of_Match.append("Negative YTD Tax/Wages.*\n.*")
            # Status = 'Condition Match'
            Has_Data = True
            Temp_Data = Match.group(0).strip()
            Match = Temp_Data.split('\n')
            if Match[0].upper().find('CODE') != -1:
                row_Match = False
                for row in range(1,len(Match)):
                    Temp_Row = re.sub('\s\s+','\t',Match[row].upper().strip())
                    row_List = Temp_Row.split('\t')
                    if len(row_List) == 7:
                        List_Of_Match.append(Match[row].strip())
                        row_Match = True
                        if row_List[2].strip() != 'ZZERC':
                            return False,Status,[]
                    else:
                        if row_Match:
                            break
                        else:
                            return False,Status,[]
            else:
                return False,Status,[]
        else:
            if Has_Data:
                return True,Status,List_Of_Match
            else:
                return False,Status,[]


def SUI_Dif_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Match = re.search(r'Client SUI Setup\n\s*Difference(\n.*- On permanent hold)*',Temp_Data)
    if Match != None:
        List_Of_Match.append(r'Client SUI Setup\n\s*Difference(\n.*- On permanent hold)*')
        return True,Status,List_Of_Match
    else:
        return False,Status,[]


def Mid_QTR_Start_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Match = re.search(r'TAX EDIT: Mid Quarter Start\s*\n\s*Client has liabilities without associated impounds, or assoc impounds are of type Balance Entry', Temp_Data)
    if Match != None:
        List_Of_Match.append(r'TAX EDIT: Mid Quarter Start\s*\n\s*Client has liabilities without associated impounds, or assoc impounds are of type Balance Entry')
        return True,Status,List_Of_Match
    else:
        return False,Status,[]


def Successor_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Match = re.search(r'TAX EDIT: Successorship Client\s*\n\s*Client is a Successorship', Temp_Data)
    if Match != None:
        List_Of_Match.append(r'TAX EDIT: Successorship Client\s*\n\s*Client is a Successorship')
        return True,Status,List_Of_Match
    else:
        return False,Status,[]


def NVQBC_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Match = re.search(r'(QTD SUI vs SMISC Wages\s*\n.*)', Temp_Data)
    if Match != None:
        List_Of_Match.append(r'(QTD SUI vs SMISC Wages\s*\n.*\n.*)')
        Status = 'Condition Match'
        if Match.group(0).find('NVQBC Wages') != -1:
            Match = re.search(r'YTD SUI vs SMISC Wages\s*\n.*', Temp_Data)
            if Match != None:
                List_Of_Match.append(r'YTD SUI vs SMISC Wages\s*\n.*\n.*')
                if Match.group(0).find('NVQBC Wages') != -1:
                    return True,Status,List_Of_Match
    return False,Status,[]


def FUI_SUI_Exempt_FP(Data):
    List_Of_Match = []
    Is_Result_Found = False
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    while True:
        Match = re.search(r'(?<=Employee Missing SUI)\s*\n.*\n((.*\n)*)', Temp_Data)
        if Match != None:
            Temp_Data = Match.group(1)
            Status = 'Condition Match'
            Match = Match.group(1).strip().split('\n')
            for line in Match:
                line1 = re.sub('\s\s\s+','\t',line.strip())
                line1 = line1.split('\t')
                if line1[0].strip().isdigit():
                    if len(line1) <= 2:
                        Is_Result_Found = True
                        List_Of_Match.append(line)
                    else:
                        Is_Result_Found = False
                        break
                else:
                    break
        else:
            break
    if Is_Result_Found:
        Match = re.search(r'(?<=Quarter End Exception Report: QEER Notes).*\n(.*\n)*', Data)
        if Match != None:
            Temp_Data = Match.group(0).upper()
            Match = re.search(r'FUI\s(OR|\&)\sSUI EXEMPT|FUTA\s(OR|\&)\sSUTA EXEMPT|(FUI|FUTA) EXEMPT|(SUI|SUTA) EXEMPT',Temp_Data)
            if Match != None:
                return True,Status,List_Of_Match
    return False,Status,[]


def NIA_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    List_Of_Check = ['QTD MED','QTD SOC','YTD MED','YTD SOC']
    List_of_Differences = []
    Match = re.search(r'(?<=Quarter End Exception Report: Employee Detail)(.*\n)*', Data)
    if Match != None:
        Match = Match.group(0)
        pos = Match.find('Quarter End Exception Report: QEER Notes')
        if pos != -1:
            Temp_Data = Match[:pos]
        else:
            Temp_Data = Match
        Has_Data = False
        for con in List_Of_Check:
            Temp_Data_1 = Temp_Data
            while True:
                Match = re.search(r'(?<=' + con + ' Wages vs\. Earnings).*\n.*((\n.*)*)', Temp_Data_1)
                if Match != None:
                    List_Of_Match.append(r'(?=' + con + ' Wages vs. Earnings).*\n.*\n.*')
                    Has_Data = True
                    Temp_Data_1 = Match.group(1).strip()
                    Match = Temp_Data_1.split('\n')
                    Has_Row = False
                    for row in Match:
                        row = row.strip()
                        Match = re.search(r'^(\d+).*', row)
                        if Match != None:
                            List_Of_Match.append(row.replace("(", "\(").replace(")", "\)"))
                            Match = re.sub(r'\s\s+', '\t', Match.group(0))
                            Match = Match.split('\t')
                            if len(Match) >= 6:
                                Has_Row = True
                                Total_Wages = float(Match[2].strip())
                                Tax_exempt_reason = Match[5].strip()
                                if not ((Tax_exempt_reason == 'Nonimmigrant Alien' or Tax_exempt_reason == 'Other') and Total_Wages == 0):
                                    return False,Status,[]
                            else:
                                return False,Status,[]
                        else:
                            break
                    if not Has_Row:
                        return False,Status,[]
                else:
                    break
        if Has_Data:
            return True,Status,List_Of_Match
    else:
        return False,Status,[]


def Total_Agr_FP(Data):
    List_Of_Match = []
    List_Of_Items = ['QTD MED','QTD SOC','YTD MED','YTD SOC']
    Status = 'No Condition Match'
    Match = re.search(r'(?<=Quarter End Exception Report: Employee Detail)(.*\n)*',Data)
    if Match != None:
        Match = Match.group(0)
        pos = Match.find('Quarter End Exception Report: QEER Notes')
        if pos != -1:
            Temp_Data = Match[:pos]
            Has_Data = False
            for con in List_Of_Items:
                Temp_Data_1 = Temp_Data
                while True:
                    Match = re.search(r'(?<='+con+' Wages vs\. Earnings).*\n.*((\n.*)*)', Temp_Data_1)
                    if Match != None:
                        List_Of_Match.append(r'(?=' + con + ' Wages vs. Earnings).*\n.*\n.*')
                        #Status = 'Condition Match'
                        Has_Data = True
                        Temp_Data_1 = Match.group(1).strip()
                        Match = Temp_Data_1.split('\n')
                        Has_Row = False
                        for row in Match:
                            Match = re.search(r'^(\d+).*',row.strip())
                            if Match != None:
                                List_Of_Match.append(row.replace("(","\(").replace(")","\)"))
                                Match = re.sub(r'\s\s+','\t',Match.group(0))
                                Match =  Match.split('\t')
                                if len(Match) >= 3:
                                    Has_Row = True
                                    Total_Wages = float(Match[2].strip())
                                    if Total_Wages != 0:
                                        return False,Status,[]
                                else:
                                    break
                            else:
                                break
                        if not Has_Row:
                            return False,Status,[]
                    else:
                        break
            else:
                if not Has_Data:
                    return False,Status,[]
    else:
        return False,Status,[]
    Match = re.search(r'(?<=Quarter End Exception Report: QEER Notes)(.*\n)*',Data)
    if Match != None:
        Match = Match.group(0).upper()
        if Match.find('TOTALIZATION AGREEMENT') != -1 or Match.find('TOTALIZATION') != -1:
            return True,Status,List_Of_Match
    return False,Status,[]

def Multi_State_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    List_Of_Checks = ['QTD State Taxable vs. Federal','YTD State Taxable vs. Federal','QTD State Exempt vs. Federal','YTD State Exempt vs. Federal']
    Has_Data = False
    for row in List_Of_Checks:
        Match = re.search(r"(?<="+row+").*\n(.*\n.*)", Temp_Data)
        if Match != None:
            Status = 'Condition Match'
            Has_Data = True
            Match = Match.group(1).strip()
            Match = Match.split('\n')
            if Match[0].find('Difference') != -1:
                Match = re.sub('\s\s+', '\t', Match[1].strip())
                Match = Match.split('\t')
                Difference1 = Match[len(Match) - 1].strip().replace(',','')
                if Difference1.find("(") != -1 or Difference1.find(")") != -1:
                    Difference1 = "-" + Difference1.replace("(", "").replace(")", "")
                #print(Difference1)
                if float(Difference1) >= 0:
                    return False,Status,[]
                else:
                    List_Of_Match.append(r"(?=" + row + ").*\n(.*\n.*)")
            else:
                return False,Status,[]
    if not Has_Data:
        return False,Status,[]
    pos1 = Data.find('Quarter End Exception Report: QEER Notes')
    Temp_Data = Data[pos1:].upper()
    Match = re.search(r'MULTI\s?STATE', Temp_Data)
    if Match != None:
        return True,Status,List_Of_Match
    return False,Status,[]

def Clergy_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    List_Of_Check = ['QTD FITWH','YTD FITWH']
    Match = re.search(r'(?<=Quarter End Exception Report: Employee Detail)(.*\n)*', Data)
    if Match != None:
        Match = Match.group(0)
        pos = Match.find('Quarter End Exception Report: QEER Notes')
        if pos != -1:
            Temp_Data = Match[:pos]
        else:
            Temp_Data = Match
        Has_Data = False
        for con in List_Of_Check:
            Temp_Data_1 = Temp_Data
            while True:
                Match = re.search(r'(?<=' + con + ' Wages vs\. Earnings).*\n.*((\n.*)*)', Temp_Data_1)
                if Match != None:
                    List_Of_Match.append(r'(?=' + con + ' Wages vs. Earnings).*\n.*')
                    Status = 'Condition Match'
                    Has_Data = True
                    Temp_Data_1 = Match.group(1).strip()
                    Match = Temp_Data_1.split('\n')
                    Has_Row = False
                    for row in Match:
                        row = row.strip()
                        Match_1 = re.search(r'^(\d+).*', row)
                        if Match_1 != None:
                            Match_1 = re.sub(r'\s\s+', '\t', Match_1.group(0))
                            Match_1 = Match_1.split('\t')
                            if len(Match_1) >= 6:
                                Has_Row = True
                                Total_Wages = float(Match_1[2].strip())
                                Tax_exempt_reason = Match_1[5].strip()
                                if not (Tax_exempt_reason == 'Clergy' and Total_Wages == 0):
                                    return False,Status,[]
                                else:
                                    List_Of_Match.append(row.replace(")","\)").replace("(","\("))
                            else:
                                return False,Status,[]
                        else:
                            break
                    if not Has_Row:
                        return False,Status,[]
                else:
                    break
        if Has_Data:
            return True,Status,List_Of_Match
    return False,Status,[]

def _3PS_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    Is_Match_Found = False
    while True:
        Match = re.search(r'(?<=QEER ThirdPartySick).*\n.*((\n.*)*)', Temp_Data)
        if Match != None:
            List_Of_Match.append(r'(?=QEER ThirdPartySick).*\n.*')
            Temp_Data = Match.group(1).strip()
            Status = 'Condition Match'
            Match = Match.group(1).strip().split("\n")
            for Line in Match:
                Line1 = re.sub('\s\s+','\t',Line.strip())
                Line1 = Line1.split('\t')[0].strip()
                if Line1.isnumeric():
                    List_Of_Match.append(Line)
                    Is_Match_Found = True
                else:
                    break
        else:
            break
    if Is_Match_Found:
        return True,Status,List_Of_Match
    else:
        return False,Status,[]

def WV_FP_AND_CO_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    List_Of_Check = ['QTD', 'YTD']
    Has_Data = False
    for con in List_Of_Check:
        Match = re.search(r'(?<='+con+' Local Wage vs\. W\/H - Wages for EE with differences only\.).*\n(.*\n){2}', Temp_Data)
        if Match != None:
            List_Of_Match.append(r'(?='+con+' Local Wage vs\. W\/H - Wages for EE with differences only\.).*\n(.*\n){2}')
            Status = 'Condition Match'
            Match = Match.group(0).strip()
            Match = Match.split('\n')
            Row1 = Match[0].strip().upper()
            Row2 = Match[1].strip().upper()
            if (Row2.startswith('CO') or Row2.startswith('WV')) and Row1.startswith('CODE'):
                Row1 = re.sub('\s{3,}','\t',Row1).split('\t')[1].strip()
                Row2 = re.sub('\s{3,}', '\t', Row2).split('\t')[1].strip()
                if Row1 == 'RATE' and float(Row2) == 0:
                    Has_Data = True
                else:
                    return False,Status,[]
            else:
                return False,Status,[]
    if Has_Data:
        return True,Status,List_Of_Match
    return False,Status,[]

def FUI_SUI_Rounding_FP(Data):
    List_Of_Match = []
    Status = 'No Condition Match'
    pos1 = Data.find('Quarter End Exception Report: Employee Detail')
    if pos1 != -1:
        Temp_Data = Data[0:pos1]
    else:
        Temp_Data = Data
    List_Of_Check = ['YTD FUI', 'YTD SUI','QTD FUI','QTD SUI']
    Is_Match_Found = False
    for con in List_Of_Check:
        Match = re.search(r'(?<='+con+' Wage vs. W\/H).*\n(.*\n){2}', Temp_Data)
        if Match != None:
            Status = 'Condition Match'
            Is_Match_Found = True
            Match = Match.group(0).strip()
            Match = Match.split('\n')
            Row1 = Match[0].strip().upper()
            Row1 = re.sub('\s\s+', '\t', Row1).split('\t')
            Row1 = Row1[len(Row1)-1]
            Row2 = Match[1].strip().upper()
            Row2 = re.sub('\s\s+', '\t', Row2).split('\t')
            Row2 = Row2[len(Row2) - 1]
            if not (Row1 == 'DIFFERENCE' and float(Row2) < 2.50):
                return False,Status
            else:
                List_Of_Match.append(r'(?='+con+' Wage vs. W\/H).*\n(.*\n){2}')
    if Is_Match_Found:
        Is_Any_Con_Match = False
        for con in List_Of_Check:
            Temp_Data = Data
            Is_Page = True
            while Is_Page:
                Emp_Detail = 'Quarter End Exception Report: Employee Detail'
                pos1 = Temp_Data.find(Emp_Detail)
                if pos1 != -1:
                    Temp_Data = Temp_Data[pos1+len(Emp_Detail):]
                else:
                    break
                Match = re.search(r'(?<='+ con +' Wage vs\. W\/H).*\n.*((\n.*)*)', Temp_Data)
                if Match != None:
                    Is_Any_Con_Match = True
                    Match = Match.group(1).strip().split('\n')
                    Has_Row = False
                    for row in Match:
                        row = row.strip()
                        Match = re.search(r'^(\d+).*', row)
                        if Match != None:
                            Match = re.sub(r'\s\s+', '\t', Match.group(0))
                            Match = Match.split('\t')
                            if len(Match) >= 6:
                                List_Of_Match.append(row.replace("(","\(").replace(")","\)"))
                                Has_Row = True
                                Difference = Match[len(Match)-1].strip()
                                if not (float(Difference) < 1):
                                    return False,Status,[]
                            else:
                                return False,Status,[]
                        else:
                            break
                    if not Has_Row:
                        return False,Status,[]
                else:
                    break
        if Is_Any_Con_Match:
            return True,Status,List_Of_Match
    return False,Status,[]




def Main_Fun(MyArg):
    Conditions_List = [ESL_FP, FUI_Finalized_FP, IN_County_FP, Taxes_On_Hold_FP, Live_in_Locals_FP, Invalid_SSN_FP,
                       ZZERC_NEG_Tax_FP,SUI_Dif_FP,Mid_QTR_Start_FP,Successor_FP,NVQBC_FP,FUI_SUI_Exempt_FP,
                       NIA_FP,Total_Agr_FP,Multi_State_FP,Clergy_FP,_3PS_FP,WV_FP_AND_CO_FP,FUI_SUI_Rounding_FP]
    Data = MyArg[0]
    Result = False
    List_Of_Results = []
    for fun in Conditions_List:
        try:
            Result,Status,List_Of_Matches_Found = fun(Data)
            if not(Result) and Status == "Condition Match":
                print('False positive condition does not satisfied based on the scenario: ' + fun.__name__)
                return False, fun.__name__ + ' condition not satisfied'
            elif Result:
                Data = replace_Text(Data,List_Of_Matches_Found)
                List_Of_Results.insert(len(List_Of_Results),fun.__name__)
        except:
            Result = False
    if len(List_Of_Results) > 0:
        List_Of_Results = '/'.join(List_Of_Results)
        print('False Positive !!\n(' + List_Of_Results+ ') condition(s) satisfied')
        Is_any_other_conditions_found = check_for_other_conditions(Data)
        if Is_any_other_conditions_found:
            print('False Positive conditions does not satisfied !')
            return False, '(' +List_Of_Results+ ') condition(s) satisfied.. but some other reasons found !'
        else:
            return True, '(' +List_Of_Results+ ') condition(s) satisfied'
    else:
        print('False Positive conditions does not satisfied !')
        return False,'False Positive conditions does not satisfied !'


# if __name__ == '__main__':
#     File = open(r"E:\Salix Data\Paycor\Paycor 3 - Tax Editing\Input\Input\Temp Text\Test.txt",mode = 'r')
#     Data = File.read()
#     Main_Fun([Data])
