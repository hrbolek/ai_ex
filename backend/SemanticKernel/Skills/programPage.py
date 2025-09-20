
from typing import TypedDict, Optional, List, Any, Annotated
import uuid
import datetime


class ProgramInputFilter(TypedDict, total=False):


    # Filter method
    _or: Optional[List["ProgramInputFilterOr"]]

    # Filter method
    _and: Optional[List["ProgramInputFilterAnd"]]

    # Filter method
    id: Optional["UuidFilter"]

    # Filter method
    name: Optional["StrFilter"]




class ProgramInputFilterOr(TypedDict, total=False):


    # Filter method
    _and: Optional[List["ProgramInputFilterAnd"]]

    # Filter method
    id: Optional["UuidFilter"]

    # Filter method
    name: Optional["StrFilter"]




class ProgramInputFilterAnd(TypedDict, total=False):


    # Filter method
    _or: Optional[List["ProgramInputFilterOr"]]

    # Filter method
    id: Optional["UuidFilter"]

    # Filter method
    name: Optional["StrFilter"]




class UuidFilter(TypedDict, total=False):


    # operation for select.filter() method
    _eq: Optional[uuid.UUID]

    # operation for select.filter() method
    _in: Optional[List[uuid.UUID]]




class StrFilter(TypedDict, total=False):


    # operation for select.filter() method
    _eq: Optional[str]

    # operation for select.filter() method
    _le: Optional[str]

    # operation for select.filter() method
    _lt: Optional[str]

    # operation for select.filter() method
    _ge: Optional[str]

    # operation for select.filter() method
    _gt: Optional[str]

    # operation for select.filter() method
    _like: Optional[str]

    # operation for select.filter() method
    _ilike: Optional[str]

    # operation for select.filter() method
    _startswith: Optional[str]

    # operation for select.filter() method
    _endswith: Optional[str]






from typing import TypedDict, Optional, List, Any, Annotated
import uuid
import datetime


class ProgramGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # Admissions for this program
    admissions: List["AdmissionGQLModel"]

    # Name of program
    name: Optional[str]

    # Eng. name of program
    nameEn: Optional[str]

    # Program subjects
    subjects: List["SubjectGQLModel"]

    # students
    students: List["StudentGQLModel"]

    # guarantors of programme
    groupId: Optional[uuid.UUID]

    # guarantors of programme
    guarantors: Optional["GroupGQLModel"]

    # Foreign key referencing the group (e.g., faculty or department) that is officially authorized to deliver this accredited study program.
    licencedGroupId: Optional[uuid.UUID]

    # The group (e.g., faculty or department) that is officially authorized to deliver this accredited study program.
    licencedGroup: Optional["GroupGQLModel"]

    # type of programme
    typeId: Optional[uuid.UUID]

    # type of pragramme
    type: Optional["ProgramTypeGQLModel"]




class UserGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # All related external ids
    externalIds: List["ExternalIdGQLModel"]

    # studies, aka what user is studying (with state)
    studies: List["StudentGQLModel"]

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # Full name (if in database)  Celé jméno (pokud je v databázi)
    name: Optional[str]

    # User's name (like John)  Jméno uživatele (např. John)
    givenname: Optional[str]

    # Middle name  Střední jméno
    middlename: Optional[str]

    # Email address  Emailová adresa
    email: Optional[str]

    # User's first name (like John)  Křestní jméno uživatele (např. John)
    firstname: Optional[str]

    # User's family name (like Obama)  Rodinné jméno uživatele (např. Obama)
    surname: Optional[str]

    # User validity status  Stav platnosti uživatele
    valid: Optional[bool]

    # Account start date  Datum zahájení účtu
    startdate: Optional[datetime.datetime]

    # Account end date  Datum ukončení účtu
    enddate: Optional[datetime.datetime]

    # User type identifier  Identifikátor typu uživatele
    typeId: Optional[uuid.UUID]

    # List of memberships associated with the user  Seznam členství spojených s uživatelem
    memberships: List["MembershipGQLModel"]

    # Deprecated: list of memberships (use memberships)  Zastaralé: seznam členství (použijte memberships)
    membership: List["MembershipGQLModel"]

    # Roles assigned to the user  Role přiřazené uživateli
    roles: List["RoleGQLModel"]

    # Checks if the current record belongs to the logged-in user  Zjistí, zda záznam patří přihlášenému uživateli
    isThisMe: bool

    # Fetches roles related to the user  Načte role vztažené k uživateli
    rolesOn: List["RoleGQLModel"]

    # Performs GDPR compliance check  Provádí kontrolu souladu s GDPR
    gdpr: Optional[str]

    # Concatenates user's name parts into full name  Spojí části jména uživatele do celého jména
    fullname: Optional[str]

    # Retrieves a list of groups of a specified type where the user is a member  Načte seznam skupin daného typu, kde je uživatel členem
    memberOf: List["GroupGQLModel"]




class ExternalIdGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # Inner id
    innerId: Optional[uuid.UUID]

    # Outer id
    outerId: Optional[uuid.UUID]

    # Type of id
    type: Optional["ExternalIdTypeGQLModel"]

    # Type name of id
    typeName: Optional[str]

    # html link
    link: Optional[str]




class RBACObjectGQLModel(TypedDict, total=False):


    # id
    id: uuid.UUID

    # Roles associated with this RBAC
    roles: List["RoleGQLModel"]

    # If logged user is authorized to operation on rbacobject_id
    userCanWithState: Optional[bool]

    # If logged user is authorized to operation on rbacobject_id
    userCanWithoutState: Optional[bool]




class RoleGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # If the user still holds this role  Jestli uživatel tuto roli stále zastává
    valid: Optional[bool]

    # Indicates if this role is assigned as deputy  Ukazuje, zda je tato role přiřazena jako zástupce
    deputy: Optional[bool]

    # The date when the user assumed this role  Datum, kdy uživatel tuto roli převzal
    startdate: Optional[datetime.datetime]

    # The date when the user was removed from this role  Datum, kdy byl uživatel odebrán z této role
    enddate: Optional[datetime.datetime]

    # Identifier of the role type  Identifikátor typu role
    roletypeId: Optional[uuid.UUID]

    # Identifier of the user who holds this role  Identifikátor uživatele, který tuto roli zastává
    userId: Optional[uuid.UUID]

    # Identifier of the group to which this role belongs  Identifikátor skupiny, ke které tato role patří
    groupId: Optional[uuid.UUID]

    # Role type detail (e.g. Dean)  Detail typu role (např. Dekan)
    roletype: Optional["RoleTypeGQLModel"]

    # User associated with this role  Uživatel spojený s touto rolí
    user: Optional["UserGQLModel"]

    # Group in which the role is assigned  Skupina, ve které je role přiřazena
    group: Optional["GroupGQLModel"]




class RoleTypeGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # Materialized path technique, not implemented
    path: Optional[str]

    # Unique identifier for the master type of this group type
    mastertypeId: Optional[uuid.UUID]

    # Detailed information about the master type that this group type is associated with
    mastertype: Optional["RoleTypeGQLModel"]

    # List of subtypes associated with this group type
    subtypes: Optional[List["RoleTypeGQLModel"]]




class GroupGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # All related external ids
    externalIds: List["ExternalIdGQLModel"]

    # List of accredited study programs that are implemented (offered and delivered) by this organizational unit (typically a faculty).
    accreditedPrograms: List["ProgramGQLModel"]

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # Group's email address.    Emailová adresa skupiny.
    email: Optional[str]

    # Abbreviation or short name for the group.    Zkratka nebo krátký název skupiny.
    abbreviation: Optional[str]

    # Start date of the group's activity.    Datum zahájení aktivity skupiny.
    startdate: Optional[datetime.datetime]

    # End date of the group's activity (if applicable).    Datum ukončení aktivity skupiny (je-li relevantní).
    enddate: Optional[datetime.datetime]

    # Identifier for the group's type.    Identifikátor typu skupiny.
    grouptypeId: Optional[uuid.UUID]

    # The type of the group represented as an object (e.g., Department).    Typ skupiny reprezentovaný jako objekt (např. oddělení).
    grouptype: Optional["GroupTypeGQLModel"]

    # List of directly subordinate groups.    Seznam přímo podřízených skupin.
    subgroups: List["GroupGQLModel"]

    # Identifier of the master (commanding) group.    Identifikátor nadřazené (řídící) skupiny.
    mastergroupId: Optional[uuid.UUID]

    # The master group that commands this group.    Nadřazená skupina, která řídí tuto skupinu.
    mastergroup: Optional["GroupGQLModel"]

    # Materialized path representing the group's hierarchical location.    Materializovaná cesta reprezentující umístění skupiny v hierarchii.
    path: Optional[str]

    # List of membership records for users in this group.    Seznam záznamů členství uživatelů v této skupině.
    memberships: List["MembershipGQLModel"]

    # List of roles defined for the group.    Seznam rolí definovaných pro tuto skupinu.
    roles: List["RoleGQLModel"]

    # Indicates whether the group is currently active.    Indikuje, zda je skupina aktuálně aktivní.
    valid: Optional[bool]

    # Returns the hierarchy of master groups from the topmost to the immediate master.    Vrací hierarchii nadřazených skupin od nejvyšší po bezprostředního nadřízeného.
    mastergroups: List["GroupGQLModel"]

    # Aggregates roles along the group's hierarchical path.    Agreguje role podél hierarchie skupiny.
    rolesOn: List["RoleGQLModel"]




class GroupTypeGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # Materialized path technique, not implemented
    path: Optional[str]

    # Unique identifier for the master type of this group type
    mastertypeId: Optional[uuid.UUID]

    # Detailed information about the master type that this group type is associated with
    mastertype: Optional["GroupTypeGQLModel"]

    # List of subtypes associated with this group type
    subtypes: Optional[List["GroupTypeGQLModel"]]




class MembershipGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # Returns the RBAC object associated with this membership.  Vrací RBAC objekt spojený s tímto členstvím.
    rbacobject: Optional["RBACObjectGQLModel"]

    # ID of associated user.  ID spojeného uživatele.
    userId: Optional[uuid.UUID]

    # ID of associated group.  ID spojené skupiny.
    groupId: Optional[uuid.UUID]

    # Indicates whether the membership is valid.  Indikuje, zda je členství platné.
    valid: Optional[bool]

    # Date when the membership begins.  Datum začátku členství.
    startdate: Optional[datetime.datetime]

    # Date when the membership ends.  Datum ukončení členství.
    enddate: Optional[datetime.datetime]

    # User object associated with the membership.  Objekt uživatele spojený s členstvím.
    user: Optional["UserGQLModel"]

    # Group object associated with the membership.  Objekt skupiny spojený s členstvím.
    group: Optional["GroupGQLModel"]




class ExternalIdTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    
    name: Optional[str]

    
    nameEn: Optional[str]

    # who changed this entity
    masterId: Optional[uuid.UUID]

    
    urlformat: Optional[str]

    # Master type of this type, allows tree organization of types
    masterType: Optional["ExternalIdTypeGQLModel"]

    # subtypes
    subTypes: List["ExternalIdTypeGQLModel"]




class StudentGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # Platby za přijímací řízení
    payment: Optional["PaymentGQLModel"]

    # Platby za přijímací řízení
    myId: Optional[uuid.UUID]

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # id of the user
    userId: Optional[uuid.UUID]

    # who is student
    student: Optional["UserGQLModel"]

    
    programId: Optional[uuid.UUID]

    # which program student is studying
    program: Optional["ProgramGQLModel"]

    
    stateId: Optional[uuid.UUID]

    # semester of study
    semesterNumber: Optional[int]

    # State of the user study
    state: Optional["StateGQLModel"]

    # given grades
    evaluations: List["EvaluationGQLModel"]




class PaymentGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # unikátní identifikátor platby vystavený bankou (link do banky)
    bankUniqueData: Optional[str]

    # uvedený variabilní symbol
    variableSymbol: Optional[str]

    # zaplacená částka
    amount: Optional[float]

    # Generální platební podmínky
    paymentInfoId: Optional[uuid.UUID]

    # identifikovaná přihláška / student
    studentId: Optional[uuid.UUID]

    # Informace o platebních podmínkách
    paymentInfo: Optional["PaymentInfoGQLModel"]

    # Student, který měl platbu provést nebo platbu provedl
    student: Optional["StudentGQLModel"]




class PaymentInfoGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # číslo účtu s kódem banky za lomítkem
    accountNumber: Optional[str]

    # specifický symbol
    specificSymbol: Optional[str]

    # konstantní symbol
    constantSymbol: Optional[str]

    # IBAN code
    IBAN: Optional[str]

    # SWIFT bank code
    SWIFT: Optional[str]

    # Částka k zaplacení
    amount: Optional[float]

    # Všechny platby, které proběhly nebo byly uznány jako splnění těchto platebních podmínek
    payments: List["PaymentGQLModel"]

    # Přijímací řízení, kte kterému se tyto platební podmínky vztahují
    admission: Optional["AdmissionGQLModel"]




class AdmissionGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # name en
    nameEn: Optional[str]

    # stav přijímacího řízení
    stateId: Optional[uuid.UUID]

    # Program, pro který je přijímací řízení vypsáno
    programId: Optional[uuid.UUID]

    # platební podmínky
    paymentInfoId: Optional[uuid.UUID]

    # Od kdy lze podávat přihlášky
    applicationStartDate: Optional[datetime.datetime]

    # Poslední možnost podání přihlášky
    applicationLastDate: Optional[datetime.datetime]

    # Konec přijímacího řízení
    endDate: Optional[datetime.datetime]

    # Do kdy lze doložit splnění podmínek
    conditionDate: Optional[datetime.datetime]

    # Do kdy lze zaplatit poplatek
    paymentDate: Optional[datetime.datetime]

    # Prodloužená lhůta pro doložení splnění podmínek
    conditionExtendedDate: Optional[datetime.datetime]

    # Lhůta do kdy lze požádat o proudloužení pro doložení splnění podmínek
    requestConditionExtendDate: Optional[datetime.datetime]

    # Lhůta do kdy lze požádat o specifické podmínky přijímacího řízení
    requestExtraConditionsDate: Optional[datetime.datetime]

    # Lhůta do kdy lze požádat o extra termín přijímacích zkoušek
    requestExtraDateDate: Optional[datetime.datetime]

    # První možný den přijímacích zkoušek
    examStartDate: Optional[datetime.datetime]

    # Poslední možný den přijímacích zkoušek
    examLastDate: Optional[datetime.datetime]

    # Den zápisu
    studentEntryDate: Optional[datetime.datetime]

    # Program, ke kterému je přijímací řízení
    program: Optional["ProgramGQLModel"]

    # Pokyny k platbě
    paymentInfo: Optional["PaymentInfoGQLModel"]

    # Stav přijímacího řízení
    state: Optional["StateGQLModel"]




class StateGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # Id of state machine
    statemachineId: Optional[uuid.UUID]

    # Id of roletype list
    writerslistId: Optional[uuid.UUID]

    # list of roles which can read at this state
    readerslistId: Optional[uuid.UUID]

    # Owing state machine
    statemachine: Optional["StateMachineGQLModel"]

    # position in list of states
    order: Optional[int]

    # Transitions linked into thist state
    sources: List["StateTransitionGQLModel"]

    # Transitions going out of this state
    targets: List["StateTransitionGQLModel"]

    # All roletypes associated with this state, all roles will be enabled for update
    roletypes: List["RoleTypeGQLModel"]

    # If logged user is authorized to operation on rbacobject_id
    userCan: Optional[bool]




class StateMachineGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # All states associated with this state machine
    states: List["StateGQLModel"]

    # All states associated with this state machine
    transitions: List["StateTransitionGQLModel"]

    # state machine type id
    typeId: Optional[uuid.UUID]




class StateTransitionGQLModel(TypedDict, total=False):


    # Primary key of the entity.  Primární klíč entity.
    id: uuid.UUID

    # Timestamp of the last change.  Časové razítko poslední změny.
    lastchange: Optional[datetime.datetime]

    # Date and time when the entity was created.  Datum a čas vytvoření entity.
    created: Optional[datetime.datetime]

    # Identifier of the user who created this entity.  Identifikátor uživatele, který vytvořil tuto entitu.
    createdbyId: Optional[uuid.UUID]

    # Identifier of the user who last modified this entity.  Identifikátor uživatele, který naposledy upravil tuto entitu.
    changedbyId: Optional[uuid.UUID]

    # Reference to the RBAC object governing permissions.  Reference na RBAC objekt, který řídí oprávnění.
    rbacobjectId: Optional[uuid.UUID]

    # The user who created this entity.  Uživatel, který vytvořil tuto entitu.
    createdby: Optional["UserGQLModel"]

    # The user who last modified this entity.  Uživatel, který naposledy upravil tuto entitu.
    changedby: Optional["UserGQLModel"]

    # The RBAC object associated with this entity.  RBAC objekt spojený s touto entitou.
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    
    sourceId: Optional[uuid.UUID]

    # Going from state
    source: Optional["StateGQLModel"]

    
    targetId: Optional[uuid.UUID]

    # Going to state
    target: Optional["StateGQLModel"]

    
    statemachineId: Optional[uuid.UUID]

    # Owing state machine
    statemachine: Optional["StateMachineGQLModel"]




class EvaluationGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # index of attempt
    order: Optional[int]

    # given points for this exam
    points: Optional[int]

    # True if student passed this exam
    passed: Optional[bool]

    # description given to student and exam
    description: Optional[str]

    # given grade / mark
    grade: Optional[str]

    # id of the student
    studentId: Optional[uuid.UUID]

    # student who is examined
    student: Optional["StudentGQLModel"]

    # who examined
    examinerId: Optional[uuid.UUID]

    # Who examined
    examiner: Optional["UserGQLModel"]

    # to which semester / subject this examination belongs
    semesterId: Optional[uuid.UUID]

    # semester to which this examination belongs to
    semester: Optional["SemesterGQLModel"]

    # Exam plan
    examId: Optional[uuid.UUID]

    # related exam conditions
    exam: Optional["ExamGQLModel"]

    # the event when exam happened and evaluation has been stored
    eventId: Optional[uuid.UUID]

    
    event: Optional["EventGQLModel"]

    # id of exam which this is part
    parentId: Optional[uuid.UUID]

    # exam of which is this part
    parent: Optional["EvaluationGQLModel"]

    # sub parts of this evaluation
    parts: List["EvaluationGQLModel"]

    # Formal given grade
    classificationlevelId: Optional[uuid.UUID]




class SemesterGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # order in same subject
    order: Optional[int]

    # True if every student must pass this subject
    mandatory: Optional[bool]

    # credits
    credits: Optional[int]

    # subject id
    classificationtypeId: Optional[uuid.UUID]

    # subject id
    subjectId: Optional[uuid.UUID]

    # subject
    subject: Optional["SubjectGQLModel"]

    # subjects vhcin must be studied at first
    prerequisites: List["SubjectGQLModel"]

    # Semester topics
    topics: List["TopicGQLModel"]

    # plans of study execution
    plans: List["StudyPlanGQLModel"]




class SubjectGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # subject name
    name: Optional[str]

    # subject name in english
    nameEn: Optional[str]

    # subject description
    description: Optional[str]

    # subject description in english
    descriptionEn: Optional[str]

    # program id
    programId: Optional[uuid.UUID]

    # program entity
    program: Optional["ProgramGQLModel"]

    # subject semesters
    semesters: List["SemesterGQLModel"]

    # guarantors of programme
    groupId: Optional[uuid.UUID]

    # guarantors of programme
    guarantors: Optional["GroupGQLModel"]




class TopicGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # topic name
    name: Optional[str]

    # topic name
    nameEn: Optional[str]

    # topic name
    order: Optional[int]

    # topic description
    description: Optional[str]

    # semester id
    semesterId: Optional[uuid.UUID]

    # semester
    semester: Optional["SemesterGQLModel"]

    # lessons
    lessons: List["LessonGQLModel"]




class LessonGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # how many virtual time units
    count: Optional[int]

    # to which topic belongs
    topicId: Optional[uuid.UUID]

    # to which topic belongs
    topic: Optional["TopicGQLModel"]

    
    typeId: Optional[uuid.UUID]

    
    type: Optional["LessonTypeGQLModel"]




class LessonTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # abbreviation
    abbr: Optional[str]




class StudyPlanGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # ID of Semester to which the plan is related
    semesterId: Optional[uuid.UUID]

    # Semester to which the plan is related
    semester: Optional["SemesterGQLModel"]

    # ID of classification conditions
    examId: Optional[uuid.UUID]

    # part of study plan
    lessons: List["StudyPlanLessonGQLModel"]

    # Exam Rules
    exam: Optional["ExamGQLModel"]

    # Time period when the plan will live
    eventId: Optional[uuid.UUID]

    # Time period when the plan will live
    event: Optional["EventGQLModel"]




class StudyPlanLessonGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # order in plan
    order: Optional[int]

    # lesson name
    name: Optional[str]

    # lesson name in english
    nameEn: Optional[str]

    # length in fictive units
    length: Optional[int]

    # id of event which has been planed for this lesson
    eventId: Optional[uuid.UUID]

    # event which has been planed for this lesson
    event: Optional["EventGQLModel"]

    # Topic to which the Lesson is related
    topicId: Optional[uuid.UUID]

    # Topic to which the Lesson is related
    topic: Optional["TopicGQLModel"]

    # Lesson type
    lessontypeId: Optional[uuid.UUID]

    # type of the lesson
    lessontype: Optional["LessonTypeGQLModel"]

    
    linkedWithId: Optional[uuid.UUID]

    # Plan which owns this lesson
    planId: Optional[uuid.UUID]

    
    plan: Optional["StudyPlanGQLModel"]

    # list of linked othe planned lessons
    linkedWith: List["StudyPlanLessonGQLModel"]

    # whos teach the lesson
    instructors: List["UserGQLModel"]

    # study groups
    studyGroups: List["GroupGQLModel"]

    # places for this lesson
    facilities: List["FacilityGQLModel"]




class EventGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # All related external ids
    externalIds: List["ExternalIdGQLModel"]

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Event name assigned by an administrator
    name: Optional[str]

    # Event eng name assigned by an administrator
    nameEn: Optional[str]

    # Event description
    description: Optional[str]

    # Event start date
    startdate: Optional[datetime.datetime]

    # Event end date
    enddate: Optional[datetime.datetime]

    # len
    duration_raw: Optional[Any]

    # where the event will happen
    place: Optional[str]

    # place where the event will happen
    facilityId: Optional[uuid.UUID]

    # place where the event will happen
    facility: Optional["FacilityGQLModel"]

    # reservations for this event
    reservations: List["EventFacilityReservationGQLModel"]

    # Event parent id
    mastereventId: Optional[uuid.UUID]

    # Event type id
    typeId: Optional[uuid.UUID]

    # Event type
    type: Optional["EventTypeGQLModel"]

    # Event invitations
    invitations: List["EventInvitationGQLModel"]

    # Event duration, implicitly in minutes
    duration: Optional[float]




class FacilityGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # All related external ids
    externalIds: List["ExternalIdGQLModel"]

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Facility name assigned by an administrator
    name: Optional[str]

    # Facility eng name assigned by an administrator
    nameEn: Optional[str]

    # Facility full name assigned by an administrator
    label: Optional[str]

    # Facility datetime 
    startdate: Optional[datetime.datetime]

    # Facility datetime 
    enddate: Optional[datetime.datetime]

    # Facility address
    address: Optional[str]

    # is the facility still valid
    valid: Optional[bool]

    # Facility's capacity
    capacity: Optional[int]

    # Facility geometry (SVG)
    geometry: Optional[str]

    # Facility geo address (WGS84+zoom)
    geolocation: Optional[str]

    # reservations for this event
    reservations: List["EventFacilityReservationGQLModel"]

    # Facility geo address (WGS84+zoom)
    groupId: Optional[uuid.UUID]

    # Facility geo address (WGS84+zoom)
    facilitytypeId: Optional[uuid.UUID]

    # Facility geo address (WGS84+zoom)
    masterFacilityId: Optional[uuid.UUID]

    # Facility type
    type: Optional["FacilityTypeGQLModel"]

    # Facility above this
    masterFacility: Optional["FacilityGQLModel"]

    # Facilities above this
    masterFacilities: List["FacilityGQLModel"]

    # Facilities inside facility (like buildings in an areal)
    subFacilities: List["FacilityGQLModel"]

    # Group
    group: Optional["GroupGQLModel"]




class EventFacilityReservationGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Event id
    eventId: Optional[uuid.UUID]

    # event linked to this reservation
    event: Optional["EventGQLModel"]

    # facility id
    facilityId: Optional[uuid.UUID]

    # facility linked to this reservation
    facility: Optional["FacilityGQLModel"]

    # state of reservation
    stateId: Optional[uuid.UUID]

    # state of this reservation
    state: Optional["StateGQLModel"]




class FacilityTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Facility type name assigned by an administrator
    name: Optional[str]

    # Facility type eng name assigned by an administrator
    nameEn: Optional[str]

    # Facility type parent
    parent: Optional["FacilityTypeGQLModel"]

    # Facility type parent id
    parentId: Optional[uuid.UUID]

    # Facility type children
    children: List["FacilityTypeGQLModel"]




class EventTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Event Type name
    name: Optional[str]

    # Event Type eng name
    nameEn: Optional[str]

    # Event Type description
    description: Optional[str]

    # Event Type parent id
    parentId: Optional[uuid.UUID]

    # Event Type parent
    parent: Optional["EventTypeGQLModel"]

    # Event Type children
    children: List["EventTypeGQLModel"]

    # Event Type events
    events: List["EventGQLModel"]




class EventInvitationGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who changed this entity
    changedby: Optional["UserGQLModel"]

    # rbac ruling object
    rbacobject: Optional["RBACObjectGQLModel"]

    # Event assigned to the invitation
    eventId: Optional[uuid.UUID]

    # User assigned to the invitation
    userId: Optional[uuid.UUID]

    # State assigned to the invitation
    stateId: Optional[uuid.UUID]

    # Event assigned to the invitation
    event: Optional["EventGQLModel"]

    # User assigned to the invitation
    user: Optional["UserGQLModel"]

    # State assigned to the invitation
    state: Optional["StateGQLModel"]




class ExamGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    
    name: Optional[str]

    
    nameEn: Optional[str]

    # extended description of exam conditions
    description: Optional[str]

    # extended description of exam conditions
    descriptionEn: Optional[str]

    # defined minimum points to pass the exam
    minScore: Optional[int]

    # defined maximum achievable points
    maxScore: Optional[int]

    # id of exam type
    typeId: Optional[uuid.UUID]

    # type of classification
    type: Optional["ClassificationTypeGQLModel"]

    # id of exam which is part
    parentId: Optional[uuid.UUID]

    # exam is part of exam
    parent: Optional["ExamGQLModel"]

    # exam parts
    parts: List["ExamGQLModel"]

    # evaluations of users during exams
    evaluations: List["EvaluationGQLModel"]

    # study plan which the exam belongs to
    planId: Optional[uuid.UUID]

    # study plan which the exam belongs to
    plan: Optional["StudyPlanGQLModel"]




class ClassificationTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # the name
    name: Optional[str]

    # the name
    nameEn: Optional[str]




class ProgramTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # level of programme
    levelId: Optional[uuid.UUID]

    # level of programme
    levelType: Optional["ProgramLevelTypeGQLModel"]

    # title given to student
    titleId: Optional[uuid.UUID]

    # title given to student
    titleType: Optional["ProgramTitleTypeGQLModel"]

    # language used in programme
    languageId: Optional[uuid.UUID]

    # language used in programme
    languageType: Optional["ProgramLanguageTypeGQLModel"]

    # teaching form, like presential, distance, etc.
    formId: Optional[uuid.UUID]

    # teaching form, like presential, distance, etc.
    formType: Optional["ProgramFormTypeGQLModel"]




class ProgramLevelTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]

    # how many years for standard study
    length: Optional[int]

    # 1 for Bc., 2 for Mgr. or NMgr., 3 for Ph.D., etc.
    priority: Optional[int]




class ProgramTitleTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]




class ProgramLanguageTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]




class ProgramFormTypeGQLModel(TypedDict, total=False):


    # primary key
    id: uuid.UUID

    # timestamp
    lastchange: Optional[datetime.datetime]

    # date & time of unit born
    created: Optional[datetime.datetime]

    # who created this entity
    createdbyId: Optional[uuid.UUID]

    # who changed this entity
    changedbyId: Optional[uuid.UUID]

    # rbac ruling object
    rbacobjectId: Optional[uuid.UUID]

    # who created this entity
    createdby: Optional["UserGQLModel"]

    # who created this entity
    changedby: Optional["UserGQLModel"]

    # rbac holds relations of user
    rbacobject: Optional["RBACObjectGQLModel"]

    # name
    name: Optional[str]

    # english name
    nameEn: Optional[str]






from semantic_kernel.functions import kernel_function
# import requests
# import json
from semantic_kernel.functions import KernelArguments

