from simulator.scheduler import Scheduler, PMImp, OldAndForgotten


def recognizeSchedulerName(name):
    if name == "DM":
        return Scheduler.DM
    if name == "EDF":
        return Scheduler.EDF
    elif name == "PTEDF":
        return Scheduler.PTEDF
    elif name == "PALLF":
        return OldAndForgotten.PALLF
    elif name == "PMImp":
        return PMImp.PMImp
    elif name == "CKEDF":
        return OldAndForgotten.ChooseKeepEDF
    elif name == "LLF":
        return Scheduler.LLF
    elif name == "Meumeu":
        return Scheduler.ExhaustiveFixedPriority  # similar results
    elif name == "ExhaustiveFTP":
        return Scheduler.ExhaustiveFixedPriority
    return None
