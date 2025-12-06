import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'merchant-onboarding-ai-project', 'database'))
from models import MerchantApplication, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

# Update business names
updates = [
    ('APP_20251105_143240', 'TechFlow Solutions LLC'),
    ('APP_20251105_141005', 'Green Valley Organics'),
    ('APP_20251105_130016', 'Metro Coffee Roasters'),
    ('APP_20251105_125634', 'Digital Marketing Pro'),
    ('APP_20251105_125448', 'Coastal Construction Co')
]

session = Session()
for app_id, name in updates:
    app = session.query(MerchantApplication).filter_by(id=app_id).first()
    if app:
        app.business_name = name
        print(f"Updated {app_id}: {name}")

session.commit()
session.close()
print("Done!")