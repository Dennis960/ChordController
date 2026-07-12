from enum import Enum


class TrainerSection(Enum):
    GUIDED_COURSE = "Guided Course"
    PRACTICE = "Practice"


class LearningStage(Enum):
    BEGINNER = "Beginner"
    EARLY = "Early"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
