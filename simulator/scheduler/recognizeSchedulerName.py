from simulator.scheduler import Scheduler, PMImp


def recognizeSchedulerName(name):
    if name == "EDF":
        return Scheduler.EDF
    elif name == "PTEDF":
        return Scheduler.PTEDF
    elif name == "PMImp":
        return PMImp.PMImp
    elif name == "LLF":
        return Scheduler.LLF
    elif name == "Meumeu":
        return Scheduler.ExhaustiveFixedPriority  # similar results
    elif name == "ExhaustiveFTP":
        return Scheduler.ExhaustiveFixedPriority
    return None
