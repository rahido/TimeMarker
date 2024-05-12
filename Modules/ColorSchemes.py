# Color schemes
# Functions return tuple ("light theme color", "dark theme color")

# Backgrounds (same as default customTkinter)
def getLayer1():
    return ("#ebebeb","#242424")
def getLayer2():
    return ("#cfcfcf","#333333")
def getLayer3():
    return ("#dbdbdb","#2b2b2b")
def getLayer4():
    return ("#C5C5C5","#262626")

# Texts. (inversed layer colors). Used with segmented buttons (tabs)
def getText1():
    return ("#242424","#ebebeb")

# Tabs
def getTabSelected():
    return ("#C6DCD9","#4a4a4a")
def getTabUnselected():
    return ("#cfcfcf","#2b2b2b")
def getTabSelectedHover():
    return getTabSelected()
def getTabUnselectedHover():
    return ("#A1A1A1","#3F3F3F")