class programPageplugin:
    # @kernel_function(
    #     # description="Automaticaly generated skill for acces to graphql endpoint from sdl for Query.programPage."
    # )
    async def programPage(
        self,
        skip: Annotated[int, "how many entities will be ignored"] = 0,
        limit: Annotated[int, "how many entities will be taken"] = 10,
        orderby: Annotated[str, "name of field which will determite the order"] = None,
        # where: Annotated["ProgramInputFilter", "filter"] = None, 
        arguments: KernelArguments = None
    ) -> List["ProgramGQLModel"]:
        """
        
        returns study programs
        

        Parameters:
        
        - skip (int), optional: how many entities will be ignored
        
        - limit (int), optional: how many entities will be taken
        
        - orderby (str), optional: name of field which will determite the order
        
        - where ("ProgramInputFilter"), optional: filter
        
        Returns: List["ProgramGQLModel"]
        """
        endpoint = ""
        query = """
        query programPage($skip: Int, $limit: Int, $orderby: String, $where: ProgramInputFilter) {
  programPage(skip: $skip, limit: $limit, orderby: $orderby, where: $where) {
    id
    lastchange
    created
    createdbyId
    changedbyId
    rbacobjectId
    createdby {
      id
      externalIds {
        __typename
      }
      studies {
        __typename
      }
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      givenname
      middlename
      email
      firstname
      surname
      valid
      startdate
      enddate
      typeId
      memberships {
        __typename
      }
      membership {
        __typename
      }
      roles {
        __typename
      }
      isThisMe
      rolesOn {
        __typename
      }
      gdpr
      fullname
      memberOf {
        __typename
      }
    }
    changedby {
      id
      externalIds {
        __typename
      }
      studies {
        __typename
      }
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      givenname
      middlename
      email
      firstname
      surname
      valid
      startdate
      enddate
      typeId
      memberships {
        __typename
      }
      membership {
        __typename
      }
      roles {
        __typename
      }
      isThisMe
      rolesOn {
        __typename
      }
      gdpr
      fullname
      memberOf {
        __typename
      }
    }
    rbacobject {
      id
      roles {
        __typename
      }
    }
    admissions {
      id
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      nameEn
      stateId
      programId
      paymentInfoId
      applicationStartDate
      applicationLastDate
      endDate
      conditionDate
      paymentDate
      conditionExtendedDate
      requestConditionExtendDate
      requestExtraConditionsDate
      requestExtraDateDate
      examStartDate
      examLastDate
      studentEntryDate
      program {
        __typename
      }
      paymentInfo {
        __typename
      }
      state {
        __typename
      }
    }
    name
    nameEn
    subjects {
      id
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      nameEn
      description
      descriptionEn
      programId
      program {
        __typename
      }
      semesters {
        __typename
      }
      groupId
      guarantors {
        __typename
      }
    }
    students {
      id
      payment {
        __typename
      }
      myId
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      userId
      student {
        __typename
      }
      programId
      program {
        __typename
      }
      stateId
      semesterNumber
      state {
        __typename
      }
      evaluations {
        __typename
      }
    }
    groupId
    guarantors {
      id
      externalIds {
        __typename
      }
      accreditedPrograms {
        __typename
      }
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      nameEn
      email
      abbreviation
      startdate
      enddate
      grouptypeId
      grouptype {
        __typename
      }
      subgroups {
        __typename
      }
      mastergroupId
      mastergroup {
        __typename
      }
      path
      memberships {
        __typename
      }
      roles {
        __typename
      }
      valid
      mastergroups {
        __typename
      }
      rolesOn {
        __typename
      }
    }
    licencedGroupId
    licencedGroup {
      id
      externalIds {
        __typename
      }
      accreditedPrograms {
        __typename
      }
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      nameEn
      email
      abbreviation
      startdate
      enddate
      grouptypeId
      grouptype {
        __typename
      }
      subgroups {
        __typename
      }
      mastergroupId
      mastergroup {
        __typename
      }
      path
      memberships {
        __typename
      }
      roles {
        __typename
      }
      valid
      mastergroups {
        __typename
      }
      rolesOn {
        __typename
      }
    }
    typeId
    type {
      id
      lastchange
      created
      createdbyId
      changedbyId
      rbacobjectId
      createdby {
        __typename
      }
      changedby {
        __typename
      }
      rbacobject {
        __typename
      }
      name
      nameEn
      levelId
      levelType {
        __typename
      }
      titleId
      titleType {
        __typename
      }
      languageId
      languageType {
        __typename
      }
      formId
      formType {
        __typename
      }
    }
  }
}
        """
        variables = {
            "skip": skip, "limit": limit, "orderby": orderby, # "where": where
        }
        print(f"volam skill arguments: {arguments}")
        # extra_context = arguments["extra_context"]
        gqlclient = arguments["gqlclient"]
        rows = await gqlclient(query=query, variables=variables)
        # rows = await response.json()

        assert "data" in rows, f"the response does not contain the data key {rows}"
        data = rows["data"]
        return [ProgramGQLModel (**x) for x in data["programPage"]]
