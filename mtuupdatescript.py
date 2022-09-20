from datetime import date
serverlistodd = ["10.1.1.1","10.1.1.2"]
serverlisteven = ["10.1.1.3","10.1.1.4"]

def scriptgenerator(serverlist,evenodd):
    branch = evenodd
    today =date.today()
    with open("mtuscript.txt","a") as a:
        a.write(f"Today's ({today})script for {branch} branches is :\n")
        with open("mtuchangescopes.txt") as f:
            for line in f.readlines():
                if not line.strip():
                    continue
                else:
                    for i in serverlist:
                        a.write(f"Dhcp Server {i} Scope {line.strip()} set optionvalue 26 WORD \"1400\"\n")
        f.close()
    a.close()

def main():
    evenodd = input("even or odd list?(select e/o): ")
    if evenodd == "o":
        scriptgenerator(serverlistodd,"odd")
    if evenodd == "e":
        scriptgenerator(serverlisteven,"even")



main()

