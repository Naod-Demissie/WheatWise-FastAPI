from enum import Enum


class RegionTypeEnum(Enum):
    Addis_Ababa = "Addis Ababa"
    Afar = "Afar"
    Amhara = "Amhara"
    Benishangul_Gumuz = "Benishangul-Gumuz"
    Dire_Dawa = "Dire Dawa"
    Gambela = "Gambela"
    Harari = "Harari"
    Oromia = "Oromia"
    Sidama = "Sidama"
    Somali = "Somali"
    South_West_Ethiopia_Peoples = "SWEP's Region"
    Southern_Nations_Nationalities_and_Peoples = "SNNP's Region"
    Tigray = "Tigray"


class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class UserTypeEnum(Enum):
    USER = "User"
    ADMIN = "Admin"
    SYSTEM_ADMIN = "System Admin"


class SexTypeEnum(Enum):
    MALE = "male"
    FEMALE = "female"


class DiseaseTypeEnum(Enum):
    BROWN_RUST = "Brown Rust"
    YELLOW_RUST = "Yellow Rust"
    SEPTORIA = "Septoria"
    HEALTHY = "Healthy"
    MILDEW = "Mildew"
    OTHER = "Other"
