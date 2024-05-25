from common.types import BaseEnum


class Gender(BaseEnum):
    Male = "Male"
    Female = "Female"


class ProblemType(BaseEnum):
    LowMotivation = "Low Motivation (I want to be more productive)"
    LowConfidence = "Low Confidence (I want to build self-esteem)"
    MissingSomeone = "Missing Someone (I want to live on without someone who is really dear to me)"
    HighStress = "High Stress (I want to reduce stress in my life)"
    CannotSayNo = "Cannot say NO (I want to learn how to say NO to people)"
    Other = "Other (anything else that is important to me?)"
