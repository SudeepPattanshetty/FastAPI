from inspect import Parameter
from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

# Nested Model
class Address(BaseModel):
    city: str
    state: str
    pin: str

class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, title="Name of the Patient", description="name must be below 50 characters") ]
    email: EmailStr
    age: int
    # linkedin_url: AnyUrl
    weight: float = Field(gt=0, lt=100)
    height: float
    address: Address
    # married: bool = False
    # allergies: Optional[List[str]] = None
    contact_details: Dict[str, str]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/self.height**2, 2)
        return bmi

    @field_validator('email')
    @classmethod
    def email_validator(cls, value):

        valid_domains = ['hdfc.com', 'icici.com']
        domain_name = value.split('@')[-1]
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value

    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()

    @model_validator(mode='after')
    def validate_emergency_contact(cls, model): 
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError('Patients older than 60 must have an emergency contact')
        return model

def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.bmi)
    print(patient.contact_details)
    print(patient.address)
    print(patient.address.pin)
    print("Inserted data")

address_dict = {'city': 'Belagavi', 'state': 'Karnataka', 'pin': '590011'}
address1 = Address(**address_dict)

patient_info = {'name': 'Suresh', 'age': 65, 'email': 'abc@hdfc.com', 'contact_details': {'phone': '9108421719', 'emergency': '123456789'}, 'weight': 75.2, 'height': 1.72, 'address': address1}
patient1 = Patient(**patient_info)

temp = patient1.model_dump(include={'name'})

print(temp)

insert_patient_data(patient1)