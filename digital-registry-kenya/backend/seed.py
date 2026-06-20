from app import create_app
from models import db, User, Birth, Death
from datetime import date
import random
from werkzeug.security import generate_password_hash

K_COUNTIES = {
    "Nairobi": ["Westlands", "Dagoretti North", "Dagoretti South", "Langata", "Kibra", "Roysambu", "Kasarani", "Ruaraka", "Embakasi South", "Embakasi North", "Embakasi Central", "Embakasi East", "Embakasi West", "Makadara", "Kamukunji", "Starehe", "Mathare"],
    "Mombasa": ["Mvita", "Kisauni", "Nyali", "Likoni", "Jomvu", "Changamwe"],
    "Kisumu": ["Kisumu Central", "Kisumu East", "Kisumu West", "Seme", "Nyando", "Muhoroni", "Nyakach"],
    "Kiambu": ["Kiambu", "Kikuyu", "Ruiru", "Thika", "Juja", "Githunguri", "Lari", "Limuru"],
    "Nakuru": ["Nakuru Town East", "Nakuru Town West", "Naivasha", "Gilgil", "Molo", "Njoro", "Rongai", "Bahati", "Kuresoi North", "Kuresoi South", "Subukia"]
}

def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin', county='Nairobi')
        reg1 = User(username='registrar1', password_hash=generate_password_hash('reg123'), role='registrar', county='Nairobi')
        reg2 = User(username='registrar2', password_hash=generate_password_hash('reg123'), role='registrar', county='Mombasa')
        db.session.add_all([admin, reg1, reg2])
        
        first_names_m = ["John", "James", "Peter", "Paul", "Samuel", "Daniel", "David", "Joseph", "Michael", "Charles"]
        first_names_f = ["Mary", "Jane", "Ann", "Joyce", "Grace", "Faith", "Hope", "Mercy", "Sarah", "Esther"]
        last_names = ["Mwangi", "Otieno", "Kamau", "Akinyi", "Njoroge", "Wanjiku", "Wambui", "Ochieng", "Omondi", "Chebet"]
        causes = ["Malaria", "Pneumonia", "Road Accident", "Cancer", "Heart Disease", "Stroke", "Tuberculosis", "HIV/AIDS", "Diabetes", "Maternal Death"]
        
        reg_counter = 1000
        births = []
        deaths = []
        for i in range(50):
            gender = random.choice(['Male', 'Female'])
            if gender == 'Male':
                child_name = random.choice(first_names_m) + " " + random.choice(last_names)
            else:
                child_name = random.choice(first_names_f) + " " + random.choice(last_names)
            county = random.choice(list(K_COUNTIES.keys()))
            sub_county = random.choice(K_COUNTIES[county])
            dob = date(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28))
            birth = Birth(
                registration_number=f"BRN-{reg_counter}",
                child_name=child_name,
                gender=gender,
                date_of_birth=dob,
                county=county,
                sub_county=sub_county,
                mother_name="Mama " + child_name.split()[0],
                father_name="Baba " + child_name.split()[0],
            )
            reg_counter += 1
            births.append(birth)
            
            if i % 3 == 0:
                death_gender = random.choice(['Male', 'Female'])
                dname = (random.choice(first_names_m if death_gender == 'Male' else first_names_f) + " " + random.choice(last_names))
                death_dob = date(random.randint(1940, 2000), random.randint(1, 12), random.randint(1, 28))
                death_date = date(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28))
                death = Death(
                    registration_number=f"DRN-{reg_counter}",
                    deceased_name=dname,
                    gender=death_gender,
                    date_of_birth=death_dob,
                    date_of_death=death_date,
                    cause_of_death=random.choice(causes),
                    county=county,
                    sub_county=sub_county,
                    informant_name="Informant " + dname.split()[0]
                )
                reg_counter += 1
                deaths.append(death)
        
        db.session.add_all(births)
        db.session.add_all(deaths)
        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed()
    