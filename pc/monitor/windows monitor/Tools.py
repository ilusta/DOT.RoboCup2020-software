def isNumber(val):
    try:
        num = float(val)
        return True
    except ValueError:
        return False

def l_error(s):
    print("$e$" + str(s))

def l_warn(s):
    print("$w$" + str(s))

def l_log(s):
    print("$l$" + str(s))

def l_text(s):
    print("$t$" + str(s))

def l_complete(s):
    print("$c$" + str(s))
